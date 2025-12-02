from ufa_scraper.clients.http_client import HttpClient

class StatsPage:
    def __init__(self, client: HttpClient):
        self.client = client

    def get_player_stats_html(self, player_id: str):
        path = f"/league/players/{player_id}"
        return self.client.get(path)
