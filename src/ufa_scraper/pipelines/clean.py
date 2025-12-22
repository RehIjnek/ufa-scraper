def clean_player_stats(data: dict) -> dict:
    if data["stats"] == []:
        return {
            "stats": [
                {
                    "year": None,
                    "teamAbbrev": None,
                    "regSeason": None,
                    "assists": None,
                    "goals": None,
                    "hockeyAssists": None,
                    "completions": None,
                    "throwaways": None,
                    "stalls": None,
                    "throwsAttempted": None,
                    "catches": None,
                    "drops": None,
                    "blocks": None,
                    "callahans": None,
                    "pulls": None,
                    "obPulls": None,
                    "recordedPulls": None,
                    "recordedPullsHangtime": None,
                    "gamesPlayed": None,
                    "oPointsPlayed": None,
                    "oPointsScored": None,
                    "dPointsPlayed": None,
                    "dPointsScored": None,
                    "secondsPlayed": None,
                    "yardsReceived": None,
                    "yardsThrown": None,
                    "hucksCompleted": None,
                    "hucksAttempted": None
                }
            ]
        }
    else:
        return data
