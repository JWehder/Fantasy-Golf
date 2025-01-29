from typing import List, Optional, Union
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

class Hole(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    Strokes: int
    HolePar: int
    Par: Optional[bool]
    NetScore: Optional[Union[int, None]]
    HoleNumber: int
    Birdie: bool
    Bogey: bool
    Eagle: bool
    Albatross: bool
    DoubleBogey: bool
    WorseThanDoubleBogey: bool
    GolferTournamentDetailsId: PyObjectId
    RoundId: PyObjectId
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        hole_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in hole_dict and hole_dict['_id'] is not None:
            # Update existing document
            result = db.holes.update_one({'_id': hole_dict['_id']}, {'$set': hole_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(hole_dict['_id']))
        else:
            # Insert new document
            result = db.holes.insert_one(hole_dict)
            self.id = result.inserted_id
        return self.id

    @field_validator('Strokes')
    def strokes_must_be_positive(cls, v):
        if v == None:
            return v
        if v < 0:
            raise ValueError('Strokes cannot be a negative integer.')
        return v

    @field_validator('HoleNumber')
    def hole_number_must_be_valid(cls, v):
        if not (1 <= v <= 18):
            raise ValueError('Hole number must be between 1 and 18')
        return v