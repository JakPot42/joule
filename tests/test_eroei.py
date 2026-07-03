import pytest

from eroei import get_eroei, list_sources


def test_list_sources_includes_known_keys():
    sources = list_sources()
    assert "nuclear" in sources
    assert "solar_pv_utility" in sources


def test_get_eroei_known_source():
    r = get_eroei("nuclear")
    assert r.eroi_low == 59
    assert r.eroi_high == 75
    assert "Weissbach" in r.citation
    assert r.installation_context is None


def test_get_eroei_unknown_source_raises():
    with pytest.raises(ValueError):
        get_eroei("cold fusion")


def test_get_eroei_with_installation_context():
    r = get_eroei("nuclear", "naval station newport")
    assert r.installation_context is not None
    assert "Naval Station Newport" in r.installation_context


def test_get_eroei_context_unknown_installation_raises():
    with pytest.raises(ValueError, match="not in joule's installation roster"):
        get_eroei("nuclear", "nonexistent base")


def test_source_key_normalizes_spaces_and_hyphens():
    a = get_eroei("natural_gas_ccgt")
    b = get_eroei("natural gas ccgt")
    assert a.eroi_low == b.eroi_low
