from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Game, Projection, Quote, Recommendation
from ..parks import PARKS
from ..util import (
    american_profit_per_unit,
    american_to_implied,
    canonical_team,
    game_key,
    no_vig_probability,
)
from .mlb import MLBClient
from .model_engine import ModelEngine
from .odds import OddsClient
from .weather import WeatherClient


class Pipeline:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.odds = OddsClient()
        self.mlb = MLBClient()
        self.weather = WeatherClient()
        self.engine = ModelEngine()

    async def refresh(self, db: Session, force_official: bool = False) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        local_now = now.astimezone(ZoneInfo(self.settings.timezone))
        today = local_now.date()
        errors: list[str] = []
        try:
            schedule = await self.mlb.schedule(today - timedelta(days=7), today + timedelta(days=1))
        except Exception as exc:
            schedule = []
            errors.append(f"MLB schedule refresh failed: {exc}")

        try:
            odds_events = await self.odds.fetch_mlb_odds()
        except Exception as exc:
            odds_events = []
            errors.append(f"Odds refresh failed: {exc}")

        if not odds_events and self.settings.demo_mode:
            odds_events = self._demo_events(now)

        odds_rows = self.odds.flatten_events(odds_events)
        schedule_map = self._schedule_map(schedule)
        touched_games: set[str] = set()

        for event in odds_events:
            commence = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
            game_date = commence.astimezone(ZoneInfo(self.settings.timezone)).date()
            away = canonical_team(event["away_team"])
            home = canonical_team(event["home_team"])
            key = game_key(game_date, away, home)
            touched_games.add(key)
            mlb = schedule_map.get(key, {})
            venue, lat, lon, _ = PARKS.get(home, (mlb.get("venue"), None, None, 1.0))
            game = db.get(Game, key)
            if not game:
                game = Game(
                    id=key,
                    game_date=game_date,
                    commence_time=commence,
                    provider_game_id=event.get("id"),
                    away_team=away,
                    home_team=home,
                )
                db.add(game)
            game.commence_time = commence
            game.provider_game_id = event.get("id")
            game.mlb_game_pk = mlb.get("game_pk")
            game.away_team_id = mlb.get("away_team_id")
            game.home_team_id = mlb.get("home_team_id")
            game.away_pitcher = mlb.get("away_pitcher")
            game.home_pitcher = mlb.get("home_pitcher")
            game.away_pitcher_id = mlb.get("away_pitcher_id")
            game.home_pitcher_id = mlb.get("home_pitcher_id")
            game.venue = venue
            game.latitude = lat
            game.longitude = lon
            game.status = mlb.get("status", game.status)
            game.away_score = mlb.get("away_score")
            game.home_score = mlb.get("home_score")
            game.updated_at = now

        db.flush()

        for row in odds_rows:
            commence = datetime.fromisoformat(row["commence_time"].replace("Z", "+00:00"))
            key = game_key(commence.astimezone(ZoneInfo(self.settings.timezone)).date(), row["away_team"], row["home_team"])
            db.add(Quote(
                game_id=key,
                bookmaker=row["bookmaker"],
                market=row["market"],
                selection=canonical_team(row["selection"]) if row["market"] != "totals" else row["selection"],
                line=row["line"],
                price=row["price"],
                fetched_at=row["fetched_at"],
            ))

        # Also refresh final scores for prior official picks.
        for item in schedule:
            if not item.get("away_team") or not item.get("home_team"):
                continue
            commence = item.get("game_date")
            try:
                game_date = datetime.fromisoformat(commence.replace("Z", "+00:00")).astimezone(ZoneInfo(self.settings.timezone)).date()
            except Exception:
                continue
            key = game_key(game_date, item["away_team"], item["home_team"])
            game = db.get(Game, key)
            if game:
                game.status = item.get("status", game.status)
                game.away_score = item.get("away_score")
                game.home_score = item.get("home_score")
                game.mlb_game_pk = item.get("game_pk")
                game.updated_at = now

        db.commit()

        projections = 0
        candidates = 0
        for game_id in touched_games:
            game = db.get(Game, game_id)
            if not game:
                continue
            result = await self._project_and_recommend(db, game)
            projections += 1
            candidates += result

        db.commit()
        self.grade_pending(db)
        should_create_card = force_official or local_now.hour >= self.settings.daily_pick_hour_et
        official_created = self.create_official_card(db, today, force=force_official) if should_create_card else 0
        db.commit()
        return {
            "games": len(touched_games),
            "projections": projections,
            "candidates": candidates,
            "official_created": official_created,
            "demo_mode": not bool(self.settings.odds_api_key),
            "errors": errors,
            "refreshed_at": now.isoformat(),
        }

    async def _project_and_recommend(self, db: Session, game: Game) -> int:
        season = game.game_date.year
        away_team = await self.mlb.team_snapshot(game.away_team_id, season)
        home_team = await self.mlb.team_snapshot(game.home_team_id, season)
        away_pitcher = await self.mlb.pitcher_snapshot(game.away_pitcher_id, season)
        home_pitcher = await self.mlb.pitcher_snapshot(game.home_pitcher_id, season)
        weather = await self.weather.forecast_for(game.latitude, game.longitude, game.commence_time)
        game.weather_json = json.dumps(weather)

        latest = self._latest_quotes(db, game.id)
        market_home = self._consensus_h2h(latest, game.home_team, game.away_team)
        park_factor = PARKS.get(game.home_team, ("", 0, 0, 1.0))[3]
        projection = self.engine.project_game(
            away_team, home_team, away_pitcher, home_pitcher,
            weather, park_factor, market_home,
        )
        db.add(Projection(
            game_id=game.id,
            model_version=self.settings.model_version,
            away_runs=projection.away_runs,
            home_runs=projection.home_runs,
            away_win_prob=projection.away_win_prob,
            home_win_prob=projection.home_win_prob,
            data_quality=projection.quality,
            reasons_json=json.dumps(projection.reasons),
        ))

        grouped: dict[tuple[str, str, float | None], list[Quote]] = defaultdict(list)
        for quote in latest:
            grouped[(quote.market, quote.selection, quote.line)].append(quote)

        # Remove stale non-official candidate snapshots for this game before inserting the latest.
        stale = db.scalars(select(Recommendation).where(
            Recommendation.game_id == game.id,
            Recommendation.official.is_(False),
            Recommendation.status == "candidate",
        )).all()
        for item in stale:
            db.delete(item)

        count = 0
        for (market, selection, line), quotes in grouped.items():
            model_prob = self.engine.candidate_probability(
                market, selection, line, game.away_team, game.home_team, projection
            )
            if model_prob is None:
                continue

            opposite = self._find_opposite(grouped, market, selection, line, game)
            if not opposite:
                continue

            # Choose the best selected price, but use the matching book's opposite side for no-vig.
            selected_by_book = {q.bookmaker: q for q in quotes}
            opposite_by_book = {q.bookmaker: q for q in opposite}
            viable = []
            for book, selected_quote in selected_by_book.items():
                opp = opposite_by_book.get(book)
                if opp:
                    market_prob = no_vig_probability(selected_quote.price, opp.price)
                    eval_ = self.engine.evaluate(model_prob, market_prob, selected_quote.price, projection.quality)
                    viable.append((eval_["expected_value"], book, selected_quote, market_prob, eval_))
            if not viable:
                continue
            viable.sort(reverse=True, key=lambda x: x[0])
            _, book, selected_quote, market_prob, eval_ = viable[0]
            if eval_["units"] <= 0:
                continue

            explanation = projection.reasons + [
                f"No-vig market probability: {market_prob:.1%}",
                f"Model probability: {model_prob:.1%}",
                f"Edge: {eval_['edge']:.1%}; expected value: {eval_['expected_value']:.1%}.",
            ]
            db.add(Recommendation(
                pick_date=game.game_date,
                game_id=game.id,
                model_version=self.settings.model_version,
                market=market,
                selection=selection,
                line=line,
                bookmaker=book,
                odds=selected_quote.price,
                model_prob=model_prob,
                market_prob=market_prob,
                fair_odds=eval_["fair_odds"],
                edge=eval_["edge"],
                expected_value=eval_["expected_value"],
                units=eval_["units"],
                grade=eval_["grade"],
                data_quality=projection.quality,
                explanation_json=json.dumps(explanation),
                official=False,
                status="candidate",
            ))
            count += 1
        return count

    def create_official_card(self, db: Session, pick_date: date, force: bool = False) -> int:
        existing = db.scalar(select(Recommendation.id).where(
            Recommendation.pick_date == pick_date,
            Recommendation.official.is_(True),
        ).limit(1))
        if existing and not force:
            return 0

        if force:
            officials = db.scalars(select(Recommendation).where(
                Recommendation.pick_date == pick_date,
                Recommendation.official.is_(True),
                Recommendation.status == "pending",
            )).all()
            for item in officials:
                item.official = False
                item.status = "candidate"

        candidates = db.scalars(
            select(Recommendation)
            .where(
                Recommendation.pick_date == pick_date,
                Recommendation.official.is_(False),
                Recommendation.status == "candidate",
            )
            .order_by(desc(Recommendation.expected_value), desc(Recommendation.edge))
        ).all()

        # One official recommendation per game to reduce correlated exposure.
        chosen = []
        seen_games = set()
        exposure = 0.0
        for item in candidates:
            if item.game_id in seen_games:
                continue
            remaining = self.settings.max_daily_units - exposure
            if remaining <= 0:
                break
            item.units = min(item.units, remaining)
            if item.units <= 0:
                continue
            chosen.append(item)
            seen_games.add(item.game_id)
            exposure += item.units
            if len(chosen) >= self.settings.max_official_picks:
                break

        for item in chosen:
            item.official = True
            item.status = "pending"
        return len(chosen)

    def grade_pending(self, db: Session) -> int:
        pending = db.scalars(select(Recommendation).where(
            Recommendation.official.is_(True),
            Recommendation.status == "pending",
        )).all()
        graded = 0
        for pick in pending:
            game = db.get(Game, pick.game_id)
            if not game or game.away_score is None or game.home_score is None:
                continue
            if game.status not in {"final", "game over"}:
                continue

            result = self._settle(pick, game)
            if result is None:
                continue
            pick.result = result
            pick.status = "graded"
            pick.graded_at = datetime.now(timezone.utc)
            if result == "win":
                pick.profit_units = pick.units * american_profit_per_unit(pick.odds)
            elif result == "loss":
                pick.profit_units = -pick.units
            else:
                pick.profit_units = 0.0

            closing = self._closing_quote(db, pick, game.commence_time)
            if closing:
                pick.closing_odds = closing.price
                pick.clv = american_to_implied(closing.price) - american_to_implied(pick.odds)
            graded += 1
        db.commit()
        return graded

    @staticmethod
    def _settle(pick: Recommendation, game: Game) -> str | None:
        away, home = game.away_score, game.home_score
        if away is None or home is None:
            return None
        if pick.market == "h2h":
            winner = game.away_team if away > home else game.home_team
            return "win" if pick.selection == winner else "loss"
        if pick.market == "spreads" and pick.line is not None:
            score = away if pick.selection == game.away_team else home
            opp = home if pick.selection == game.away_team else away
            adjusted = score + pick.line
            return "win" if adjusted > opp else ("loss" if adjusted < opp else "push")
        if pick.market == "totals" and pick.line is not None:
            total = away + home
            if total == pick.line:
                return "push"
            if pick.selection.lower() == "over":
                return "win" if total > pick.line else "loss"
            return "win" if total < pick.line else "loss"
        return None

    def _latest_quotes(self, db: Session, game_id: str) -> list[Quote]:
        all_quotes = db.scalars(
            select(Quote).where(Quote.game_id == game_id).order_by(desc(Quote.fetched_at))
        ).all()
        latest: dict[tuple[str, str, str, float | None], Quote] = {}
        for q in all_quotes:
            key = (q.bookmaker, q.market, q.selection, q.line)
            if key not in latest:
                latest[key] = q
        return list(latest.values())

    @staticmethod
    def _consensus_h2h(quotes: list[Quote], home: str, away: str) -> float | None:
        by_book: dict[str, dict[str, Quote]] = defaultdict(dict)
        for q in quotes:
            if q.market == "h2h":
                by_book[q.bookmaker][q.selection] = q
        probs = []
        for sides in by_book.values():
            if home in sides and away in sides:
                probs.append(no_vig_probability(sides[home].price, sides[away].price))
        return sum(probs) / len(probs) if probs else None

    @staticmethod
    def _find_opposite(grouped, market, selection, line, game):
        if market == "h2h":
            opposite_selection = game.home_team if selection == game.away_team else game.away_team
            return grouped.get((market, opposite_selection, line))
        if market == "totals":
            opposite_selection = "Under" if selection.lower() == "over" else "Over"
            return grouped.get((market, opposite_selection, line))
        if market == "spreads" and line is not None:
            opposite_selection = game.home_team if selection == game.away_team else game.away_team
            return grouped.get((market, opposite_selection, -line))
        return None

    def _closing_quote(self, db: Session, pick: Recommendation, commence_time: datetime) -> Quote | None:
        return db.scalar(
            select(Quote)
            .where(
                Quote.game_id == pick.game_id,
                Quote.bookmaker == pick.bookmaker,
                Quote.market == pick.market,
                Quote.selection == pick.selection,
                Quote.line == pick.line,
                Quote.fetched_at <= commence_time,
            )
            .order_by(desc(Quote.fetched_at))
            .limit(1)
        )

    @staticmethod
    def _schedule_map(schedule: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        out = {}
        for item in schedule:
            try:
                dt = datetime.fromisoformat(item["game_date"].replace("Z", "+00:00"))
            except Exception:
                continue
            out[game_key(dt.astimezone(ZoneInfo(get_settings().timezone)).date(), item["away_team"], item["home_team"])] = item
        return out

    @staticmethod
    def _demo_events(now: datetime) -> list[dict[str, Any]]:
        # Clearly labeled interface demo; these are not live prices.
        games = [
            ("demo-1", "New York Yankees", "Boston Red Sox", 2),
            ("demo-2", "Los Angeles Dodgers", "San Diego Padres", 4),
            ("demo-3", "Chicago Cubs", "St. Louis Cardinals", 6),
        ]
        result = []
        for event_id, away, home, hours in games:
            commence = (now + timedelta(hours=hours)).isoformat().replace("+00:00", "Z")
            result.append({
                "id": event_id,
                "sport_key": "baseball_mlb",
                "commence_time": commence,
                "away_team": away,
                "home_team": home,
                "bookmakers": [
                    {
                        "key": "fanduel",
                        "markets": [
                            {"key": "h2h", "outcomes": [
                                {"name": away, "price": 115},
                                {"name": home, "price": -125},
                            ]},
                            {"key": "spreads", "outcomes": [
                                {"name": away, "price": -105, "point": 1.5},
                                {"name": home, "price": -115, "point": -1.5},
                            ]},
                            {"key": "totals", "outcomes": [
                                {"name": "Over", "price": -110, "point": 8.5},
                                {"name": "Under", "price": -110, "point": 8.5},
                            ]},
                        ],
                    },
                    {
                        "key": "draftkings",
                        "markets": [
                            {"key": "h2h", "outcomes": [
                                {"name": away, "price": 118},
                                {"name": home, "price": -128},
                            ]},
                            {"key": "spreads", "outcomes": [
                                {"name": away, "price": -108, "point": 1.5},
                                {"name": home, "price": -112, "point": -1.5},
                            ]},
                            {"key": "totals", "outcomes": [
                                {"name": "Over", "price": -105, "point": 8.5},
                                {"name": "Under", "price": -115, "point": 8.5},
                            ]},
                        ],
                    },
                ],
            })
        return result
