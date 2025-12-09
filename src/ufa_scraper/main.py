import logging
import time
from ufa_scraper.clients.http_client import HttpClient
from ufa_scraper.pages.players_page import PlayersPage
from ufa_scraper.pages.stats_page import StatsPage
from ufa_scraper.parsers.players_parser import PlayersParser
from ufa_scraper.parsers.stats_parser import StatsParser
from ufa_scraper.pipelines.clean import clean_stats
from ufa_scraper.pipelines.storage import save_player_stats, save_players
from ufa_scraper.utils.logging_setup import setup_logging

CURRENT_PAGE = 49
MAX_PAGES = 187

def main():
    # Setup
    setup_logging()
    logger = logging.getLogger(__name__)
    client = HttpClient()

    # Scrape players
    players_page = PlayersPage(client)
    players_parser = PlayersParser()

    for page_id in range(CURRENT_PAGE, MAX_PAGES):
        logger.info(f"Beginning player page {page_id} scraping")
        players_html = players_page.get_players(page_id)
        players_data = players_parser.parse_players(players_html)
        logger.info(f"Ending player page {page_id} scraping with {len(players_data['players'])} players scraped")
        save_players(players_data, filename=f"players_{page_id}.csv")

        # Scrape stats for each player
        stats_page = StatsPage(client)
        stats_parser = StatsParser()
        for i in range(len(players_data["players"])):
            logger.info(f"Beginning stats scraping for player {players_data['players'][i]['player_id']}")
            stats_html = stats_page.get_player_stats_backend(players_data["players"][i]["player_id"])
            stats_data = stats_parser.parse_player_stats_backend(stats_html)
            cleaned_stats_data = clean_stats(stats_data)
            logger.info(f"Ending stats scraping for player {players_data['players'][i]['player_id']}")
            save_player_stats(cleaned_stats_data, filename=f"{players_data['players'][i]['player_id']}_stats.csv")

if __name__ == "__main__":
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print(f"Finished in {end - start:.2f} seconds")
