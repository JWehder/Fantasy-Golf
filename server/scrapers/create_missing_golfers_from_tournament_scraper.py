import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys
import requests
from pydantic import ValidationError
from pymongo.errors import BulkWriteError
from pydantic import ValidationError
from datetime import datetime
from typing import List
from pymongo.client_session import ClientSession
from bson.objectid import ObjectId


# Adjust the paths for MacOS
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_app.config import db
from flask_app.models import Golfer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def calculate_age(birth_date):
    """Calculate age from the given birth date."""
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def convert_to_date(date_string):
    """Convert a date string in MM/DD/YYYY format to a datetime object."""
    return datetime.strptime(date_string, "%m/%d/%Y")

def setup_driver():
    """Setup Selenium WebDriver with headless options."""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless=new')
    return webdriver.Chrome(options=options)

def get_golfer_links(driver, tournament_url):
    """Extract golfer profile links from the tournament leaderboard."""
    logging.info(f"Navigating to tournament URL: {tournament_url}")
    driver.get(tournament_url)
    golfer_links = driver.find_elements(By.CSS_SELECTOR, "a.AnchorLink.leaderboard_player_name")
    logging.info(f"Found {len(golfer_links)} golfers in the tournament.")
    return golfer_links

def parse_golfer_details(driver, golfer_link):
    """Parse golfer details from their profile page."""
    logging.info(f"Processing golfer profile: {golfer_link}")
    driver.get(golfer_link)
    golfer_detail = {}

    player_header = driver.find_element(By.CSS_SELECTOR, "div.PlayerHeader__Container")

    right_side_data = player_header.find_element(By.CSS_SELECTOR, "div.flex.brdr-clr-gray-07.pl4.bl.bl--dotted.n8.brdr-clr-gray-07")
    keys = right_side_data.find_elements(By.CSS_SELECTOR, "div.ttu")
    values = right_side_data.find_elements(By.CSS_SELECTOR, "div.fw-medium.clr-black")
    
    # Extract basic info
    golfer_detail["Country"] = player_header.find_element(By.CSS_SELECTOR, "ul.PlayerHeader__Team_Info").text
    player_name = player_header.find_element(By.CSS_SELECTOR, "h1.PlayerHeader__Name").text.split('\n')
    golfer_detail["FirstName"], golfer_detail["LastName"] = [name[0] + name[1:].lower() for name in player_name]

    # Extract additional details
    for key, value in zip(keys, values):
        key_text = ''.join([word[0] + word[1:].lower() for word in re.findall('[A-Za-z]+', key.text)])
        golfer_detail[key_text] = value.text
        if key_text == "Birthdate":
            birth_date = convert_to_date(value.text.split(' ')[0])
            golfer_detail[key_text] = birth_date
            golfer_detail["Age"] = calculate_age(birth_date)

    logging.info(f"Extracted details for golfer: {golfer_detail['FirstName']} {golfer_detail['LastName']}")
    return golfer_detail

def check_golfer_in_database(golfer_detail):
    """
    Placeholder for database check.
    Return True if golfer exists in the database, otherwise False.
    """
    # Replace this with actual database query logic

    logging.info(f"Checking if golfer exists in database: {golfer_detail['FirstName']} {golfer_detail['LastName']}")
    return False

def scrape_tournament_golfers(tournament_url):
    """
    Scrape golfer details from a tournament and identify those not in the database.
    """
    driver = setup_driver()
    try:
        golfer_links = get_golfer_links(driver, tournament_url)
        golfer_links_not_in_db = []
        golfers_not_in_db = []

        for golfer_link in golfer_links:

            # Extract and clean the golfer's name
            golfer_full_name = golfer_link.text.split(' ')
            first_name = golfer_full_name[0]
            
            # Join remaining parts of the name and remove any "(a)" using regex
            last_name = ' '.join(golfer_full_name[1:])
            last_name = re.sub(r'\(a\)', '', last_name).strip()  # Remove "(a)" and extra spaces

            # Query the database
            golfer_doc = db.golfers.find_one({"FirstName": first_name, "LastName": last_name})

            if not golfer_doc:
                print(f"Could not find [{first_name}, {last_name}]")
                golfer_links_not_in_db.append(golfer_link.get_attribute('href'))

        for golfer_link_not_in_db in golfer_links_not_in_db:
            golfer_detail = parse_golfer_details(driver, golfer_link_not_in_db)
            golfers_not_in_db.append(golfer_detail)

        logging.info(f"Found {len(golfers_not_in_db)} golfers not in the database.")
        # Insert golfers atomically
        try:
            insert_golfers_atomic(golfers_not_in_db)
        except Exception as e:
            logging.error(f"Failed to insert golfers: {e}")

    finally:
        driver.quit()
        logging.info("WebDriver session ended.")

def convert_to_golfer_instance(golfer_data: dict) -> Golfer:
    """
    Convert a dictionary to a Golfer instance for validation.
    """
    try:
        golfer_data["_id"] = ObjectId()
        golfer = Golfer(**golfer_data)
        return golfer
    except ValidationError as e:
        logging.error(f"Validation error for golfer: {golfer_data}. Error: {e}")
        raise

def convert_golfer_to_dict(golfer: Golfer) -> dict:
    """
    Convert a Golfer instance back to a dictionary for database insertion.
    """
    golfer_dict = golfer.dict(by_alias=True, exclude_none=True)
    golfer_dict["created_at"] = golfer_dict.get("created_at") or datetime.utcnow()
    golfer_dict["updated_at"] = golfer_dict.get("updated_at") or datetime.utcnow()
    return golfer_dict

def insert_golfers_atomic(golfers: List[dict]):
    """
    Insert golfers into the database using a transaction.
    """
    golfer_docs = []
    for golfer_data in golfers:
        try:
            # Convert dictionary to Golfer instance for validation
            golfer_instance = convert_to_golfer_instance(golfer_data)

            # Convert Golfer instance back to dictionary for MongoDB
            golfer_doc = convert_golfer_to_dict(golfer_instance)
            golfer_docs.append(golfer_doc)
        except ValidationError as e:
            logging.error(f"Skipping invalid golfer data: {golfer_data}. Error: {e}")
            continue

    if not golfer_docs:
        logging.info("No valid golfers to insert.")
        return

    # Start a MongoDB session for atomicity
    with db.client.start_session() as session:
        try:
            with session.start_transaction():
                db.golfers.insert_many(golfer_docs, session=session)
                logging.info(f"Successfully inserted {len(golfer_docs)} golfers.")
        except BulkWriteError as e:
            logging.error(f"Bulk write error: {e.details}")
            session.abort_transaction()
            raise
        except Exception as e:
            logging.error(f"Error during golfer insertion: {e}")
            session.abort_transaction()

# Example usage
if __name__ == "__main__":
    tournament_url = "https://www.espn.com/golf/leaderboard"
    missing_golfers = scrape_tournament_golfers(tournament_url)
    logging.info(f"Golfers not in database: {missing_golfers}")
