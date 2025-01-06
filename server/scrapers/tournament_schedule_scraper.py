from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import re
from selenium.common.exceptions import NoSuchElementException
import os
import sys
from bson.objectid import ObjectId

# Adjust the paths for MacOS
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_app.config import db
from scripts.create_tourneys import handle_tournament_data

def create_date(month, day):
    current_year = datetime.now().year  # Get the current year
    month_num = datetime.strptime(month, '%b').month
    return f'{current_year}-{month_num:02d}-{int(day):02d}T00:00:00'

def check_data_exists(parent_element, query_element):
    try:
        data = parent_element.find_element(By.CSS_SELECTOR, query_element)
        return True if data else False
    except NoSuchElementException:
        return False

options = Options()

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.headless = True

options.add_argument('--headless=new')

# Only pass options once when creating the WebDriver instance
wd = webdriver.Chrome(options=options)

driver = wd

# Load page
driver.get("https://www.espn.com/golf/schedule/_/season/2025")

# schedule_season_div = driver.find_element(By.CSS_SELECTOR, "div.event-schedule__season.mb5")
# select_button = schedule_season_div.find_element(By.CSS_SELECTOR, "select.dropdown__select")
# select = Select(select_button)
# select.select_by_visible_text("2025")

tables = driver.find_elements(By.CSS_SELECTOR, "div.ResponsiveTable")

# scheduled_tourneys_table = tables[2]

def digest_schedule_rows(tables):
    tournaments = []
    for table in tables:
        # grab all the headers for the schedule table
        headers = table.find_elements(By.CSS_SELECTOR, "th.Table__TH")

        data_rows = table.find_elements(By.CSS_SELECTOR, "tr.Table__TR")

        for row in data_rows[1:]:
            tournament = {}

            row_array = row.text.split('\n')

            date_col = None

            if check_data_exists(row, "td.dateRange__col"):
            # find the dates and parse them
                date_col = row.find_element(By.CSS_SELECTOR,"td.dateRange__col").text
            elif check_data_exists(row, "td.dateAndTickets__col"):
                date_col = row.find_element(By.CSS_SELECTOR,"div").text

            # Split the string into an array
            parts = date_col.split(' ')

            end_month = None

            # get rid of dash
            parts.pop(2)

            end_day = parts[-1]

            if len(parts) > 3:
                # if the tourney stretches over 2 separate months
                end_month = parts[2]
                tournament['EndDate'] = create_date(end_month, end_day)
            else:
                # Extract individual elements
                month = parts[0]
            start_day = parts[1]
            tournament['EndDate'] = create_date(month, end_day)

            tournament['StartDate'] = create_date(month, start_day)

            end_day = parts[-1]

            tournament_name = row.find_element(By.CSS_SELECTOR, "p.eventAndLocation__tournamentLink").text
            tournament["Name"] = tournament_name

            # parses data from the event location and venue
            tournament_location_event = row.find_element(By.CSS_SELECTOR, "div.eventAndLocation__tournamentLocation").text
            tournament_location_event = tournament_location_event.split('\n')

            # some events have multiple venues for some reason
            if len(tournament_location_event) > 1:
                # If there are multiple locations, initialize 'Venue' as a list
                tournament['Venue'] = []
                for tournament_location in tournament_location_event:
                    # Use text attribute to get the text content of the element
                    location_info = re.split(r' - |, ', tournament_location.text)
                    tournament['Venue'].append(location_info[0])
                    if not tournament['City'] or tournament['State']:
                        tournament['City'] = location_info[1]
                        tournament['State'] = location_info[2]
            else:
                # If there's only one location, initialize 'Venue' as a list with one element
                tournament['Venue'] = []
                # Use text attribute to get the text content of the element
                location_info = re.split(r' - |, ', tournament_location_event[0])
                tournament['Venue'].append(location_info[0])
                tournament['City'] = location_info[1]
                tournament['State'] = location_info[2]


            # Find all links within the current row
            links_in_row = row.find_elements(By.CSS_SELECTOR, "a.AnchorLink")

            # Extract the href attribute from each link
            links_href = [link.get_attribute('href') for link in links_in_row]

            tournament['Links'] = links_href

            tournaments.append(tournament)
    return tournaments

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

initial_tournaments = digest_schedule_rows(tables)

def process_single_tournament(tournament):
    """
    Process a single tournament, add it to the database, and return its ID.
    """
    pro_season_id = ObjectId("6776b8fc11a937336f032474")
    
    try:
        # Add ProSeasonId to the tournament
        tournament["ProSeasonId"] = pro_season_id

        # Process the tournament and get its ID
        tournament_id = handle_tournament_data(tournament)

        if tournament_id:
            # Update the proSeasons document with this tournament ID
            db.proSeasons.update_one(
                {"_id": pro_season_id},
                {"$addToSet": {"Competitions": tournament_id}}
            )
            print(f"Processed tournament: {tournament['Name']} with ID {tournament_id}")
        else:
            print(f"Warning: No ID returned for tournament {tournament['Name']}")

        return tournament_id

    except Exception as e:
        print(f"An error occurred while processing tournament {tournament['Name']}: {e}")
        return None


# Process each tournament one at a time
for tournament in initial_tournaments:
    if not tournament["Links"] or not tournament["Links"][0]:
        print(f"Could not find a valid link for {tournament['Name']}")
        continue

    # Load page
    driver.get(tournament["Links"][0])

    # Parse tournament header data from the page
    tourney_header_data = parse_tournament_header(driver)

    # Update the missing fields with the values from tourney_header_data
    tournament["Purse"] = tournament.get("Purse") or tourney_header_data.get("Purse")
    tournament["PreviousWinner"] = tournament.get("PreviousWinner") or tourney_header_data.get("PreviousWinner")
    tournament["Par"] = tournament.get("Par") or tourney_header_data.get("Par")
    tournament["Yardage"] = tournament.get("Yardage") or tourney_header_data.get("Yardage")

    # Parse string dates into datetime objects
    end_date = datetime.strptime(tournament["EndDate"], "%Y-%m-%dT%H:%M:%S")
    start_date = datetime.strptime(tournament["StartDate"], "%Y-%m-%dT%H:%M:%S")

    # Perform comparisons with datetime.utcnow()
    tournament["IsCompleted"] = datetime.utcnow() > end_date
    tournament["InProgress"] = start_date < datetime.utcnow() < end_date

    # Process the tournament
    process_single_tournament(tournament)

# Quit Selenium
driver.quit()