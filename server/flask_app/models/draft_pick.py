from typing import Optional
from pydantic import BaseModel, Field, field_validator, root_validator
from datetime import datetime
from bson import ObjectId
from datetime import timedelta
from . import PyObjectId 

# Add this line to ensure the correct path
import sys
import os

# Adjust the paths for MacOS to get the server directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.base_model import Base
from config import db

class DraftPick(Base):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    TeamId: PyObjectId
    GolferId: PyObjectId
    RoundNumber: int
    PickNumber: int
    LeagueId: PyObjectId
    DraftId: PyObjectId
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        draft_picks_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in draft_picks_dict and draft_picks_dict['_id'] is not None:
            # Update existing document
            result = db.draftPicks.update_one({'_id': draft_picks_dict['_id']}, {'$set': draft_picks_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(draft_picks_dict['_id']))
        else:
            # Insert new document
            result = db.draftPicks.insert_one(draft_picks_dict)
            self.id = result.inserted_id
            
            # Append the new draft pick to the DraftPicks array in the drafts collection
            db.drafts.update_one(
                {"_id": draft_picks_dict['DraftId']},
                {"$push": {"DraftPicks": self.id}}
            )
        
        return self.id

    # @root_validator(pre=True)
    # def run_validations(cls, values):
    #     pass
    #     # Use the raw values dictionary for validation purposes
    #     league_settings = db.leagueSettings.find_one({"LeagueId": values['LeagueId']})
    #     if not league_settings:
    #         raise ValueError("League settings not found")

    #     team_golfers_count = db.golfers.count_documents({"TeamId": values['TeamId']})
    #     if team_golfers_count >= league_settings['MaxGolfersPerTeam']:
    #         raise ValueError("Team already has the maximum number of golfers allowed")

    #     draft = db.drafts.find_one({"_id": values['DraftId']})
    #     if not draft:
    #         raise ValueError("Draft not found")

    #     current_time = datetime.now()
    #     draft_start_time = draft['StartDate']
    #     pick_duration = draft.get('TimeToDraft', 7200)
    #     draft_picks_count = db.draftPicks.count_documents({ "DraftId": values['DraftId'] })
    #     picks_per_round = draft_picks_count / draft['Rounds']
    #     expected_pick_time = draft_start_time + timedelta(
    #         seconds=(values['RoundNumber'] - 1) * picks_per_round * pick_duration +
    #                 (values['PickNumber'] - 1) * pick_duration
    #     )

    #     if current_time < draft_start_time or current_time > expected_pick_time + timedelta(seconds=pick_duration):
    #         raise ValueError("Pick is not within the allowed time period")

    #     if len(draft['Picks']) >= values['PickNumber'] + (values['RoundNumber'] - 1) * picks_per_round:
    #         raise ValueError("Invalid pick order")

    #     return values

    @field_validator('RoundNumber', 'PickNumber')
    def pick_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Round number and pick number must be positive')
        return v
