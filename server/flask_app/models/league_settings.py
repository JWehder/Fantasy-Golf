from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from bson import ObjectId
import re

# Add this line to ensure the correct path
import sys
import os

# Adjust the paths for MacOS to get the server directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.base_model import Base
from models import PyObjectId
from config import db

class LeagueSettings(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    created_at: Optional[datetime] = None
    Sport: str = Field(default="Golf", description="Type of fantasy sports league.")
    CutPenalty: int = Field(default=0, description="Default points for players finishing outside the defined placements")
    DraftingFrequency: int = Field(default=0, description="The number of times the league drafts in between tournaments.")
    DraftStartDayOfWeek: Optional[str] = Field(default="Monday", description="Day of the week in which the draft starts before a tournament or season.")
    DraftStartTime: Optional[str] = Field(default="12:00", description="Time of day when the draft starts, in HH:MM format.")
    DropDeadline: Optional[str] = None
    ForceDrops: Optional[int] = 0
    LeagueId: PyObjectId
    MaxDraftedPlayers: int = Field(default=1, ge=0, description="Number of draft players per period")
    MaxGolfersPerTeam: int = Field(default=3, ge=1, description="Maximum number of golfers per team")
    MaxNumOfGolferUses: Optional[int] = Field(default=None, description="Number of times a golfer can be used")
    MinFreeAgentDraftRounds: int = Field(default=3, ge=1, description="Minimum number of draft rounds that need to be created each period")
    NumOfBenchGolfers: int = Field(default=1, ge=0, description="Number of bench players per team")
    NumOfStarters: int = Field(default=2, ge=1, description="Number of starters per team")
    NumberOfTeams: Optional[int] = Field(default=8, description="Number of the teams within the league.")
    PointsPerPlacing: Optional[List[int]] = Field(default=[], description="Points awarded for placements")
    PointsPerScore: Optional[dict] = Field(default_factory=lambda: {
        'Albatross': 7,
        'Eagles': 5,
        'Birdies': 3,
        'Pars': 1,
        'Bogeys': -1,
        'DoubleBogeys': -3,
        'WorseThanDoubleBogeys': -5
    }, description="Points awarded per round performance")
    Game: Literal["Standard", "Head to Head", "Match Play"] = Field(default="Stroke Play", description="Decide whether to score by the sum of strokes, points awarded via score under or over par, or match golfers up and give out points per round won.")
    PointsType: Literal["Strokes", "Points per Score", "Matchup Win"] = Field(default="Strokes", description="Choose whether to award points via strokes, a number of points based on how the league agrees to hand out points, or based on who wins a matchup.")
    SecondsPerDraftPick: Optional[int] = Field(default=3600, description="Time to draft in seconds, default is 3600 seconds (1 hour)")
    DraftType: Literal["Snake Draft", "Standard"] = Field(default="Snake Draft", description="The order of picks reverses with each round.")
    TimeZone: str = "UTC"
    updated_at: Optional[datetime] = None
    WaiverDeadline: Optional[str] = Field(default="Wednesday", description="Day of the week where players on waivers are distributed.")
    WaiverType: str = Field(default="Reverse Standings", description="Determine the priority with which teams receive in picking up free agents")
    Sport: Literal["Golf"] = "Golf"
    ProSeasonId: PyObjectId

    def determine_points_per_placing(self):
        if not self.PointsPerPlacing:
            self.PointsPerPlacing = list(range(self.NumberOfTeams, 0, -1))

    # Function to determine drafting frequency options
    def determine_drafting_frequency_options(self) -> List[int]:
        # Fetch the league document using the LeagueId
        league = db.leagues.find_one({"_id": self.LeagueId})
        
        if league is None:
            raise ValueError("No league found with the provided LeagueId")
        
        num_of_tournaments = len(league['tournaments'])
        
        # Possible drafting frequency options (can be adjusted as needed)
        nums = [1, 2, 3, 4, 5]
        
        # Return the numbers that evenly divide the number of tournaments
        return [num for num in nums if num_of_tournaments % num == 0]

    def save(self, league_id: Optional[PyObjectId] = None) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        league_settings_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in league_settings_dict and league_settings_dict['_id'] is not None:
            # Update existing document
            result = db.leagueSettings.update_one({'_id': league_settings_dict['_id']}, {'$set': league_settings_dict})

            # If league_id is provided, associate the new LeagueSettings with the League
            if league_id is not None:
                db.leagues.update_one({'_id': league_id}, {'$set': {'LeagueSettings': league_settings_dict}})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(league_settings_dict['_id']))
        else:
            # Insert new document
            result = db.leagueSettings.insert_one(league_settings_dict)
            self.id = result.inserted_id
            # If league_id is provided, associate the new LeagueSettings with the League
            if league_id is not None:
                db.leagues.update_one({'_id': league_id}, {'$set': {'LeagueSettings': league_settings_dict}})

        return self.id

    @field_validator('DraftStartTime')
    def validate_draft_start_time(cls, v):
        if not re.match(r'^\d{2}:\d{2}$', v):
            raise ValueError('DraftStartTime must be in HH:MM format')
        hours, minutes = map(int, v.split(':'))
        if not (0 <= hours < 24) or not (0 <= minutes < 60):
            raise ValueError('DraftStartTime must be a valid time in HH:MM format')
        return v

    # only matters if the league is running head to head matchups
    @model_validator(mode='before')
    def validate_number_of_teams(cls, values):
        number_of_teams = values.get('NumberOfTeams')
        head_to_head = values.get('HeadToHead')
        print(head_to_head, number_of_teams)

        if head_to_head and number_of_teams % 2 != 0:
            print("After validation")
            raise ValueError("The number of teams in your league must be even if you want to play a head-to-head league.")

        return values

    @field_validator("PointsPerScore", mode="before")
    def validate_points_per_score(cls, points):
        for score_type, value in points.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"Points for {score_type} must be a number.")
            if value < -9 or value > 9:
                raise ValueError(f"Points for {score_type} must be between -9 and 9.")
        return points

    @field_validator('NumberOfTeams')
    def num_of_teams_constraint(cls, v):
        print(v)
        if v > 16:
            raise ValueError("There cannot be more than 16 teams in a league.")
        return v

    @model_validator(mode='before')
    def validate_draft_rounds(cls, values):
        min_free_agent_draft_rounds = values.get('MinFreeAgentDraftRounds')
        max_golfers_per_team = values.get('MaxGolfersPerTeam')

        if max_golfers_per_team is not None and min_free_agent_draft_rounds >= max_golfers_per_team:
            raise ValueError('The amount of draft rounds that have been created is more than the max amount of players allowed per team.')
        
        return values

    @field_validator('SecondsPerDraftPick')
    def time_to_draft_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Time to draft must be a positive period of time.')
        return v

    @model_validator(mode='before')
    def validate_num_of_starters(cls, values):
        num_of_starters = values.get('NumOfStarters')
        max_golfers_per_team = values.get('MaxGolfersPerTeam')

        if max_golfers_per_team is not None and num_of_starters > max_golfers_per_team:
            raise ValueError('Number of defined players must be less than the maximum number of golfers per team.')

        return values

    @model_validator(mode='before')
    def validate_max_drafted_players(cls, values):
        max_drafted_players = values.get('MaxDraftedPlayers')
        max_golfers_per_team = values.get('MaxGolfersPerTeam')

        if max_drafted_players is not None and max_golfers_per_team is not None:
            if max_drafted_players > max_golfers_per_team:
                raise ValueError("Max draftable players must be less than or equal to the maximum golfers allowed on a team.")
        
        return values

    @field_validator('PointsPerPlacing')
    def points_per_placing_must_be_in_range(cls, v):
        if any(points < -10 or points > 10 for points in v):
            raise ValueError('Points per placing must be within the range of -10 to 10')
        return v

    @field_validator('PointsPerScore')
    def points_per_score_must_be_in_range(cls, v):
        if any(points < -10 or points > 10 for points in v.values()):
            raise ValueError('Points per score must be within the range of -10 to 10')
        return v

    @field_validator('WaiverType')
    def define_waiver_fomat(cls, v):
        if v not in ["Reverse Standings", "Bidding"]:
            raise ValueError("Waiver type must be either a bidding format or first to last.")
        return v

    @model_validator(mode = 'before')
    def bench_players_under_limit(cls, values):
        num_of_bench_golfers = values.get('NumOfBenchGolfers')
        max_golfers_per_team = values.get('MaxGolfersPerTeam')
        num_of_starters = values.get('NumOfStarters')

        if num_of_bench_golfers > max_golfers_per_team or num_of_bench_golfers > num_of_starters // 2:
            return ValueError("Your number of bench golfers must be less than half your starters count and less than max amount of players allowed on a team.")
        return values

    def drafting_period_must_be_valid(self):
        league = db.leagues.find_one({ "_id": self.LeagueId })
        season = db.fantasyLeagueSeasons.find_one({ "_id": league["CurrentFantasyLeagueSeasonId"], "LeagueId": league["_id"]})
        if self.DraftingFrequency > len(season["Tournaments"]):
            raise ValueError("You cannot have more drafts than you have selected tournaments")
        return True

    def __init__(self, **data):
        super().__init__(**data)
        self.determine_points_per_placing()