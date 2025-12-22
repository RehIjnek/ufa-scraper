'''command to run: python -m src.ufa_scraper.main'''

import logging
import time
from ufa_scraper.clients.http_client import HttpClient
from ufa_scraper.pages.games_page import GamesPage
from ufa_scraper.pages.players_page import PlayersPage
from ufa_scraper.pages.stats_page import StatsPage
from ufa_scraper.parsers.games_parser import GamesParser
from ufa_scraper.parsers.players_parser import PlayersParser
from ufa_scraper.parsers.stats_parser import StatsParser
from ufa_scraper.pipelines.clean import clean_player_stats
from ufa_scraper.pipelines.storage import save_player_stats, save_players, save_game_stats, save_games
from ufa_scraper.utils.logging_setup import setup_logging

CURRENT_PLAYER_PAGE = 0
MAX_PLAYER_PAGES = 187
CURRENT_PLAYER = 0

CURRENT_GAME_PAGE = 2
MAX_GAME_PAGES = 3
CURRENT_GAME = 2

def player_scraping():
    # Setup
    setup_logging()
    logger = logging.getLogger(__name__)
    client = HttpClient()

    # Scrape players
    players_page = PlayersPage(client)
    players_parser = PlayersParser()

    for page_id in range(CURRENT_PLAYER_PAGE, MAX_PLAYER_PAGES):
        logger.info(f"Beginning player page {page_id} scraping")
        players_html = players_page.get_players(page_id)
        players_data = players_parser.parse_players(players_html)
        logger.info(f"Ending player page {page_id} scraping with {len(players_data['players'])} players scraped")
        save_players(players_data, filename=f"players_{page_id}.csv")

        # Scrape stats for each player
        stats_page = StatsPage(client)
        stats_parser = StatsParser()
        for i in range(CURRENT_PLAYER, len(players_data["players"])):
            logger.info(f"Beginning stats scraping for player {players_data['players'][i]['player_id']}")
            stats_html = stats_page.get_player_stats_backend(players_data["players"][i]["player_id"])
            stats_data = stats_parser.parse_player_stats_backend(stats_html)
            cleaned_stats_data = clean_player_stats(stats_data)
            logger.info(f"Ending stats scraping for player {players_data['players'][i]['player_id']}")
            save_player_stats(cleaned_stats_data, filename=f"{players_data['players'][i]['player_id']}_stats.csv")

def game_scraping():
    # Setup
    setup_logging()
    logger = logging.getLogger(__name__)
    client = HttpClient()

    # Scrape games
    games_page = GamesPage(client)
    games_parser = GamesParser()

    for page_id in range(CURRENT_GAME_PAGE, MAX_GAME_PAGES):
        logger.info(f"Beginning game page {page_id} scraping")
        games_html = games_page.get_games(page_id)
        games_data = games_parser.parse_games(games_html)
        logger.info(f"Ending game page {page_id} scraping with {len(games_data['stats'])} games scraped")
        save_games(games_data, filename=f"games_{page_id}.csv")
        
        # Scrape stats for each game
        stats_page = StatsPage(client)
        stats_parser = StatsParser()
        for i in range(CURRENT_GAME, len(games_data["stats"]), 2):
            logger.info(f"Beginning stats scraping for game {games_data['stats'][i]['gameID']}")
            stats_html = stats_page.get_game_stats(games_data["stats"][i]["gameID"])
            stats_data = stats_parser.parse_game_stats(stats_html)
            # cleaned_stats_data = clean_game_stats(stats_data)
            logger.info(f"Ending stats scraping for game {games_data['stats'][i]['gameID']}")
            save_game_stats(stats_data, filename=f"{games_data['stats'][i]['gameID']}_stats.csv")

if __name__ == "__main__":
    start = time.perf_counter()
    # player_scraping()
    game_scraping()
    end = time.perf_counter()
    print(f"Finished in {int((end - start) // 3600)} hours, {int((end - start) % 3600 // 60)} minutes, and {(end - start) % 60:.2f} seconds.")
