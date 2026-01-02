'''command to run: python -m src.ufa_scraper.main'''

import logging
import time
import math
import json 
import numpy as np
import pandas as pd
from pathlib import Path
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

# WEB SCAPER VARIABLES
CURRENT_PLAYER_PAGE = 0
MAX_PLAYER_PAGES = 187
CURRENT_PLAYER = 0

CURRENT_GAME_PAGE = 1   # page 77 is where advanced stats stop
MAX_GAME_PAGES = 176
CURRENT_GAME = 0

# ELO UODATER VARIABLES
START_ELO = 1500

K_BASE = 8
ALPHA = 0.35

Z_CLIP = 2.5
MIN_POINTS = 5

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
            logger.info(f"Ending stats scraping for game {games_data['stats'][i]['gameID']}")
            save_game_stats(stats_data, filename=f"{games_data['stats'][i]['gameID']}_stats.csv")

def compute_team_elo(team_df, players):
    total = 0.0
    weight = 0.0

    for _, row in team_df.iterrows():
        pid = row["player_id"]
        pts = row["points_played"]

        if pid in players and pts > 0:
            total += players[pid]["elo"] * pts
            weight += pts

    return total / weight if weight > 0 else START_ELO

def elo_expectation(team_elo, opp_elo):
    return 1 / (1 + 10 ** ((opp_elo - team_elo) / 400))

def compute_raw_contribution(row):
    usage = (
        row.get("assists", 0)
        + row.get("goals", 0)
        + row.get("throwaways", 0)
        + row.get("drops", 0)
    )

    efficiency = 0
    if usage > 0:
        efficiency = (row.get("assists", 0) + row.get("goals", 0)) / usage

    return (
        1.0 * row.get("goals", 0)
        + 0.9 * row.get("assists", 0)
        + 0.5 * row.get("hockey_assists", 0)
        + 1.0 * row.get("blocks", 0)
        + 1.2 * row.get("breaks", 0)
        - 1.0 * row.get("throwaways", 0)
        - 0.8 * row.get("drops", 0)
        - 1.2 * row.get("stalls", 0)
        + 0.75 * efficiency
    )

def update_team_elos(team_df, opp_df, players, score_signal):
    team_df = team_df.copy()

    # Initialize players
    for _, row in team_df.iterrows():
        pid = row["player_id"]
        if pid not in players:
            players[pid] = {
                "name": row["name"],
                "elo": START_ELO,
            }

    # Team Elo expectations
    team_elo = compute_team_elo(team_df, players)
    opp_elo = compute_team_elo(opp_df, players)

    expected = elo_expectation(team_elo, opp_elo)

    # Outcome in [0,1]
    actual = (score_signal + 1) / 2

    # Contribution
    team_df["raw"] = team_df.apply(compute_raw_contribution, axis=1)
    team_df["cpp"] = team_df["raw"] / team_df["points_played"].clip(lower=1)

    mean_cpp = team_df["cpp"].mean()
    std_cpp = team_df["cpp"].std() + 1e-6

    for _, row in team_df.iterrows():
        pts = row["points_played"]
        if pts < MIN_POINTS:
            continue

        pid = row["player_id"]

        z = (row["cpp"] - mean_cpp) / std_cpp
        z = max(min(z, Z_CLIP), -Z_CLIP)

        K = K_BASE * math.sqrt(pts / 20)
        contribution = math.exp(ALPHA * z)

        delta = K * (actual - expected) * contribution
        players[pid]["elo"] += delta

def process_game_csv(filepath, players, home_team, away_team, home_score, away_score):
    df = pd.read_csv(filepath)

    score_diff = home_score - away_score
    score_signal = math.tanh(score_diff / 5)

    home_df = df[df["team"] == home_team]
    away_df = df[df["team"] == away_team]

    update_team_elos(home_df, away_df, players, score_signal)
    update_team_elos(away_df, home_df, players, -score_signal)

def run_season(game_files):
    players = {}

    for game in game_files:
        process_game_csv(
            filepath=game["file"],
            players=players,
            home_team=game["home_team"],
            away_team=game["away_team"],
            home_score=game["home_score"],
            away_score=game["away_score"],
        )

    return players

def save_elos(players, filepath="data/elos/player_elos.csv"):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "player_id": pid,
            "name": info["name"],
            "elo": round(info["elo"], 2),
        }
        for pid, info in players.items()
    ]

    df = pd.DataFrame(rows).sort_values("elo", ascending=False)
    df.to_csv(path, index=False)

def elo_update():
    # Setup
    setup_logging()
    logger = logging.getLogger(__name__)
    client = HttpClient()

    stats_page = StatsPage(client)

    # Gather all game stat files
    game_files = []
    stats_dir = Path("data/game_stats")
    for stat_file in stats_dir.glob("2025-*_stats.csv"):
        # Extract game metadata from filename or associated data source
        game_id = stat_file.stem.replace("_stats", "")
        stats_html = stats_page.get_game_stats(game_id)
        data = json.loads(stats_html)
        game_metadata = {
            "file": str(stat_file),
            "home_team": str(data["game"]["team_season_home"]["abbrev"]),
            "away_team": str(data["game"]["team_season_away"]["abbrev"]),
            "home_score": int(data["game"]["score_home"]),
            "away_score": int(data["game"]["score_away"]),
        }
        game_files.append(game_metadata)
    logger.info(f"Found {len(game_files)} game stat files for ELO update")
    logger.info("Starting ELO computation for the season")
    elos = run_season(game_files)
    logger.info("Finished ELO computation for the season")
    save_elos(elos)

if __name__ == "__main__":
    start = time.perf_counter()
    # player_scraping()
    # game_scraping()
    elo_update()
    end = time.perf_counter()
    print(f"Finished in {int((end - start) // 3600)} hours, {int((end - start) % 3600 // 60)} minutes, and {(end - start) % 60:.2f} seconds.")
