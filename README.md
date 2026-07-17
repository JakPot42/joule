# joule — DoD Energy Resilience Intelligence Tool

## Scope

Three CLI modules. Every number cites a specific real, public document —
DoD energy reports, live USGS/World Bank APIs, or published vendor/NRC/DOE
specs. Where a figure is dated, or is a disclosed estimate rather than a
live current value, that is stated explicitly in the output, not hidden.
**This tool does not make a siting recommendation or regulatory
determination** — it produces a screening priority score for further
engineering/regulatory review (`config.SCOPE_DISCLAIMER`, printed on
every command).

```
joule smr <installation>              # DoD Installation SMR Siting Priority Screen
joule eroei <source> --context <installation>   # Installation EROEI calculator
joule ally <country>                  # Allied Nation Energy Vulnerability Screener
joule installations                   # list the supported installation roster
joule demo                            # all three modules, flagship demo case
```

**Flagship demo:** `joule smr "Naval Station Newport"` — local to where
this was built, real, and ties directly into the NUWC-focused projects (the
Undersea Acoustic Intelligence Suite and the Cable Resilience Analyzer). Naval Station
Newport scores **84.4/100 — PRIORITY FOR FURTHER STUDY**: SDC A (lowest
USGS seismic hazard category), a real 25,163-person nearest population
center, and — via the GridPulse bridge — a real HIGH grid-stress
reading for the New England region.

---

## Data sourcing — the real research sprint behind every number

**The one real finding that shaped this build:** DoD's *current-format*
public energy reporting (the Annual Energy Performance, Resilience, and
Readiness Report, FY2018–present) publishes only DoD-wide and
service-level aggregates (e.g. "203,531 BBtu installation energy in
FY22") — **no per-installation breakdown**. Checked directly against the
actual FY22 AEPRR PDF (129 pages, searched programmatically) before
assuming otherwise: zero mentions of any specific installation by name,
zero MWh/kWh figures. The last public per-installation breakdown found
was the **FY2014 Annual Energy Management Report, Appendix E** — real,
specific, per-base total site delivered energy (BBtu), gross square
footage, and energy intensity (BTU/SF), for every DoD installation. That
is what this tool uses, dated and disclosed as FY2014 rather than
silently presented as current. This is the same "verify before building
on it" discipline the rest of this portfolio has hit repeatedly —
here the check confirmed a real reporting gap rather than resolving one.

**Installation roster (4, chosen because FY2014 Appendix E has real data
for each):**

| Installation | FY2014 total site energy | Nearest population center (2020 Census) | USGS SDC |
|---|---|---|---|
| Naval Station Newport, RI | 626 BBtu (183,463 MWh-eq/yr) | Newport, RI — 25,163 | **A** |
| Naval Submarine Base Kings Bay, GA | 687 BBtu (201,340 MWh-eq/yr) | Kingsland, GA — 18,337 | B |
| Edwards AFB, CA | 743 BBtu (217,752 MWh-eq/yr) | Lancaster, CA — 173,516 | D |
| Travis AFB, CA | 447 BBtu (130,983 MWh-eq/yr) | Fairfield, CA — 119,881 | D |

That FY2014 BBtu figure is **total site delivered energy across all
fuels** (electricity + natural gas + other) — not an electricity-only
figure. No public per-installation electricity-only split was found
either; this is disclosed in every score's basis line, not silently
treated as electricity demand.

**SMR designs — real, published specs:**
- **NuScale VOYGR**: 77 MWe/module (NRC-approved uprated design, May 30,
  2025); VOYGR-4/6/12 = 308/462/924 MWe. EPZ claim: site boundary only
  (NRC ACRS-concurred methodology, 2022 — final EPZ size is still a
  site-specific NRC determination). Source: DOE energy.gov, NuScale press
  releases.
- **GE-Hitachi BWRX-300**: 300 MWe net / 870 MWt, single-unit design.
  Power block footprint 430ft×200ft, 6.7-acre protected area. EPZ claim:
  1,000 m from site boundary. Source: GE Vernova "BWRX-300 General
  Description" (005N9751 Rev).

**Live APIs — both confirmed working with no authentication during this
build:**
- **USGS Design Ground Motions** (`earthquake.usgs.gov/ws/designmaps`) —
  real ASCE 7-22 Seismic Design Category (A–F) for any lat/lon. Used
  live by default; a cached snapshot of each roster installation's exact
  live response (fetched during this build) is the fallback.
- **World Bank Open Data** (`api.worldbank.org`) — `EG.IMP.CONS.ZS`
  (energy imports, % of energy use) and `EG.FEC.RNEW.ZS` (renewable
  share). Used live by default for `joule ally`; cached fallback for 6
  countries (Japan, Poland, Philippines, South Korea, Germany, Australia)
  fetched live during this build. Census Bureau's API now requires a key
  (recent change — checked directly, not assumed); population figures
  instead cite specific 2020 Decennial Census QuickFacts values directly.

**EROEI table** — World Nuclear Association's "Energy Return on
Investment" compilation (aggregating Weissbach et al. 2013 and Gagnon et
al. 2002), cross-checked against NREL's own PV EROEI publication for
solar specifically. **Diesel/liquid-fuel generators are deliberately
excluded** — no EROEI figure for them exists in DoD literature (fully
burdened cost of fuel / logistics-tail metrics are the standard DoD
framing instead); omitted rather than estimated.

---

## GridPulse integration

`gridpulse_bridge.py` reads GridPulse's real `to_joule_format()` export —
loose file-based coupling between two separate repos, not a cross-repo
Python import. `data/gridpulse_export_sample.json`
was generated by actually running `python main.py export --format json`
in the gridpulse repo, not fabricated. Only 2 of joule's 4 installations
fall in a GridPulse-covered region (NE for Newport, CAL for Edwards/Travis);
Georgia isn't one of GridPulse's 6 regions, so Kings Bay's score is
**genuinely computed over 3 components instead of 4** (rescaled to 100,
not silently zeroed) — see `smr_screener.py`'s docstring.

---

## SMR Siting Priority Score — the formula, in full

Four disclosed, weighted components (max 100 when all are available):

1. **Seismic siting fitness (0–35)** — live USGS Seismic Design Category:
   A→35, B→28, C→18, D→8, E→3, F→0.
2. **Regional grid resilience value (0–30, when covered)** — GridPulse
   stress tier: LOW→5, ELEVATED→15, HIGH→25, CRITICAL→30.
3. **Population-proximity siting simplicity (0–20)** — nearest 2020
   Census population: <20k→20, 20–50k→15, 50–150k→10, ≥150k→5.
4. **Installation energy-demand magnitude (0–15)** — FY2014 BBtu scaled
   against a fixed 1,000-BBtu reference band (so the score doesn't shift
   if more installations are added later).

**The real, honest finding this scoring surfaced:** every SMR
configuration considered — even a single 77 MWe NuScale module — produces
**13×–41× more energy per year** than any one of these installations'
entire FY2014 site energy demand (at a disclosed 92% capacity factor,
the U.S. nuclear fleet's typical EIA-reported average). Demand-matching
isn't a real differentiator at the single-installation scale; the
genuine siting question is seismic/regulatory/land fit and regional grid
value, and that's what the score actually measures. `joule smr` states
this directly in every brief rather than manufacturing an artificial
"right-sized" framing.

---

## Honest limitations

- **FY2014 is the most recent public per-installation energy figure** —
  11+ years old at the time of this build; current DoD reporting doesn't
  publish this at the installation level (see "Data sourcing" above).
- **Total site energy, not electricity-only** — no public electricity/gas
  split by installation was found.
- **Population-proximity scoring is a simplification**, not the formal
  NRC Emergency Planning Zone determination (which both SMR designs here
  already claim is at or near the site boundary).
- **The 70/30 ally-vulnerability weighting is disclosed, not a published
  DoD formula** — none was found in this build's research.
- **4-installation roster only** — chosen because FY2014 Appendix E has
  real data for each; not a general-purpose installation lookup.
- **92% nuclear capacity factor is a fleet-average assumption**, not an
  SMR-specific figure (no SMR is yet operating commercially to measure).

---

## Tech stack

Python, Click, Rich (`box.ASCII2`), `requests` (live USGS + World Bank),
Anthropic Claude (Haiku, `DEMO_MODE`-gated). 43 tests, all passing.
