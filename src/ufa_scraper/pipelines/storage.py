import csv
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def save_player_stats(data: dict, filename="player_stats.csv"):
    filepath = DATA_DIR / filename

    write_header = not filepath.exists()

    with open(filepath, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(data)
