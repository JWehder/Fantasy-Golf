from flask import jsonify, abort, request, Blueprint
import sys
import os
from bson.objectid import ObjectId
from pydantic import ValidationError 
import traceback
import datetime

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import Golfer, GolferTournamentDetails, Round

golfers_collection = db.golfers
golfers_tourney_details_collection = db.golfertournamentdetails
teams_collection = db.teams
rounds_collection = db.rounds
tournaments_collection = db.tournaments

golfers_bp = Blueprint('golfers', __name__)

@golfers_bp.route('/golfers/<golfer_id>', methods=['GET'])
def get_golfer(golfer_id):
    """Fetches a golfer by ID"""
    golfer_data = golfers_collection.find_one({"_id": ObjectId(golfer_id)})
    if golfer_data:
        golfer = Golfer(**golfer_data)
        return jsonify({
            golfer
        })
    return abort(404, description="Golfer not found")

@golfers_bp.route('/<golfer_id>/tournament-details', methods=["GET"])
def get_golfer_details(golfer_id):
    """Fetches a golfer's tournament details."""
    
    try:
        all_golfers_details = golfers_tourney_details_collection.find({
            "GolferId": ObjectId(golfer_id)
        })
        golfers_details_list = []

        for golfer_details in all_golfers_details:
            try:
                golfer_instance = GolferTournamentDetails(**golfer_details)
                rounds = rounds_collection.find({
                    "GolferTournamentDetailsId": ObjectId(golfer_instance.id)
                })
                
                # append the actual round results rather than just the id
                rounds_dicts = [(Round(**_round)).to_dict() for _round in rounds]

                # create a dict with custom method for the ability to jsonify
                golfer_tourney_details_dict = golfer_instance.to_dict()

                golfer_tourney_details_dict["Rounds"] = rounds_dicts

                # pull the tournament's details
                tournament_details = tournaments_collection.find_one({
                    "_id": ObjectId(golfer_tourney_details_dict["TournamentId"])
                })

                # pull the highest scoring golfer's score to compare against the current golfer's score
                winning_golfer = golfers_tourney_details_collection.find_one({
                    "TournamentId": ObjectId(tournament_details["_id"]),
                    "Position": "1" 
                })

                golfer_tourney_details_dict["HoleData"] = tournament_details["Holes"]
                golfer_tourney_details_dict["TournamentName"] = tournament_details["Name"]
                golfer_tourney_details_dict["WinningScore"] = winning_golfer["Score"]

                # Parse the ISO date string
                start_date = tournament_details["StartDate"]

                # Format it to a readable string
                readable_date = start_date.strftime("%B %d, %Y")  # e.g., "March 17, 2024"

                golfer_tourney_details_dict["StartDate"] = readable_date

                golfers_details_list.append(golfer_tourney_details_dict)
                
            except ValidationError as e:
                print(f"there was an issue: {e}")
                return jsonify({"error": f"There was an issue creating an instance: {e}"}), 400

            except Exception as e:
                # Catch any other exceptions and print the traceback
                print("An unexpected error occurred:", type(e).__name__)
                print("Error details:", str(e))
                print("Traceback:")
                traceback.print_exc()
                return jsonify({"error": "An unexpected error occurred. Please check server logs for details."}), 500

        if golfers_details_list:
            try:
                return jsonify({"details": golfers_details_list}), 200
            except Exception as e:
                # Catch any other exceptions and print the traceback
                print("An unexpected error occurred:", type(e).__name__)
                print("Error details:", str(e))
                print("Traceback:")
                traceback.print_exc()
                return jsonify({"error": "An unexpected error occurred. Please check server logs for details."}), 500
        else:
            print("no tourney details")
            return jsonify({"error": "No tournament details found for this golfer."}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@golfers_bp.route('/available_golfers/leagues/<league_id>', methods=['GET'])
def get_available_golfers(league_id):
    """Fetches available golfers for a league with pagination"""

    from models import League
    # Get pagination parameters
    page = request.args.get('page', default=0, type=int)
    limit = 50  # Number of golfers per page

    # Find the league by ID
    league = db.leagues.find_one({
        "_id": ObjectId(league_id)
    })

    if not league:
        return jsonify({"error": "Sorry, we do not recognize that league."}), 404
    
    league = League(**league)

    # Slice the list of available players for pagination
    start_index = page * limit
    end_index = start_index + limit

    # Get all available golfers
    available_golfers, num_of_total_available_golfers = league.get_available_golfers(limit=limit, page=page)

    if available_golfers:
        
        # Check if there is a next page
        next_page = page + 1 if end_index < num_of_total_available_golfers else None

        return jsonify({
            "golfers": available_golfers,
            "nextPage": next_page
        }), 200

    return jsonify({"error": "Available golfers not found. Please try again."}), 404


@golfers_bp.route('/available_golfers/leagues/<league_id>/tournaments/<tournament_id>', methods=['GET'])
def get_available_golfers_by_tournament(league_id, tournament_id):
    """Fetches available golfers for a tournament with pagination"""

    from models import League
    # Get pagination parameters
    page = request.args.get('page', default=0, type=int)
    limit = 50  # Number of golfers per page

    # Find the league by ID
    league = db.leagues.find_one({
        "_id": ObjectId(league_id)
    })

    if not league:
        return jsonify({"error": "Sorry, we do not recognize that league."}), 404
    
    league_instance = League(**league)

    # Calculate the number of documents to skip
    offset = page * limit

    # Slice the list of available players for pagination
    start_index = page * limit
    end_index = start_index + limit

    # get all the golfers that are currently rostered
    unavailable_golfers_ids = league_instance.get_all_rostered_players()

    # filter query by golfers who are already on a team and a part of this tourney
    associated_golfer_tournament_details = db.golfertournamentdetails.find(
        {
            "TournamentId": tournament_id,
            "GolferId": {"$nin": unavailable_golfers_ids}
        }
    )

    available_golfers_ids = [golfer["GolferId"] for golfer in associated_golfer_tournament_details]

    available_golfers = db.golfers.find({
        "GolferId": {"$in": available_golfers_ids}
    }).sort("OGWR").skip(offset).limit(limit)

    # Count the total number of available golfers with OWGR and FedexPts
    number_of_total_available_golfers = db.golfers.count_documents({
        '_id': {'$nin': list(unavailable_golfers_ids)},
        'OGWR': {'$exists': True, '$ne': None}
    })

    available_golfers_dicts = [Golfer(golfer).to_dict() for golfer in available_golfers]

    if available_golfers:
        
        # Check if there is a next page
        next_page = page + 1 if end_index < number_of_total_available_golfers else None

        return jsonify({
            "golfers": available_golfers_dicts,
            "nextPage": next_page
        }), 200

    return jsonify({"error": "Available golfers not found. Please try again."}), 404
