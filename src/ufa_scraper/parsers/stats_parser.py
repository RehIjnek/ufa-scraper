from bs4 import BeautifulSoup
import json
from collections import defaultdict
from math import hypot

# ---------------------------------------------
# Helpers
# ---------------------------------------------

def yard_distance(e1, e2):
    """Compute yardage between two field coordinates."""
    if "x" not in e1 or "y" not in e1 or "x" not in e2 or "y" not in e2:
        return 0
    # return hypot(e2["x"] - e1["x"], e2["y"] - e1["y"])
    return e2["y"] - e1["y"]

# ---------------------------------------------
# Event type constants (decoded from the JS)
# ---------------------------------------------
O_LINE = 1
D_LINE = 2
PULL = 3
OB_PULL = 4
BLOCK = 5
CALLAHAN = 6
THROWAWAY = 8
DROP = 19
THROW = 20
GOAL = 22
PULL_DROPPED = 33
O_LINE_CHANGE = 40
D_LINE_CHANGE= 41
D_OFFSIDES = 44
O_OFFSIDES = 45

# These DO NOT involve a player id:
THROWAWAY_CAUSED = 9
STOPPAGE_START = 11
STOPPAGE_END = 12
DEAD_DISC = 13
TIMEOUT = 14
STALL = 17
OPPONENT_SCORED = 21
GAME_START = 50

class StatsParser:
    def parse_player_stats_frontend(self, html_str: str) -> dict:
        soup = BeautifulSoup(html_str, "lxml")

        # player stats page parsing logic goes here
        # TODO

        return {
            "stats": "No stats found"
        }
    
    def parse_player_stats_backend(self, json_str: str) -> dict:
        data = json.loads(json_str)

        return data

    def parse_game_stats(self, json_str: str) -> dict:
        """Parse a UFA TSG JSON object and return per-player statistics."""

        # Teams
        json_data = json.loads(json_str)
        teams = {
            "home": json_data["tsgHome"],
            "away": json_data["tsgAway"],
        }

        # Rosters indexed by roster ID
        rosters = {
            "home": {r["id"]: r for r in json_data["rostersHome"]},
            "away": {r["id"]: r for r in json_data["rostersAway"]},
        }
        
        # Team abbrevs
        team_abbrev = {
            "home": json_data["game"]["team_season_home"]["abbrev"],
            "away": json_data["game"]["team_season_away"]["abbrev"],
        }
        
        # ---------------------------------------------
        # Stat storage
        # ---------------------------------------------
        stats = defaultdict(lambda: {
            "name": "",
            "team": "",
            "number": "",

            "points_played": 0,
            "o_points": 0,
            "d_points": 0,

            "assists": 0,
            "goals": 0,
            "blocks": 0,
            "plus_minus": 0,

            "receiving_yards": 0,
            "throwing_yards": 0,
            "yards": 0,

            "completions": 0,
            "throws_attempted": 0,
            "completion_pct": 0,

            "hockey_assists": 0,
            "throwaways": 0,
            "stalls": 0,
            "callahans": 0,
            "drops": 0,

            "holds": 0,
            "breaks": 0,
            "holds_pct": 0,
            "breaks_pct": 0,
        })
        
        # ---------------------------------------------
        # Process each team
        # ---------------------------------------------
        if teams["home"]["events"] and teams["away"]["events"]:
            for side, tsg in teams.items():
                events = json.loads(tsg["events"])

                roster = rosters[side]

                last_throw_event = None
                last_thrower = None
                prev_thrower = None

                curr_line = None
                is_offense = None

                for i, e in enumerate(events):

                    t = e.get("t")
                    pid = e.get("r")
                    line = e.get("l")
                
                    # -------------------------
                    # Point start
                    # -------------------------
                    if t in {O_LINE, D_LINE, O_LINE_CHANGE, D_LINE_CHANGE} and line:
                        if t in {O_LINE, D_LINE}:
                            is_offense = t
                        is_line_change = t in {O_LINE_CHANGE, D_LINE_CHANGE}

                        new_line = set(line)
                        old_line = set(curr_line) if curr_line else set()

                        for p in new_line:
                            # Initialize player identity once
                            if stats[p]["name"] == "":
                                info = roster[p]["player"]
                                stats[p]["name"] = f"{info['first_name']} {info['last_name']}"
                                stats[p]["number"] = roster[p]["jersey_number"]
                                stats[p]["team"] = team_abbrev[side]

                            # Starting line OR newly subbed-in player
                            if not is_line_change or p not in old_line:
                                stats[p]["points_played"] += 1
                                if is_offense == O_LINE:
                                    stats[p]["o_points"] += 1
                                else:
                                    stats[p]["d_points"] += 1
                            
                        curr_line = new_line

                    # If no player id, skip event
                    if not pid and t not in {THROWAWAY, STALL}:
                        continue

                    # ------------------------------------------------------
                    # THROW
                    # ------------------------------------------------------
                    if t == THROW:
                        # Count attempt
                        stats[pid]["throws_attempted"] += 1

                        # If there was a previous throw, it was completed
                        if last_thrower is not None:
                            stats[last_thrower]["completions"] += 1

                            # Yardage
                            yards = yard_distance(last_throw_event, e)
                            stats[last_thrower]["throwing_yards"] += yards
                            stats[pid]["receiving_yards"] += yards

                        # Shift throw chain
                        prev_thrower = last_thrower
                        last_thrower = pid
                        last_throw_event = e

                    # ------------------------------------------------------
                    # GOAL
                    # ------------------------------------------------------
                    elif t == GOAL:
                        scorer = pid
                        
                        stats[scorer]["goals"] += 1
                        stats[scorer]["plus_minus"] += 1

                        if last_thrower is not None and last_thrower != scorer:
                            stats[last_thrower]["assists"] += 1
                            stats[last_thrower]["plus_minus"] += 1

                            # Completion + yards still apply
                            stats[last_thrower]["completions"] += 1
                            yards = yard_distance(last_throw_event, e)
                            stats[last_thrower]["throwing_yards"] += yards
                            stats[scorer]["receiving_yards"] += yards
                        
                        # Hockey assist
                        if prev_thrower is not None:
                            stats[prev_thrower]["hockey_assists"] += 1

                        # Holds and breaks
                        if curr_line:
                            if is_offense == O_LINE:
                                for p in curr_line:
                                    stats[p]["holds"] += 1
                            else:
                                for p in curr_line:
                                    stats[p]["breaks"] += 1

                        # Reset possession
                        last_thrower = None
                        prev_thrower = None
                        last_throw_event = None

                    # ------------------------------------------------------
                    # BLOCK
                    # ------------------------------------------------------
                    elif t == BLOCK:
                        stats[pid]["blocks"] += 1
                        stats[pid]["plus_minus"] += 1
                        # Possession flips → erase chain
                        last_thrower = None
                        prev_thrower = None
                        last_throw_event = None

                    # ------------------------------------------------------
                    # THROWAWAY
                    # ------------------------------------------------------
                    elif t == THROWAWAY:
                        stats[last_thrower]["throwaways"] += 1
                        stats[last_thrower]["plus_minus"] -= 1
                        last_thrower = None
                        prev_thrower = None
                        last_throw_event = None

                    # ------------------------------------------------------
                    # DROP
                    # ------------------------------------------------------
                    elif t == DROP:
                        stats[pid]["drops"] += 1
                        stats[pid]["plus_minus"] -= 1
                        # drop ends possession
                        last_thrower = None
                        prev_thrower = None
                        last_throw_event = None

                    # ------------------------------------------------------
                    # STALL
                    # ------------------------------------------------------
                    elif t == STALL:
                        stats[last_thrower]["stalls"] += 1
                        # Stall-out is a turnover → reset throw chain
                        last_thrower = None
                        prev_thrower = None
                        last_throw_event = None

                    # ------------------------------------------------------
                    # CALLAHAN
                    # ------------------------------------------------------
                    elif t == CALLAHAN:
                        stats[pid]["callahans"] += 1
                        stats[pid]["blocks"] += 1
                        stats[pid]["goals"] += 1
                        stats[pid]["plus_minus"] += 2

                    # ------------------------------------------------------
                    # CATCH EVENTS NOT IN TABLE
                    # ------------------------------------------------------
                    else:
                        if t not in {PULL, OB_PULL, D_OFFSIDES, O_OFFSIDES, PULL_DROPPED}:
                            print(f"Unrecognized event type {t} for player {pid} at event index {i}")

            # ------------------------------------------------
            # Finalize stats
            # ------------------------------------------------
            for pid, s in stats.items():
                if s["throws_attempted"] > 0:
                    s["completion_pct"] = s["completions"] / s["throws_attempted"]
                s["yards"] = s["receiving_yards"] + s["throwing_yards"]
                if s["holds"] > 0:
                    s["holds_pct"] = s["holds"] / (s["o_points"])
                if s["breaks"] > 0:
                    s["breaks_pct"] = s["breaks"] / (s["d_points"])
        else:
            for side, tsg in teams.items():
                roster = rosters[side]

                for pid, r in roster.items():
                    if stats[pid]["name"] == "":
                        info = r["player"]
                        stats[pid]["name"] = f"{info['first_name']} {info['last_name']}"
                        stats[pid]["number"] = r["jersey_number"]
                        stats[pid]["team"] = team_abbrev[side]

        return stats