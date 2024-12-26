import os
import sys
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_app.config import db

first_period = db.periods.find_one({"_id": ObjectId('66d1d4cc3b1cc1328ac7f84b')})

draft = db.drafts.find_one({"_id": ObjectId('66d1d4cc3b1cc1328ac7f84a')})

team_results = db.teamResults.find({"PeriodId": first_period["_id"]})

for team_result in team_results:
    golfer_tourney_ids = [ObjectId(golfer_tourney_id) for golfer_tourney_id in team_result["GolfersScores"]]
    golfers = list(db.golfertournamentdetails.find({"_id": {"$in": golfer_tourney_ids}}))

    golfers_ids = [golfer_tourney_detail["GolferId"] for golfer_tourney_detail in golfers]

    draft_picks = list(db.draftPicks.find({
        "DraftId": draft['_id'],
        "TeamId": team_result["TeamId"]
    }))

    for golfer_id, draft_pick in zip(golfers_ids, draft_picks):
        print(golfer_id)
        db.draftPicks.update_one(
            {"_id": draft_pick["_id"]},
            {"$set": {"GolferId": golfer_id}}
        )
