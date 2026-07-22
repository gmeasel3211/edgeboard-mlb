from datetime import datetime, timezone
from typing import Any

import httpx

from ..config import get_settings

BASE = "https://api.the-odds-api.com/v4"


class OddsClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_mlb_odds(self) -> list[dict[str, Any]]:
        if not self.settings.odds_api_key:
            return []
        params = {
            "apiKey": self.settings.odds_api_key,
            "bookmakers": "fanduel,draftkings",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{BASE}/sports/baseball_mlb/odds", params=params)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def flatten_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        fetched_at = datetime.now(timezone.utc)
        for event in events:
            for book in event.get("bookmakers", []):
                book_key = book.get("key")
                if book_key not in {"fanduel", "draftkings"}:
                    continue
                for market in book.get("markets", []):
                    market_key = market.get("key")
                    for outcome in market.get("outcomes", []):
                        rows.append({
                            "provider_game_id": event.get("id"),
                            "commence_time": event.get("commence_time"),
                            "away_team": event.get("away_team"),
                            "home_team": event.get("home_team"),
                            "bookmaker": book_key,
                            "market": market_key,
                            "selection": outcome.get("name"),
                            "line": outcome.get("point"),
                            "price": int(outcome.get("price")),
                            "fetched_at": fetched_at,
                        })
        return rows
