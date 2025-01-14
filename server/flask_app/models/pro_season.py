from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, Dict
from datetime import datetime
from bson import ObjectId

# Add this line to ensure the correct path
import sys
import os

# Adjust the paths for MacOS to get the server directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.base_model import Base
from models import PyObjectId 
from config import db

class ProSeason(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    LeagueName: str
    StartDate: datetime
    EndDate: datetime
    Competitions: List[PyObjectId] = []
    Active: bool = Field(default=False, description="Determine whether the season is currently active")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def save(self) -> PyObjectId:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        season_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in season_dict and season_dict['_id'] is not None:
            result = db.proSeasons.update_one({'_id': season_dict['_id']}, {'$set': season_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(season_dict['_id']))
        else:
            result = db.proSeasons.insert_one(season_dict)
            self.id = result.inserted_id

        return self.id
