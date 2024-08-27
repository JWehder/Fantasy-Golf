from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

passcode = os.getenv("MONGO_PASSWORD")

uri = f"mongodb+srv://jakewehder:{passcode}@cluster0.gbnbssg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# MongoDB Connection
client = MongoClient(uri)
db = client.scramble

def delete_tournament_data(tournament_id):
    tournament_id = ObjectId('66a6a29b27abbbf82b5c39c1')

    # Find all holes associated with the rounds
    round_cursor = db.rounds.find({ "TournamentId": tournament_id })
    
    round_ids = [round["_id"] for round in round_cursor]
        
    # Delete all rounds associated with the golfer tournament details
    db.rounds.delete_many({ "TournamentId": tournament_id })
        
    # Delete all holes associated with the rounds
    db.holes.delete_many({"RoundId": {"$in": round_ids}})
    
    # Delete the golfer tournament details
    db.golfertournamentdetails.delete_many({ "TournamentId": tournament_id })
    
    # Finally, delete the tournament itself
    db.tournaments.delete_one({"_id": tournament_id})

if __name__ == "__main__":
    # Replace 'your_tournament_id_here' with the actual tournament id
    tournament_id = "your_tournament_id_here"
    delete_tournament_data(tournament_id)
    print(f"All data associated with the tournament {tournament_id} has been deleted.")