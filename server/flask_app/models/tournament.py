from typing import List, Optional, Dict, Union
from pydantic import Field, field_validator
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

class Tournament(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    EndDate: datetime
    StartDate: datetime
    Name: str
    Venue: List[str]
    City: str
    State: str
    Links: List[str]
    Purse: Optional[int] = None
    PreviousWinner: Optional[PyObjectId] = None
    Par: Optional[str] = None
    Yardage: Optional[str] = None
    IsCompleted: bool = False
    InProgress: bool = False
    ProSeasonId: Optional[PyObjectId]
    Holes: Optional[List[Dict[str, Union[str, int]]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        tournament_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in tournament_dict and tournament_dict['_id'] is not None:
            # Update existing document
            result = db.tournaments.update_one({'_id': tournament_dict['_id']}, {'$set': tournament_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(tournament_dict['_id']))
        else:
            # Insert new document
            result = db.tournaments.insert_one(tournament_dict)
            self.id = result.inserted_id
        return self.id

    @field_validator('Par')
    def par_must_be_valid(cls, v):
        # Check if the value is not null
        if v is not None and v != '':
            # Check if the value is a valid integer
            try:
                value = int(v)
            except ValueError:
                raise ValueError(f'Invalid value: {v}. Par must parse to a number.')

            # Ensure the numerical value is below 80
            if value > 80:
                raise ValueError(f'Invalid value: {value}. Par must be less than or equal to 80.')
        
        return v