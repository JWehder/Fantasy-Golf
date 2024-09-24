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

# Adjust the paths for MacOS
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_app.config import db
from scripts.create_tourneys import handle_golfer_data

def check_data_exists(parent_element: str, query_element: str) -> bool:
    try:
        data = parent_element.find_element(By.CSS_SELECTOR, query_element)
        return True if data else False
    except NoSuchElementException:
        return False

def save_tournament(tournament_name: str, tournament_details: object) -> None:
    output_file_name = f"../results/{tournament_name}.json"

    # Get the absolute path of the current script
    dir_path = os.path.dirname(os.path.abspath(__file__))

    try:
        # Construct the absolute path to the data file
        file_path = os.path.join(dir_path, '..', 'results', output_file_name)

        # Now, 'players' contains the summarized data for each player's rounds
        # Writing the results to a file
        with open(file_path, "w") as outfile:
            json.dump(tournament_details, outfile, indent=4)

        # Add the output file to .gitignore
        gitignore_file = "../.gitignore"
        with open(gitignore_file, "a") as gitignore:
            gitignore.write(f"\n{output_file_name}")

        print(f"Data written to {output_file_name}")

    except Exception as e:
        print(f"An error occurred: {e}")

tournaments = [
    {
        "EndDate": "2024-07-21T00:00:00",
        "StartDate": "2024-07-18T00:00:00",
        "Name": "The Open",
        "Venue": [
            "Royal Troon Golf Course"
        ],
        "City": "Troon",
        "State": "Scotland",
        "Links": [
            "https://www.espn.com/golf/leaderboard?tournamentId=401580360",
            "https://www.espn.com/golf/player/_/id/1225/brian-harman"
        ]
    }
]

def determine_score_from_rounds(rounds: list):
    score_total = 0

    for r in rounds:
        score_total += r["Score"]

    if score_total > 0:
        return "+" + str(score_total)
    elif score_total == 0:
        return "E"
    else:
        return str(score_total)

def determine_score_from_holes(holes: list):

    score_total = 0

    for hole in holes:
        if hole["NetScore"] == None:
            continue
        score_total += hole["NetScore"]

    return score_total

def wait_for_dropdown_text_change(driver, select_element, original_text, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: select_element.text != original_text
        )
    except TimeoutException:
        print("Timeout waiting for the dropdown text to change.")

def parse_leaderboard(par, leaderboard, driver, specific_golfers=[]):

    competitors_table = leaderboard

    golfers = []

    table_rows = competitors_table.find_elements(By.CSS_SELECTOR, "tr.PlayerRow__Overview")

    for row in table_rows:

        golfer_tournament_results = {
        "Position": None,
        "Name": None,
        "Score": 0,
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

        # Assuming table_rows[0] is the desired table row to click
        element_to_click = row

        # grab specifically the position element and assign it to the position key
        golfer_tournament_results["Position"] = element_to_click.find_element(By.CSS_SELECTOR, "td.tl").text
    
        # grab specifically the golfers name element and assign it to the name key
        golfer_full_name = element_to_click.find_element(By.CSS_SELECTOR, "a.AnchorLink")
        golfer_full_name = golfer_full_name.text.split(' ')
        golfer_first_name = golfer_full_name[0]
        golfer_last_name = " ".join(golfer_full_name[1:])

        golfer_tournament_results["Name"] = golfer_first_name + " " + golfer_last_name

        # If specific_golfers list is not empty and the current golfer is not in the list, skip this golfer
        if specific_golfers and golfer_tournament_results["Name"] not in specific_golfers:
            continue

        # grab the remaining elements
        remaining = element_to_click.find_elements(By.CSS_SELECTOR, "td.Table__TD")

        for key, element in zip(golfer_tournament_results.keys(), remaining[1:]):
            if key == "Score" and element.text == "WD":
                golfer_tournament_results["WD"] = True
                golfer_tournament_results["Cut"] = False
            elif key == "Score" and element.text == "CUT":
                golfer_tournament_results["Cut"] = True
                golfer_tournament_results["WD"] = False
            golfer_tournament_results[key] = element.text

        golfer_tournament_results['Earnings'] = ''.join(re.findall(r'(\d+)', golfer_tournament_results['Earnings']))

        # Scroll to the element
        actions = ActionChains(driver)
        actions.move_to_element(element_to_click).perform()

        # Now click the element
        element_to_click.click()

        try:
            player_detail = WebDriverWait(driver, 8).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.Leaderboard__Player__Detail"))
            )

            select_button = player_detail.find_element(By.CSS_SELECTOR, "select.dropdown__select")

            # Instantiate the select button
            select = Select(select_button)

            round_detail = parse_round_details(player_detail, select.options[0].text, golfer_tournament_results["WD"], par)
            golfer_tournament_results['Rounds'].append(round_detail)

            for option in select.options[1:]:

                # Select the next round
                select.select_by_visible_text(option.text)

                # Wait until the dropdown text changes
                # wait_for_dropdown_text_change(driver, select_button, original_text)

                round_detail = parse_round_details(player_detail, option.text, golfer_tournament_results["WD"], par)
                golfer_tournament_results['Rounds'].append(round_detail)

            golfer_tournament_results['Score'] = determine_score_from_rounds(golfer_tournament_results["Rounds"])

            print(golfer_tournament_results["Name"], golfer_tournament_results["Score"])

            golfers.append(golfer_tournament_results)

        except NoSuchElementException:
            print("No select dropdown found for this player.")
            # Handle the case where there's no dropdown as needed
            golfers.append(golfer_tournament_results)

        # Close the player detail by clicking the element again
        element_to_click.click()

        # Allow some time for the page to update before proceeding
        WebDriverWait(driver, 2).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.Leaderboard__Player__Detail"))
        )

    return golfers

def parse_round_details(player_detail, round_text, wd_bool, par):
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
        "Holes": []
    }

    table = player_detail.find_element(By.CSS_SELECTOR, "table.Table")
    score_elements = table.find_elements(By.CSS_SELECTOR, "span.Scorecard__Score:not(.total)")
    total_score_elements = table.find_elements(By.CSS_SELECTOR, "span.Scorecard__Score.total")

    scores = [elem.text for elem in score_elements]
    midpoint = len(scores) // 2
    par_score_scores = scores[:midpoint]
    golfer_scores = scores[midpoint:]

    parsed_par = int(par)
    total_strokes = total_score_elements[7].text

    if not wd_bool:
        round_detail["Score"] = int(total_strokes) - int(parsed_par)

    # Handle strokes and par scores, considering that some values might be "-"
    hole_strokes = [int(match) if match != "-" else None for match in golfer_scores]
    par_scores = [int(match) if match != '' else None for match in par_score_scores]

    round_detail["StrokesPlayed"] = int(total_strokes)
    round_detail["TotalPar"] = int(parsed_par)

    hole = 1

    for strokes, par_score in zip(hole_strokes, par_scores):
        if strokes is not None and par_score is not None:
            score = strokes - par_score
        else:
            score = None  # No score difference available

        score_types = {
            'albatross': score == -3 if score is not None else False,
            'eagle': score == -2 if score is not None else False,
            'birdie': score == -1 if score is not None else False,
            'par': score == 0 if score is not None else False,
            'bogey': score == 1 if score is not None else False,
            'double_bogey': score == 2 if score is not None else False,
            'worse_than_double_bogey': score > 2 if score is not None else False,
            'no_score': score == 'None'
        }

        hole_result = {
            'Strokes': strokes,
            'Par': par_score,
            'NetScore': score,
            "HoleNumber": hole,
            'Birdie': score_types['birdie'],
            'Bogey': score_types['bogey'],
            'Par': score_types['par'],
            'Eagle': score_types['eagle'],
            'Albatross': score_types['albatross'],
            'DoubleBogey': score_types['double_bogey'],
            'WorseThanDoubleBogey': score_types['worse_than_double_bogey'],
            'NoScore': score_types['no_score']
        }

        round_detail["Holes"].append(hole_result)
        hole += 1

        if score_types['albatross']:
            round_detail['Albatross'] += 1
        elif score_types['eagle']:
            round_detail['Eagles'] += 1
        elif score_types['birdie']:
            round_detail['Birdies'] += 1
        elif score_types['par']:
            round_detail['Pars'] += 1
        elif score_types['bogey']:
            round_detail['Bogeys'] += 1
        elif score_types['double_bogey']:
            round_detail['DoubleBogeys'] += 1
        elif score_types['worse_than_double_bogey']:
            round_detail['WorseThanDoubleBogeys'] += 1

    if wd_bool:
        round_detail["Score"] = determine_score_from_holes(round_detail["Holes"])

    return round_detail

import re
from datetime import datetime

def print_children(element):
    divs = element.find_elements(By.CSS_SELECTOR, "div")
    for div in divs:
        print(div.get_attribute("class"), div.text)

def parse_tournament_header(webpage_data):
  # grab the tournament info from the header
  header = webpage_data.find_element(By.CSS_SELECTOR, "div.Leaderboard__Header")

  par, yardage = None, None

  if check_data_exists(header, "div.Leaderboard__Course__Location__Detail"):
    # grab the par and yardage
    par_yardage = webpage_data.find_element(By.CSS_SELECTOR, "div.Leaderboard__Course__Location__Detail")
    par, yardage = re.findall(r'(\d+)', str(par_yardage.text))

  # what's the status of the tournament? In progress, finished?
  status = webpage_data.find_element(By.CSS_SELECTOR, "div.status")

  # grab the specific element with the text that discloses the tournament status
  status_text = status.find_element(By.CSS_SELECTOR, "span").text

  # grab the tournament info from the header
  purse_previous_winner_text = webpage_data.find_element(By.CSS_SELECTOR, "div.n7").text
  print(purse_previous_winner_text)

  # Split the string based on the expected patterns
  split_values = re.findall(r'[A-Z][^A-Z]*', purse_previous_winner_text)

  purse = None
  previous_winner = None

  # Handle the different possible cases
  if len(split_values) >= 1:

      # Case 1: Only the purse value
      if "Purse" in split_values[0]:
          purse = re.findall(r'(\d+)', split_values[0])
          purse = int(''.join(purse)) if purse else None

      # Case 2: Both purse and previous winner
      if len(split_values) > 1:
          previous_winner = ''.join(split_values[-2:]).strip()
        
      # Case 3: Only previous winner
      if "Purse" not in split_values[0] and len(split_values) > 1:
          previous_winner = ' '.join(split_values[-2:]).strip()

  return {
      "Purse": purse,
      "PreviousWinner": previous_winner,
      "Par": par,
      "Yardage": yardage
      }

def parse_winner_score(score_str):
    # Use regular expressions to remove parentheses
    score_match = re.match(r'(\d+) \((-\d+)\)', score_str)
    if score_match:
        total_strokes = int(score_match.group(1))
        score_under_par = int(score_match.group(2))
        return {'winnerScoreUnderPar': -score_under_par, 'winnerTotalStrokes': total_strokes}
    else:
        return None

def parse_playoff_leaderboard(table):
  playoff = {
      "PlayoffHoles": None,
      "PlayoffWinningStrokes": 0,
      "PlayoffWinnerName": None,
      "Golfers": []
  }

  data = table.find_elements(By.CSS_SELECTOR, "tr.Table__TR")
  playoff_holes = re.findall(r'(\d+)', data[1].text)
  playoff["PlayoffHoles"] = playoff_holes
  for datap in data[2:]:
    golfer = {}
    data_split = datap.text.split(' ')
    golfer["FirstName"] = data_split[0]
    golfer["LastName"] = data_split[1]
    golfer["PlayoffHolesTotalStrokes"] = int(data_split[-1])
    if playoff["PlayoffWinningStrokes"] == 0 or playoff["PlayoffWinningStrokes"] > golfer["PlayoffHolesTotalStrokes"]:
      playoff["PlayoffWinningStrokes"] = golfer["PlayoffHolesTotalStrokes"]
      playoff["PlayoffWinnerName"] = golfer["FirstName"] + " " + golfer["LastName"]
    golfer["Holes"] = [{"PlayoffHoleNumber": idx + 1, "Strokes": int(strokes), "HoleNumber": playoff_holes[idx]} for idx, strokes in enumerate(data_split[2:-1])]
    playoff["Golfers"].append(golfer)

    return playoff

def get_tournament_status(start_date_str, end_date_str):
    # Define the local timezone
    local_timezone = pytz.timezone('US/Eastern')
    
    # Get the current local time
    current_local_time = datetime.now(local_timezone)
    
    # Parse the start and end date strings into datetime objects
    start_date = datetime.fromisoformat(start_date_str).replace(tzinfo=local_timezone)
    end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=local_timezone)
    
    # Determine if the tournament is in progress or completed
    tournament_info = {
        "isInProgress": start_date <= current_local_time < end_date,
        "isCompleted": current_local_time >= end_date
    }
    
    return tournament_info

def parse_tournaments(tournaments):

    options = Options()

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.headless = True

    options.add_argument('--headless=new')

    # Only pass options once when creating the WebDriver instance
    wd = webdriver.Chrome(options=options)

    driver = wd

    parsed_tournaments = []

    for item in tournaments:
        if 'DATES' in item:
            continue

        print(item)
        name = item["Name"]

        # found_one = db.tournaments.find_one({ "Name": item["Name"], "StartDate": datetime.strptime(item["StartDate"], '%Y-%m-%dT%H:%M:%S') })

        # if found_one:
        #     print(f"Found {name} in the db. Skipping...")
        #     continue

        # Load page
        driver.get(item['Links'][0])

        # retrieve purse, previous winner, par, and yardage
        # item.update(parse_tournament_header(driver))

        # item.update(get_tournament_status(item["StartDate"], item["EndDate"]))

        if check_data_exists(driver, "div.leaderboard_no_data"):
            print("here")
            parsed_tournaments.append(item)
            name = item['Name'].split(' ')
            name = '-'.join(name)
            save_tournament(name, item)
            continue

        competitors_table = driver.find_element(By.CSS_SELECTOR, "div.competitors")

        responsive_tables = competitors_table.find_elements(By.CSS_SELECTOR, "div.ResponsiveTable")

        # determine the amount of headers within the responsive table
        table_headers = responsive_tables[-1].find_elements(By.CSS_SELECTOR, "th")

        # test if it's a legit scoreboard if it's before the tourney and they are just showing tee times.
        if len(table_headers) <= 3:
          # record the tee times
          data = responsive_tables[-1].find_elements(By.CSS_SELECTOR, "tr.Table__TR")
          item["Golfers"] = []
          for datap in data[1:]:
              tee_times = datap.text.split('\n')  # Split the text into lines
              name = tee_times[0]
              tee_time_str = tee_times[1]
              tee_time = datetime.strptime(tee_time_str, "%I:%M %p")
              # Convert datetime to string before appending
              tee_time_str = tee_time.strftime("%Y-%m-%d %H:%M:%S")
              item["Golfers"].append({"name": name, "tee_time": tee_time_str})
          parsed_tournaments.append(item)
          continue

        # determine if playoff holes took place
        if len(responsive_tables) > 1:
          item["Playoff"] = True
          item["PlayoffDetails"] = parse_playoff_leaderboard(responsive_tables[0])

        item['Golfers'] = parse_leaderboard(item["Par"], item, responsive_tables[-1], driver)

        first_place_golfer = item['Golfers'][0]

        item['WinnerScore'] = first_place_golfer['Score']
        item['WinnerStrokes'] = first_place_golfer['TotalStrokes']
        item['WinnerName'] = first_place_golfer['FirstName'] + " " + first_place_golfer['LastName'] 

        # parsed_tournaments.append(item)

        found_tournament = db.tournaments.find_one({
            "Name": item["Name"]
        })

        if found_tournament:
            handle_golfer_data(item, found_tournament["_id"])
        else:
            name = item['Name'].split(' ')
            name = '-'.join(name)

            save_tournament(name, item)

    driver.quit()

    return True

if __name__ == "__main__":

    # Define the cutoff date
    cutoff_date = datetime(2024, 8, 21)

    # Query tournaments that ended before August 21
    tournaments = db.tournaments.find({
        "EndDate": {"$lt": cutoff_date},
        "Golfers": []
    })

    options = Options()

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.headless = True

    options.add_argument('--headless=new')

    # Only pass options once when creating the WebDriver instance
    wd = webdriver.Chrome(options=options)

    driver = wd

    for tournament in tournaments:
        # Load page
        driver.get(tournament['Links'][0])

        competitors_table = driver.find_element(By.CSS_SELECTOR, "div.competitors")

        responsive_tables = competitors_table.find_elements(By.CSS_SELECTOR, "div.ResponsiveTable")

        print(tournament['Links'][0])

        tournament_dict = dict(tournament)

        tournament_dict["Golfers"] = parse_leaderboard(tournament_dict["Par"], responsive_tables[-1], driver)
        
        handle_golfer_data(tournament_dict, tournament["_id"])


