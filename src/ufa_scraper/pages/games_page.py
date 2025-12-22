from ufa_scraper.clients.http_client import HttpClient

class GamesPage:
    def __init__(self, client: HttpClient):
        self.client = client
    
    def get_games(self, page_id: str):
        path = f"/stats/team-game-stats?page={page_id}"
        return self.client.get_frontend(path)
    