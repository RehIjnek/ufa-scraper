import csv
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

STATS_DIR = DATA_DIR / "stats"
STATS_DIR.mkdir(exist_ok=True)

PLAYERS_DIR = DATA_DIR / "players"
PLAYERS_DIR.mkdir(exist_ok=True)

def save_player_stats(data: dict, filename="player_stats.csv"):
    filepath = STATS_DIR / filename

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
