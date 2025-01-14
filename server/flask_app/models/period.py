from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from bson import ObjectId
from itertools import groupby

# Add this line to ensure the correct path
import sys
import os

# Adjust the paths for MacOS to get the server directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.base_model import Base
from helper_methods import convert_utc_to_local, get_day_number
from models import PyObjectId
from config import db

TeamResult = Any

class Period(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    StartDate: Any
    EndDate: Any
    PeriodNumber: int = Field(description="whatever number field this is in the list of periods total")
    WaiverPool: Optional[List[Dict]] = []
    FantasyLeagueSeasonId: PyObjectId
    Standings: Optional[List[PyObjectId]] = []                                        
    FreeAgentSignings: Optional[Dict[str, List[PyObjectId]]] = {}
    Matchups: Optional[List[Tuple[PyObjectId, PyObjectId]]] = []
    Drops: Optional[Dict[PyObjectId, List]] = {}
    TournamentId: PyObjectId
    TeamResults: Optional[List[PyObjectId]] = Field(default_factory=list)  # Unique per instance
    LeagueId: PyObjectId
    DraftId: Optional[PyObjectId] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def determine_reverse_standings_winners(self):
        for golfer_id, waivers in self.WaiverPool.items():
            sorted_waiver_numbers = sorted(waivers, key=lambda x: list(x.values())[0])
            for entry in sorted_waiver_numbers:
                winner_id = list(entry.keys())[0]
                team = db.teams.find_one({"OwnerId": winner_id, "LeagueId": self.LeagueId})
                if len(team["Golfers"]) < team["MaxGolfersPerTeam"]:
                    team["Golfers"].append(golfer_id)
                    db.teams.update_one({"_id": team["_id"]}, {"$set": {"Golfers": team["Golfers"]}})
                    break
                else:
                    raise ValueError("There is not enough space on this team to add this golfer. Please remove a golfer.")

    def determine_faab_winners(self):
        for golfer_id, bids in self.WaiverPool.items():
            sorted_bids = sorted(bids, key=lambda x: list(x.values())[0], reverse=True)
            winner_entry = sorted_bids[0]
            winner_id = list(winner_entry.keys())[0]
            winner_bid = list(winner_entry.values())[0]

            team = db.teams.find_one({"OwnerId": winner_id, "LeagueId": self.LeagueId})
            team["Golfers"].append(golfer_id)
            team["FAAB"] -= winner_bid

            db.teams.update_one({"_id": team["_id"]}, {"$set": {"Golfers": team["Golfers"], "FAAB": team["FAAB"]}})

    def determine_waiver_winners(self) -> None:
        league = db.leagues.find_one({"_id": self.LeagueId})
        league_settings = league["LeagueSettings"]

        league_timezone = league_settings["TimeZone"]
        
        utc_now = datetime.now(timezone.utc)
        local_now = convert_utc_to_local(utc_now, league_timezone)
        today_day_number = local_now.weekday()
        
        waiver_day_number = get_day_number(league_settings["WaiverDeadline"])

        if today_day_number <= waiver_day_number:
            raise ValueError("The waiver deadline has not passed yet.")
        
        if league_settings["WaiverType"] == "FAAB":
            self.determine_faab_winners()
        elif league_settings["WaiverType"] == "Reverse Standings":
            self.determine_reverse_standings_winners()
        else:
            raise ValueError("Invalid waiver type specified in league settings.")

    def add_to_waiver_pool(self, golfer_id: PyObjectId, user_id: PyObjectId, bid: int) -> bool:
        from models import League

        # Fetch the league and its settings
        league = db.leagues.find_one({"_id": self.LeagueId})
        league_settings = league["LeagueSettings"]
        team = db.teams.find_one({"OwnerId": user_id, "LeagueId": self.LeagueId})

        league_timezone = league_settings["TimeZone"]
        
        # Convert current UTC time to user's local time
        utc_now = datetime.now(timezone.utc)
        local_now = convert_utc_to_local(utc_now, league_timezone)
        today_day_number = get_day_number(local_now.weekday())
        
        waiver_day_number = get_day_number(league_settings["WaiverDeadline"])

        if today_day_number > waiver_day_number:
            raise ValueError("The waiver deadline has passed.")

        # Check if the golfer exists
        check_golfer_in_db = db.golfers.find_one({"_id": golfer_id})
        if not check_golfer_in_db:
            raise ValueError("Sorry, that golfer does not exist.")

        # Add or update the waiver pool based on waiver type
        if golfer_id not in self.WaiverPool:
            self.WaiverPool[golfer_id] = []

        if league_settings["WaiverType"] == "FAAB":
            existing_entry = next((entry for entry in self.WaiverPool[golfer_id] if user_id in entry), None)
            if existing_entry:
                existing_entry[user_id] = bid
            else:
                self.WaiverPool[golfer_id].append({user_id: bid})
        elif league_settings["WaiverType"] == "Reverse Standings":
            if user_id not in (entry.keys() for entry in self.WaiverPool[golfer_id]):
                self.WaiverPool[golfer_id].append({user_id: team["WaiverNumber"]})
                league = League(**league)
                league.determine_waiver_order()
        else:
            raise ValueError("Invalid waiver type specified in league settings.")

        # Save the updated waiver pool
        self.save()
        return True

    def save(self) -> Optional[ObjectId]:
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        period_dict = self.dict(by_alias=True, exclude_unset=True)

        if '_id' in period_dict and period_dict['_id'] is not None:
            # Update existing document
            result = db.periods.update_one({'_id': period_dict['_id']}, {'$set': period_dict})
            if result.matched_count == 0:
                raise ValueError("No document found with _id: {}".format(period_dict['_id']))
        else:
            # Insert new document
            result = db.periods.insert_one(period_dict)
            self.id = result.inserted_id
        return self.id

    def set_standings(self) -> bool:
        from models import TeamResult

        league_id = self.LeagueId

        # Find league settings in the db. Will be used for multiple things
        league_settings = db.leagueSettings.find_one({"LeagueId": league_id})

        # If the league is head-to-head, standings do not need to be set
        # because points per placing are irrelevant; standings are determined by wins and losses.
        if league_settings["HeadToHead"]:
            return False

        team_results = []

        # Accumulate all of the team's results into an array
        for team_result_id in self.TeamResults:
            team_result_doc = db.teamResults.find_one({"_id": team_result_id})
            # Ensure it is not None type
            if team_result_doc:
                team_results.append(TeamResult(**team_result_doc))

        current_time = datetime.now()

        # Ensure there are team results and the period is over 
        # before applying points to teams
        if team_results:
            if league_settings is None:
                raise ValueError("League settings not found.")

            # Sort teams by TeamScore (lower scores are better)
            team_results.sort(key=lambda x: x.TeamScore)

            # Group by TeamScore (find tied teams)
            grouped_by_score = groupby(team_results, key=lambda x: x.TeamScore)

            sorted_team_results = []

            for score, tied_teams in grouped_by_score:
                tied_teams_list = list(tied_teams)

                # If there's more than one team with the same TeamScore, apply tiebreaker
                if len(tied_teams_list) > 1:
                    # Sort tied teams by the highest golfer score (lower is better)
                    sorted_tied_teams = sorted(
                        tied_teams_list,
                        key=lambda x: self.get_highest_golfer_score(x)  # Tiebreaker
                    )
                    sorted_team_results.extend(sorted_tied_teams)
                else:
                    # No tie, just append the team
                    sorted_team_results.extend(tied_teams_list)

            period_over = current_time >= self.EndDate

            # Ensure the period is over before applying points to teams
            if period_over:
                for placing, team_result in enumerate(sorted_team_results, start=1):
                    points_from_placing = 0

                    points_per_placing_arr = league_settings["PointsPerPlacing"]

                    # Check the array for the number of places awarded points
                    num_of_scoring_places = len(points_per_placing_arr)

                    # If this team is in the scoring threshold, we will award points.
                    if placing <= num_of_scoring_places:
                        points_from_placing += points_per_placing_arr[placing - 1]

                    # Update the placing and points earned within teamResults
                    db.teamResults.update_one(
                        {"_id": team_result.id},
                        {"$set": {
                            "Placing": placing, 
                            "PointsFromPlacing": points_from_placing
                        }}
                    )

                # Add the points that the team accumulated from the place they came in
                self.contribute_placing_points_to_teams()

            # Adjust the standings 
            self.Standings = [team_result.TeamId for team_result in sorted_team_results]

            for team_id in self.Standings:
                team = db.teams.find_one({"_id": team_id})
                print(team["TeamName"], team["Points"])

            self.save()

        return True
    
    # Tiebreaker method to get the highest scoring golfer in a team
    def get_highest_golfer_score(self, team_result: "TeamResult") -> int:
        # Retrieve the golfer scores associated with the team
        golfer_scores = []

        for golfer_details_id in team_result.GolfersScores:
            golfer_details = db.golfertournamentdetails.find_one({
                "_id": golfer_details_id
            })
            
            if golfer_details and "Score" in golfer_details:
                score = golfer_details["Score"]

                # Handle "E" (even par)
                if score == 'E':
                    score = 0
                else:
                    # Ensure score is a valid integer
                    try:
                        score = int(score)
                    except ValueError:
                        score = 1000  # Assign a high value if there's an error parsing the score

                golfer_scores.append(score)
        
        # Return the lowest score (since lower is better), or a large value if no scores are found
        print(min(golfer_scores))
        return min(golfer_scores) if golfer_scores else 1000

    def contribute_placing_points_to_teams(self) -> bool:

        team_results = self.TeamResults

        # iterate through each team result
        for team_result_id in team_results:

            # find the team result doc from the db
            team_result_doc = db.teamResults.find_one({
                "_id": team_result_id
            })

            # handle None type
            if not team_result_doc:
                raise ValueError("Team Result does not exist.")

            # grab team from db to add points to
            associated_team = db.teams.find_one({ 
                "_id": team_result_doc["TeamId"]
            })

            # handle None type
            if not associated_team:
                raise ValueError("Team does not exist.")

            # add up points and set to a variable
            associated_team_points = associated_team["Points"] + team_result_doc["PointsFromPlacing"]

            # update the team in the database
            db.teams.update_one(
                {"_id": associated_team["_id"]},
                {"$set": {"Points": associated_team_points}}
            )
        
        return True

    # @model_validator(mode='before')
    # def validate_dates(cls, values):
    #     start_date = values.get('StartDate')
    #     end_date = values.get('EndDate')
    #     today = datetime.now()

    #     # Check if the start date is before today's date
    #     if start_date and start_date < today:
    #         raise ValueError('Start date cannot be before today\'s date')

    #     # Check if end date is after start date
    #     if start_date and end_date and end_date <= start_date:
    #         raise ValueError('End date must be after start date')

    #     return values

    @field_validator('TournamentId')
    def check_tournament_id_exists(cls, v):
        tournament = db.tournaments.find_one({"_id": v})
        if not tournament:
            raise ValueError("The tournament does not exist.")
        return v

    @field_validator('PeriodNumber')
    def period_number_must_be_valid(cls, v):
        tournament_count = db.tournaments.count_documents({})
        if not (1 <= v <= tournament_count):
            raise ValueError(f'Period number must be between 1 and the number of tournaments available to play: {tournament_count}')
        return v