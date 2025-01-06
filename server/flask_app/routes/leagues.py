from flask import jsonify, abort, Blueprint, session
import sys
import os
from bson.objectid import ObjectId
import traceback
from datetime import datetime

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import League

teams_collection = db.teams
leagues_collection = db.leagues

leagues_bp = Blueprint('leagues', __name__)

@leagues_bp.route('/<league_id>', methods=['GET'])
def get_teams_by_league_id(league_id):
    """Fetches a league by ID, including its teams."""
    from models import Team

    try:
        league = leagues_collection.find_one({"_id": ObjectId(league_id)})
        
        if not league:
            return jsonify({"error": "League not found."}), 404

        league = League(**league)

        if len(league.Teams) > 1:
            # Convert team IDs to ObjectId
            team_ids = [ObjectId(team_id) for team_id in league.Teams]
            
            # Query to fetch all teams in one go
            teams = list(teams_collection.find({"_id": {"$in": team_ids}}).sort("Placement"))

            team_dicts = []

            for team in teams:
                team_instance = Team(**team)
                team_dict = team_instance.to_dict()
                team_dict["Golfers"] = team_instance.get_all_current_golfers()
                team_dicts.append(team_dict)
            
            # Check if all teams were found
            if len(teams) != len(league.Teams):
                missing_ids = set(team_ids) - {team["_id"] for team in teams}
                return jsonify({"error": f'Some team IDs do not exist: {missing_ids}'}), 404

            league_dict = league.to_dict()
            league_dict["Teams"] = team_dicts

        league_dict["IsCommish"] = session.get('user_id') == league_dict["CommissionerId"]

        pro_season_id = league_dict["LeagueSettings"]["ProSeasonId"]
        pro_season_name = db.proSeasons.find_one({"_id": ObjectId(pro_season_id)})["LeagueName"]

        league_dict["LeagueSettings"]["ProSeason"] = pro_season_name

        # Is the fantasy league season over? True or False
        # Will input into league_dict[FantasySeasonActive]

        try:
            season_id = ObjectId(league_dict["CurrentFantasyLeagueSeasonId"])
        except (KeyError):
            # Handle missing or invalid ID
            season_id = None

        if season_id:
            # find the fantasy league season
            fantasy_league_season =  db.fantasyLeagueSeasons.find_one({
                "_id": ObjectId(season_id)
            })

            # If there is an associated fantasy league found, let's determine if it's over
            if fantasy_league_season:
                datetime_now = datetime.utcnow()

                if fantasy_league_season["Active"] and datetime_now > fantasy_league_season["EndDate"]:
                    db.fantasyLeagueSeasons.update_one(
                        {"_id": fantasy_league_season["_id"]},
                        {"$set": {"Active": False}}
                    )
                    league_dict["ActiveFantasySeason"] = False
                else:
                    league_dict["ActiveFantasySeason"] = fantasy_league_season["Active"]

        return jsonify(league_dict), 200
    except Exception as e:
        # Log the exception traceback for debugging purposes
        error_message = traceback.format_exc()  # Get the detailed traceback
        print(error_message)  # Print or log this somewhere for later analysis

        # Return a generic error response to the user
        return jsonify({"error": "An error occurred. Please try again later."}), 500

@leagues_bp.route('/create_league', methods=['POST'])
def create_league():
    pass