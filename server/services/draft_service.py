import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from bson import ObjectId
import random
from ..flask_app.config import db

app = FastAPI()

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, league_id: str):
        await websocket.accept()
        if league_id not in self.active_connections:
            self.active_connections[league_id] = []
        self.active_connections[league_id].append(websocket)

    def disconnect(self, websocket: WebSocket, league_id: str):
        if league_id in self.active_connections:
            self.active_connections[league_id].remove(websocket)
            if not self.active_connections[league_id]:
                del self.active_connections[league_id]

    async def broadcast(self, league_id: str, message: dict):
        if league_id in self.active_connections:
            for connection in self.active_connections[league_id]:
                await connection.send_json(message)


manager = ConnectionManager()

# Shared asyncio.Event for coordinating draft picks
pick_event = asyncio.Event()
current_pick = None  # Variable to store the current pick details

@app.websocket("/ws/{league_id}")
async def websocket_endpoint(websocket: WebSocket, league_id: str):
    from ..flask_app.models import Team

    await manager.connect(websocket, league_id)
    try:
        while True:
            # Wait for a pick from the client
            data = await websocket.receive_json()
            if data.get("event") == "make_pick":
                team_id = data["team_id"]
                golfer_id = data["golfer_id"]

                # Process the draft pick
                golfer = db.golfers.find_one({"_id": ObjectId(golfer_id)})
                if not golfer:
                    await websocket.send_json({"error": "Golfer not found."})
                    continue

                # Update the team and mark golfer as drafted
                team_instance = Team(**db.teams.find_one(
                    {"_id": ObjectId(team_id)},
                ))

                team_instance.add_to_golfer_usage(golfer["_id"])

                # Notify all clients about the draft pick
                await manager.broadcast(
                    league_id,
                    {
                        "event": "player_drafted",
                        "team_id": team_id,
                        "golfer": {"id": golfer_id, "name": golfer["Name"]}
                    }
                )

                # Update the current pick and signal the event
                global current_pick
                current_pick = {"team_id": team_id, "golfer_id": golfer_id}
                pick_event.set()  # Signal that a pick has been made
    except WebSocketDisconnect:
        manager.disconnect(websocket, league_id)


@app.post("/start-draft/{draft_id}")
async def start_draft(draft_id: str):
    from ..flask_app.models import League, Team, Golfer

    draft = db.drafts.find_one({"_id": ObjectId(draft_id)})
    if not draft:
        return {"error": "Draft not found."}

    league_id = str(draft["LeagueId"])
    team_ids = draft.get("DraftOrder", [])

    league_instance = League(**db.leagues.find_one({"_id": ObjectId(league_id)}))
    league_settings = league_instance.LeagueSettings

    # find associated tournament based on period id
    period = db.periods.find_one({"_id": draft["PeriodId"]})

    # get all the golfers that are currently rostered
    unavailable_golfers_ids = league_instance.get_all_rostered_players()

    # filter query by golfers who are already on a team and a part of this tourney
    associated_golfer_tournament_details = db.golfertournamentdetails.find(
        {
            "TournamentId": period["TournamentId"],
            "GolferId": {"$nin": unavailable_golfers_ids}
        }
    )

    available_golfers_ids = [golfer["GolferId"] for golfer in associated_golfer_tournament_details]

    available_golfers = db.golfers.find({
        "GolferId": {"$in": available_golfers_ids}
    }).sort("OGWR")

    available_golfers_dicts = [Golfer(golfer).to_dict() for golfer in available_golfers]

    if not team_ids:
        teams = list(db.teams.find({"LeagueId": ObjectId(league_id)}))
        team_ids = [str(team["_id"]) for team in teams]
        random.shuffle(team_ids)
        db.drafts.update_one({"_id": ObjectId(draft_id)}, {"$set": {"DraftOrder": team_ids}})

    total_rounds = draft["Rounds"]
    for round_num in range(1, total_rounds + 1):
        for team_id in team_ids:
            # Notify all clients about the current pick
            await manager.broadcast(
                league_id,
                {"event": "current_pick", "round": round_num, "team_id": team_id}
            )

            # Wait for the pick or timeout
            try:
                global current_pick
                current_pick = None  # Reset the current pick
                pick_event.clear()  # Clear the event
                await asyncio.wait_for(pick_event.wait(), timeout=league_settings["SecondsPerDraftPick"])

                if current_pick and current_pick["team_id"] == team_id:
                    # Pick was successfully made
                    continue
            except asyncio.TimeoutError:
                # Auto-pick logic
                if available_golfers:
                    golfer = random.shuffle(available_golfers)
                    team_instance = Team(**db.teams.find_one(
                        {"_id": ObjectId(team_id)}
                    ))

                    num_of_current_golfers = len(team_instance.get_all_current_golfers())

                    team_instance.add_to_golfer_usage(golfer["_id"])
                              
                    if num_of_current_golfers :
                        await manager.broadcast(
                            league_id,
                            {
                                "event": "player_drafted",
                                "team_id": team_id,
                                "golfer": {"id": golfer["_id"], "name": golfer["Name"]}
                            }
                        )

    db.drafts.update_one({"_id": ObjectId(draft_id)}, {"$set": {"IsComplete": True}})
    await manager.broadcast(league_id, {"event": "draft_complete"})
    return {"message": "Draft completed successfully."}
