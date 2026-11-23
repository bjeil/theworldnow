# Methodology

theworldnow shows **estimates, not measurements**. Every number is a model computed in the browser
from public datasets and published rates. This page documents the model and the sources.

## Model

The smallest unit is a **region = (country × IANA time zone)** — built by intersecting Natural Earth
country polygons with timezone-boundary-builder polygons (see `scripts/build_regions.py`). This
makes multi-timezone countries (USA, Russia, France, Australia, Brazil, Canada, ...) work
automatically: each region has its own `tzid` and therefore its own local time and day rhythm.

For each activity `A` and region `r` at UTC time `t`:

```
λ_A,r(t) = popFor(A, r) × n_A × f_A(localTime_r(t), weekday_r(t)) / 86400
λ_A(t)   = Σ_r λ_A,r(t)                      (events per second, "per second")
S_A(t)   = λ_A(t) × duration_A              ("right now", Little's law L = λ·W)
```

- `popFor(A, r)` is `pop`, `popM15plus`, `popF15plus` or their sum, depending on the counter's
  `demographic` (sex-related counters use the 15+ population).
- `localTime_r(t)` comes from `Intl.DateTimeFormat` with `timeZone: r.tzid` — DST and weekends are
  handled automatically.
- `f_A` is a normalized 24-point curve per weekday/weekend (`curves.json`), linearly interpolated at
  the fractional local hour; curves sum to 24, so a full local day integrates to exactly `n_A`
  events per person.
- For `kind: "state"` counters (sleeping, online, working, ...), `nPerDay` is hours per day and
  `S_A = Σ_r pop_r × n_A/24 × f_A` (share of the day in that state), so states never exceed the
  population.
- "So far today" integrates each region's curve from its own local midnight.
- Consistency: counters are hierarchical per region (`maxOf` in `activities.json`) — `awake` is
  derived as `population − sleeping`, and every activity that can only happen while awake (online,
  eating, working, driving, sex, on-toilet, ...) is clamped to `awake`; `dreaming` ≤ `sleeping`,
  `peeing`/`pooping` ≤ `on-toilet`. So e.g. "online" can never exceed "awake".
- Country filter: re-sums only that country's regions in the same tick — purely client-side.
- The map aggregates regions into 360 one-degree longitude bands (`bands.json`) via their
  population-weighted centroids.

## Data sources

| Data                         | Source                                                                                                                                                                                                                  | Pinned                        |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| Country polygons (ISO3)      | Natural Earth 110m                                                                                                                                                                                                      | commit `9380cca`              |
| Timezone polygons            | timezone-boundary-builder                                                                                                                                                                                               | release `2024a`               |
| Population raster 30 arc-sec | JRC GHSL `GHS_POP_E2020_GLOBE_R2023A_4326_30ss`                                                                                                                                                                         | R2023A V1-0                   |
| Age/sex 15+ per country      | UN WPP 2024 `WPP2024_PopulationByAge5GroupSex_Medium`                                                                                                                                                                   | WPP 2024, year ≤ 2025         |
| Activity rates/durations     | per-counter citations in `public/data/activities.json` (Waldinger 2005, Bhat & Shastry 2020, Durex/Natsal/GSS/NSFG, OECD/HETUS/OWID, UN WPP, DataReportal, ICAO/FlightRadar24, NCA/ICO, clinical/physiology literature) | see file                      |
| Day curves                   | `public/data/curves.json` (documented estimates; per-country measured curves can be added as overrides)                                                                                                                 | see `scripts/build_curves.py` |

## Open questions (from the idea, tracked deliberately)

- Stock ("right now") vs rate ("per second") as the main view — currently both are shown.
- Calendar holidays (e.g. Ramadan) and seasonality in the day curves.
- Taste boundary: which activities to include.
- Per-country sex-rate sourcing (Durex/GSS/Natsal weighting) and how to communicate uncertainty.
- Per-timezone breakdown within a selected country (the map can show it; UI currently shows local
  times per zone).
