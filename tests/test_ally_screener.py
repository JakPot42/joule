import pytest

from ally_screener import screen_country


def test_screen_japan_high_vulnerability():
    r = screen_country("Japan", use_live=False)
    assert r.import_dependency_pct == pytest.approx(87.3)
    assert r.tier == "HIGH VULNERABILITY"
    assert 0 <= r.score <= 100


def test_screen_australia_net_exporter_low_vulnerability():
    r = screen_country("Australia", use_live=False)
    assert r.import_dependency_pct < 0
    assert r.tier == "LOW VULNERABILITY"
    assert r.score >= 0   # clamped, not negative despite negative input


def test_screen_unknown_country_raises():
    with pytest.raises(ValueError):
        screen_country("Atlantis", use_live=False)


def test_score_formula_matches_disclosed_weights():
    r = screen_country("Poland", use_live=False)
    import_clamped = max(0.0, min(100.0, r.import_dependency_pct))
    renewable_clamped = max(0.0, min(100.0, r.renewable_share_pct))
    expected = round(import_clamped * 0.70 + (100.0 - renewable_clamped) * 0.30, 1)
    assert r.score == expected
