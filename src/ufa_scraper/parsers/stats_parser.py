from bs4 import BeautifulSoup

class StatsParser:
    def parse_player_stats(self, html: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        # stats table parsing logic goes here
        stats = soup.find("div", class_="svelte-player-stats-table svelte-mkdd1m") or None

        return {
            stats: stats.text.strip() if stats else "No stats found"
        }
