from gridpulse_bridge import get_grid_context, load_export


def test_load_export_reads_bundled_sample():
    data = load_export()
    assert "NE" in data
    assert "stress_score" in data["NE"]


def test_get_grid_context_none_region_returns_none():
    assert get_grid_context(None) is None


def test_get_grid_context_missing_file_returns_none():
    assert get_grid_context("NE", export_path="does_not_exist.json") is None


def test_get_grid_context_returns_valid_context_for_covered_region():
    ctx = get_grid_context("NE")
    assert ctx is not None
    assert ctx.region == "NE"
    assert ctx.tier in {"LOW", "ELEVATED", "HIGH", "CRITICAL"}


def test_get_grid_context_returns_none_for_uncovered_region():
    assert get_grid_context("SE") is None
