import sys
import os
from bson.objectid import ObjectId
from flask import Blueprint, jsonify

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import ProSeason

pro_seasons_bp = Blueprint('pro_seasons', __name__)

pro_seasons_collection = db.proSeasons

@pro_seasons_bp.route('/<pro_season_id>/competition_schedule', methods=['GET'])
def get_pro_season_competitions(pro_season_id):
    from models import Tournament

    if not pro_season_id:
        return {"error": "There was no season id specified."}

    pro_season = db.proSeasons.find_one({"_id": pro_season_id})

    if not pro_season:
        return {"error": "Could not find any competitions for that particular season id."}

    # Find all tournaments with IDs in the league season's tournaments list
    tournaments = db.tournaments.find({"_id": {"$in": [ObjectId(t_id) for t_id in pro_season["competitions"]]}}).sort("StartDate")

    if tournaments:
        # Convert each tournament to a dictionary
        tournament_dicts = [Tournament(**tournament).to_dict() for tournament in tournaments]

        for tournament_dict in tournament_dicts:
            if tournament_dict["IsCompleted"]:

                winner = db.golfertournamentdetails.find_one({
                    "TournamentId": ObjectId(tournament_dict["id"]),
                    "Position": "1"
                })

                tournament_dict["Winner"] = winner["Name"] + " " + f'({str(winner["Score"])})'
            else:
                previous_winner = db.golfers.find_one({
                    "_id": ObjectId(tournament_dict["PreviousWinner"])
                })

                if previous_winner:
                    tournament_dict["PreviousWinner"] = previous_winner["FirstName"] + " " + previous_winner["LastName"]
                
            if tournament_dict["Purse"] and tournament_dict["Purse"] > 0:
                tournament_dict["Purse"] = tournament_dict["Purse"] // 1000000
                tournament_dict["Purse"] = "$" + str(tournament_dict["Purse"]) + "M"

        # Respond with the tournaments, or an empty array if none found
        return jsonify({"upcomingProSeasonTournaments": tournament_dicts})

    return {"error": "There are no tournaments associated with this particular pro season."}, 404
    
