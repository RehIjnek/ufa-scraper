from ufa_scraper.clients.http_client import HttpClient

class StatsPage:
    def __init__(self, client: HttpClient):
        self.client = client

    def get_player_stats_frontend(self, player_id: str):
        path = f"/league/players/{player_id}"
        return self.client.get_frontend(path)
    
    def get_player_stats_backend(self, player_id: str):
        path = f"/web-v1/roster-stats-for-player?playerID={player_id}"
        return self.client.get_backend(path)
    
    def get_game_stats_backend(self, game_id: str):
        path = f"/stats-pages/game/{game_id}"
        return self.client.get_backend(path)
    
    