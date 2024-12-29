from flask import jsonify, abort, Blueprint, request
import sys
import os
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import Draft

drafts_collection = db.drafts
drafts_bp = Blueprint('drafts', __name__)

@drafts_bp.route('/<draft_id>', methods=['GET', "POST"])
def get_draft(draft_id):

    if request.method == "GET":
        from models import DraftPick, Golfer
        from bson.errors import InvalidId

        try:
            draft_id = ObjectId(draft_id)
        except InvalidId:
            return jsonify({"error": "Invalid draft ID", "status": 400}), 400

        draft_data = drafts_collection.find_one({"_id": ObjectId(draft_id)})
        if not draft_data:
            return jsonify({"error": "Draft not found"}), 404

        draft_picks = list(
            db.draftPicks.find({"DraftId": draft_id})
            .sort([("RoundNumber", 1), ("PickNumber", 1)])
        )

        if draft_picks:
            draft_dict = Draft(**draft_data).to_dict()

            draft_dict["DraftPicks"] = []
            for pick in draft_picks:
                try:
                    # Convert each pick to DraftPick model
                    draft_dict["DraftPicks"].append(DraftPick(**pick).to_dict())
                except Exception as e:
                    print(f"Error processing pick: {pick}, Error: {e}")

            draft_dict["DraftOrder"] = [pick["TeamId"] for pick in draft_dict["DraftPicks"]]

            golfer_ids = [pick["GolferId"] for pick in draft_picks]
            golfers = {
                str(golfer["_id"]): Golfer(**golfer).to_dict()
                for golfer in db.golfers.find({"_id": {"$in": golfer_ids}})
            }

            for pick in draft_dict["DraftPicks"]:
                pick["Golfer"] = golfers.get(pick["GolferId"], None)

        return jsonify({"draft": draft_dict}), 200
    elif request.method == "POST":
        draft = db.drafts.find_one({"_id": ObjectId(draft_id)})

        if not draft:
            return jsonify({"error": "draft not found."}), 404

        