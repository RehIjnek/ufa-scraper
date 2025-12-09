from ufa_scraper.clients.http_client import HttpClient
from ufa_scraper.pages.players_page import PlayersPage
from ufa_scraper.pages.stats_page import StatsPage

def test_get_players_page_html():
    client = HttpClient()
    players_page = PlayersPage(client)

    page_id = "0"
    html = players_page.get_players(page_id)

    assert isinstance(html, str)


def test_get_player_stats_html():
    client = HttpClient()
    stats_page = StatsPage(client)

    player_id = "bjagt"
    html = stats_page.get_player_stats_backend(player_id)

    assert isinstance(html, str)
