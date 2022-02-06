import requests
from bs4 import BeautifulSoup
import json

def getSoup(url):
    response = requests.get(url)
    html, status_code = response.text, response.status_code

    #html = html.replace('\n', '')
    #html = html.replace('\t', '')

    #print(html)
    #with open('readme.txt', 'w') as f:
    #    f.write(html)

    return BeautifulSoup(html, "html.parser"), status_code

class Vlr:
    def match(self, match_id):
        
        # Default variables
        patch_out = "-"
        team1_score_out = "-"
        team2_score_out = "-"
        team1_elo_out = "-"
        team2_elo_out = "-"
        notes_out = "-"

        url = f'https://www.vlr.gg/{match_id}'
        soup, status = getSoup(url)

        base_container = soup.find("div", class_="col mod-3")

        date_tourney_container = base_container.find("div", class_="match-header-super")

        # date, time, patch
        date_container = date_tourney_container.find("div", class_="match-header-date")
        date_time = date_container.find_all("div", class_="moment-tz-convert")

        date_out = date_time[0].get_text().strip()
        time_out = date_time[1].get_text().strip()
        
        if date_container.find("div", style="font-style: italic;") != None:
            patch_out = (
                date_container.find("div", style="font-style: italic;")
                .get_text()
                .strip()
            )

        # tourney
        tourney_container = date_tourney_container.find("a", class_="match-header-event")
        tourney_url_out = tourney_container["href"]
        tourney_url_out = tourney_url_out[1:]

        tourney_icon = tourney_container.find("img")["src"]
        tourney_icon_out = f"https:{tourney_icon}"

        tourney_name = tourney_container.get_text().strip()
        tourney_name = tourney_name.split("\n")
        tourney_name_out = tourney_name[0].replace('\t', '')

        tourney_round = (
            tourney_container.find("div", class_="match-header-event-series")
            .get_text()
            .strip()
        )
        tourney_round = tourney_round.replace('\n', '')
        tourney_round_out = tourney_round.replace('\t', '')

        # score teams format status
        score_teams_container = base_container.find("div", class_="match-header-vs")
        teams_container = score_teams_container.find_all("a", class_="match-header-link")

        team1_url_out = teams_container[0]["href"]
        team2_url_out = teams_container[1]["href"]
        team1_url_out = team1_url_out[1:]
        team2_url_out = team2_url_out[1:]

        team1_name_elo = teams_container[0].get_text().strip()
        team1_name_elo = team1_name_elo.replace('\n', '')
        team1_name_elo = team1_name_elo.replace('\t', '')
        
        team1_name_elo = team1_name_elo.split('[')

        team1_name_out = team1_name_elo[0]
        if len(team1_name_elo) > 1:
            team1_elo_out = team1_name_elo[1]
            team1_elo_out = '[' + team1_elo_out

        team2_name_elo = teams_container[1].get_text().strip()
        team2_name_elo = team2_name_elo.replace('\n', '')
        team2_name_elo = team2_name_elo.replace('\t', '')
        
        team2_name_elo = team2_name_elo.split('[')

        team2_name_out = team2_name_elo[0]
        if len(team2_name_elo) > 1:
            team2_elo_out = team2_name_elo[1]
            team2_elo_out = '[' + team2_elo_out

        team1_logo = teams_container[0].find("img")["src"]
        team1_logo_out = f"https:{team1_logo}"

        team2_logo = teams_container[1].find("img")["src"]
        team2_logo_out = f"https:{team2_logo}"

        score_status_container = score_teams_container.find("div", class_="match-header-vs-score")
        status_format_container = score_status_container.find_all("div", class_="match-header-vs-note")

        format_out = status_format_container[1].get_text().strip()
        status_out = status_format_container[0].get_text().strip()

        score_base_container = score_status_container.find("div", class_="match-header-vs-score")
        score_container = score_base_container.find("div", class_="js-spoiler")

        if score_container:
            team1_2_score = score_container.get_text().strip()
            team1_2_score = team1_2_score.replace('\n', '')
            team1_2_score = team1_2_score.replace('\t', '')

            team1_score_out, team2_score_out = team1_2_score.split(':',1)

        # notes
        notes_container = base_container.find("div", class_="match-header-note")
        if notes_container:
            notes_out = notes_container.get_text().strip()

        # Streams Vods
        streams_out = []

        stream_vods_container = base_container.find("div", class_="match-streams-bets-container")
        stream_container = stream_vods_container.find("div", class_="match-streams")

        other_streams = stream_container.find_all("div", class_="wf-card")

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

                streams_out.append(
                    {
                        "name": stream_name,
                        "flag": stream_flag,
                        "url": stream_url,
                        "type": "twitch / other"
                    }
                )

        yt_streams = stream_container.find_all("a", class_="wf-card")

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

                streams_out.append(
                    {
                        "name": stream_name,
                        "flag": stream_flag,
                        "url": stream_url,
                        "type": "youtube"
                    }
                )

        vods_out = []

        vods_container = stream_vods_container.find("div", {"class": "match-vods"})
        all_vods = vods_container.find_all("a", {"class": "wf-card"})

        for module in all_vods:
            vods_url = module.get("href")
            vods_name = module.get_text().strip()

            vods_out.append(
                {
                    "name": vods_name,
                    "url": vods_url
                }
            )

        #  ___ _        _      
        # / __| |_ __ _| |_ ___
        # \__ \  _/ _` |  _(_-<
        # |___/\__\__,_|\__/__/

        overview = []

        team1_players = []
        team2_players = []
        game_map = []
        game_ids = []

        map_player_stats_container = base_container.find("div", class_="vm-stats")
        game_maps = map_player_stats_container.find_all("div", class_="vm-stats-gamesnav-item")

        for module in game_maps:
            module_text = module.get_text().strip()
            module_text = module_text.replace('\n', '')
            module_text = module_text.replace('\t', '')
            if 'N/A' in module_text:
                continue
            else:
                module_text = ''.join([i for i in module_text if not i.isdigit()])
                game_map.append(module_text)

            game_ids.append(module.get("data-game-id"))

        stats_base_container = map_player_stats_container.find("div", class_="vm-stats-container")
        game_stats = stats_base_container.find_all("div", class_="vm-stats-game")

        if len(game_ids) > 0:
            for i in range(len(game_stats)):
                stats_container = stats_base_container.find("div", {"data-game-id": game_ids[i]})
                team_stats_container = stats_container.find_all("table", class_="wf-table-inset")

                team1_stats_body = team_stats_container[0].find("tbody")
                team1_player = team1_stats_body.find_all("tr")

                for player in team1_player:
                    player_name_team_base_container = player.find("td", class_="mod-player")

                    player_flag_container = player_name_team_base_container.find("i")
                    player_flag_dirty = player_flag_container["class"]
                    player_flag = player_flag_dirty[0] + '_' + player_flag_dirty[1].replace("mod-", "")

                    player_name_team = player_name_team_base_container.find("a")
                    player_url = player_name_team["href"]
                    player_url = player_url[1:]

                    player_name_team_container = player_name_team.find_all("div")
                    player_name = player_name_team_container[0].get_text().strip()
                    player_team = player_name_team_container[1].get_text().strip()

                    agents = []

                    agents_base_container = player.find("td", class_="mod-agents")
                    agents_list = agents_base_container.find_all("span", class_="stats-sq")

                    for agent in agents_list:
                        agent_name = agent.find("img")["title"]
                        agent_icon = agent.find("img")["src"]
                        agent_icon = f'https://vlr.gg{agent_icon}'
                        agents.append(
                            {
                                "name": agent_name,
                                "icon": agent_icon
                            }
                        )

                    player_stats_container = player.find_all("td", class_="mod-stat")

                    player_acs = player_stats_container[0].get_text().strip()
                    player_kills = player_stats_container[1].get_text().strip()
                    player_deaths = player_stats_container[2].get_text().strip()
                    player_assists = player_stats_container[3].get_text().strip()
                    player_plus_minus = player_stats_container[4].get_text().strip()
                    player_kast = player_stats_container[5].get_text().strip()
                    player_adr = player_stats_container[6].get_text().strip()
                    player_hs = player_stats_container[7].get_text().strip()
                    player_first_kills = player_stats_container[8].get_text().strip()
                    player_first_deaths = player_stats_container[9].get_text().strip()
                    player_first_plus_minus = player_stats_container[10].get_text().strip()

                    team1_players.append(
                        {
                            "name": player_name,
                            "team": player_team,
                            "flag": player_flag,
                            "url": player_url,
                            "agents": agents,
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

                team2_stats_body = team_stats_container[1].find("tbody")
                team2_player = team2_stats_body.find_all("tr")

                for player in team2_player:
                    player_name_team_base_container = player.find("td", class_="mod-player")

                    player_flag_container = player_name_team_base_container.find("i")
                    player_flag_dirty = player_flag_container["class"]
                    player_flag = player_flag_dirty[0] + '_' + player_flag_dirty[1].replace("mod-", "")

                    player_name_team = player_name_team_base_container.find("a")
                    player_url = player_name_team["href"]
                    player_url = player_url[1:]

                    player_name_team_container = player_name_team.find_all("div")
                    player_name = player_name_team_container[0].get_text().strip()
                    player_team = player_name_team_container[1].get_text().strip()

                    agents = []

                    agents_base_container = player.find("td", class_="mod-agents")
                    agents_list = agents_base_container.find_all("span", class_="stats-sq")

                    for agent in agents_list:
                        agent_name = agent.find("img")["title"]
                        agent_icon = agent.find("img")["src"]
                        agent_icon = f'https://vlr.gg{agent_icon}'
                        agents.append(
                            {
                                "name": agent_name,
                                "icon": agent_icon
                            }
                        )

                    player_stats_container = player.find_all("td", class_="mod-stat")

                    player_acs = player_stats_container[0].get_text().strip()
                    player_kills = player_stats_container[1].get_text().strip()
                    player_deaths = player_stats_container[2].get_text().strip().replace("/", '')
                    player_assists = player_stats_container[3].get_text().strip()
                    player_plus_minus = player_stats_container[4].get_text().strip()
                    player_kast = player_stats_container[5].get_text().strip()
                    player_adr = player_stats_container[6].get_text().strip()
                    player_hs = player_stats_container[7].get_text().strip()
                    player_first_kills = player_stats_container[8].get_text().strip()
                    player_first_deaths = player_stats_container[9].get_text().strip()
                    player_first_plus_minus = player_stats_container[10].get_text().strip()

                    team2_players.append(
                        {
                            "name": player_name,
                            "team": player_team,
                            "flag": player_flag,
                            "url": player_url,
                            "agents": agents,
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

            for i in range(len(game_map)):
                team1_players_out = []
                team2_players_out = []
                for x in range(5):
                    team1_players_out.append(team1_players[x + (i*5)])
                    team2_players_out.append(team2_players[x + (i*5)])
                
                overview.append(
                    {
                        "map": game_map[i],
                        "team1_players": team1_players_out,
                        "team2_players": team2_players_out
                    }
                )

        return (
            date_out, 
            time_out, 
            patch_out, 
            tourney_name_out, 
            tourney_round_out, 
            tourney_icon_out,
            tourney_url_out,
            format_out,
            status_out,
            notes_out,
            team1_name_out,
            team1_elo_out,
            team1_url_out,
            team1_score_out,
            team2_name_out,
            team2_elo_out,
            team2_url_out,
            team2_score_out,
            team1_logo_out,
            team2_logo_out,
            streams_out,
            vods_out,
            overview
        ) 

    def team(self, team_id, type):
        if type == "overview":
            url = f'https://www.vlr.gg/team/{team_id}'
            soup, status = getSoup(url)
        else:
            url = f'https://www.vlr.gg/team/{type}/{team_id}'
            soup, status = getSoup(url)

        base_container = soup.find("div", class_="col mod-1")

        team_info_base_container = base_container.find_all("div", class_="wf-card")
        team_info_container = team_info_base_container[0].find("div", class_="team-header")

        logo_container = team_info_container.find("div", class_="wf-avatar")
        logo_out = logo_container.find("img")["src"]
        logo_out = f'https:{logo_out}'

        name_tag_base_container = team_info_container.find("div", class_="wf-title")
        name_out = name_tag_base_container.find("h1").get_text().strip()
        tag_out = name_tag_base_container.find("h2").get_text().strip()

        website_container = team_info_container.find("div", class_="team-header-website")
        website_out = website_container.find("a")["href"]

        twitter_container = team_info_container.find("div", class_="team-header-twitter")
        twitter_out = twitter_container.find("a")["href"]

        country_flag_container = team_info_container.find("div", class_="team-header-country")
        country_out = country_flag_container.get_text().strip()

        flag_container = country_flag_container.find("i")
        flag_dirty = flag_container["class"]
        flag_out = flag_dirty[0] + '_' + flag_dirty[1].replace("mod-", "")

        if type == "overview":

            roster = []
            staff_out = []
            tournaments = []

            overview_container = base_container.find("div", class_="team-summary-container")
            roster_rating_base_container = overview_container.find("div", class_="team-summary-container-1")
            roster_rating_container = roster_rating_base_container.find_all("div", class_="wf-card")

            roster_container = roster_rating_container[0]
            players_staff_container = roster_container.find_all("div", {"style": "display: flex; flex-wrap: wrap;"})

            players_container = players_staff_container[0]
            players = players_container.find_all("div", class_="team-roster-item")

            for player in players:
                player_url = player.find("a")["href"]
                player_url = player_url[1:]

                player_image_container = player.find("div", class_="team-roster-item-img")
                player_image = player_image_container.find("img")["src"]
                player_image = f'https:{player_image}'

                player_name_flag_container = player.find("div", class_="team-roster-item-name")
                player_name = player_name_flag_container.find("div", class_="team-roster-item-name-real").get_text().strip()

                player_ign_container = player_name_flag_container.find("div", class_="team-roster-item-name-alias")
                player_ign = player_ign_container.get_text().strip()

                flag_container = player_ign_container.find("i")
                flag_dirty = flag_container["class"]
                player_flag = flag_dirty[0] + '_' + flag_dirty[1].replace("mod-", "")

                roster.append({
                    "ign": player_ign,
                    "url": player_url,
                    "image": player_image,
                    "real_name": player_name,
                    "flag": player_flag
                })

            staff_container = players_staff_container[1]
            staffs = staff_container.find_all("div", class_="team-roster-item")

            for staff in staffs:
                staff_url = staff.find("a")["href"]
                staff_url = staff_url[1:]

                staff_image_container = staff.find("div", class_="team-roster-item-img")
                staff_image = staff_image_container.find("img")["src"]
                staff_image = f'https:{staff_image}'

                staff_name_flag_container = staff.find("div", class_="team-roster-item-name")
                staff_name = staff_name_flag_container.find("div", class_="team-roster-item-name-real").get_text().strip()

                staff_ign_container = staff_name_flag_container.find("div", class_="team-roster-item-name-alias")
                staff_ign = staff_ign_container.get_text().strip()

                flag_container = staff_ign_container.find("i")
                flag_dirty = flag_container["class"]
                staff_flag = flag_dirty[0] + '_' + flag_dirty[1].replace("mod-", "")

                staff_out.append({
                    "ign": staff_ign,
                    "url": staff_url,
                    "image": staff_image,
                    "real_name": staff_name,
                    "flag": staff_flag
                })

            rating_container = roster_rating_container[1]
            rating_info_base_container = rating_container.find("div", class_="team-rating-info")
            rating_info_container = rating_info_base_container.find_all("div", class_="team-rating-info-section")

            rank_url = rating_info_container[0].find("a")["href"]
            rank_url = rank_url[1:]

            rank = rating_info_container[0].find("div", class_="rank-num").get_text().strip()
            rank_region = rating_info_container[0].find("div", class_="rating-txt").get_text().strip()
            rating = rating_info_container[1].find("div", class_="rating-num").get_text().strip()
            wins = rating_info_container[2].find("span", class_="win").get_text().strip()
            loss = rating_info_container[2].find("span", class_="loss").get_text().strip()

            event_placement_base_container = overview_container.find("div", class_="team-summary-container-2")
            event_placement_container = event_placement_base_container.find_all("div", class_="wf-card")

            winnings_container = event_placement_container[1].find("div")
            winnings = winnings_container.find("span").get_text().strip()

            tournaments_container = event_placement_container[1].find_all("a")

            for tourneys in tournaments_container:
                tourney_url = tourneys["href"]
                tourney_url = tourney_url[1:]

                tourney_name = tourneys.find("div", class_="text-of").get_text().strip()
                tourney_placement = tourneys.find("span", class_="team-event-item-series").get_text().strip()
                tourney_placement = tourney_placement.replace("\n", "")
                tourney_placement = tourney_placement.replace("\t", "")



                tournaments.append({
                    "name": tourney_name,
                    "placement": tourney_placement,
                    #"prize": tourney_prize,
                    #"year": tourney_year,
                    "url": tourney_url
                })

            match_data_out = {
                "roster_rating": {
                    "current_roster": {
                        "players": roster,     # List
                        "staff": staff_out       # List
                    },   
                    "current_rank": rank,
                    "rank_region": rank_region,
                    "region_rank_url": rank_url,
                    "rating": rating,
                    "record": {
                        "wins": wins,
                        "losses": loss
                    }
                },
                "event_placements": {
                    "total_winnings": winnings,
                    "tournament_placements": tournaments # List
                }
            }
        

        return (
            name_out,
            tag_out,
            website_out,
            twitter_out,
            country_out,
            flag_out,
            logo_out,
            match_data_out
        )
