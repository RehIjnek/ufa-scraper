import logging
from ufa_scraper.clients.http_client import HttpClient
from ufa_scraper.pages.stats_page import StatsPage
from ufa_scraper.parsers.stats_parser import StatsParser
from ufa_scraper.pipelines.clean import clean_stats
from ufa_scraper.pipelines.storage import save_player_stats
from ufa_scraper.utils.logging_setup import setup_logging

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    client = HttpClient()
    stats_page = StatsPage(client)
    parser = StatsParser()

    player_id = "12345"  # Example; replace with real ID
    logger.info(f"Scraping stats for player {player_id}")

    html = stats_page.get_player_stats_html(player_id)
    data = parser.parse_player_stats(html)
    data = clean_stats(data)

    save_player_stats(data)

    logger.info(f"Saved stats: {data}")

if __name__ == "__main__":
    main()
