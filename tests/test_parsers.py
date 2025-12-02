from ufa_scraper.parsers.stats_parser import StatsParser

def test_parse_player_stats():
    sample_html = """
    <div class="player-name">John Doe</div>
    <div class="team-name">Windbreakers</div>
    """
    parser = StatsParser()
    result = parser.parse_player_stats(sample_html)

    assert result["name"] == "John Doe"
    assert result["team"] == "Windbreakers"
