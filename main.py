# TODO
# - vlr_upcoming
#   - missing data to scrape and add to json
#       - tourney url
# - vlr_match
#   - missing data to scrape and add to json
#       - vods
#       - overview, performance, economy, comments 

import requests
from bs4 import BeautifulSoup
import json

def getSoup(url):
    response = requests.get(url)
    html, status_code = response.text, response.status_code

    return BeautifulSoup(html, "html.parser"), status_code


class Vlr:
    
# __  __       _       _     
#|  \/  |     | |     | |    
#| \  / | __ _| |_ ___| |__  
#| |\/| |/ _` | __/ __| '_ \ 
#| |  | | (_| | || (__| | | |
#|_|  |_|\__,_|\__\___|_| |_|

    def vlr_match(self, match_id=66842):
        team1_score = '-'
        team2_score = '-'

        url = f'https://www.vlr.gg/{match_id}/?game=all&tab=overview'
        soup, status = getSoup(url)
        print(f'vlr_match status: {status}')

        base_container = soup.find(id="wrapper")
        base = base_container.find("div", {"class": "col mod-3"})

        # Match date, time, patch
        date_time_patch_container = base.find("div", {"class": "match-header-date"})
        date_time_container = date_time_patch_container.find_all("div", {"class": "moment-tz-convert"})

        date = date_time_container[0].get_text().strip()
        time = date_time_container[1].get_text().strip()
        patch = (
            date_time_patch_container.find("div", {"style": "font-style: italic;"})
            .get_text()
            .strip()
        )

        # Tourney data
        tourney_container = base.find("a", {"class": "match-header-event"})
        tourney_url = tourney_container["href"]

        tourney_icon = tourney_container.find("img")["src"]
        tourney_icon = f"https:{tourney_icon}"

        tourney = (
            tourney_container.find("div", {"style": "font-weight: 700;"})
            .get_text()
            .strip()
        )
        tourney_round = (
            tourney_container.find("div", {"class": "match-header-event-series"})
            .get_text()
            .strip()
        )
        tourney_round = tourney_round.replace('\n', '')
        tourney_round = tourney_round.replace('\t', '')

        team_container = base.find_all("a", {"class": "match-header-link"})
        
        # Team 1
        team1_container = team_container[0]
        
        team1_url = team1_container["href"]
        
        team1_icon = team1_container.find("img")["src"]
        team1_icon = f"https:{team1_icon}"

        team1_name = (
            team1_container.find("div", {"class": "wf-title-med"})
            .get_text()
            .strip()
        )
        team1_elo = (
            team1_container.find("div", {"class": "match-header-link-name-elo"})
            .get_text()
            .strip()
        )

        # Team 2
        team2_container = team_container[1]
        
        team2_url = team2_container["href"]
        
        team2_icon = team2_container.find("img")["src"]
        team2_icon = f"https:{team2_icon}"

        team2_name = (
            team2_container.find("div", {"class": "wf-title-med"})
            .get_text()
            .strip()
        )
        team2_elo = (
            team2_container.find("div", {"class": "match-header-link-name-elo"})
            .get_text()
            .strip()
        )

        # Match status, score, format
        status_score_format_container = base.find("div", {"class": "match-header-vs-score"})
        status_format_container = base.find_all("div", {"class": "match-header-vs-note"})

        match_status = status_format_container[0].get_text().strip()
        match_format = status_format_container[1].get_text().strip()

        score_container = status_score_format_container.find("div", {"class": "js-spoiler"})
        if score_container:
            scores = score_container.get_text().strip()
            scores = scores.replace('\n', '')
            scores = scores.replace('\t', '')

            team1_score, team2_score = scores.split(':',1)

        # Streams
        streams = []
        stream_container = base.find("div", {"class": "match-streams"})

        other_streams = stream_container.find_all("div", {"class": "wf-card"})

        other_streams_text = other_streams[0].get_text().strip()
        other_streams_text = other_streams_text.replace('\n', '')
        other_streams_text = other_streams_text.replace('\t', '')

        if other_streams_text != "No stream available":
            for module in other_streams:
                stream_url = module.find("a").get("href")
                stream_name = module.get_text().strip()

                stream_flag_container = module.find("i")
                stream_flag_dirty = stream_flag_container["class"]
                stream_flag = stream_flag_dirty[0] + '_' + stream_flag_dirty[1].replace("mod-", "")

                streams.append(
                    {
                        "name": stream_name,
                        "flag": stream_flag,
                        "url": stream_url,
                        "type": "twitch / other"
                    }
                )

        yt_streams = stream_container.find_all("a", {"class": "wf-card"})

        if yt_streams:
            for i in range(len(yt_streams)):
                if yt_streams[i].get("href") == None:
                    temp = i
            yt_streams.pop(temp)

            for module in yt_streams:
                stream_url = module.get("href")
                stream_name = module.get_text().strip()

                stream_flag_container = module.find("i")
                stream_flag_dirty = stream_flag_container["class"]
                stream_flag = stream_flag_dirty[0] + '_' + stream_flag_dirty[1].replace("mod-", "")

                streams.append(
                    {
                        "name": stream_name,
                        "flag": stream_flag,
                        "url": stream_url,
                        "type": "youtube"
                    }
                )

        # Vods
        vods = []
        vods_container = base.find("div", {"class": "match-vods"})
        all_vods = vods_container.find_all("a", {"class": "wf-card"})

        for module in all_vods:
            vods_url = module.get("href")
            vods_name = module.get_text().strip()

            vods.append(
                {
                    "name": vods_name,
                    "url": vods_url
                }
            )

        #  ___ _        _      
        # / __| |_ __ _| |_ ___
        # \__ \  _/ _` |  _(_-<
        # |___/\__\__,_|\__/__/

        # Overview
        overview = []
        game = []
        game_names = []

        team1_players = []
        team2_players = []

        games_container = base.find("div", {"class": "vm-stats-gamesnav-container"})
        games = games_container.find_all("div", {"class": "vm-stats-gamesnav-item"})
        for module in games:
            module_text = module.get_text().strip()
            module_text = module_text.replace('\n', '')
            module_text = module_text.replace('\t', '')
            if module_text == '3N/A':
                continue
            else:
                module_text = ''.join([i for i in module_text if not i.isdigit()])
                game_names.append(module_text)

            game.append(module.get("data-game-id"))

        tab = 'overview'

        for i in range(len(game)):
            url = f'https://www.vlr.gg/{match_id}/?game={game[i]}&tab={tab}'
            soup_stats, status_stats = getSoup(url)

            base_container_stats = soup_stats.find(id="wrapper")
            base_stats = base_container_stats.find("div", {"class": "col mod-3"})

            game_map = game_names[i]

            player_stats_container = base_stats.find("div", {"class": "vm-stats-container"})
            player_stats = player_stats_container.find_all("table", {"class": "wf-table-inset"})

            # Team 1
            team1_stats_body = player_stats[0].find("tbody")
            team1_stats = team1_stats_body.find_all("tr")

            for module in team1_stats:
                player_name_team_container = module.find("td", {"class": "mod-player"})
                player_name_team = player_name_team_container.find("a")
                
                player_url = player_name_team.get("href")
                
                player_name_team_dirty = player_name_team.get_text().strip()
                player_name_team_dirty = player_name_team_dirty.replace('\n', '')
                player_name_team_dirty = player_name_team_dirty.replace('\t', '')
                
                player_name, player_team = player_name_team_dirty.split(' ',1)

                player_flag_container = player_name_team_container.find("i")
                player_flag_dirty = player_flag_container["class"]
                player_flag = player_flag_dirty[0] + '_' + player_flag_dirty[1].replace("mod-", "")

                team1_stats_container = module.find_all("td", {"class": "mod-stat"})

                player_acs = team1_stats_container[0].get_text().strip()
                player_kills = team1_stats_container[1].get_text().strip()
                player_deaths = team1_stats_container[2].get_text().strip()
                player_deaths = player_deaths.replace("/", "")
                player_assists = team1_stats_container[3].get_text().strip()
                player_plus_minus = team1_stats_container[4].get_text().strip()
                player_kast = team1_stats_container[5].get_text().strip()
                player_adr = team1_stats_container[6].get_text().strip()
                player_hs = team1_stats_container[7].get_text().strip()
                player_first_kills = team1_stats_container[8].get_text().strip()
                player_first_deaths = team1_stats_container[9].get_text().strip()
                player_first_plus_minus = team1_stats_container[10].get_text().strip()

                team1_players.append(
                    {
                        "name": player_name,
                        "team": player_team,
                        "flag": player_flag,
                        "url": player_url,
                        #"agents": player_agents,
                        "acs": player_acs,
                        "kills": player_kills,
                        "deaths": player_deaths,
                        "assists": player_assists,
                        "+/-": player_plus_minus,
                        "kast": player_kast,
                        "adr": player_adr,
                        "hs%": player_hs,
                        "first_kills": player_first_kills,
                        "first_deaths": player_first_deaths,
                        "first_+/-": player_first_plus_minus
                    }
                )

            # Team 2
            team2_stats_body = player_stats[1].find("tbody")
            team2_stats = team2_stats_body.find_all("tr")

            for module in team2_stats:
                player_name_team_container = module.find("td", {"class": "mod-player"})
                player_name_team = player_name_team_container.find("a")
                
                player_url = player_name_team.get("href")
                
                player_name_team_dirty = player_name_team.get_text().strip()
                player_name_team_dirty = player_name_team_dirty.replace('\n', '')
                player_name_team_dirty = player_name_team_dirty.replace('\t', '')
                
                player_name, player_team = player_name_team_dirty.split(' ',1)

                player_flag_container = player_name_team_container.find("i")
                player_flag_dirty = player_flag_container["class"]
                player_flag = player_flag_dirty[0] + '_' + player_flag_dirty[1].replace("mod-", "")

                team2_stats_container = module.find_all("td", {"class": "mod-stat"})

                player_acs = team2_stats_container[0].get_text().strip()
                player_kills = team2_stats_container[1].get_text().strip()
                player_deaths = team2_stats_container[2].get_text().strip()
                player_deaths = player_deaths.replace("/", "")
                player_assists = team2_stats_container[3].get_text().strip()
                player_plus_minus = team2_stats_container[4].get_text().strip()
                player_kast = team2_stats_container[5].get_text().strip()
                player_adr = team2_stats_container[6].get_text().strip()
                player_hs = team2_stats_container[7].get_text().strip()
                player_first_kills = team2_stats_container[8].get_text().strip()
                player_first_deaths = team2_stats_container[9].get_text().strip()
                player_first_plus_minus = team2_stats_container[10].get_text().strip()

                team2_players.append(
                    {
                        "name": player_name,
                        "team": player_team,
                        "flag": player_flag,
                        "url": player_url,
                        #"agents": player_agents,
                        "acs": player_acs,
                        "kills": player_kills,
                        "deaths": player_deaths,
                        "assists": player_assists,
                        "+/-": player_plus_minus,
                        "kast": player_kast,
                        "adr": player_adr,
                        "hs%": player_hs,
                        "first_kills": player_first_kills,
                        "first_deaths": player_first_deaths,
                        "first_+/-": player_first_plus_minus
                    }
                )

            # Bad solution - for loop is broken 
            # Function above only outputs info from map 1
            # Outputs all info 3 times
            while len(team1_players) > 5: 
                team1_players.pop()
                team2_players.pop()

            overview.append(
                {
                    "map": game_map,
                    "team1_players": team1_players,
                    "team2_players": team2_players
                }
            )
 
        data = {
            "match_info": {
                "date": date,
                "time": time,
                "status": match_status,
                "patch": patch,
                "tourney": tourney,
                "tourney_round": tourney_round,
                "tourney_icon": tourney_icon,
                "tourney_url": tourney_url,
                "format": match_format,
                "streams": streams,
                "vods": vods
            },
            "match_stats": {
                "team1": team1_name,
                "team1_elo": team1_elo,
                "team1_score": team1_score,
                "team2": team2_name,
                "team2_elo": team2_elo,
                "team2_score": team2_score,
                "team1_icon": team1_icon,
                "team2_icon": team2_icon,
                "team1_url": team1_url,
                "team2_url": team2_url,
                "overview": overview,
                #"performance": performance,
                #"economy": economy
            },
            #"comments": comments
        }

        json_string = json.dumps(data, sort_keys=False, indent=4)
        
        with open('vlr_match.json', 'w') as outfile:
            outfile.write(json_string)

        return json_string
        

# _    _                           _             
#| |  | |                         (_)            
#| |  | |_ __   ___ ___  _ __ ___  _ _ __   __ _ 
#| |  | | '_ \ / __/ _ \| '_ ` _ \| | '_ \ / _` |
#| |__| | |_) | (_| (_) | | | | | | | | | | (_| |
# \____/| .__/ \___\___/|_| |_| |_|_|_| |_|\__, |
#       | |                                 __/ |
#       |_|                                |___/ 

    # 50 items per page on vlr.gg
    def vlr_upcoming(self, page=1):
        url = f'https://www.vlr.gg/matches/?page={page}'
        soup, status = getSoup(url)
        print(f'vlr_upcoming status: {status}')

        base = soup.find(id="wrapper")

        # Return none when there are no matches on the page
        if not base.find_all("div", {"class": "wf-label"}):
            #print("Empty Page")
            return

        vlr_module_day = base.find_all("div", {"class": "wf-label"})

        vlr_base_card = base.find_all("div", {"class": "wf-card"})
        vlr_base_card.pop(0)

        matches = []

        for i in range(len(vlr_base_card)):
            vlr_module = vlr_base_card[i].find_all(
                "a",
                {"class": "wf-module-item"}
            )
            
            day = vlr_module_day[i].get_text().strip()
        
            for module in vlr_module:
                # Match info link
                url_path = module["href"]

                # Match ETA Time
                eta_container = module.find("div", {"class": "match-item-eta"})
                eta_status = eta_container.find("div", {"class": "ml-status"})
                eta_status = eta_status.get_text().strip()
                if eta_status == "Upcoming":
                    eta_time = eta_container.find("div", {"class": "ml-eta"})
                    eta = (eta_time.get_text().strip()) + " remaining"
                elif eta_status == "LIVE":
                    eta = "LIVE"
                else:
                    eta = "TBD"

                # Round of the tournament
                round_container = module.find("div", {"class": "match-item-event text-of"})
                round = (
                    round_container.find("div", {"class": "match-item-event-series text-of"})
                    .get_text()
                    .strip()
                )
                round = round.replace("\u2013", "-")

                # Tournament name
                tourney = (
                    module.find("div", {"class": "match-item-event text-of"})
                    .get_text()
                    .strip()
                )
                tourney = tourney.replace("\t", " ")
                tourney = tourney.strip().split("\n")[1]
                tourney = tourney.strip()

                # Tournament icon
                tourney_icon = module.find("img")["src"]
                tourney_icon = f"https:{tourney_icon}"

                # Flags
                flags_container = module.findAll("div", {"class": "text-of"})
                flag1 = flags_container[0].span.get("class")[1]
                flag1 = flag1.replace("-", " ")
                flag1 = "flag_" + flag1.strip().split(" ")[1]

                flag2 = flags_container[1].span.get("class")[1]
                flag2 = flag2.replace("-", " ")
                flag2 = "flag_" + flag2.strip().split(" ")[1]

                # Match items
                match_container = (
                    module.find("div", {"class": "match-item-vs"}).get_text().strip()
                )

                match_array = match_container.replace("\t", " ").replace("\n", " ")
                match_array = match_array.strip().split(
                    "                                  "
                )
                team1 = "TBD"
                team2 = "TBD"
                if match_array is not None and len(match_array) > 1:
                    team1 = match_array[0]
                    team2 = match_array[2].strip()

                # Match Score
                scores = module.find_all("div", {"class": "match-item-vs-team-score"})
                team1Score = scores[0].get_text().strip()
                team1Score = team1Score.replace("\u2013", "-")
                team2Score = scores[1].get_text().strip()
                team2Score = team2Score.replace("\u2013", "-")

                # Match Time
                match_time = (
                module.find("div", {"class": "match-item-time"})
                .get_text()
                .strip()
                )

                matches.append(
                    {
                        "team1": team1,
                        "team2": team2,
                        "flag1": flag1,
                        "flag2": flag2,
                        "team1Score": team1Score,
                        "team2Score": team2Score,
                        "time_until_match": eta,
                        "match_time": match_time,
                        "match_date": day,
                        "round_info": round,
                        "tournament_name": tourney,
                        "match_page": url_path,
                        "tournament_icon": tourney_icon
                    }
                )

        data = {'matches' : matches}
        json_string = json.dumps(data, sort_keys=False, indent=4)
        
        with open('vlr_upcoming.json', 'w') as outfile:
            outfile.write(json_string)

        return json_string

    def vlr_results(self, page=1):
        url = f'https://www.vlr.gg/matches/results/?page={page}'
        soup, status = getSoup(url)
        print(f'vlr_results status: {status}')

VLR = Vlr()

VLR.vlr_match()

output = VLR.vlr_upcoming()
#print(output)
