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

    def vlr_match(self, match_id=51276):
        url = f'https://www.vlr.gg/{match_id}'
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

        #print(date)
        #print(time)
        #print(patch)

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

        #print(tourney)
        #print(tourney_icon)
        #print(tourney_round)
        #print(tourney_url)

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

        #print(team1_name)
        #print(team1_elo)
        #print(team1_icon)
        #print(team1_url)

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

        #print(team2_name)
        #print(team2_elo)
        #print(team2_icon)
        #print(team2_url)

        # Match status, score, format
        status_score_format_container = base.find("div", {"class": "match-header-vs-score"})
        status_format_container = base.find_all("div", {"class": "match-header-vs-note"})

        match_status = status_format_container[0].get_text().strip()
        match_format = status_format_container[1].get_text().strip()

        score_container = status_score_format_container.find("div", {"class": "js-spoiler"})
        scores = score_container.get_text().strip()
        scores = scores.replace('\n', '')
        scores = scores.replace('\t', '')

        team1_score, team2_score = scores.split(':',1)

        #print(match_status)
        #print(match_format)
        #print(team1_score)
        #print(team2_score)

        overview = performance = economy = comments = vods = []

        # Streams
        streams = []
        stream_container = base.find("div", {"class": "match-streams-container"})

        other_streams = stream_container.find_all("div", {"class": "wf-card"})

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
                "performance": performance,
                "economy": economy
            },
            "comments": comments
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
