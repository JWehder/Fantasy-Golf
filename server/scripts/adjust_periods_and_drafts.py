from pymongo import errors
import os
import json
import sys
from datetime import datetime
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import models from flask_app
from flask_app.config import db, client

def convert_to_date(date_str):
    # Convert to a datetime object
    date_obj = datetime.strptime(date_str, "%m/%d/%Y")

    # Return the datetime object
    return date_obj

def fix_periods(fantasyLeagueSeasonId):
    from flask_app.models import Period, Draft

    for period in list(db.periods.find({"FantasyLeagueSeasonId": fantasyLeagueSeasonId})):
        print(period)

        # Remove the "id" key if it exists
        period.pop("id", None)

        print(period)

        # Process Period
        period["StartDate"] = convert_to_date(period["StartDate"])
        period["EndDate"] = convert_to_date(period["EndDate"])

        # Process Draft
        draft = db.drafts.find_one({"_id": period["DraftId"]})
        if draft:  # Ensure a draft was found
            draft.pop("id", None)  # Remove "id" if present
            if not isinstance(draft["StartDate"], datetime):
                draft["StartDate"] = convert_to_date(draft["StartDate"])
            db.drafts.update_one({"_id": draft["_id"]}, {"$set": draft})

        db.periods.update_one({"_id": period["_id"]}, {"$set": period})

fix_periods(ObjectId("66cfb58fcb1c3460e49138c4"))