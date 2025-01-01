from flask import request, jsonify, abort
from dotenv import load_dotenv
from bson.objectid import ObjectId

from config import db, app

from routes import (
    leagues_bp, periods_bp, teams_bp, fantasy_league_seasons_bp,
    draft_picks_bp, drafts_bp, golfers_bp, golfer_tournament_details_bp,
    holes_bp, rounds_bp, team_results_bp, users_bp,
    league_settings_bp, tournaments_bp
)

# HTTP Constants 
HTTP_SUCCESS = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_BAD_REQUEST = 400
HTTP_CONFLICT = 409
HTTP_SERVER_ERROR = 500
HTTP_UNPROCESSABLE_ENTITY = 422

# Register blueprints
# Register blueprints with optional URL prefixes
app.register_blueprint(leagues_bp, url_prefix='/leagues')
app.register_blueprint(periods_bp, url_prefix='/periods')
app.register_blueprint(teams_bp, url_prefix='/teams')
app.register_blueprint(fantasy_league_seasons_bp, url_prefix='/fantasy_league_seasons')
app.register_blueprint(draft_picks_bp, url_prefix='/draft_picks')
app.register_blueprint(drafts_bp, url_prefix='/drafts')
app.register_blueprint(golfers_bp, url_prefix='/golfers')
app.register_blueprint(golfer_tournament_details_bp, url_prefix='/golfer_tournament_details')
app.register_blueprint(holes_bp, url_prefix='/holes')
app.register_blueprint(rounds_bp, url_prefix='/rounds')
app.register_blueprint(team_results_bp, url_prefix='/team_results')
app.register_blueprint(users_bp, url_prefix='/auth')
app.register_blueprint(league_settings_bp, url_prefix='/league_settings')
app.register_blueprint(tournaments_bp, url_prefix='/tournaments')

@app.route('/get_facebook_appId', methods=["GET"])
def get_facebook_appId():
    # Authentication: You might use a more secure method here
    # For simplicity, let's assume the request comes from an allowed origin
    if request.referrer and "http://localhost:3000/" in request.referrer:
        import os

        load_dotenv()

        client_id = os.getenv("FACEBOOK_APP_ID")

        return jsonify({"facebook_app_id": client_id}), HTTP_SUCCESS
    else:
        return jsonify({"error": "Unauthorized"}), HTTP_UNAUTHORIZED

@app.route("/get_client_id", methods=["GET"])
def get_client_id():
    # Authentication: You might use a more secure method here
    # For simplicity, let's assume the request comes from an allowed origin
    if request.referrer and "http://localhost:3000/" in request.referrer:
        import os

        load_dotenv()

        client_id = os.getenv("CLIENT_ID")

        return jsonify({"client_id": client_id}), HTTP_SUCCESS
    else:
        return jsonify({"error": "Unauthorized"}), HTTP_UNAUTHORIZED

if __name__ == '__main__':
    app.run(port=5555, debug=True)

