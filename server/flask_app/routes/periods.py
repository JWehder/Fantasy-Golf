from flask import jsonify, abort, Blueprint, request, session
import sys
import os
from bson.objectid import ObjectId
from datetime import datetime

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import db
from models import Period

periods_collection = db.periods
team_results_collection = db.teamResults

periods_bp = Blueprint('periods', __name__)

@periods_bp.route('/fetch_participating_golfers/tournaments/<tournament_id>', methods=['POST'])
def find_period_for_league_and_tournament(tournament_id):
    data = request.get_json()
    league_id = data.get("leagueId")

    period = periods_collection.find_one({
        "LeagueId": ObjectId(league_id),
        "TournamentId": ObjectId(tournament_id)
    })

    # Assuming you have the `period` variable defined
    if period:
        golfer_tournament_details_ids = []

        # Query team_results collection for documents with the matching PeriodId
        team_results = team_results_collection.find({
            "PeriodId": period["_id"]
        })

        # Iterate over each team result document
        for team_result in team_results:
            # Retrieve the GolferScores array from each document
            golfers_scores = team_result.get("GolfersScores", [])
            
            # Collect all IDs from GolfersScores into a flat list
            for golfer_id in golfers_scores:
                golfer_tournament_details_ids.append(str(golfer_id))

        return jsonify({"golfer_scores_ids": golfer_tournament_details_ids}), 200

    else:
        jsonify({"error": "Sorry, there is currently not a period that matches the league and tournament info you entered."}), 404

@periods_bp.route('/leagues/<league_id>', methods=['POST'])
def find_upcoming_league_periods(league_id):
    from models import League
    from bson.objectid import ObjectId

    page = request.args.get('page', default=0, type=int)
    limit = 2  # Number of periods per page

    # Find the league by ID
    league_data = db.leagues.find_one({"_id": ObjectId(league_id)})

    if not league_data:
        return jsonify({"error": "Sorry, we do not recognize that league."}), 404

    # Create League object
    league = League(**league_data)

    # Pagination indices
    start_index = page * limit
    end_index = start_index + limit

    # Query for upcoming periods
    upcoming_periods_cursor = db.periods.find({
        "$or": [
            {"_id": league.CurrentPeriodId},  # Match the current period
            {"StartDate": {"$gte": datetime.utcnow()}},  # Match future periods
        ]
    }).sort("StartDate", 1)  # Sort by start date in ascending order

    # Convert cursor to list
    upcoming_periods_list = list(upcoming_periods_cursor)

    # Apply pagination
    total_events = len(upcoming_periods_list)
    paginated_periods = upcoming_periods_list[start_index:end_index]

    events = []
    for period in paginated_periods:
        associated_draft = db.drafts.find_one({
            "_id": period["DraftId"]
        })
        associated_tournament = db.tournaments.find_one({
            "_id": period["TournamentId"]
        })

        # Assuming period["StartDate"], associated_draft["StartDate"], and other dates are datetime objects:
        events.append({
            "PeriodNumber": period["PeriodNumber"],
            "PeriodStartDate": period["StartDate"].strftime("%Y-%m-%d") if isinstance(period["StartDate"], datetime) else str(period["StartDate"]),
            "DraftStartDate": associated_draft["StartDate"].strftime("%Y-%m-%d") if isinstance(associated_draft["StartDate"], datetime) else str(associated_draft["StartDate"]),
            "DraftRounds": associated_draft["Rounds"],
            "TournamentName": associated_tournament["Name"],
            "TournamentVenue": associated_tournament["Venue"],
            "DraftId": period["DraftId"],
            "TournamentId": str(period["TournamentId"]),
            "TournamentLocation": associated_tournament["City"] + ", " + associated_tournament["State"],
            "TournamentStartDate": associated_tournament["StartDate"].strftime("%Y-%m-%d") if isinstance(associated_tournament["StartDate"], datetime) else str(associated_tournament["StartDate"]),
            "TournamentEndDate": associated_tournament["EndDate"].strftime("%Y-%m-%d") if isinstance(associated_tournament["EndDate"], datetime) else str(associated_tournament["EndDate"])
        })
            
    if events:
        # Check if there is a next page
        next_page = page + 1 if end_index < total_events else None

        return jsonify({
            "events": events,
            "nextPage": next_page
        }), 200

    return jsonify({"error": "No upcoming periods found."}), 404

@periods_bp.route('/user_events', methods=['POST'])
def find_upcoming_user_periods():
    from bson.objectid import ObjectId

    page = request.args.get('page', default=0, type=int)
    limit = 2  # Number of periods per page

    user = db.users.find_one({"_id":  ObjectId(session.get("user_id"))})

    if not user:
        return jsonify({"error": "Sorry, we do not recognize this user."}), 404

    # Pagination indices
    start_index = page * limit
    end_index = start_index + limit

    events = []

    for team_id in user["Teams"]:

        team = db.teams.find_one({
            "_id": team_id
        })

        league = db.leagues.find_one({
            "_id": team["LeagueId"]
        })

        # Query for upcoming periods
        upcoming_periods_cursor = db.periods.find({
            "$or": [
                {"_id": league["CurrentPeriodId"]},  # Match the current period
                {"StartDate": {"$gte": datetime.utcnow()}},  # Match future periods
            ]
        }).sort("StartDate", 1)  # Sort by start date in ascending order

        # Convert cursor to list
        upcoming_periods_list = list(upcoming_periods_cursor)

        # Apply pagination
        total_events = len(upcoming_periods_list)
        paginated_periods = upcoming_periods_list[start_index:end_index]

        for period in paginated_periods:
            associated_draft = db.drafts.find_one({
                "_id": period["DraftId"]
            })
            associated_tournament = db.tournaments.find_one({
                "_id": period["TournamentId"]
            })

            # Assuming period["StartDate"], associated_draft["StartDate"], and other dates are datetime objects:
            events.append({
                "PeriodNumber": period["PeriodNumber"],
                "PeriodStartDate": period["StartDate"].strftime("%Y-%m-%d") if isinstance(period["StartDate"], datetime) else str(period["StartDate"]),
                "DraftStartDate": associated_draft["StartDate"].strftime("%Y-%m-%d") if isinstance(associated_draft["StartDate"], datetime) else str(associated_draft["StartDate"]),
                "DraftRounds": associated_draft["Rounds"],
                "TournamentName": associated_tournament["Name"],
                "TournamentId": str(period["TournamentId"]),
                "TournamentVenue": associated_tournament["Venue"],
                "DraftId": str(period["DraftId"]),
                "TournamentLocation": associated_tournament["City"] + ", " + associated_tournament["State"],
                "TournamentStartDate": associated_tournament["StartDate"].strftime("%Y-%m-%d") if isinstance(associated_tournament["StartDate"], datetime) else str(associated_tournament["StartDate"]),
                "TournamentEndDate": associated_tournament["EndDate"].strftime("%Y-%m-%d") if isinstance(associated_tournament["EndDate"], datetime) else str(associated_tournament["EndDate"])
            })
            
    if events:
        # Check if there is a next page
        next_page = page + 1 if end_index < total_events else None

        print(events)

        return jsonify({
            "events": events,
            "nextPage": next_page
        }), 200

    return jsonify({"error": "No upcoming periods found."}), 404