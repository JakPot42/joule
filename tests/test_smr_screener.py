import pytest

from smr_screener import compute_module_fits, screen_installation


def test_screen_newport_returns_valid_result():
    r = screen_installation("naval station newport")
    assert r.display_name == "Naval Station Newport, RI"
    assert 0 <= r.total_score <= 100
    assert r.tier in {"PRIORITY FOR FURTHER STUDY", "WORTH INVESTIGATING", "LOWER PRIORITY"}
    assert r.grid_context is not None   # NE is a covered GridPulse region
    assert len(r.components) == 4       # seismic + population + demand + grid


def test_screen_kings_bay_excludes_grid_component():
    r = screen_installation("naval submarine base kings bay")
    assert r.grid_context is None       # GA isn't a covered GridPulse region
    assert len(r.components) == 3       # grid component genuinely excluded, not zeroed
    assert 0 <= r.total_score <= 100


def test_screen_unknown_installation_raises_with_helpful_message():
    with pytest.raises(ValueError, match="not in joule's installation roster"):
        screen_installation("nonexistent base")


def test_higher_seismic_hazard_scores_lower_component():
    newport = screen_installation("naval station newport")   # SDC A
    edwards = screen_installation("edwards air force base")  # SDC D
    newport_seismic = next(c for c in newport.components if "Seismic" in c.name)
    edwards_seismic = next(c for c in edwards.components if "Seismic" in c.name)
    assert newport_seismic.points > edwards_seismic.points


def test_module_fits_all_exceed_installation_demand():
    fits = compute_module_fits(installation_demand_mwh=100_000.0)
    assert len(fits) == 4   # BWRX-300 single unit + 3 VOYGR configs
    for f in fits:
        assert f.output_to_demand_ratio > 1.0   # every real config vastly exceeds a real installation's demand


def test_module_fits_sorted_ascending_by_capacity():
    fits = compute_module_fits(installation_demand_mwh=100_000.0)
    mwe_values = [f.total_mwe for f in fits]
    assert mwe_values == sorted(mwe_values)


def test_module_fits_zero_demand_does_not_crash():
    fits = compute_module_fits(installation_demand_mwh=0.0)
    assert all(f.output_to_demand_ratio == float("inf") for f in fits)
