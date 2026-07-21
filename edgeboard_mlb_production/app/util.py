import math
import re
from datetime import datetime
from zoneinfo import ZoneInfo


TEAM_ALIASES = {
    "arizona diamondbacks": "Arizona Diamondbacks",
    "athletics": "Athletics",
    "oakland athletics": "Athletics",
    "atlanta braves": "Atlanta Braves",
    "baltimore orioles": "Baltimore Orioles",
    "boston red sox": "Boston Red Sox",
    "chicago cubs": "Chicago Cubs",
    "chicago white sox": "Chicago White Sox",
    "cincinnati reds": "Cincinnati Reds",
    "cleveland guardians": "Cleveland Guardians",
    "colorado rockies": "Colorado Rockies",
    "detroit tigers": "Detroit Tigers",
    "houston astros": "Houston Astros",
    "kansas city royals": "Kansas City Royals",
    "los angeles angels": "Los Angeles Angels",
    "los angeles dodgers": "Los Angeles Dodgers",
    "miami marlins": "Miami Marlins",
    "milwaukee brewers": "Milwaukee Brewers",
    "minnesota twins": "Minnesota Twins",
    "new york mets": "New York Mets",
    "new york yankees": "New York Yankees",
    "philadelphia phillies": "Philadelphia Phillies",
    "pittsburgh pirates": "Pittsburgh Pirates",
    "san diego padres": "San Diego Padres",
    "san francisco giants": "San Francisco Giants",
    "seattle mariners": "Seattle Mariners",
    "st. louis cardinals": "St. Louis Cardinals",
    "st louis cardinals": "St. Louis Cardinals",
    "tampa bay rays": "Tampa Bay Rays",
    "texas rangers": "Texas Rangers",
    "toronto blue jays": "Toronto Blue Jays",
    "washington nationals": "Washington Nationals",
}


def canonical_team(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", name.strip().lower())
    return TEAM_ALIASES.get(cleaned, name.strip())


def game_key(game_date, away: str, home: str) -> str:
    return f"{game_date.isoformat()}::{canonical_team(away)}::{canonical_team(home)}"


def american_to_implied(odds: int | float) -> float:
    odds = float(odds)
    return (-odds) / ((-odds) + 100.0) if odds < 0 else 100.0 / (odds + 100.0)


def implied_to_american(prob: float) -> int:
    prob = min(max(prob, 0.001), 0.999)
    return round(-100 * prob / (1 - prob)) if prob >= 0.5 else round(100 * (1 - prob) / prob)


def american_profit_per_unit(odds: int | float) -> float:
    odds = float(odds)
    return 100.0 / (-odds) if odds < 0 else odds / 100.0


def no_vig_probability(selected_odds: int, opposite_odds: int) -> float:
    a = american_to_implied(selected_odds)
    b = american_to_implied(opposite_odds)
    return a / (a + b)


def expected_value(prob: float, odds: int) -> float:
    return prob * american_profit_per_unit(odds) - (1 - prob)


def fractional_kelly(prob: float, odds: int, fraction: float) -> float:
    b = american_profit_per_unit(odds)
    raw = max(0.0, (b * prob - (1 - prob)) / b)
    return raw * fraction


def normal_cdf(x: float, mean: float, std: float) -> float:
    z = (x - mean) / max(std, 0.001)
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def local_now(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))
