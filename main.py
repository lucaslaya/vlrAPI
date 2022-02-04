# Endpoints
# -General-
#   Match, tourney, team, player, search

# Upcoming matches, recent match results
# Upcoming tourneys, completed tourneys
# Rankings, stats

import flask
from flask import request, jsonify, Flask
from mainScraping import Vlr

app = Flask(__name__)
app.config["DEBUG"] = True

VLR = Vlr()

# Base Endpoint
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''

# Match data Endpoint
@app.route('/api/v1/match', methods=['GET'])
def api_match():
    # Check for id in url
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id.", 404

    return {"data": id}, 200

# Upcoming matches Endpoint
@app.route('/api/v1/upcoming/match', methods=['GET'])
def api_upcomingMatch():
    matches = VLR.vlr_upcoming()
    data = {"matches": matches}

    return {"data": data}, 200

app.run()
