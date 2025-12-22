from bs4 import BeautifulSoup

class PlayersParser:
    def parse_players(self, html_str: str) -> dict:
        soup = BeautifulSoup(html_str, "lxml")

        players = soup.find_all("td", class_="views-field views-field-field-player-display-name")
        for i in range(len(players)):
            player_id = players[i].find("a")["href"].replace("/league/players/", "")
            player_name = players[i].text.strip()
            players[i] = {
                "player_id": player_id,
                "player_name": player_name
            }
        return {
            "players": players
        }
    