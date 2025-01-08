from flask import jsonify, abort, request, Blueprint, session
import sys
import os
from bson.objectid import ObjectId
from pydantic import ValidationError

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import LeagueSettings

leagues_settings_collection = db.leagueSettings
league_collection = db.leagues

league_settings_bp = Blueprint('league_settings', __name__)

@league_settings_bp.route('/leagues_settings/leagues/<league_id>', methods=['GET'])
def get_leagues_settings_by_league_id(league_id):
    """Fetches a round by ID"""
    league = league_collection.find_one({"_id": ObjectId(league_id)})
    if league:
        leagues_settings_data = league["LeagueSettings"]
        if leagues_settings_data:
            return jsonify({
                leagues_settings_data
            })
        return abort(404, description="League settings not found for this league.")
    else:
        return abort(404, description="League not found.")

@league_settings_bp.route('/leagues_settings/<leagues_settings_id>', methods=['PATCH'])
def update_leagues_settings(leagues_settings_id):
    """Update specific fields in league settings with validation before database update"""
    user_id = session.get('user_id')

    data = request.get_json()  # Get the partial data from the request body
    leagues_settings = leagues_settings_collection.find_one({"_id": ObjectId(leagues_settings_id)})

    # get league to see who the commissioner is
    league = db.leagues.find_one({"_id": ObjectId(leagues_settings["LeagueId"])})

    if not user_id or user_id != league["CommissionerId"]:
        return jsonify({"error": "You are not authorized to make changes to this endpoint."}), 401

    if leagues_settings:
        # Merge the existing data with the new patch data
        updated_data = {**leagues_settings, **data}
        
        # Validate the merged data using the LeagueSettings model
        try:
            league_settings_instance = LeagueSettings(**updated_data)
            # If validation passes, proceed with the database update
            league_settings_instance.save()

            # Return the validated, updated instance
            return jsonify(league_settings_instance.to_dict()), 200
        except ValidationError as e:
            # If validation fails, return an error response
            return jsonify({"error": str(e)}), 400
    else:
        return abort(404, description="League settings not found.")

@league_settings_bp.route('/default_settings/fantasy_games/<sport_str>', methods=['GET'])
def get_leagues_settings_by_game_str(sport_str):
    from datetime import datetime
    """
    Get default league settings for a given fantasy game.
    :param sport_str: The string representing the fantasy sport (e.g., 'golf').
    :return: JSON response containing the default settings for the game.
    """

    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "You are not authorized to access this endpoint. Please sign in and try again."}), 401

    try:
        # Fetch the current year
        current_year = datetime.now().year

        # Find the fantasy game settings in the database
        fantasy_game = db.fantasySportsGames.find_one({"Sport": sport_str, "Year": current_year})
        if not fantasy_game:
            return jsonify({'error': f'No fantasy game found for sport: {sport_str}'}), 404

        # Get the default settings and convert to dictionary
        default_settings = LeagueSettings(fantasy_game["defaultSettings"]).to_dict()
        if not default_settings:
            return jsonify({'error': f'No default settings found for game: {sport_str}'}), 404

        # Add the current year to the response if needed
        default_settings["currentYear"] = current_year

        return jsonify(default_settings), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
