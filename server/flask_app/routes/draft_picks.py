from flask import jsonify, abort
from flask import Blueprint
import sys
import os
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import DraftPick

draft_picks_collection = db.draftPicks

draft_picks_bp = Blueprint('draft_picks', __name__) 

@draft_picks_bp.route('/drafts/<draft_id>', methods=['GET'])
def get_draft_picks(draft_id):
    """Lists all draft picks by draft ID"""
    draft_picks_data = list(draft_picks_collection.find_one({"_id": ObjectId(draft_id)}))
    if draft_picks_data:
        draft_picks = []
        for draft_pick in draft_picks_data:
            draft_pick_dict = DraftPick(**draft_picks_data).to_dict()

            draft_pick_dict["Golfer"] = db.golfers.find_one({"_id": ObjectId(draft_pick_dict["GolferId"])})

            draft_picks.append(draft_pick)
        return jsonify({
            draft_picks
        })
    return abort(404, description="No draft picks were found for this draft.")

@draft_picks_bp.route('/draft_picks/teams/<team_id>', methods=['GET'])
def get_draft_picks_by_team_id(team_id):
    """Fetches draft pick by its team ID"""
    draft_picks_data = list(draft_picks_collection.find_one({"_id": ObjectId(team_id)}))
    if draft_picks_data:
        draft_picks = []
        for draft_pick in draft_picks_data:
            draft_pick = DraftPick(**draft_picks_data)
            draft_picks.append(draft_pick)
        return jsonify({
            draft_picks
        })
    return abort(404, description="No draft picks were found for this draft.")