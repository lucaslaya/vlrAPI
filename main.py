# Endpoints
# -General-
#   Match, tourney, team, player, search

# Upcoming matches, recent match results
# Upcoming tourneys, completed tourneys
# Rankings, stats

from nis import match
import flask
from flask import request, jsonify, Flask
from vlrScraping import Vlr
import json

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['JSON_SORT_KEYS'] = False

base_vlr = Vlr()

# Base Endpoint
@app.route('/', methods=['GET'])
def home():
    return ("vlrAPI.Beta.v1 \n made by lucasssssss#0001 \n"
            +"API for vlr.gg made by webscraping the sites html \n" 
            +"Feel free to DM me if there are any issues")

# Match data Endpoint
# DONE
@app.route('/match', methods=['GET'])
def api_match():
    # Check for id in url
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id.", 404

    try:
        (date,time,patch,tourney,tourney_round,tourney_icon,tourney_url,match_format,
        status,notes,team1,team1_elo,team1_url,team1_score,team2,team2_elo,team2_url,
        team2_score,team1_icon,team2_icon,streams,vods,overview) = base_vlr.match(id)
    except:
        return "Error", 404

    
    data = {
        "match_info": {
            "date": date,
            "time": time,
            "patch": patch,
            "tourney": tourney,
            "tourney_round": tourney_round,
            "tourney_icon": tourney_icon,
            "tourney_url": tourney_url,
            "format": match_format,
            "status": status,
            "notes": notes,
            "team1": team1,
            "team1_elo": team1_elo,
            "team1_url": team1_url,
            "team1_score": team1_score,
            "team2": team2,
            "team2_elo": team2_elo,
            "team2_url": team2_url,
            "team2_score": team2_score,
            "team1_icon": team1_icon,
            "team2_icon": team2_icon,
            "streams": streams,         #List
            "vods": vods                #List
        },
        "match_stats": {
            "overview": overview,       #List
#            "performance": performance, #List
#            "economy": economy          #List
        },
#        "comments": comments            #List
    }

    return jsonify({"match": data}), 200

# Team Endpoint
@app.route('/team', methods=['GET'])
def api_team():
    # Check for id in url
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id.", 404
    
    # Check for info in url
    if 'info' in request.args:
        info = str(request.args['info'])
    else:
        info = "overview"

    (name, tag, website, twitter, country, flag, logo, match_data) = base_vlr.team(id, info)

    data = {
        "name": name,
        "tag": tag,
        "website": website,
        "twitter": twitter,
        "country": country,
        "flag": flag,
        "logo": logo,
        "match_data": match_data    # List
    }
    
    return jsonify({"team": data}), 200

# Upcoming matches Endpoint
@app.route('/upcoming/match', methods=['GET'])
def api_upcomingMatch():
    
    return jsonify({"upcoming": "upcoming endpoint"})


app.run()
