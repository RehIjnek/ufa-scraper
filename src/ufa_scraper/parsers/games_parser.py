from bs4 import BeautifulSoup

class GamesParser:
    def parse_games(self, html_str: str) -> dict:
        soup = BeautifulSoup(html_str, "lxml")

        games = soup.find_all("td", class_="svelte-1gs1t9w")
        for i in range(len(games)):
            game_id = games[i].find("a")["href"]
            game_name = games[i].text.strip()
            games[i] = {
                "game_id": game_id,
                "game_name": game_name
            }
        return {
            "games": games
        }