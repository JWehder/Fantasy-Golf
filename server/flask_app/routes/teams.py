from flask import jsonify, abort, Blueprint, request
import sys
import os
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import Team

teams_collection = db.teams

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    """Fetches a team by ID"""
    team_data = teams_collection.find_one({"_id": ObjectId(team_id)})
    if team_data:
        fetched_team = Team(**team_data)
        return jsonify({
            fetched_team
        })
    return abort(404, description="Team not found")

@teams_bp.route('/', methods=['POST'])
def insert_teams():
    """Inserts multiple teams into the database"""
    try:
        # Parse the JSON data from the request
        team_data = request.json.get("teams", [])
        
        if not team_data:
            return abort(400, description="No team data provided")

        # Optional: Add ObjectId conversion or data validation here
        for team in team_data:
            team["_id"] = ObjectId()  # Add an ObjectId if not already present

        # Insert data into the collection
        result = teams_collection.insert_many(team_data)

        return jsonify({
            "message": "Teams successfully inserted",
            "inserted_ids": [str(_id) for _id in result.inserted_ids]
        }), 201

    except Exception as e:
        return abort(500, description=f"An error occurred: {str(e)}")