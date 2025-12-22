import csv
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PLAYER_STATS_DIR = DATA_DIR / "player_stats"
PLAYER_STATS_DIR.mkdir(exist_ok=True)

PLAYERS_DIR = DATA_DIR / "players"
PLAYERS_DIR.mkdir(exist_ok=True)

GAME_STATS_DIR = DATA_DIR / "game_stats"
GAME_STATS_DIR.mkdir(exist_ok=True)

GAMES_DIR = DATA_DIR / "games"
GAMES_DIR.mkdir(exist_ok=True)

def save_player_stats(data: dict, filename="player_stats.csv"):
    filepath = PLAYER_STATS_DIR / filename

    write_header = not filepath.exists()

    fieldnames = data["stats"][0].keys()

    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(data["stats"])

def save_players(data: dict, filename="players.csv"):
    filepath = PLAYERS_DIR / filename

    write_header = not filepath.exists()

    fieldnames = data["players"][0].keys()

    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(data["players"])

def save_game_stats(data: dict, filename="game_stats.csv"):
    filepath = GAME_STATS_DIR / filename

    # Convert defaultdict → dict
    data = dict(data)

    if not data:
        raise ValueError("No data to write")

    fieldnames = [
        "player_id",
        "name", "team", "number",
        "points_played", "o_points", "d_points",
        "assists", "goals", "blocks", "plus_minus",
        "receiving_yards", "throwing_yards", "yards",
        "completions", "throws_attempted", "completion_pct",
        "hockey_assists", "throwaways", "stalls",
        "callahans", "drops",
        "holds", "breaks", "holds_pct", "breaks_pct"
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"  # protects against extra keys
        )

        # ✅ Always write header in "w" mode
        writer.writeheader()

        for player_id, stats in data.items():
            writer.writerow({"player_id": player_id, **stats})

def save_games(data: dict, filename="games.csv"):
    filepath = GAMES_DIR / filename

    write_header = not filepath.exists()

    fieldnames = data["stats"][0].keys()

    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(data["stats"])
