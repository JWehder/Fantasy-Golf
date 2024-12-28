from flask import jsonify, abort, Blueprint
import sys
import os
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import Tournament

tournaments_collection = db.tournaments
leagues_collection = db.leagues

tournaments_bp = Blueprint('tournaments', __name__)

@tournaments_bp.route('/pro_seasons/<pro_season_id>', methods=['GET'])
def get_tournaments(pro_season_id):
    """Fetches a round by ID"""
    tournaments_data = tournaments_collection.find({"ProSeasonId": ObjectId(pro_season_id)})
    if tournaments_data:    
        return jsonify({
            tournaments_data
        })
    return abort(404, description="Tournament not found. Please check the ID and try again.")

@tournaments_bp.route('/<tournament_id>', methods=['GET'])
def get_tournament_by_id(tournament_id):
    """Fetches a tournament by ID"""
    tournament_data = tournaments_collection.find_one({
        "_id": ObjectId(tournament_id)
    })

    tournament_data = Tournament(**tournament_data).to_dict()
    if tournament_data:
        return jsonify({
            "tournament": tournament_data
        })
    return abort(404, description="The tournament that you requested could not be found. Please review your query value and try again.")



