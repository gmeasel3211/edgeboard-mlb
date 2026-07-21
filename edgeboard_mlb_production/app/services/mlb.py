from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import httpx

BASE = "https://statsapi.mlb.com/api"


class MLBClient:
    def __init__(self) -> None:
        self._team_cache: dict[tuple[int, int], dict[str, Any]] = {}
        self._pitcher_cache: dict[tuple[int, int], dict[str, Any]] = {}

    async def schedule(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        params = {
            "sportId": 1,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "hydrate": "probablePitcher,venue,linescore",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{BASE}/v1/schedule", params=params)
            response.raise_for_status()
            payload = response.json()

        games: list[dict[str, Any]] = []
        for day in payload.get("dates", []):
            for g in day.get("games", []):
                teams = g.get("teams", {})
                away = teams.get("away", {})
                home = teams.get("home", {})
                games.append({
                    "game_pk": str(g.get("gamePk")),
                    "game_date": g.get("gameDate"),
                    "status": g.get("status", {}).get("abstractGameState", "Preview").lower(),
                    "away_team": away.get("team", {}).get("name"),
                    "home_team": home.get("team", {}).get("name"),
                    "away_team_id": away.get("team", {}).get("id"),
                    "home_team_id": home.get("team", {}).get("id"),
                    "away_pitcher": away.get("probablePitcher", {}).get("fullName"),
                    "home_pitcher": home.get("probablePitcher", {}).get("fullName"),
                    "away_pitcher_id": away.get("probablePitcher", {}).get("id"),
                    "home_pitcher_id": home.get("probablePitcher", {}).get("id"),
                    "away_score": away.get("score"),
                    "home_score": home.get("score"),
                    "venue": g.get("venue", {}).get("name"),
                })
        return games

    async def team_snapshot(self, team_id: int | None, season: int) -> dict[str, Any]:
        if not team_id:
            return self._neutral_team()
        key = (team_id, season)
        if key in self._team_cache:
            return self._team_cache[key]

        # Standings contains enough stable information for the MVP's team-strength layer.
        params = {
            "leagueId": "103,104",
            "season": season,
            "standingsTypes": "regularSeason",
            "hydrate": "team",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{BASE}/v1/standings", params=params)
                response.raise_for_status()
                payload = response.json()
            for record_group in payload.get("records", []):
                for rec in record_group.get("teamRecords", []):
                    if rec.get("team", {}).get("id") == team_id:
                        league = rec.get("leagueRecord", {})
                        runs_scored = rec.get("runsScored")
                        runs_allowed = rec.get("runsAllowed")
                        snapshot = {
                            "wins": int(league.get("wins", 0)),
                            "losses": int(league.get("losses", 0)),
                            "runs_scored": float(runs_scored) if runs_scored is not None else None,
                            "runs_allowed": float(runs_allowed) if runs_allowed is not None else None,
                        }
                        self._team_cache[key] = self._finish_team(snapshot)
                        return self._team_cache[key]
        except Exception:
            pass

        neutral = self._neutral_team()
        self._team_cache[key] = neutral
        return neutral

    async def pitcher_snapshot(self, person_id: int | None, season: int) -> dict[str, Any]:
        if not person_id:
            return {"era": 4.50, "whip": 1.30, "innings": 0.0, "quality": 45}
        key = (person_id, season)
        if key in self._pitcher_cache:
            return self._pitcher_cache[key]
        params = {"stats": "season", "group": "pitching", "season": season}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{BASE}/v1/people/{person_id}/stats", params=params)
                response.raise_for_status()
                payload = response.json()
            split = payload.get("stats", [{}])[0].get("splits", [{}])[0]
            stat = split.get("stat", {})
            result = {
                "era": float(stat.get("era", 4.50)),
                "whip": float(stat.get("whip", 1.30)),
                "innings": float(stat.get("inningsPitched", 0.0)),
                "quality": 75 if float(stat.get("inningsPitched", 0.0)) >= 30 else 58,
            }
        except Exception:
            result = {"era": 4.50, "whip": 1.30, "innings": 0.0, "quality": 45}
        self._pitcher_cache[key] = result
        return result

    @staticmethod
    def _neutral_team() -> dict[str, Any]:
        return {
            "wins": 0, "losses": 0, "runs_scored": None, "runs_allowed": None,
            "win_pct": 0.5, "pythag": 0.5, "runs_for_game": 4.5,
            "runs_against_game": 4.5, "quality": 45,
        }

    @staticmethod
    def _finish_team(snapshot: dict[str, Any]) -> dict[str, Any]:
        games = snapshot["wins"] + snapshot["losses"]
        win_pct = snapshot["wins"] / games if games else 0.5
        rs = snapshot["runs_scored"]
        ra = snapshot["runs_allowed"]
        if rs is not None and ra is not None and rs + ra > 0 and games:
            exponent = 1.83
            pythag = (rs ** exponent) / ((rs ** exponent) + (ra ** exponent))
            rfg = rs / games
            rag = ra / games
            quality = 78 if games >= 30 else 62
        else:
            pythag, rfg, rag, quality = win_pct, 4.5, 4.5, 55
        return {
            **snapshot,
            "win_pct": win_pct,
            "pythag": pythag,
            "runs_for_game": rfg,
            "runs_against_game": rag,
            "quality": quality,
        }
