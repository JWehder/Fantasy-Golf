from typing import List, Optional, Dict
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

from helper_methods import convert_to_datetime

class FantasyLeagueSeason(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    SeasonNumber: int
    StartDate: datetime
    EndDate: datetime
    Periods: Optional[List[PyObjectId]] = []
    CurrentPeriod: Optional[PyObjectId] = None
    Tournaments: List[PyObjectId] = []
    LeagueId: PyObjectId
    Active: bool = Field(default=False, description="determine whether the competition is league wide or just between two users")
    Winner: PyObjectId = Field(default=None, description="Winner user ObjectId of the league")
    CurrentStandings: List[PyObjectId] = Field(default=[], description="Array of teams sorted by the number of points they have or wins and losses.")
    Teams: List[PyObjectId] = []
    ProSeasonId: PyObjectId
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def start_new_period(self):
        # Create a new period starting from the end of the last tournament
        current_period = db.periods.find_one({ "_id": self.CurrentPeriod })

        next_period = db.periods.find_one({ "PeriodNumber": current_period["PeriodNumber"] + 1 })

        self.CurrentPeriod = next_period.id
        self.save()

    def update_period_end_date(self, tournament_end_date: datetime):
        # Update the end date of the current period when a tournament ends
        if self.CurrentPeriod:
            period = db.periods.find_one({"_id": self.CurrentPeriod})
            if period:
                period["EndDate"] = tournament_end_date
                db.periods.update_one({"_id": self.CurrentPeriod}, {"$set": {"EndDate": tournament_end_date}})

    def update_standings(self):
        league = db.leagues.find_one({
            "_id": self.LeagueId
        })

        standings = []
        for team_id in league.Teams:
            team = db.teams.find_one({ "_id": team_id })
            if team:
                standings.append((team_id, team['Points']))
        # Sort teams by points
        standings = standings.sort(key=lambda x: x[1], reverse=True)
        self.CurrentStandings = [team_id for team_id, points in standings]
        self.save()

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        fantasy_league_season_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in fantasy_league_season_dict and fantasy_league_season_dict['_id'] is not None:
            # Update existing document
            result = db.fantasyLeagueSeasons.update_one({'_id': fantasy_league_season_dict['_id']}, {'$set': fantasy_league_season_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(fantasy_league_season_dict['_id']))
        else:
            # Insert new document
            result = db.fantasyLeagueSeasons.insert_one(fantasy_league_season_dict)
            self.id = result.inserted_id
        return self.id

    # @field_validator('Tournaments')
    # def validate_tournament_start_dates(cls, tournament_ids_list):
    #     current_date = datetime.now()

    #     # Query the database for tournaments with the specified IDs
    #     tournaments = db.tournaments.find({
    #         "_id": {"$in": tournament_ids_list}
    #     })

    #     # Check if any tournament's start date is before today's date
    #     for tournament in tournaments:
    #         if "StartDate" in tournament and tournament["StartDate"] < current_date:
    #             raise ValueError(f"Tournament {tournament['_id']} has a start date before today.")

    #     return tournament_ids_list
    
    @model_validator(mode='before')
    def validate_and_convert_dates(cls, values):
        start_date = values.get('StartDate')
        end_date = values.get('EndDate')

        if isinstance(start_date, str):
            values['StartDate'] = datetime.fromisoformat(start_date)
        
        if isinstance(end_date, str):
            values['EndDate'] = datetime.fromisoformat(end_date)
        
        return values

    @field_validator('StartDate', 'EndDate')
    def dates_must_be_valid(cls, v, field):
        if not isinstance(v, datetime):
            raise ValueError(f'{field.name} must be a datetime')
        return v

    @model_validator(mode='before')
    def validate_dates(cls, values):
        start_date = values.get('StartDate')
        end_date = values.get('EndDate')

        if start_date and end_date and end_date <= start_date:
            raise ValueError('End date must be after start date')

        return values

    def create_season_dict(self, tournament_ids: List[ObjectId], league_id: ObjectId) -> Dict:

        from models import FantasyLeagueSeason

        if not self.FantasyLeagueSeasons or len(self.FantasyLeagueSeasons) < 1:
            if not tournament_ids:
                raise ValueError("No tournaments specified for the initial season.")

            first_tournament_doc = db.tournaments.find_one({
                "_id": ObjectId(tournament_ids[0])
            })
            last_tournament_doc = db.tournaments.find_one({
                "_id": ObjectId(tournament_ids[-1])
            })

            first_season = FantasyLeagueSeason(
                SeasonNumber=1,
                StartDate=first_tournament_doc["StartDate"],
                EndDate=last_tournament_doc["EndDate"],
                Periods=[],
                LeagueId=league_id,
                Tournaments=tournament_ids,
                Active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            first_season_dict = first_season.dict(by_alias=True, exclude_unset=True)
            first_season_dict["_id"] = ObjectId()

            return first_season_dict

    def add_tournament_and_period_to_calendar(self, tournament_id: PyObjectId):
        from models import Period, Draft

        tournament = db.tournaments.find_one({
            "_id": tournament_id
        })

        if tournament:
            # Query to find the overlapping period
            overlapping_period = db.periods.find_one({
                "FantasyLeagueSeasonId": self.id,
                "$and": [
                    {"StartDate": {"$lte": tournament["StartDate"]}},  # Period starts before or on the tournament's start date
                    {"EndDate": {"$gte": tournament["EndDate"]}}       # Period ends after or on the tournament's end date
                ]
            })

            if overlapping_period:
                overlapping_period = Period(**overlapping_period)

                league = db.leagues.find_one({
                    "_id": overlapping_period["LeagueId"]
                })

                league_settings = league["LeagueSettings"]

                draft_start_date = convert_to_datetime(
                    league_settings["DraftStartDayOfWeek"],
                    league_settings["DraftStartTime"],
                    league_settings["TimeZone"]
                )

                draft_id = ObjectId()

                new_period = Period(
                    id=ObjectId(),
                    StartDate=overlapping_period["StartDate"],
                    EndDate=overlapping_period["EndDate"],
                    PeriodNumber=overlapping_period["PeriodNumber"] + 1,
                    WaiverPool=[],
                    FantasyLeagueSeasonId= overlapping_period["FantasyLeagueSeasonId"],
                    Standings=[],
                    FreeAgentSignings={},
                    Drops={},
                    TournamentId=tournament_id,
                    TeamResults=[],
                    LeagueId=overlapping_period["LeagueId"],
                    DraftId=draft_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                draft = Draft(
                    id=draft_id,
                    LeagueId=self.id,
                    StartDate=draft_start_date,
                    Rounds=league_settings["MaxGolfersPerTeam"],
                    PeriodId=new_period.id,
                    Picks=[],
                    DraftOrder=[],
                    IsComplete=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )


