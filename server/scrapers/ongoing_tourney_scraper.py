import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import numpy as np

def scrape_ongoing_tournament(driver, leaderboard, par, specific_golfers=[]):
    """
    Scrape data for ongoing tournaments, focusing on rounds and holes not yet completed.
    """
    golfers = []
    table_rows = leaderboard.find_elements(By.CSS_SELECTOR, "tr.PlayerRow__Overview")

    for row in table_rows:
        golfer_data = extract_golfer_overview(row)

        # Skip golfers not in the specific list, if provided
        if specific_golfers and golfer_data["Name"] not in specific_golfers:
            continue

        # Skip completed tournaments
        if golfer_data["WD"] or golfer_data["Cut"]:
            continue

        # Expand golfer details and parse incomplete rounds
        parse_golfer_rounds(driver, row, golfer_data, par)

        golfers.append(golfer_data)

    return golfers


def extract_golfer_overview(row):
    """
    Extract basic overview data for a golfer from the leaderboard row.
    """
    golfer_data = {
        "Position": None,
        "Name": None,
        "Score": 0,
        "R1": None,
        "R2": None,
        "R3": None,
        "R4": None,
        "TotalStrokes": None,
        "Earnings": None,
        "FedexPts": None,
        "Rounds": [],
        "WD": False,
        "Cut": False,
    }

    # Extract golfer name
    golfer_full_name = row.find_element(By.CSS_SELECTOR, "a.AnchorLink").text.split(' ')
    golfer_data["Name"] = f"{golfer_full_name[0]} {' '.join(golfer_full_name[1:])}"

    # Extract basic tournament data
    cells = row.find_elements(By.CSS_SELECTOR, "td.Table__TD")
    for idx, cell in enumerate(cells):
        if idx == 0:
            golfer_data["Position"] = cell.text
        elif idx == 1:  # Handle WD/CUT scenarios
            text = cell.text
            golfer_data["WD"] = text == "WD"
            golfer_data["Cut"] = text == "CUT"
        else:
            key = ["Score", "R1", "R2", "R3", "R4", "TotalStrokes", "Earnings", "FedexPts"][idx - 2]
            golfer_data[key] = try_parse_int(cell.text)

    return golfer_data


def parse_golfer_rounds(driver, row, golfer_data, par):
    """
    Parse rounds and holes for a golfer, focusing on incomplete rounds and holes.
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

        # Parse rounds
        for option in select.options:
            round_text = option.text
            if is_round_complete(golfer_data, round_text):
                continue

            # Navigate to round and parse details
            select.select_by_visible_text(round_text)
            round_detail = parse_round_details(player_detail, round_text, golfer_data["WD"], par)
            golfer_data["Rounds"].append(round_detail)

        # Recalculate total score
        golfer_data["Score"] = determine_score_from_rounds(golfer_data["Rounds"])

    except NoSuchElementException:
        print(f"No details available for golfer {golfer_data['Name']}")
    finally:
        row.click()  # Close the player detail section


def is_round_complete(golfer_data, round_text):
    """
    Determine if a round is complete or if it needs to be updated.
    """
    for round_detail in golfer_data["Rounds"]:
        if round_detail["Round"] == round_text and len(round_detail["Holes"]) == 18:
            return True
    return False


def parse_round_details(player_detail, round_text, wd_bool, par):
    """
    Parse details of a specific round, including scores for holes.
    """
    round_detail = {
        "Round": round_text,
        "Birdies": 0,
        "Eagles": 0,
        "Pars": 0,
        "Albatross": 0,
        "Bogeys": 0,
        "DoubleBogeys": 0,
        "WorseThanDoubleBogeys": 0,
        "Score": 0,
        "Holes": [],
    }

    # Locate the scorecard table
    table = player_detail.find_element(By.CSS_SELECTOR, "table.Table")
    score_elements = table.find_elements(By.CSS_SELECTOR, "span.Scorecard__Score:not(.total)")
    scores = [elem.text for elem in score_elements]

    # Divide into par scores and strokes
    midpoint = len(scores) // 2
    par_scores = scores[:midpoint]
    strokes = scores[midpoint:]

    # Handle holes
    for idx, (par_score, stroke) in enumerate(zip(par_scores, strokes)):
        try:
            hole_par = int(par_score)
            hole_stroke = int(stroke)
            net_score = hole_stroke - hole_par
        except ValueError:  # Handle missing or invalid data
            hole_par = hole_stroke = net_score = None

        round_detail["Holes"].append({
            "HoleNumber": idx + 1,
            "HolePar": hole_par,
            "Strokes": hole_stroke,
            "NetScore": net_score,
        })

    # Calculate score summary
    calculate_round_summary(round_detail)

    return round_detail


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

def query_incomplete_rounds(tournament_id, current_round_num, db):
    """
    Query all rounds in the current tournament with fewer than 18 holes completed.
    """
    return list(db.rounds.find({
        "TournamentId": tournament_id,
        "Round": current_round_num,
        "$where": "this.Holes.length < 18"
    }))

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