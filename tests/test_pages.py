from ufa_scraper.clients.http_client import HttpClient
from ufa_scraper.pages.stats_page import StatsPage

def test_get_player_stats_html():
    client = HttpClient()
    stats_page = StatsPage(client)

    player_id = "bjagt"
    html = stats_page.get_player_stats_html(player_id)

    assert isinstance(html, str)
