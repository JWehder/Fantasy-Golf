from bson import ObjectId
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import random
from datetime import datetime

app = FastAPI()

from flask_app.config import db

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


@app.websocket("/ws/{league_id}")
async def websocket_endpoint(websocket: WebSocket, league_id: str):
    await manager.connect(websocket, league_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming data if necessary
    except WebSocketDisconnect:
        manager.disconnect(websocket, league_id)

@app.post("/start-draft/{draft_id}")
async def start_draft(draft_id: str):
    from ..flask_app.models import Team

    draft = db.drafts.find_one({"_id": ObjectId(draft_id)})

    if not draft:
        return {"error": "Draft not found."}

    league_id = str(draft["LeagueId"])
    team_ids = draft.get("DraftOrder")

    league = db.leagues.find_one({"_id": draft["LeagueId"]})

    if not team_ids:
        # Generate random draft order if not provided
        teams = list(db.teams.find({"LeagueId": ObjectId(league_id)}))
        team_ids = [str(team["_id"]) for team in teams]
        random.shuffle(team_ids)
        db.drafts.update_one({"_id": ObjectId(draft_id)}, {"$set": {"DraftOrder": team_ids}})

    # Start the draft rounds
    total_rounds = draft["Rounds"]
    for round_num in range(1, total_rounds + 1):
        for team_id in team_ids:
            # Notify all clients about the current draft pick
            await manager.broadcast(
                league_id,
                {"event": "current_pick", "round": round_num, "team_id": team_id, }
            )

            # Simulate waiting for the team to pick
            await asyncio.sleep(10)  # Adjust as needed for real-time interaction

            team_instance = Team(**db.teams.find_one({"_id": ObjectId(team_id)}))

            # Notify all clients about the drafted golfer
            await manager.broadcast(
                league_id,
                {
                    "event": "player_drafted",
                    "round": round_num,
                    "team_id": team_id,
                    "golfer": golfer["Name"]
                }
            )

    # Mark draft as complete
    db.drafts.update_one({"_id": ObjectId(draft_id)}, {"$set": {"IsComplete": True, "EndDate": datetime.utcnow()}})
    await manager.broadcast(league_id, {"event": "draft_complete"})

    return {"message": "Draft completed successfully."}