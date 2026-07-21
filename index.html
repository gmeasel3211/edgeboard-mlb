from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any

from ..config import get_settings
from ..util import (
    american_to_implied,
    expected_value,
    fractional_kelly,
    implied_to_american,
    no_vig_probability,
    normal_cdf,
)


@dataclass
class GameProjection:
    away_runs: float
    home_runs: float
    away_win_prob: float
    home_win_prob: float
    quality: int
    reasons: list[str]


class ModelEngine:
    LEAGUE_RA9 = 4.50
    FULL_GAME_DIFF_SD = 3.40
    FULL_GAME_TOTAL_SD = 3.10

    def __init__(self) -> None:
        self.settings = get_settings()

    def project_game(
        self,
        away_team: dict[str, Any],
        home_team: dict[str, Any],
        away_pitcher: dict[str, Any],
        home_pitcher: dict[str, Any],
        weather: dict[str, Any],
        park_factor: float,
        market_home_prob: float | None,
    ) -> GameProjection:
        away_strength = 0.60 * away_team["pythag"] + 0.40 * away_team["win_pct"]
        home_strength = 0.60 * home_team["pythag"] + 0.40 * home_team["win_pct"]

        # Log5-style independent win estimate with a modest home-field logit bump.
        a = min(max(away_strength, 0.15), 0.85)
        h = min(max(home_strength, 0.15), 0.85)
        away_logit = math.log(a / (1 - a))
        home_logit = math.log(h / (1 - h))
        independent_home = 1 / (1 + math.exp(-(home_logit - away_logit + 0.14)))

        # Starter adjustment: about 1.2 probability points per ERA run of net advantage.
        starter_delta = (away_pitcher["era"] - home_pitcher["era"]) * 0.012
        independent_home = min(max(independent_home + starter_delta, 0.20), 0.80)

        # Use offense/defense interaction to derive expected runs.
        away_base = math.sqrt(max(away_team["runs_for_game"], 2.0) * max(home_team["runs_against_game"], 2.0))
        home_base = math.sqrt(max(home_team["runs_for_game"], 2.0) * max(away_team["runs_against_game"], 2.0))

        away_sp_factor = 0.70 + 0.30 * (home_pitcher["era"] / self.LEAGUE_RA9)
        home_sp_factor = 0.70 + 0.30 * (away_pitcher["era"] / self.LEAGUE_RA9)
        environment = park_factor * weather["run_factor"]

        away_runs = max(1.5, away_base * away_sp_factor * environment)
        home_runs = max(1.5, home_base * home_sp_factor * environment + 0.12)

        run_diff_home = home_runs - away_runs
        run_based_home = 1 - normal_cdf(0, run_diff_home, self.FULL_GAME_DIFF_SD)
        independent_home = 0.55 * independent_home + 0.45 * run_based_home

        # Market anchoring stabilizes the MVP and reduces overconfidence.
        if market_home_prob is not None:
            home_prob = 0.65 * independent_home + 0.35 * market_home_prob
        else:
            home_prob = independent_home
        home_prob = min(max(home_prob, 0.15), 0.85)

        qualities = [
            away_team.get("quality", 45),
            home_team.get("quality", 45),
            away_pitcher.get("quality", 45),
            home_pitcher.get("quality", 45),
            weather.get("quality", 45),
            85 if market_home_prob is not None else 45,
        ]
        quality = round(sum(qualities) / len(qualities))
        reasons = [
            f"Independent home win estimate: {independent_home:.1%}",
            f"Projected score: away {away_runs:.2f}, home {home_runs:.2f}",
            f"Starter ERAs: away {away_pitcher['era']:.2f}, home {home_pitcher['era']:.2f}",
            f"Weather/park run factor: {environment:.3f}",
            "Model uses a 35% no-vig market anchor to limit overconfidence." if market_home_prob is not None else "No market anchor was available.",
        ]
        return GameProjection(
            away_runs=away_runs,
            home_runs=home_runs,
            away_win_prob=1 - home_prob,
            home_win_prob=home_prob,
            quality=quality,
            reasons=reasons,
        )

    def candidate_probability(
        self,
        market: str,
        selection: str,
        line: float | None,
        away_team: str,
        home_team: str,
        projection: GameProjection,
    ) -> float | None:
        if market == "h2h":
            return projection.away_win_prob if selection == away_team else projection.home_win_prob
        if market == "spreads" and line is not None:
            home_diff = projection.home_runs - projection.away_runs
            if selection == away_team:
                return normal_cdf(line, home_diff, self.FULL_GAME_DIFF_SD)
            return 1 - normal_cdf(-line, home_diff, self.FULL_GAME_DIFF_SD)
        if market == "totals" and line is not None:
            total = projection.away_runs + projection.home_runs
            if selection.lower() == "over":
                return 1 - normal_cdf(line, total, self.FULL_GAME_TOTAL_SD)
            if selection.lower() == "under":
                return normal_cdf(line, total, self.FULL_GAME_TOTAL_SD)
        return None

    def evaluate(
        self,
        model_prob: float,
        market_prob: float,
        odds: int,
        quality: int,
    ) -> dict[str, Any]:
        edge = model_prob - market_prob
        ev = expected_value(model_prob, odds)
        kelly = fractional_kelly(model_prob, odds, self.settings.kelly_fraction)
        quality_scale = min(max(quality / 100, 0.0), 1.0)
        units = min(self.settings.max_bet_units, kelly / max(self.settings.unit_percent, 0.001))
        units = round(units * quality_scale, 2)
        if edge < self.settings.min_edge or ev < self.settings.min_ev or quality < self.settings.min_data_quality:
            units = 0.0

        if ev >= 0.08 and quality >= 80:
            grade = "A+"
        elif ev >= 0.06 and quality >= 75:
            grade = "A"
        elif ev >= 0.04 and quality >= 70:
            grade = "B+"
        elif ev >= 0.025 and quality >= self.settings.min_data_quality:
            grade = "B"
        else:
            grade = "Pass"

        return {
            "fair_odds": implied_to_american(model_prob),
            "edge": edge,
            "expected_value": ev,
            "units": units,
            "grade": grade,
        }
