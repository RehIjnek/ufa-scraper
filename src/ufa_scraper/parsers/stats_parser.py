from bs4 import BeautifulSoup
import json

class StatsParser:
    def parse_player_stats_frontend(self, html_str: str) -> dict:
        soup = BeautifulSoup(html_str, "lxml")

        # player stats page parsing logic goes here
        # TODO

        return {
            "stats": "No stats found"
        }
    
    def parse_player_stats_backend(self, json_str: str) -> dict:
        data = json.loads(json_str)

        return data
    
