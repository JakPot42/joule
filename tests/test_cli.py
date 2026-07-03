from click.testing import CliRunner

from main import cli


def _run(*args):
    runner = CliRunner()
    return runner.invoke(cli, list(args))


def test_smr_command_runs_clean():
    result = _run("smr", "Naval Station Newport")
    assert result.exit_code == 0
    assert "SITING PRIORITY SCORE" in result.output


def test_smr_command_json_format():
    result = _run("smr", "Naval Station Newport", "--format", "json")
    assert result.exit_code == 0
    assert '"total_score"' in result.output


def test_smr_command_unknown_installation_exits_nonzero():
    result = _run("smr", "Nonexistent Base")
    assert result.exit_code != 0


def test_eroei_command_runs_clean():
    result = _run("eroei", "nuclear", "--context", "Naval Station Newport")
    assert result.exit_code == 0
    assert "EROI" in result.output


def test_ally_command_runs_clean():
    result = _run("ally", "Japan")
    assert result.exit_code == 0
    assert "VULNERABILITY SCORE" in result.output


def test_installations_command_lists_roster():
    result = _run("installations")
    assert result.exit_code == 0
    assert "Naval Station Newport" in result.output


def test_demo_command_runs_full_pipeline_clean():
    result = _run("demo")
    assert result.exit_code == 0
    assert "SITING PRIORITY SCORE" in result.output
    assert "VULNERABILITY SCORE" in result.output
