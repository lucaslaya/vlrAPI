import requests
from bs4 import BeautifulSoup
import json

def getSoup(url):
    response = requests.get(url)
    html, status_code = response.text, response.status_code

    return BeautifulSoup(html, "html.parser"), status_code


class Vlr:

    def vlr_match(self, match_id=68326):
        url = f'https://www.vlr.gg/{match_id}'
        soup, status = getSoup(url)
        print(f'vlr_match status: {status}')

        base_container = soup.find(id="wrapper")
        base = base_container.find("div", {"class": "col mod-3"})
       



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
        json_string = json.dumps(data, sort_keys=True, indent=2)
        
        with open('vlr_upcoming.json', 'w') as outfile:
            outfile.write(json_string)

        return json_string

    def vlr_results(self, page=1):
        url = f'https://www.vlr.gg/matches/results/?page={page}'
        soup, status = getSoup(url)
        print(f'vlr_results status: {status}')

VLR = Vlr()

#VLR.vlr_match()

output = VLR.vlr_upcoming()
#print(output)
