import csv
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

load_dotenv()

passcode = os.getenv("MONGO_PASSWORD")

uri = f"mongodb+srv://jakewehder:{passcode}@cluster0.gbnbssg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# MongoDB Connection
client = MongoClient(uri)
db = client.scramble

# Open the CSV file
csv_file_path = 'downloaded_rankings (2).csv'
players_to_insert = []

number_of_players_found = 0

# Read player name and rank from the CSV file
with open(csv_file_path, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')

    # Skip the header row
    next(reader)

    # Iterate over each row in the CSV
    for row in reader:
        if number_of_players_found >= 352:
            break

        row = row[0].split(",")

        # Remove quotes from each element in the row
        row = [item.strip('"') for item in row]

        _, rank, _, _, _, full_name, _, _, _, _, _, _, _, _, _, _ = row

        if "(Am)" in full_name:
            # Regex pattern to match "(Am)" followed by optional whitespace
            pattern = r'\(Am\)\s*'

            # Replace "(Am)" with an empty string
            full_name = re.sub(pattern, '', full_name)

        # Split full name into first name and last name
        first_name, last_name = full_name.split(maxsplit=1)

        found_golfer = db.golfers.find_one({ "FirstName": first_name, "LastName": last_name })

        if found_golfer:
            number_of_players_found += 1
            # Update the document in the collection
            db.golfers.update_one(
                { "_id": found_golfer["_id"] },  # Match the golfer by their ID
                { "$set": { "OWGR": int(rank) } }     # Update the OWGR field with the new rank
            )
            print(found_golfer["FirstName"] + " " + found_golfer["LastName"])

print(number_of_players_found)
# Delete the CSV file
# os.remove(csv_file_path)

# Close the MongoDB connection
client.close()