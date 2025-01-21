from pymongo import errors
import os
import json
import sys
from datetime import datetime
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import models from flask_app
from flask_app.models import Team
from flask_app.config import db, client

# Step 7: Prepare team copying operations
teams = list(db.teams.find({"FantasyLeagueSeasonId": ObjectId("6786dddf987554debb88269e")}))
team_ids = []
for team_data in teams:
    team_ids.append(team_data["_id"])

db.fantasyLeagueSeasons.update_one(
    {"_id": ObjectId("6786dddf987554debb88269e")},
    {"$set": {"Teams": team_ids}}
)