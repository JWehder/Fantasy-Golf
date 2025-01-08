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

        league_instance = League(**league)

        current_fantasy_league_teams = list(db.teams.find({
            "FantasyLeagueSeasonId": league["CurrentFantasyLeagueSeasonId"]
        }))

        current_fantasy_league_season = db.fantasyLeagueSeasons.find_one({
            "_id": league["CurrentFantasyLeagueSeasonId"]
        })

        if len(current_fantasy_league_teams) > 1:
            team_dicts = []

            for team in current_fantasy_league_teams:
                team_instance = Team(**team)
                team_dict = team_instance.to_dict()
                team_dict["Golfers"] = team_instance.get_all_current_golfers()
                team_dicts.append(team_dict)
            
            # Check if all teams were found
            if len(current_fantasy_league_season["Teams"]) != len(current_fantasy_league_teams):
                missing_ids = set(current_fantasy_league_season["Teams"]) - {team["_id"] for team in current_fantasy_league_teams}
                return jsonify({"error": f'Some team IDs do not exist: {missing_ids}'}), 404

            league_dict = league_instance.to_dict()
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

            # If there is an associated fantasy league found, let's determine if it's over
            if current_fantasy_league_season:
                datetime_now = datetime.utcnow()

                if current_fantasy_league_season["Active"] and datetime_now > current_fantasy_league_season["EndDate"]:
                    db.fantasyLeagueSeasons.update_one(
                        {"_id": current_fantasy_league_season["_id"]},
                        {"$set": {"Active": False}}
                    )
                    league_dict["ActiveFantasySeason"] = False
                else:
                    league_dict["ActiveFantasySeason"] = current_fantasy_league_season["Active"]

        return jsonify(league_dict), 200
    except Exception as e:
        # Log the exception traceback for debugging purposes
        error_message = traceback.format_exc()  # Get the detailed traceback
        print(error_message)  # Print or log this somewhere for later analysis

        # Return a generic error response to the user
        return jsonify({"error": "An error occurred. Please try again later."}), 500

@leagues_bp.route('/<league_id>/fantasy_league_seasons/create_new_season', methods=['POST'])
def create_new_season(league_id):
    from bson import ObjectId

    user_id = session.get('user_id')

    # Fetch the league
    league = db.leagues.find_one({"_id": ObjectId(league_id)})

    old_fantasy_league_season_id = league["CurrentFantasyLeagueSeasonId"]

    if not league:
        return {"error": "League not found"}, 404

    if league["OwnerId"] != user_id:
        league_id = league["_id"]
        return {"error": f"You are unauthorized to access this action on {league_id}"}, 422
    
    league_instance = League(**league)

    new_fantasy_league_season_id = league_instance.transition_to_next_season()

    new_pro_season_id = league_instance.transition_to_next_pro_season()

    if old_fantasy_league_season_id == new_fantasy_league_season_id:
        return jsonify({
            "error": "The old fantasy league season ID is the same as the new one. Unable to transition to the next season."
        }), 400
    
    # Test that the current fantasy league season was created and the new fantasy league season id is correct
    current_fantasy_league_season = db.fantasyLeagueSeasons.find_one({
        "_id": ObjectId(league_instance.CurrentFantasyLeagueSeasonId)
    })

    if not current_fantasy_league_season:
        return {"error": "Current fantasy league season not found"}, 404

    
    return {"message": "New fantasy league season created successfully", "newSeasonId": str(new_fantasy_league_season_id), "newProSeasonId": new_pro_season_id}, 201
    
@leagues_bp.route('/<league_id>/users', methods=['GET'])
def get_leagues_users(league_id):
    """Retrieve users associated with the current league."""
    from models import User
    from bson.objectid import ObjectId  # To validate ObjectId if needed

    user_id = session.get('user_id')

    # Validate the league_id
    if not ObjectId.is_valid(league_id):
        return jsonify({"error": "Invalid league ID."}), 400

    # Fetch the league and ensure it exists
    league = db.leagues.find_one({"_id": ObjectId(league_id)})
    if not league:
        return jsonify({"error": "League not found."}), 404

    # Check if the user is authorized (is the commissioner)
    if not user_id or ObjectId(user_id) != league.get("CommissionerId"):
        return jsonify({"error": "You are unauthorized to view this content."}), 403

    # Fetch the current teams in the league's season
    current_teams = db.teams.find({
        "FantasyLeagueSeasonId": league.get("CurrentFantasyLeagueSeasonId")
    })

    if not current_teams:
        return jsonify({"error": "No teams found for the current fantasy league season."}), 404

    try:
        # Extract user IDs from teams
        user_ids = [team.get("OwnerId") for team in current_teams if "OwnerId" in team]

        # Fetch only username and email for the associated users
        users = db.users.find(
            {"_id": {"$in": [ObjectId(uid) for uid in user_ids]}}
        )

        # Convert users to a list of dictionaries
        user_dicts = [User(**user).to_dict() for user in users]

        if not user_dicts:
            return jsonify({"error": "No users found for the associated teams."}), 404

        return jsonify(user_dicts)


    except Exception as e:
        return jsonify({"error": f"An error occurred while processing your request: {str(e)}"}), 500

