from flask import jsonify, abort, Blueprint
import sys
import os
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import Round

rounds_collection = db.rounds

rounds_bp = Blueprint('rounds', __name__)

@rounds_bp.route('/rounds/<round_id>', methods=['GET'])
def get_round(round_id):
    """Fetches a round by ID"""
    round_data = rounds_collection.find_one({"_id": ObjectId(round_id)})
    if round_data:
        fetched_round = Round(**round_data)
        return jsonify({
            fetched_round
        })
    return abort(404, description="Round not found")

@rounds_bp.route('/rounds/<golfer_tournament_details_id>', methods=['GET'])
def get_round(golfer_tournament_details_id):
    """Fetches a round by ID"""
    try: 
        rounds = rounds_collection.find({"GolferTournamentDetailsId": ObjectId(golfer_tournament_details_id)})

        if not rounds:
            return jsonify({"error": "Sorry, we could not find the rounds you are looking for."}), 404

        if rounds:
                    
            # append the actual round results rather than just the id
            rounds_dicts = [(Round(**_round)).to_dict() for _round in rounds]

            return jsonify({
                "rounds": rounds_dicts
            })
    except Exception as e:
        return jsonify({f"error": "Sorry there was an error: {e}"})