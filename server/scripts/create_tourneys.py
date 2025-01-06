from pymongo import errors
import os
import json
import sys
from datetime import datetime
from bson.objectid import ObjectId

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import models from flask_app
from flask_app.models import Tournament, GolferTournamentDetails, Round, Hole
from flask_app.config import db, client

MAX_RETRIES = 5

def process_round_data(round_data, golfer_details_id, round_id, session=None):
    for hole_data in round_data["Holes"]:
        hole_data["GolferTournamentDetailsId"] = golfer_details_id
        hole_data["RoundId"] = round_id

        hole = Hole(
            Strokes=hole_data["Strokes"],
            HolePar=hole_data["HolePar"],
            Par=hole_data["Par"],
            NetScore=hole_data["NetScore"],
            HoleNumber=hole_data["HoleNumber"],
            Birdie=hole_data["Birdie"],
            Bogey=hole_data["Bogey"],
            Eagle=hole_data["Eagle"],
            Albatross=hole_data["Albatross"],
            DoubleBogey=hole_data["DoubleBogey"],
            WorseThanDoubleBogey=hole_data["WorseThanDoubleBogey"],
            GolferTournamentDetailsId=hole_data["GolferTournamentDetailsId"],
            RoundId=hole_data["RoundId"]
        )

        hole.save()

def process_tournament_data(directory, use_transaction=False):
    def run_transaction_with_retry(txn_func, session):
        for attempt in range(MAX_RETRIES):
            try:
                txn_func(session)
                break  # Exit loop if successful
            except errors.PyMongoError as e:
                if "TransientTransactionError" in e._message:
                    print(f"TransientTransactionError, retrying {attempt + 1}/{MAX_RETRIES}...")
                    continue  # Retry
                else:
                    raise e  # Raise other errors

    def txn_func(session):
        session.start_transaction()
        try:
            process_files(directory, session)
            session.commit_transaction()
            print("Transaction committed successfully.")
        except errors.PyMongoError as e:
            session.abort_transaction()
            raise e

    if use_transaction:
        with client.start_session() as session:
            try:
                run_transaction_with_retry(txn_func, session)
            except errors.PyMongoError as e:
                print(f"Transaction aborted due to an error: {e}")
    else:
        process_files(directory)

def process_files(directory, session=None):
    json_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith(".json")]

    for json_file_path in json_files:
        with open(json_file_path, "r") as file:
            tournament_data = json.load(file)

            # Check if the tournament already exists
            existing_tournament = db.tournaments.find_one(
                {"Name": tournament_data["Name"], "StartDate": datetime.strptime(tournament_data["StartDate"], '%Y-%m-%dT%H:%M:%S')}
            )

            if existing_tournament:
                print(f"Tournament {tournament_data['Name']} already exists. Skipping...")
                continue

            handle_tournament_data(tournament_data)

def handle_tournament_data(tournament_data: dict):
    golfer_doc = None

    if tournament_data.get("PreviousWinner"):
        split_full_name = tournament_data["PreviousWinner"].split(' ')
        first_name = split_full_name[0]
        last_name = ' '.join(split_full_name[1:])
        golfer_doc = db.golfers.find_one(
            {"FirstName": first_name, "LastName": last_name}
        )

    tournament = Tournament(
        EndDate=datetime.strptime(tournament_data["EndDate"], '%Y-%m-%dT%H:%M:%S'),
        StartDate=datetime.strptime(tournament_data["StartDate"], '%Y-%m-%dT%H:%M:%S'),
        Name=tournament_data["Name"],
        Venue=tournament_data["Venue"],
        City=tournament_data["City"],
        State=tournament_data["State"],
        Links=tournament_data["Links"],
        Purse=tournament_data["Purse"],
        PreviousWinner=golfer_doc["_id"] if golfer_doc else None,
        Par=tournament_data["Par"],
        Yardage=tournament_data["Yardage"],
        IsCompleted=tournament_data["IsCompleted"],
        InProgress=tournament_data["InProgress"],
        ProSeasonId=tournament_data["ProSeasonId"]
    )


    if "Golfers" in tournament_data:
        handle_golfer_data(tournament_data, tournament_id)

    tournament_id = tournament.save()

    return tournament_id

def handle_golfer_data(tournament_data: dict, tournament_id: ObjectId):
    print("for golfers")

    for golfer_data in tournament_data["Golfers"]:
        golfer_split_values = golfer_data["Name"].split(" ")
        first_name, last_name = golfer_split_values[0], ' '.join(golfer_split_values[1:])

        golfer = db.golfers.find_one({
            "FirstName": {"$regex": f"^{first_name}$", "$options": "i"},
            "LastName": {"$regex": f"^{last_name}$", "$options": "i"}
        })

        if golfer and "TournamentDetails" not in golfer:
            db.golfers.update_one(
                {"_id": golfer["_id"]},
                {"$set": {"TournamentDetails": []}}
            )

        if not golfer:
            continue

        golfer_details = GolferTournamentDetails(
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
            WD=golfer_data.get("WD")
        )

        golfer_details_id = golfer_details.save()

        db.golfers.update_one(
            {"_id": golfer["_id"]},
            {"$push": {"TournamentDetails": golfer_details_id}}
        )

        # hold all the rounds for this particular golfer detail
        round_ids = []

        for round_data in golfer_data["Rounds"]:
            round = Round(
                GolferTournamentDetailsId=golfer_details_id,
                Round=round_data["Round"],
                Birdies=round_data["Birdies"],
                Eagles=round_data["Eagles"],
                Pars=round_data["Pars"],
                Albatross=round_data["Albatross"],
                Bogeys=round_data["Bogeys"],
                DoubleBogeys=round_data["DoubleBogeys"],
                WorseThanDoubleBogeys=round_data["WorseThanDoubleBogeys"],
                Score=round_data["Score"],
                TournamentId=tournament_id,
                Holes=[]
            )

            round_id = round.save()
            round_ids.append(round_id)

            process_round_data(round_data, golfer_details_id, round_id)

            db.rounds.update_one(
                {"_id": round_id},
                {"$set": {"Holes": list(db.holes.find({"RoundId": round_id}))}},
            )

        db.golfertournamentdetails.update_one(
            {"_id": golfer_details_id},
            {"$set": {"Rounds": round_ids}}
        )

if __name__ == "__main__":
    directory = "../results"  # Replace with the actual directory path
    use_transaction = False  # Set this to False if you do not want to use transactions
    process_tournament_data(directory, use_transaction)
    client.close()