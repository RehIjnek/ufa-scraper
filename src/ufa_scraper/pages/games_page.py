from ufa_scraper.clients.http_client import HttpClient

class GamesPage:
    def __init__(self, client: HttpClient):
        self.client = client
    
    def get_games(self, page_id: str):
        path = f"/web-v1/team-game-stats?limit=20&page={page_id}"
        return self.client.get_backend(path)
    