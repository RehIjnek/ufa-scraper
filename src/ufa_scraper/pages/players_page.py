from ufa_scraper.clients.http_client import HttpClient

class PlayersPage:
    def __init__(self, client: HttpClient):
        self.client = client

    def get_players(self, page_id: int):
        path = f"/league/players?page={page_id}"
        return self.client.get_frontend(path)
    
