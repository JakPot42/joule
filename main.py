"""joule: DoD Energy Resilience Intelligence Tool CLI.

Every number cites a specific real, public document -- see
config.SCOPE_DISCLAIMER, printed on every command, and README "Data
sourcing" for the full citation list.
"""
from __future__ import annotations

import os
import sys

import click

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import dashboard
from ally_screener import screen_country
from brief import generate_ally_brief, generate_smr_brief
from dashboard import console
from eroei import get_eroei, list_sources
from smr_screener import screen_installation


@click.group()
def cli() -> None:
    """joule: DoD Energy Resilience Intelligence Tool.

    \b
    Three modules: `smr` (DoD Installation SMR Suitability Screener),
    `eroei` (Installation EROEI calculator), `ally` (Allied Nation Energy
    Vulnerability Screener). Every data point cites a specific real, public
    source -- see the Scope panel and README.
    """


@cli.command()
@click.argument("installation")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
@click.option("--no-live", is_flag=True, default=False, help="Use cached data only, skip live USGS/GridPulse calls.")
def smr(installation: str, fmt: str, no_live: bool) -> None:
    """DoD Installation SMR Siting Priority Screen.

    \b
    Example: joule smr "Naval Station Newport"
    """
    try:
        result = screen_installation(installation, use_live=not no_live)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1)

    brief_text = generate_smr_brief(result)

    if fmt == "json":
        dashboard.print_json({
            "installation": result.display_name,
            "total_score": result.total_score,
            "tier": result.tier,
            "components": [{"name": c.name, "points": c.points, "max_points": c.max_points, "basis": c.basis} for c in result.components],
            "seismic": {"sdc": result.seismic.sdc, "pga_m": result.seismic.pga_m, "source": result.seismic.source},
            "installation_demand_mwh": result.installation_demand_mwh,
            "brief": brief_text,
        })
        return

    dashboard.print_banner()
    dashboard.print_smr_result(result)
    dashboard.print_brief(brief_text)
    if config.DEMO_MODE:
        console.print("[dim]DEMO_MODE=True -- brief uses a deterministic template, not a live Claude call.[/dim]")


@cli.command()
@click.argument("source")
@click.option("--context", "context_installation", default=None, help="Installation to contextualize against (e.g. 'Naval Station Newport').")
def eroei(source: str, context_installation: str | None) -> None:
    """Installation EROEI (Energy Return on Energy Invested) lookup.

    \b
    Example: joule eroei nuclear --context "Naval Station Newport"
    """
    try:
        result = get_eroei(source, context_installation)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1)

    dashboard.print_banner()
    dashboard.print_eroei_result(result)


@cli.command()
def eroei_sources() -> None:
    """List available EROEI source keys."""
    dashboard.print_banner()
    console.print("Available sources: " + ", ".join(list_sources()))


@cli.command()
@click.argument("country")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
@click.option("--no-live", is_flag=True, default=False, help="Use cached data only, skip live World Bank calls.")
def ally(country: str, fmt: str, no_live: bool) -> None:
    """Allied Nation Energy Vulnerability Screener.

    \b
    Example: joule ally Japan
    """
    try:
        result = screen_country(country, use_live=not no_live)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1)

    brief_text = generate_ally_brief(result)

    if fmt == "json":
        dashboard.print_json({
            "country": result.country,
            "score": result.score,
            "tier": result.tier,
            "import_dependency_pct": result.import_dependency_pct,
            "import_year": result.import_year,
            "renewable_share_pct": result.renewable_share_pct,
            "renewable_year": result.renewable_year,
            "brief": brief_text,
        })
        return

    dashboard.print_banner()
    dashboard.print_ally_result(result)
    dashboard.print_brief(brief_text)


@cli.command()
def installations() -> None:
    """List joule's supported installation roster."""
    dashboard.print_banner()
    console.rule("[bold]Supported Installations[/bold]")
    for key, inst in config.INSTALLATIONS.items():
        console.print(f"  {inst['display_name']}  [dim](key: '{key}')[/dim]")


@cli.command()
def demo() -> None:
    """Run all three modules against the flagship demo case (Naval Station
    Newport, Japan) -- bundled/cached data, no API key or network needed
    beyond the live USGS/World Bank calls (auto-fallback to cache if
    offline)."""
    dashboard.print_banner()

    console.rule("[bold]Demo 1: SMR Siting Screen -- Naval Station Newport[/bold]")
    smr_result = screen_installation("naval station newport")
    dashboard.print_smr_result(smr_result)
    dashboard.print_brief(generate_smr_brief(smr_result))

    console.rule("[bold]Demo 2: EROEI -- Nuclear, contextualized to Naval Station Newport[/bold]")
    eroei_result = get_eroei("nuclear", "naval station newport")
    dashboard.print_eroei_result(eroei_result)

    console.rule("[bold]Demo 3: Allied Nation Vulnerability -- Japan[/bold]")
    ally_result = screen_country("Japan")
    dashboard.print_ally_result(ally_result)
    dashboard.print_brief(generate_ally_brief(ally_result))

    console.print("[dim]All demo output cites real sources -- see README. DEMO_MODE=True uses deterministic brief templates.[/dim]")


if __name__ == "__main__":
    cli()
