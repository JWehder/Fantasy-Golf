from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
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

class TeamResult(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    TeamId: PyObjectId
    TournamentId: PyObjectId
    PeriodId: PyObjectId
    OpponentId: Optional[PyObjectId] = None
    TeamScore: int = 0
    GolfersScores: List[PyObjectId] = Field(default={}, description="Dictionary with a string for the golfer tourney details id as the key and ")
    Placing: Optional[int] = 0
    PointsFromPlacing: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        team_result_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in team_result_dict and team_result_dict['_id'] is not None:
            # Update existing document
            result = db.teamResults.update_one({'_id': team_result_dict['_id']}, {'$set': team_result_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(team_result_dict['_id']))
        else:
            # Insert new document
            result = db.teamResults.insert_one(team_result_dict)
            self.id = result.inserted_id
            
            # Insert id into the associated Period
            period_id = team_result_dict.get("PeriodId")
            if period_id:
                db.periods.update_one(
                    {"_id": period_id},
                    {"$push": {"TeamResults": self.id}}
                )
            else:
                raise ValueError("PeriodId is missing or invalid in team_result_dict")

        return self.id
    
    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}
    
    @model_validator(mode = 'before')
    def placing_is_less_than_teams(cls, values):
        period_id = values.get('PeriodId')

        period = db.periods.find_one({ "_id": period_id })
        league_id = period["LeagueId"]

        placing = values.get('Placing')

        num_of_teams_in_league = len(db.leagues.find_one({"_id": league_id })["Teams"])
        if placing > num_of_teams_in_league:
            raise ValueError('The placing the team currently is in is not possible based on the amount of teams in the league')
        return values

    def calculate_player_scores(self, db):
        league_settings = db.leaguessettings.find_one({"LeagueId": self.LeagueId})
        
        if league_settings is None:
            raise ValueError("League settings not found.")
        
        points_per_score = league_settings["PointsPerScore"]
        
        for golfer_id in self.GolfersScores.items():
            golfer_details = db.golfertournamentdetails.find_one({"GolferId": golfer_id, "TournamentId": self.TournamentId})
            
            if golfer_details is None:
                continue
            
            if league_settings["StrokePlay"]:
                self.GolfersScores[golfer_id]['TotalScore'] = golfer_details.get('TotalScore', 0)
            elif league_settings["ScorePlay"]:
                for score_type in ['Birdies', 'Pars', 'Bogeys', 'DoubleBogeys', 'WorseThanDoubleBogeys']:
                    historical_num_of_score_type = self.GolfersScores[golfer_id].get(score_type, 0)
                    curr_num_of_score_type = golfer_details.get(score_type, 0)
                    if historical_num_of_score_type != curr_num_of_score_type:
                        difference_in_score_type_count = curr_num_of_score_type - historical_num_of_score_type
                        self.TotalPoints += (points_per_score.get(score_type, 0) * difference_in_score_type_count)
                        self.GolfersScores[golfer_id][score_type] = curr_num_of_score_type

