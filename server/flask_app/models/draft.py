from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from bson import ObjectId
import random

# Add this line to ensure the correct path
import sys
import os

# Adjust the paths for MacOS to get the server directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.base_model import Base
from models import PyObjectId
from config import db

class Draft(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    LeagueId: PyObjectId
    StartDate: Any
    Rounds: int
    PeriodId: PyObjectId
    DraftOrder: Optional[List[PyObjectId]]
    IsComplete: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        draft_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in draft_dict and draft_dict['_id'] is not None:
            # Update existing document
            result = db.drafts.update_one({'_id': draft_dict['_id']}, {'$set': draft_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(draft_dict['_id']))
        else:
            # Insert new document
            result = db.drafts.insert_one(draft_dict)
            self.id = result.inserted_id
        return self.id

    def determine_draft_order(self):
        from models import League

        # Find the league document
        league = db.leagues.find_one({"_id": self.LeagueId})
        
        if not league:
            raise ValueError("League not found")

        league = League(**league)

        # Access the latest season
        latest_season = league.get_most_recent_season()

        if not latest_season['Active']:
            raise ValueError("Season is not active")

        # Check if this is the first draft of the season
        draft_count = db.drafts.count_documents({ "SeasonId": latest_season["_id"] })
        
        if draft_count == 0:
            # Randomly generate draft order
            teams = list(db.teams.find({ "LeagueId": self.LeagueId }))
            self.DraftOrder = [team['_id'] for team in teams]
            random.shuffle(self.DraftOrder)
        else:
            # Get the most recent period
            most_recent_period = league.get_most_recent_period()
            
            # if there is a most recent period and that period has standings
            # set the draft to be the reverse of the standings
            if most_recent_period and most_recent_period.Standings:
                self.DraftOrder = most_recent_period.Standings[::-1]
            else:
                raise ValueError("Most recent period or standings not found")
        
        # Update the draft order in the database
        db.drafts.update_one(
            {"FantasyLeagueSeasonId": self.LeagueId},
            {"$set": {"DraftOrder": self.DraftOrder}},
            upsert=True
        )

    @field_validator('Rounds')
    def rounds_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Number of rounds must be positive')
        return v

    # @field_validator('StartDate')
    # def dates_must_be_valid(cls, v):
    #     if not isinstance(v, datetime):
    #         raise ValueError(f'StartDate must be a valid datetime')
    #     return v

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }