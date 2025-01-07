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

@leagues_bp.route('/<league_id>/create_new_season', methods=['POST'])
def create_new_season(league_id):
    from models import FantasyLeagueSeason, Team
    import datetime
    from bson import ObjectId

    user_id = session.get('user_id')

    # Fetch the league
    league = db.leagues.find_one({"_id": ObjectId(league_id)})
    if not league:
        return {"error": "League not found"}, 404

    if league["OwnerId"] != user_id:
        league_id = league["_id"]
        return {"error": f"You are unauthorized to access this action on {league_id}"}, 422
    
    league_instance = League(**league)
    
    # Fetch the current fantasy league season
    current_fantasy_league_season = db.fantasyLeagueSeasons.find_one({
        "_id": ObjectId(league_instance.CurrentFantasyLeagueSeasonId)
    })
    if not current_fantasy_league_season:
        return {"error": "Current fantasy league season not found"}, 404

    fantasy_league_season_instance = FantasyLeagueSeason(**current_fantasy_league_season)
    
    # Create a new fantasy league season
    new_fantasy_league_season = FantasyLeagueSeason(
        SeasonNumber=fantasy_league_season_instance.SeasonNumber + 1,
        StartDate=None,  # Populate with actual start date
        EndDate=None,  # Populate with actual end date
        Periods=[],  # Reset periods
        Tournaments=[],  # Reset tournaments
        LeagueId=league_id,
        Active=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    new_fantasy_league_season_id = new_fantasy_league_season.save()
    
    # Copy teams to the new season
    teams = list(db.teams.find({"FantasyLeagueSeasonId": ObjectId(league_instance.CurrentFantasyLeagueSeasonId)}))
    for team_data in teams:
        team_instance = Team(**team_data)
        team_instance.id = None
        team_instance.FantasyLeagueSeasonId = new_fantasy_league_season_id  # Assign to new season
        team_instance.Points = 0
        team_instance.FAAB = 0
        team_instance.WaiverNumber = 0
        team_instance.TeamStats = {
            "Wins": 0,
            "TotalUnderPar": 0,
            "AvgScore": 0,
            "MissedCuts": 0,
            "Top10s": 0,
            "Placement": 0
        }
        team_instance.Golfers = {}  # Reset golfers
        team_instance.created_at = None  # Reset creation time
        team_instance.updated_at = None  # Reset updated time
        
        # Save the new team instance
        team_instance.save()

    # Update the league's current fantasy league season ID
    db.leagues.update_one(
        {"_id": ObjectId(league_id)},
        {"$set": {"CurrentFantasyLeagueSeasonId": new_fantasy_league_season_id}}
    )
    
    return {"message": "New fantasy league season created successfully", "newSeasonId": str(new_fantasy_league_season_id)}, 201
    
@leagues_bp.route('/create_league', methods=['POST'])
def create_league():
    pass