from bs4 import BeautifulSoup

class StatsParser:
    def parse_player_stats(self, html: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        # Example extraction (placeholder CSS selectors)
        name = soup.select_one(".player-name").text.strip() if soup.select_one(".player-name") else None
        team = soup.select_one(".team-name").text.strip() if soup.select_one(".team-name") else None

        return {
            "name": name,
            "team": team,
            # TODO: Add real fields when inspecting actual HTML
        }
