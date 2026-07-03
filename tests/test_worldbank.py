import pytest

from worldbank import IND_ENERGY_IMPORTS, IND_RENEWABLE_SHARE, get_indicator, resolve_iso3


def test_resolve_iso3_alias():
    assert resolve_iso3("Japan") == "JPN"
    assert resolve_iso3("south korea") == "KOR"


def test_resolve_iso3_passthrough_code():
    assert resolve_iso3("pol") == "POL"


def test_resolve_iso3_unknown_raises():
    with pytest.raises(ValueError):
        resolve_iso3("Atlantis")


def test_cached_fallback_matches_known_value():
    r = get_indicator("Poland", IND_ENERGY_IMPORTS, use_live=False)
    assert r.value == pytest.approx(48.8)
    assert r.year == 2023
    assert "cached" in r.source


def test_live_fetch_returns_plausible_value():
    r = get_indicator("Poland", IND_ENERGY_IMPORTS, use_live=True)
    assert "live" in r.source
    assert -300 < r.value < 300  # plausible range for a % indicator (net exporters go negative)


def test_negative_import_dependency_is_a_real_case_not_an_error():
    r = get_indicator("Australia", IND_ENERGY_IMPORTS, use_live=False)
    assert r.value < 0
