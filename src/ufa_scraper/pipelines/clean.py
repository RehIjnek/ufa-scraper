def clean_stats(data: dict) -> dict:
    """Clean and standardize stats data."""

    if data.get("name"):
        data["name"] = data["name"].title()

    if data.get("team"):
        data["team"] = data["team"].upper()

    return data
