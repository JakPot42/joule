import pytest

from seismicity import fetch_live, get_seismic_design


def test_cached_fallback_matches_known_values():
    r = get_seismic_design("naval station newport", 41.53, -71.31, use_live=False)
    assert r.sdc == "A"
    assert r.pga_m == pytest.approx(0.11)
    assert "cached" in r.source


def test_unknown_installation_without_live_raises():
    with pytest.raises(ValueError):
        get_seismic_design("nonexistent base", 0.0, 0.0, use_live=False)


def test_live_fetch_returns_valid_sdc():
    r = fetch_live(41.53, -71.31)
    assert r.sdc in {"A", "B", "C", "D", "E", "F"}
    assert r.pga_m >= 0
    assert "live" in r.source


def test_live_fetch_used_when_available():
    r = get_seismic_design("naval station newport", 41.53, -71.31, use_live=True)
    assert r.sdc == "A"
    assert "live" in r.source
