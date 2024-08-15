import gspread
import pandas as pd
from pymongo import MongoClient
import os
import sys
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask_app.models import LeagueSettings, User, League, FantasyLeagueSeason

passcode = os.getenv("MONGO_PASSWORD")
test_user_username = os.getenv("TEST_USER_USERNAME")
test_user_password = os.getenv("TEST_USER_PASSWORD")

uri = f"mongodb+srv://jakewehder:{passcode}@cluster0.gbnbssg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)

db = client.scramble

# Initialize the gspread client with API key
gc = gspread.service_account(filename='scramble-credentials.json')

# Open the Google Sheet
spreadsheet = gc.open("Weber Fantasy Golf Spreadsheet")

# class Draft(BaseModel):
#     _id: Optional[PyObjectId] = Field(alias='_id')
#     LeagueId: str
#     StartDate: datetime
#     EndDate: Optional[datetime] = None
#     Rounds: int
#     Picks: List[PyObjectId]
#     DraftOrder: List[PyObjectId]

tournament_ids = [
    ObjectId('663168ca74d57119dcdc701d'),
    ObjectId('66315535ee741e831355a09a'),
    ObjectId('66314f78ee741e831355465c'),
    ObjectId('66316b9774d57119dcdc99ee'),
    ObjectId('66316a3474d57119dcdc852c'),
    ObjectId('66a6d5396556c7133a4bc9ea'),
    ObjectId('66a6d99d6556c7133a4c1d92'),
    ObjectId('66a6e7246556c7133a4d2da3'),
    ObjectId('66a6ebe46556c7133a4d8bb2'),
    ObjectId('66a6f06a6556c7133a4de15d'),
    ObjectId('66a6f9b16556c7133a4e9c39'),
    ObjectId('66a6fbca6556c7133a4ec6fc'),
    ObjectId('66a6d7576556c7133a4bf2d5'),
    ObjectId('66a172dcf47cd3eec71b0d05'),
    ObjectId('66a6e7246556c7133a4d2da3')
]

# Fetch the documents based on tournament IDs
sorted_tournaments = list(db.tournaments.find(
    {"_id": {"$in": tournament_ids}},
    sort=[("StartDate")] 
))

# Function to process each worksheet
def process_worksheet(worksheet):
    # Get all values from the worksheet
    rows = worksheet.get_all_values()
    # Convert to a pandas DataFrame
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df


# id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
# SeasonNumber: int
# StartDate: datetime
# EndDate: datetime
# Periods: List[PyObjectId]
# LeagueId: PyObjectId
# Active: bool = Field(default=False, description="determine whether the competition is league wide or just between two users")
# created_at: Optional[datetime] = None
# updated_at: Optional[datetime] = None


def create_test_weber_league():
    user = User(
        Username=f'{test_user_username}',
        Email='jake.wehder@gmail.com',
        Password=f'{test_user_password}',
        Teams=[]
    )

    user_id = user.save()

    league = League(
        Name="Weber",
        CommissionerId=user_id,
        Teams=[],
        LeagueSettings= {},
        Seasons=[],
        CurrentStandings=[],
        WaiverOrder=[],
        CurrentPeriod=None
    )
    league_id = league.save()

    # Find the tournament with the earliest start date
    first_tournament = sorted_tournaments[0]

    # Find the tournament with the latest end date
    last_tournament = sorted_tournaments[-1]

    fantasy_league_season = FantasyLeagueSeason(
        SeasonNumber= 1,
        StartDate=first_tournament["StartDate"],
        EndDate=last_tournament["EndDate"],
        Tournaments=tournament_ids,
        LeagueId=league_id,
        Active=True
    )

    fantasy_league_season_id = fantasy_league_season.save()

    league.create_periods_between_tournaments()

    LeagueSettings = LeagueSettings(
        SnakeDraft=True,
        StrokePlay=True,
        ScorePlay=False,
        PointsPerScore=[],
        MinFreeAgentDraftRounds=1,
        ForceDrops=1,
        DropDeadline="Tuesday",
        TimeZone="US/Eastern",
        MaxGolfersPerTeam=4,
        WaiverType="Reverse Standings",
        NumberOfTeams=9,
        NumOfStarters=3,
        NumOfBenchGolfers=1,
        MaxDraftedPlayers=1,
        PointsPerPlacing=[10, 8, 6, 5, 4, 3, 2, 1, 0],
        Tournaments= tournament_ids,
        MaxNumberOfGolferUses=None,
        DraftingFrequency=1,
        DraftStartDayOfWeek="Wednesday",
        WaiverDeadline="Wednesday",
        SecondsPerDraftPick=3600,
        HeadToHead=False,
        LeagueId= league_id,
        DefaultPointsForNonPlacers= 0
    )

    league.create_initial_teams()


# test_league = db.leagues.find_one({ "Name": "Weber" })

# if not test_league: 
#     create_test_weber_league()

# Compile golfers' uses for each team
def compile_golfers_usage(spreadsheet):
    golfers_usage = {}

    first_spreadsheet = spreadsheet.worksheets()[3]

    a_cell_counter = 3
    while a_cell_counter < 29:
        team = first_spreadsheet.acell(f'A{a_cell_counter}').value
        golfers_usage[team] = []
        # class TeamResult(BaseModel):
        # TeamId: PyObjectId
        # LeagueId: PyObjectId
        # TournamentId: PyObjectId
        # PeriodId: PyObjectId
        # TotalPoints: int = 0
        # GolfersScores: Dict[PyObjectId, Dict[str, int]]
        # Placing: Optional[int] = 0
        # PointsFromPlacing: int = 0
        # created_at: Optional[datetime] = None
        # updated_at: Optional[datetime] = None

        b_cell_counter = a_cell_counter
        a_cell_counter += 3
        while b_cell_counter < a_cell_counter:
            player = first_spreadsheet.acell(f'B{b_cell_counter}').value

            print(player)

            test_tourney_id = ObjectId('66316b9774d57119dcdc99ee')

            golfer_tournament_details = db.golfertournamentdetails.find_one({ "Name": f"{player}", "TournamentId": test_tourney_id })

            if golfer_tournament_details:
                golfers_usage[team].append({player: golfer_tournament_details["Score"]})
            else:
                golfers_usage[team].append({player: 0})
            
            b_cell_counter += 1
        
        # class Team(BaseModel):
        #     _id: Optional[PyObjectId] = Field(alias='_id')
        #     TeamName: str
        #     ProfilePicture: Optional[str] = Field(description="Profile picture for team")
        #     Golfers: Dict[PyObjectId, Dict[str, any]] = Field(default_factory=dict, description="Dictionary of golfer IDs with usage count and team status")
        #     OwnerId: PyObjectId
        #     LeagueId: PyObjectId
        #     DraftPicks: List[PyObjectId]

    # Loop through each worksheet in the spreadsheet
    # for worksheet in spreadsheet.worksheets():
    #     df = process_worksheet(worksheet)
    #     cell_number = 3
    #     while cell_number < 29:
    #         val = worksheet.acell(f'A{cell_number}').value
    #         cell_number += 3
    #         print(val)
    #     for index, row in df.iterrows():
    #         team_name = row[0].strip('"')
    #         golfers = row[1:]

    #         for golfer in golfers:
    #             if golfer:
    #                 golfer = golfer.strip()
    #                 if team_name not in golfers_usage:
    #                     golfers_usage[team_name] = {}
    #                 if golfer not in golfers_usage[team_name]:
    #                     golfers_usage[team_name][golfer] = 0
    #                 golfers_usage[team_name][golfer] += 1
    
    # Remove the newline characters from the keys
    cleaned_golfers_usage = {key.strip(): value for key, value in golfers_usage.items()}

    # processed_dict = {}

    # for manager, players in cleaned_golfers_usage.items():
    #     main_players = []
    #     bench_players = []
        
    #     for player in players:
    #         if '(' in player and ')' in player:
    #             # Split the string into the main player and the bench player
    #             main, bench = player.split('(')
    #             main = main.strip()  # Clean up whitespace
    #             bench = bench.replace(')', '').strip()  # Remove the closing parenthesis and clean up whitespace
                
    #             # Add to respective lists
    #             main_players.append(main)
    #             bench_players.append(bench)
    #         else:
    #             main_players.append(player.strip())
        
    #     processed_dict[manager] = {
    #         'main': main_players,
    #         'bench': bench_players
    #     }

    return cleaned_golfers_usage

# Get golfers usage data
golfers_usage = compile_golfers_usage(spreadsheet)
print(golfers_usage)

# Print the usage data
# for team, golfers in golfers_usage.items():
#     print(f"Team {team}:")
#     for golfer, uses in golfers.items():
#         print(f"  {golfer}: {uses} uses")