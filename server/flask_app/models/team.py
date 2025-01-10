from typing import Optional, Dict, List, Union
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
from dataclasses import dataclass

@dataclass
class Golfer(Base):
    UsageCount: int
    CurrentlyOnTeam: bool
    IsStarter: bool
    IsBench: bool

class Team(Base):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    TeamName: str
    ProfilePicture: Optional[str] = Field(description="Profile picture for team")
    Golfers: Dict[str, Golfer] = Field(default_factory=dict, description="Dictionary of golfer IDs with usage count and team status")
    OwnerId: Optional[PyObjectId] = None
    LeagueId: PyObjectId
    Points: int = Field(default=0, description="the amount of points that the team holds for the season based on their aggregate fantasy placings")
    FAAB: int = Field(default=0, description="How much total points you have to spend on players.")
    WaiverNumber: Optional[int] = 0
    TeamStats: Dict[str, Union[int, float]] = Field(default_factory=lambda: {
        "Wins": 0,
        "TotalUnderPar": 0,
        "AvgScore": 0.00,
        "MissedCuts": 0,
        "Top10s": 0
    })
    Placement: Optional[int]
    FantasyLeagueSeasonId: PyObjectId
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Validation to ensure the length of TeamName and LeagueName is reasonable
    @field_validator('TeamName')
    def validate_name_length(cls, v):
        if len(v) < 3 or len(v) > 50:  
            # Example: setting reasonable length between 3 and 50 characters
            raise ValueError('Name must be between 3 and 50 characters long.')
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    def change_team_name(old_team_name: str, new_team_name: str, league_id: PyObjectId):
        # Find the team document in the database
        team = db.teams.find_one({
            "TeamName": old_team_name,
            "LeagueId": league_id
        })

        # Raise an error if the team is not found
        if not team:
            raise ValueError("Sorry, we could not find the team you are looking for.")

        # Raise an error if the new name is not provided
        if not new_team_name:
            raise ValueError("Please enter a new team name.")

        # Update the team name in the retrieved document
        team["TeamName"] = new_team_name

        # Create a new instance of Team for validation
        new_team = Team(**team)

        # Save the new instance to the database
        new_team.save()

    def drop_player(self, team_id: PyObjectId, golfer_id: PyObjectId) -> bool:
        # Find the team
        team = db.teams.find_one({"_id": team_id})

        if not team:
            raise ValueError("The team you entered does not exist.")

        if golfer_id not in team["Golfers"]:
            raise ValueError(f"Player with ID {golfer_id} is not on the team.")
        else:
            # Update the team by removing the golfer
            db.teams.update_one(
                {"_id": team_id},
                {"$pull": {"Golfers": golfer_id}}
            )
            
            # Update the period's drop list
            league = db.leagues.find_one({"_id": self.LeagueId})
            if league:
                current_period = db.periods.find_one({"LeagueId": self.LeagueId, "StartDate": {"$lte": datetime.utcnow()}, "EndDate": {"$gte": datetime.utcnow()}})
                if current_period:
                    period_id = current_period["_id"]
                    drops = current_period.get("Drops", {})

                    if team_id in drops:
                        drops[team_id].append(golfer_id)
                    else:
                        drops[team_id] = [golfer_id]

                    db.periods.update_one(
                        {"_id": period_id},
                        {"$set": {"Drops": drops}}
                    )
                else:
                    raise ValueError("No current period found for the league.")
        
        return True

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        team_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in team_dict and team_dict['_id'] is not None:
            # Update existing document
            result = db.teams.update_one({'_id': team_dict['_id']}, {'$set': team_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(team_dict['_id']))
        else:
            # Insert new document
            result = db.teams.insert_one(team_dict)
            self.id = result.inserted_id
        return self.id

    def sign_free_agent(self, free_agent_id: str, period_id: PyObjectId):
        """Signs a free agent for the current period."""
        current_period = db.periods.find_one({"_id": period_id})

        if not current_period:
            raise ValueError("Period does not exist. Please check the ID you entered and try again.")

        # Update FreeAgentSignings for the current period
        if self.id in current_period["FreeAgentSignings"]:
            db.periods.update_one(
                {"_id": current_period["_id"]},
                {"$push": {f"FreeAgentSignings.{self.id}": free_agent_id}}
            )
        else:
            db.periods.update_one(
                {"_id": current_period["_id"]},
                {"$set": {f"FreeAgentSignings.{self.id}": [free_agent_id]}}
        )

    def can_use_golfer(golfer, league_settings):
        max_uses = league_settings.get("MaxNumOfGolferUses", 0)
        usage_count = golfer.get("UsageCount", 0)

        if max_uses > 0 and usage_count >= max_uses:
            return False
        return True

    def add_to_golfer_usage(self, golfer_id: str) -> List[Golfer]:
        """Adds usage for a golfer or signs them to the team."""
        golfer_id_str = str(golfer_id)
        league_settings = db.leagueSettings.find_one({"LeagueId": self.LeagueId})

        # Count current golfers
        num_of_golfers = sum(1 for golfer in self.Golfers.values() if golfer.CurrentlyOnTeam)

        if num_of_golfers >= league_settings["MaxGolfersPerTeam"]:
            raise ValueError("You have reached the maximum allowable golfers per team.")

        # Count starters
        num_of_starters = sum(1 for golfer in self.Golfers.values() if golfer.IsStarter)

        if golfer_id_str in self.Golfers:
            golfer = self.Golfers[golfer_id_str]
            
            if not self.can_use_golfer(golfer, league_settings):
                return "Sorry, you have used this golfer the max amount of allowable times according to your league."

            golfer.UsageCount += 1
            golfer.CurrentlyOnTeam = True
        else:
            is_starter = num_of_starters < league_settings["NumOfStarters"]
            golfer = Golfer(
                UsageCount=1,
                CurrentlyOnTeam=True,
                IsStarter=is_starter,
                IsBench=not is_starter
            )
            self.Golfers[golfer_id_str] = golfer

        self.save()

    def remove_golfer(self, golfer_id: str):
        """Removes a golfer from the team."""
        golfer_id = str(golfer_id)

        if golfer_id in self.Golfers:
            golfer = self.Golfers[golfer_id]
            golfer.CurrentlyOnTeam = False
            golfer.IsStarter = False
            golfer.IsBench = False
        else:
            print(f"Golfer ID {golfer_id} not found on this team.")

        self.save()

    def get_golfer_usage(self, golfer_id: PyObjectId) -> int:
        """Gets the usage count for a golfer."""
        golfer = self.Golfers.get(str(golfer_id))
        return golfer.UsageCount if golfer else 0

    def is_golfer_on_team(self, golfer_id: PyObjectId) -> bool:
        """Checks if a golfer is currently on the team."""
        golfer = self.Golfers.get(str(golfer_id))
        return golfer.CurrentlyOnTeam if golfer else False

    def set_golfer_as_starter(self, golfer_id: PyObjectId):
        """Sets a golfer as a starter."""
        golfer = self.Golfers.get(str(golfer_id))
        if golfer:
            golfer.IsStarter = True
            golfer.IsBench = False
        self.save()

    def set_golfer_as_bench(self, golfer_id: str):
        """Sets a golfer as a bench player."""
        golfer = self.Golfers.get(str(golfer_id))
        if golfer:
            golfer.IsStarter = False
            golfer.IsBench = True
        self.save()

    def total_golfers(self) -> int:
        """Returns the total number of golfers currently on the team."""
        return sum(1 for golfer in self.Golfers.values() if golfer.CurrentlyOnTeam)

    def get_all_current_golfers(self) -> List[Dict]:
        from models import Golfer

        """Gets all current golfers on the team."""
        return [
            Golfer(**(db.golfers.find_one({"_id": ObjectId(golfer_id)}))).to_dict()
            for golfer_id, golfer_data in self.Golfers.items()
            if golfer_data and golfer_data.CurrentlyOnTeam
        ]

    def get_all_golfers(self, db) -> list:
        """Gets all golfers with their details."""
        golfer_ids = self.Golfers.keys()
        golfers_data = list(db.golfers.find({"_id": {"$in": [ObjectId(gid) for gid in golfer_ids]}}))

        for golfer in golfers_data:
            golfer_id_str = str(golfer["_id"])
            golfer_obj = self.Golfers[golfer_id_str]
            golfer.update({
                "UsageCount": golfer_obj.UsageCount,
                "CurrentlyOnTeam": golfer_obj.CurrentlyOnTeam,
                "IsStarter": golfer_obj.IsStarter,
                "IsBench": golfer_obj.IsBench
            })

        return golfers_data



