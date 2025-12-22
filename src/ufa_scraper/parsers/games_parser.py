from bs4 import BeautifulSoup
import json

class GamesParser:
    def parse_games(self, json_str: str) -> dict:
        data = json.loads(json_str)

        return data