from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
import os
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pytz
import sys
from create_missing_golfers_from_tournament_scraper import scrape_tournament_golfers
from datetime import datetime, timedelta
import logging
from bson.objectid import ObjectId
from scripts.create_tourneys import handle_golfer_data

from tourney_scraper import parse_round_details
from scripts.create_tourneys import process_round_data

# Adjust the paths for MacOS
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_app.config import db
from flask_app.models import Round, GolferTournamentDetails, Hole

def scrape_ongoing_tournament(driver, leaderboard, tournament, specific_golfers=[]):
    from flask_app.models import GolferTournamentDetails
    """
    Scrape ongoing tournament data, focusing on rounds and holes not yet completed.
    """
    current_round_num = tournament["CurrentRoundNum"]

    golfers = []
    table_rows = leaderboard.find_elements(By.CSS_SELECTOR, "tr.PlayerRow__Overview")

    # Query incomplete rounds and join with golfer tournament details
    incomplete_rounds = query_golfers_without_rounds(tournament["_id"], current_round_num)

    headers = leaderboard.find_elements(By.CSS_SELECTOR, "th")
    mapped_headers = [header.text for header in headers]

    # Map known table headers to keys in the golfer_tournament_results dictionary
    table_headers_equivalents = {
        "POS": "Position",
        "PLAYER": "Name",
        "SCORE": "Score",
        "TODAY": "Today",
        "THRU": "Thru",
        "R1": "R1",
        "R2": "R2",
        "R3": "R3",
        "R4": "R4",
        "TOT": "TotalStrokes",
        "EARNINGS": "Earnings",
        "FEDEX PTS": "FedexPts"
    }

    curr_round_int = int(current_round_num.replace('Round ', ''))

    for row in table_rows:
        golfer_name = extract_golfer_name(row)

        # Skip row if golfer not found in the incomplete rounds
        if golfer_name not in incomplete_rounds:
            continue

        print(golfer_name)

        golfer_overview_data = extract_golfer_overview(row, mapped_headers, table_headers_equivalents, curr_round_int)

        if not golfer_overview_data["WD"] or not golfer_overview_data["Cut"] and curr_round_int > 2:

            golfer_tournament_details = incomplete_rounds[golfer_name]
            round_data = golfer_tournament_details["CurrentRound"] if "CurrentRound" in golfer_tournament_details else {}

            new_round_data = parse_golfer_rounds(driver, row, golfer_overview_data, tournament["Par"], current_round_num, round_data)

            if "Holes" in new_round_data and len(new_round_data["Holes"]) > 1:
                golfer_overview_data["Thru"] = len(new_round_data["Holes"]) if len(new_round_data["Holes"])< 18 else "F"

            if "Holes" in new_round_data and len(new_round_data["Holes"]) > 1 and len(new_round_data["Holes"]) < 18:
                print(new_round_data["Holes"])

            if golfer_overview_data["Today"] == 0 and "Score" in new_round_data:
                golfer_overview_data["Today"] = new_round_data["Score"]
            
            golfer_tournament_details["Score"] = 0 if golfer_tournament_details[""]
            golfer_overview_data["Score"] = golfer_overview_data["Score"]

            golfer_overview_data["Rounds"].append(new_round_data)

            golfer_tourney_details_dict = dict(golfer_tournament_details)
            golfer_tourney_details_dict.update(golfer_overview_data)

            golfers.append(golfer_overview_data)

    return golfers

def extract_golfer_name(row):
    try:
        return row.find_element(By.CSS_SELECTOR, "a.AnchorLink.leaderboard_player_name").text
    except NoSuchElementException as e:
        logging.warning(f"Could not extract golfer name: {e}")
        return None

def query_golfers_without_rounds(tournament_id, current_round_num):
    """
    Query golfers who do not yet have a round document for the current round number
    or whose Cut and WD flags are false.
    """
    pipeline = [
        {
            "$match": {
                "TournamentId": ObjectId(tournament_id),
                "Cut": False,
                "WD": False
            }
        },
        {
            "$lookup": {
                "from": "rounds",  # Assuming the "rounds" collection name
                "localField": "_id",
                "foreignField": "GolferTournamentDetailsId",
                "as": "Rounds"
            }
        },
        {
            "$addFields": {
                "CurrentRound": {
                    "$arrayElemAt": [
                        {
                            "$filter": {
                                "input": "$Rounds",
                                "as": "round",
                                "cond": {
                                    "$eq": ["$$round.Round", current_round_num]
                                }
                            }
                        },
                        0
                    ]
                }
            }
        },
        {
            "$match": {
                "$or": [
                    {"CurrentRound": None},  # Golfers with no round for the current round number
                    {"Rounds": {"$eq": []}},  # Golfers with no rounds at all
                    {
                        "$and": [
                            {"CurrentRound": {"$ne": None}},  # Golfers with a round for the current round number
                            {"$expr": {"$lt": [{"$size": "$CurrentRound.Holes"}, 18]}}  # Golfers with fewer than 18 holes
                        ]
                    }
                ]
            }
        },
        {
            "$project": {
                "Rounds": 0,  # Exclude the full Rounds array if not needed
            }
        }
    ]

    incomplete_golfers = list(db.golfertournamentdetails.aggregate(pipeline))

    # Create a dictionary with golfer names and incomplete round details
    golfers_incomplete_rounds = {}
    for golfer in incomplete_golfers:
        golfers_incomplete_rounds[golfer["Name"]] = golfer

    return golfers_incomplete_rounds

def parse_golfer_rounds(driver, row, golfer_data, par, round_text, existing_round):
    """
    Parse specific unplayed holes for a golfer in a particular round.
    """
    actions = ActionChains(driver)
    actions.move_to_element(row).perform()
    row.click()

    try:
        player_detail = WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.Leaderboard__Player__Detail"))
        )
        select_button = player_detail.find_element(By.CSS_SELECTOR, "select.dropdown__select")
        select = Select(select_button)

        # Navigate to the specific round
        select.select_by_visible_text(round_text)
        round_detail = parse_round_details(player_detail, round_text, golfer_data["WD"], par)
        
        if bool(existing_round):
            merged_round = dict(existing_round)  # Convert existing_round to a dictionary if not already
            merged_round.update(round_detail)  # Merge round_detail into merged_round
            existing_round = merged_round
        else:
            existing_round = round_detail

    except Exception as e:
        golfer_name = golfer_data['Name']
        # print(f"Error parsing rounds for golfer {golfer_name}: {e}")
    finally:
        row.click()  # Close the player detail section

    return existing_round

def extract_golfer_overview(row, mapped_headers, table_headers_equivalents, current_round_num):
    """
    Extract basic overview data for a golfer from the leaderboard row.
    """

    # Initialize golfer results with default values
    golfer_tournament_results = {
        "Position": None,
        "Name": None,
        "Score": 0,
        "Today": 0,
        "Thru": 0,
        "R1": 0,
        "R2": 0,
        "R3": 0,
        "R4": 0,
        "TotalStrokes": None,
        "Earnings": None,
        "FedexPts": None,
        "Rounds": [],
        "WD": False,
        "Cut": False
    }

    # Extract golfer name
    try:
        golfer_full_name = row.find_element(By.CSS_SELECTOR, "a.AnchorLink").text.split(' ')
        golfer_tournament_results["Name"] = f"{golfer_full_name[0]} {' '.join(golfer_full_name[1:])}"
    except Exception as e:
        print(f"Error extracting golfer name: {e}")
        return

    # Extract table row data
    row_data = row.find_elements(By.CSS_SELECTOR, "td.Table__TD")
    row_text = [cell.text.strip() for cell in row_data]

    # Map data to headers using table_headers_equivalents
    for header, value in zip(mapped_headers, row_text):
        equivalent_key = table_headers_equivalents.get(header)  # Get the mapped key
        if equivalent_key in golfer_tournament_results:
            # Handle special cases for "Score", "WD", "CUT", and numeric fields
            if equivalent_key == "Score":
                if value == "WD":
                    golfer_tournament_results["WD"] = True
                    golfer_tournament_results["Cut"] = False
                elif value == "CUT":
                    golfer_tournament_results["Cut"] = True
                    golfer_tournament_results["WD"] = False
                else:
                    golfer_tournament_results["Score"] = value
            elif equivalent_key == "Earnings":
                # Parse numeric earnings
                golfer_tournament_results["Earnings"] = ''.join(re.findall(r'(\d+)', value)) if value else None
            elif equivalent_key in ["R1", "R2", "R3", "R4", "TotalStrokes"]:
                try:
                    golfer_tournament_results[equivalent_key] = int(value)
                except ValueError:
                    golfer_tournament_results[equivalent_key] = value
            else:
                golfer_tournament_results[equivalent_key] = value
    return golfer_tournament_results

def is_round_complete(golfer_data, round_text):
    """
    Determine if a round is complete or if it needs to be updated.
    """
    for round_detail in golfer_data["Rounds"]:
        if round_detail["Round"] == round_text and len(round_detail["Holes"]) == 18:
            return True
    return False

def calculate_round_summary(round_detail):
    """
    Calculate summary statistics for a round (e.g., birdies, pars).
    """
    for hole in round_detail["Holes"]:
        if hole["NetScore"] == -3:
            round_detail["Albatross"] += 1
        elif hole["NetScore"] == -2:
            round_detail["Eagles"] += 1
        elif hole["NetScore"] == -1:
            round_detail["Birdies"] += 1
        elif hole["NetScore"] == 0:
            round_detail["Pars"] += 1
        elif hole["NetScore"] == 1:
            round_detail["Bogeys"] += 1
        elif hole["NetScore"] == 2:
            round_detail["DoubleBogeys"] += 1
        elif hole["NetScore"] > 2:
            round_detail["WorseThanDoubleBogeys"] += 1

    round_detail["Score"] = sum(hole["NetScore"] for hole in round_detail["Holes"] if hole["NetScore"] is not None)

def determine_score_from_rounds(rounds):
    """
    Calculate a golfer's total score from all rounds.
    """
    score_total = sum(round_["Score"] for round_ in rounds if round_["Score"] is not None)
    if score_total > 0:
        return f"+{score_total}"
    elif score_total == 0:
        return "E"
    return str(score_total)


def try_parse_int(value):
    """
    Attempt to parse an integer from a string. Return None on failure.
    """
    try:
        return int(value)
    except ValueError:
        return None

def get_holes_left_to_play(round_data):
    """
    Determine the holes a golfer hasn't played yet based on the round data.
    """
    completed_holes = {hole["HoleNumber"] for hole in round_data["Holes"]}
    all_holes = set(range(1, 19))  # Holes 1 through 18
    return list(all_holes - completed_holes)

def is_tee_time(value):
    """
    Check if a value is a tee time using regex.
    Matches formats like '10:30 AM' or '2:45 PM'.
    """
    time_pattern = r"^(1[0-2]|0?[1-9]):[0-5][0-9] (AM|PM)$"
    return bool(re.match(time_pattern, value))

def main():

    options = Options()

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.headless = True

    options.add_argument('--headless=new')

    # Only pass options once when creating the WebDriver instance
    wd = webdriver.Chrome(options=options)

    driver = wd

        # Define the current date
    current_date = datetime.now()

    # Calculate the date 4 days from now
    four_days_from_now = datetime.utcnow() + timedelta(days=4)

    # Query to find tournaments ending in less than 4 days
    in_progress_tournaments = db.tournaments.find({
        "InProgress": True # Ensure the tournament is still in progress
    })

    print(in_progress_tournaments[0])

    for tournament in in_progress_tournaments:
        print(tournament["Links"][0])
        driver.get(tournament["Links"][0])

        # Attempt to locate the competitors table
        competitors_table = driver.find_element(By.CSS_SELECTOR, "div.competitors")
        responsive_tables = competitors_table.find_elements(By.CSS_SELECTOR, "div.ResponsiveTable")

        golfers = scrape_ongoing_tournament(driver, responsive_tables[-1], tournament)

        process_golfer_data(golfers, tournament["_id"])

def process_golfer_data(golfers, tournament_id):
    from pymongo.errors import PyMongoError

    print("Processing golfer data for the tournament.")

    round_dicts = []
    hole_dicts = []
    golfer_tournament_details_dicts = []

    for golfer_data in golfers:

        if "GolferId" not in golfer_data:
            golfer_split_values = golfer_data["Name"].split(" ")
            first_name, last_name = golfer_split_values[0], ' '.join(golfer_split_values[1:])

            golfer = db.golfers.find_one({
                "FirstName": {"$regex": f"^{first_name}$", "$options": "i"},
                "LastName": {"$regex": f"^{last_name}$", "$options": "i"}
            })

        rounds = golfer_data.pop("Rounds")

        if not golfer and "GolferId" not in golfer_data:
            golfer_name = golfer_data["Name"]
            print(f"Could not find {golfer_name}.")
            continue
        
        golfer_details_id = ObjectId() if "_id" not in golfer_data else golfer_data["_id"]
        if "_id" not in golfer_data:
            print("I do not see a golfer details id")
            # Create an instance of GolferTournamentDetails
            golfer_details = GolferTournamentDetails(
                _id=golfer_details_id,
                GolferId=golfer["_id"],
                Position=golfer_data.get("Position"),
                Name=golfer_data.get("Name"),
                Score=golfer_data.get("Score"),
                R1=golfer_data.get("R1"),
                R2=golfer_data.get("R2"),
                R3=golfer_data.get("R3"),
                R4=golfer_data.get("R4"),
                TotalStrokes=golfer_data.get("TotalStrokes"),
                Earnings=golfer_data.get("Earnings"),
                FedexPts=golfer_data.get("FedexPts"),
                TournamentId=tournament_id,
                Rounds=[],
                Cut=golfer_data.get("Cut"),
                WD=golfer_data.get("WD"),
                Today=golfer_data.get("Today"),
                Thru=golfer_data.get("Thru")
            )

            golfer_details_dict = golfer_details.dict(by_alias=True, exclude_unset=True)
        else:
            golfer_details_dict = golfer_data

        round_ids = []
        if rounds:
            for round_data in rounds:
                round_id = ObjectId if "_id" not in round_data else round_data["_id"]
                if "_id" not in round_data:
                    # Create an instance of Round
                    round_instance = Round(
                        _id=round_id,
                        GolferTournamentDetailsId=golfer_details_id,
                        Round=round_data.get("Round"),
                        Birdies=round_data.get("Birdies"),
                        Eagles=round_data.get("Eagles"),
                        Pars=round_data.get("Pars"),
                        Albatross=round_data.get("Albatross"),
                        Bogeys=round_data.get("Bogeys"),
                        DoubleBogeys=round_data.get("DoubleBogeys"),
                        WorseThanDoubleBogeys=round_data.get("WorseThanDoubleBogeys"),
                        Score=round_data.get("Score"),
                        TournamentId=tournament_id,
                        Holes=[],
                    )

                    round_dict = round_instance.dict(by_alias=True, exclude_unset=True)                  
                else:
                    round_dict = round_data  

                # Validate and append round to lists
                round_ids.append(round_id)
                holes = process_round_data(round_data, golfer_details_id, round_id)
                round_dict["Holes"] = [hole_dict for hole_dict in holes]
                round_dicts.append(round_dict)
                hole_dicts.extend(holes)

        golfer_details_dict["Rounds"] = round_ids
        golfer_tournament_details_dicts.append(golfer_details_dict)

    print(hole_dicts[0], hole_dicts[1], hole_dicts[2])
    print(golfer_details_dict[0], golfer_details_dict[1], golfer_details_dict[2])
    print(round_dicts[0])

    # try:
    #     # Start a session for the transaction
    #     with db.client.start_session() as db_session:
    #         with db_session.start_transaction():
    #             # Insert golfer tournament details
    #             if golfer_tournament_details_dicts:
    #                 db.golfertournamentdetails.insert_many(golfer_tournament_details_dicts, session=db_session)

    #             # Insert rounds
    #             if round_dicts:
    #                 db.rounds.insert_many(round_dicts, session=db_session)

    #             # Insert holes
    #             if hole_dicts:
    #                 db.holes.insert_many(hole_dicts, session=db_session)

    #             print("All golfer data successfully processed and stored.")

    # except PyMongoError as e:
    #     raise RuntimeError(f"Failed to execute operations: {e}")

if __name__ == "__main__":
    main()