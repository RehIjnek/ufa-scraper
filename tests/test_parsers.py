from ufa_scraper.clients.http_client import HttpClient
from ufa_scraper.pages.players_page import PlayersPage
from ufa_scraper.pages.stats_page import StatsPage
from ufa_scraper.parsers.players_parser import PlayersParser
from ufa_scraper.parsers.stats_parser import StatsParser

def test_parse_players_page():
    client = HttpClient()
    players_page = PlayersPage(client)
    players_parser = PlayersParser()
    html = players_page.get_players(0)
    data = players_parser.parse_players(html)

    assert isinstance(data, dict)

def test_parse_player_stats():
    client = HttpClient()
    stats_page = StatsPage(client)
    stats_parser = StatsParser()
    html = stats_page.get_player_stats_backend("bjagt")
    data = stats_parser.parse_player_stats_backend(html)

    assert isinstance(data, dict)
