from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from ..config import get_settings
from ..util import expected_value, fractional_kelly, implied_to_american, normal_cdf


@dataclass
class GameProjection:
    away_runs: float
    home_runs: float
    away_win_prob: float
    home_win_prob: float
    quality: int
    reasons: list[str]
    confidence: float = 0.0
    disagreement: float = 0.0


class ModelEngine:
    """Hybrid MLB projection and betting evaluation engine."""

    LEAGUE_RA9 = 4.50
    FULL_GAME_DIFF_SD = 3.40
    FULL_GAME_TOTAL_SD = 3.10

    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return min(max(value, low), high)

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
        away_strength = 0.55 * away_team["pythag"] + 0.45 * away_team["win_pct"]
        home_strength = 0.55 * home_team["pythag"] + 0.45 * home_team["win_pct"]

        a = self._clamp(away_strength, 0.15, 0.85)
        h = self._clamp(home_strength, 0.15, 0.85)
        away_logit = math.log(a / (1 - a))
        home_logit = math.log(h / (1 - h))
        team_home_prob = 1 / (1 + math.exp(-(home_logit - away_logit + 0.14)))

        away_era = float(away_pitcher.get("era", self.LEAGUE_RA9))
        home_era = float(home_pitcher.get("era", self.LEAGUE_RA9))
        away_whip = float(away_pitcher.get("whip", 1.30))
        home_whip = float(home_pitcher.get("whip", 1.30))

        starter_home_prob = self._clamp(
            team_home_prob
            + (away_era - home_era) * 0.012
            + (away_whip - home_whip) * 0.035,
            0.18,
            0.82,
        )

        away_base = math.sqrt(
            max(float(away_team["runs_for_game"]), 2.0)
            * max(float(home_team["runs_against_game"]), 2.0)
        )
        home_base = math.sqrt(
            max(float(home_team["runs_for_game"]), 2.0)
            * max(float(away_team["runs_against_game"]), 2.0)
        )

        away_sp_factor = 0.68 + 0.32 * (home_era / self.LEAGUE_RA9)
        home_sp_factor = 0.68 + 0.32 * (away_era / self.LEAGUE_RA9)
        away_whip_factor = self._clamp(0.84 + 0.12 * home_whip, 0.90, 1.10)
        home_whip_factor = self._clamp(0.84 + 0.12 * away_whip, 0.90, 1.10)

        environment = self._clamp(
            park_factor * float(weather.get("run_factor", 1.0)),
            0.82,
            1.22,
        )

        away_runs = max(1.5, away_base * away_sp_factor * away_whip_factor * environment)
        home_runs = max(
            1.5,
            home_base * home_sp_factor * home_whip_factor * environment + 0.12,
        )

        run_diff_home = home_runs - away_runs
        run_based_home = 1 - normal_cdf(0, run_diff_home, self.FULL_GAME_DIFF_SD)
        independent_home = 0.52 * starter_home_prob + 0.48 * run_based_home

        disagreement = 0.0
        if market_home_prob is not None:
            disagreement = abs(independent_home - market_home_prob)
            source_quality = sum([
                away_team.get("quality", 45),
                home_team.get("quality", 45),
                away_pitcher.get("quality", 45),
                home_pitcher.get("quality", 45),
                weather.get("quality", 45),
            ]) / 5
            market_weight = self._clamp(
                0.42 - (source_quality - 60) * 0.003,
                0.22,
                0.42,
            )
            home_prob = (
                (1 - market_weight) * independent_home
                + market_weight * market_home_prob
            )
        else:
            home_prob = independent_home

        home_prob = self._clamp(home_prob, 0.15, 0.85)

        qualities = [
            away_team.get("quality", 45),
            home_team.get("quality", 45),
            away_pitcher.get("quality", 45),
            home_pitcher.get("quality", 45),
            weather.get("quality", 45),
            85 if market_home_prob is not None else 45,
        ]
        base_quality = sum(qualities) / len(qualities)
        quality = round(
            self._clamp(base_quality - min(disagreement * 120, 12.0), 0, 100)
        )

        confidence = self._clamp(
            0.50 * (quality / 100)
            + 0.30 * min(abs(home_prob - 0.5) / 0.20, 1.0)
            + 0.20 * (1 - min(disagreement / 0.12, 1.0)),
            0.0,
            1.0,
        )

        reasons = [
            f"Hybrid independent home estimate: {independent_home:.1%}",
            f"Projected score: away {away_runs:.2f}, home {home_runs:.2f}",
            (
                f"Starter comparison: away {away_era:.2f} ERA/{away_whip:.2f} WHIP; "
                f"home {home_era:.2f} ERA/{home_whip:.2f} WHIP"
            ),
            f"Weather and park run factor: {environment:.3f}",
            f"Hybrid data quality: {quality}/100; confidence: {confidence:.0%}",
        ]
        if market_home_prob is not None:
            reasons.append(
                f"No-vig market anchor: {market_home_prob:.1%}; "
                f"model-market disagreement: {disagreement:.1%}."
            )
        else:
            reasons.append("No market anchor was available; uncertainty was increased.")

        return GameProjection(
            away_runs=away_runs,
            home_runs=home_runs,
            away_win_prob=1 - home_prob,
            home_win_prob=home_prob,
            quality=quality,
            reasons=reasons,
            confidence=confidence,
            disagreement=disagreement,
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
            return (
                projection.away_win_prob
                if selection == away_team
                else projection.home_win_prob
            )
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
        raw_kelly = fractional_kelly(
            model_prob,
            odds,
            self.settings.kelly_fraction,
        )

        quality_scale = self._clamp(quality / 100, 0.0, 1.0)
        edge_scale = self._clamp(edge / 0.08, 0.0, 1.0)
        ev_scale = self._clamp(ev / 0.10, 0.0, 1.0)
        disagreement = abs(model_prob - market_prob)

        if -180 <= odds <= 160:
            price_scale = 1.0
        elif -220 <= odds <= 220:
            price_scale = 0.78
        else:
            price_scale = 0.52

        hybrid_score = 100 * (
            0.34 * ev_scale
            + 0.27 * edge_scale
            + 0.24 * quality_scale
            + 0.15 * price_scale
        )

        units = min(
            self.settings.max_bet_units,
            raw_kelly / max(self.settings.unit_percent, 0.001),
        )
        units *= (
            quality_scale
            * price_scale
            * self._clamp(hybrid_score / 80, 0.45, 1.0)
        )
        units = round(units, 2)

        passes = (
            edge >= self.settings.min_edge
            and ev >= self.settings.min_ev
            and quality >= self.settings.min_data_quality
            and hybrid_score >= self.settings.min_hybrid_score
            and -250 <= odds <= 300
            and disagreement <= self.settings.max_model_market_disagreement
        )
        if not passes:
            units = 0.0

        if hybrid_score >= 82 and ev >= 0.075 and quality >= 78:
            grade = "A+"
        elif hybrid_score >= 74 and ev >= 0.055 and quality >= 74:
            grade = "A"
        elif hybrid_score >= 66 and ev >= 0.04 and quality >= 70:
            grade = "B+"
        elif passes:
            grade = "B"
        else:
            grade = "Pass"

        return {
            "fair_odds": implied_to_american(model_prob),
            "edge": edge,
            "expected_value": ev,
            "units": units,
            "grade": grade,
            "hybrid_score": round(hybrid_score, 1),
        }
