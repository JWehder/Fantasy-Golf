from flask import jsonify, abort, Blueprint
import sys
import os
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import Draft

drafts_collection = db.holes
drafts_bp = Blueprint('leagues_settings', __name__)

@drafts_bp.route('/drafts/<draft_id>', methods=['GET'])
def get_draft(draft_id):
    from models import DraftPick, Golfer
    from bson.errors import InvalidId

    try:
        draft_id = ObjectId(draft_id)
    except InvalidId:
        return jsonify({"error": "Invalid draft ID", "status": 400}), 400

    draft_data = drafts_collection.find_one({"_id": draft_id})
    if not draft_data:
        return jsonify({"error": "Draft not found", "status": 404}), 404

    draft_dict = Draft(**draft_data).to_dict()

    if draft_dict.get("DraftPicks"):
        draft_picks = list(
            db.draftPicks.find({"DraftId": draft_id})
            .sort([("RoundNumber", 1), ("PickNumber", 1)])
        )
        draft_dict["DraftPicks"] = [DraftPick(**pick).to_dict() for pick in draft_picks]
        draft_dict["DraftOrder"] = [pick["TeamId"] for pick in draft_dict["DraftPicks"]]

        golfer_ids = [pick["GolferId"] for pick in draft_picks]
        golfers = {
            golfer["_id"]: Golfer(**golfer).to_dict()
            for golfer in db.golfer.find({"_id": {"$in": golfer_ids}})
        }

        for pick in draft_dict["DraftPicks"]:
            pick["Golfer"] = golfers.get(pick["GolferId"], None)

    return jsonify(draft_dict), 200