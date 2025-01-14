from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, field_validator
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

class Golfer(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    Rank: Optional[int] = None
    FirstName: str
    LastName: str
    Age: Optional[int] = None
    Earnings: Optional[int] = None
    FedexPts: Optional[int] = None
    Events: Optional[int] = None
    Rounds: Optional[int] = None
    Flag: Optional[str] = None
    Cuts: Optional[int] = None
    Top10s: Optional[int] = None
    Wins: Optional[int] = None
    AvgScore: Optional[float] = None
    GolferPageLink: Optional[str] = ""
    Birthdate: Optional[datetime] = None
    Birthplace: Optional[str] = ""
    HtWt: Optional[str] = ""
    College: Optional[str] = None
    Swing: Optional[str] = None
    TurnedPro: Optional[str] = None
    OWGR: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        golfer_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in golfer_dict and golfer_dict['_id'] is not None:
            # Update existing document
            result = db.golfers.update_one({'_id': golfer_dict['_id']}, {'$set': golfer_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(golfer_dict['_id']))
        else:
            # Insert new document
            result = db.golfers.insert_one(golfer_dict)
            self.id = result.inserted_id
        return self.id

    @model_validator(mode='before')
    def set_defaults(cls, values):
        field_defaults = {
            int: 0,
            float: 0.0,
            str: "",
            list: [],
            dict: {},
        }
        
        for field, value in values.items():
            if value is None:
                field_type = cls.__annotations__.get(field)
                if field_type in field_defaults:
                    values[field] = field_defaults[field_type]
        
        return values

    @field_validator('Rank', 'OWGR')
    def rank_and_owgr_must_be_valid(cls, v):
        if int(v) <= 0:
            raise ValueError('Rank and OWGR must be positive integers')
        return v

    @field_validator('Age')
    def age_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Age must be a positive integer')
        return v

    @field_validator('Earnings', 'FedexPts', 'Events', 'Rounds', 'Cuts', 'Top10s', 'Wins')
    def must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Value must be non-negative')
        return v

    @field_validator('AvgScore')
    def avg_score_must_be_valid(cls, v):
        if not v:
            return v
        if v <= 0 or v > 120:
            raise ValueError('Average score must be a positive number and realistic')
        return v

    @field_validator('GolferPageLink')
    def must_be_valid_url(cls, v):
        if not v.startswith("http"):
            raise ValueError('Golfer page link must be a valid URL')
        return v

    @field_validator('Birthdate')
    def birthdate_must_be_valid(cls, v):
        if not isinstance(v, datetime):
            raise ValueError('Birthdate must be a valid datetime')
        return v

    @field_validator('TurnedPro')
    def turned_pro_must_be_valid_year(cls, v):
        if not v.isdigit() or int(v) < 1900 or int(v) > datetime.now().year:
            raise ValueError('TurnedPro must be a valid year')
        return v

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }