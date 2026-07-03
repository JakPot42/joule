import config
from ally_screener import screen_country
from brief import generate_ally_brief, generate_smr_brief
from smr_screener import screen_installation


def test_smr_brief_demo_mode_deterministic_template():
    r = screen_installation("naval station newport", use_live=False)
    text = generate_smr_brief(r)
    assert "SITING PRIORITY SCORE" in text
    assert config.SCOPE_DISCLAIMER in text
    assert "grid-export resource" in text


def test_ally_brief_demo_mode_deterministic_template():
    r = screen_country("Japan", use_live=False)
    text = generate_ally_brief(r)
    assert "VULNERABILITY SCORE" in text
    assert config.SCOPE_DISCLAIMER in text


def test_smr_brief_falls_back_to_template_when_claude_call_fails(monkeypatch):
    monkeypatch.setattr(config, "DEMO_MODE", False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = screen_installation("naval station newport", use_live=False)
    text = generate_smr_brief(r)
    assert "SITING PRIORITY SCORE" in text   # fell back to the template, didn't crash


def test_ally_brief_falls_back_to_template_when_claude_call_fails(monkeypatch):
    monkeypatch.setattr(config, "DEMO_MODE", False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = screen_country("Japan", use_live=False)
    text = generate_ally_brief(r)
    assert "VULNERABILITY SCORE" in text
