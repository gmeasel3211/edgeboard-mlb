from app.services.model_engine import ModelEngine
from app.util import expected_value, no_vig_probability


def test_no_vig_probability():
    p = no_vig_probability(-110, -110)
    assert abs(p - 0.5) < 1e-9


def test_positive_ev():
    assert expected_value(0.55, -110) > 0


def test_projection_probabilities_sum_to_one():
    engine = ModelEngine()
    team = {
        "pythag": 0.52, "win_pct": 0.52, "runs_for_game": 4.7,
        "runs_against_game": 4.4, "quality": 75,
    }
    pitcher = {"era": 4.1, "quality": 75}
    weather = {"run_factor": 1.0, "quality": 75}
    p = engine.project_game(team, team, pitcher, pitcher, weather, 1.0, 0.53)
    assert abs(p.home_win_prob + p.away_win_prob - 1.0) < 1e-9
    assert 0 < p.away_runs < 15
    assert 0 < p.home_runs < 15
