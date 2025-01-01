from flask import Flask, jsonify, request
from flask_sock import Sock
from bson import ObjectId
import asyncio
import random
from ..flask_app.config import db, app
from ..flask_app.models import Team, DraftPick, League, Golfer, Draft

sock = Sock(app)

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    def connect(self, websocket, league_id):
        if league_id not in self.active_connections:
            self.active_connections[league_id] = []
        self.active_connections[league_id].append(websocket)

    def disconnect(self, websocket, league_id):
        if league_id in self.active_connections:
            self.active_connections[league_id].remove(websocket)
            if not self.active_connections[league_id]:
                del self.active_connections[league_id]

    def broadcast(self, league_id, message):
        if league_id in self.active_connections:
            disconnected_sockets = []
            for connection in self.active_connections[league_id]:
                try:
                    connection.send_json(message)
                except Exception:
                    disconnected_sockets.append(connection)
            for socket in disconnected_sockets:
                self.disconnect(socket, league_id)

manager = ConnectionManager()
pick_event = asyncio.Event()
current_pick = {"round": 1, "pick": 1}

# WebSocket endpoint for draft
@sock.route('/ws/<league_id>')
def websocket_endpoint(ws, league_id):
    manager.connect(ws, league_id)
    try:
        while True:
            data = ws.receive_json()
            if data.get("event") == "make_pick":
                team_id = data["team_id"]
                golfer_id = data["golfer_id"]
                draft_id = data["draft_id"]

                golfer = db.golfers.find_one({"_id": ObjectId(golfer_id)})
                if not golfer:
                    ws.send_json({"error": "Golfer not found."})
                    continue

                team_instance = Team(**db.teams.find_one({"_id": ObjectId(team_id)}))
                league = db.leagues.find_one({"_id": ObjectId(team_instance.LeagueId)})

                team_instance.add_to_golfer_usage(golfer["_id"])

                draft_pick = DraftPick(
                    TeamId=team_id,
                    GolferId=golfer["_id"],
                    RoundNumber=current_pick["round"],
                    PickNumber=current_pick["pick"],
                    LeagueId=ObjectId(league_id),
                    DraftId=ObjectId(draft_id),
                )
                draft_pick.save()
                draft_pick_dict = draft_pick.to_dict()

                manager.broadcast(
                    league_id,
                    {
                        "event": "player_drafted",
                        "team_id": team_id,
                        "draftPick": draft_pick_dict,
                        "timeRemaining": league["LeagueSettings"]["SecondsPerDraftPick"]
                    },
                )

                global current_pick
                current_pick["pick"] += 1
                pick_event.set()
    except Exception:
        manager.disconnect(ws, league_id)

# Start Draft Endpoint
@app.route('/start-draft/<draft_id>', methods=['POST'])
def start_draft(draft_id):
    draft = db.drafts.find_one({"_id": ObjectId(draft_id)})
    if not draft:
        return jsonify({"error": "Draft not found."}), 404

    draft_instance = Draft(**draft)
    league_id = str(draft["LeagueId"])
    team_ids = draft.get("DraftOrder", [])

    league_instance = League(**db.leagues.find_one({"_id": ObjectId(league_id)}))
    league_settings = league_instance.LeagueSettings

    period = db.periods.find_one({"_id": draft["PeriodId"]})
    unavailable_golfers_ids = league_instance.get_all_rostered_players()

    associated_golfers = db.golfertournamentdetails.find(
        {
            "TournamentId": period["TournamentId"],
            "GolferId": {"$nin": unavailable_golfers_ids},
        }
    )

    available_golfers_ids = [golfer["GolferId"] for golfer in associated_golfers]
    available_golfers = list(
        db.golfers.find({"_id": {"$in": available_golfers_ids}}).sort("OGWR")
    )

    if not team_ids:
        teams = list(db.teams.find({"LeagueId": ObjectId(league_id)}))
        team_ids = [str(team["_id"]) for team in teams]
        random.shuffle(team_ids)
        draft_instance.DraftOrder = team_ids
        draft_instance.save()

    total_rounds = draft["Rounds"]

    for round_num in range(1, total_rounds + 1):
        for pick_num, team_id in enumerate(team_ids, start=1):
            manager.broadcast(
                league_id,
                {
                    "event": "current_pick",
                    "round": round_num,
                    "team_id": team_id,
                    "pick": pick_num,
                },
            )

            try:
                global current_pick
                current_pick = {"round": round_num, "pick": pick_num}
                pick_event.clear()
                pick_event.wait(timeout=league_settings["SecondsPerDraftPick"] + 2)

                if current_pick["round"] == round_num and current_pick["pick"] == pick_num:
                    continue
            except asyncio.TimeoutError:
                if available_golfers:
                    golfer = available_golfers.pop(0)
                    team_instance = Team(**db.teams.find_one({"_id": ObjectId(team_id)}))
                    team_instance.add_to_golfer_usage(golfer["_id"])

                    draft_pick = DraftPick(
                        TeamId=team_id,
                        GolferId=golfer["_id"],
                        RoundNumber=round_num,
                        PickNumber=pick_num,
                        LeagueId=ObjectId(league_id),
                        DraftId=ObjectId(draft_id),
                    )
                    draft_pick.save()
                    manager.broadcast(
                        league_id,
                        {
                            "event": "player_drafted",
                            "team_id": team_id,
                            "round": round_num,
                            "pick": pick_num,
                            "draftPick": draft_pick.to_dict(),
                        },
                    )

    db.drafts.update_one({"_id": ObjectId(draft_id)}, {"$set": {"IsComplete": True}})
    manager.broadcast(league_id, {"event": "draft_complete"})
    return jsonify({"message": "Draft completed successfully."})
