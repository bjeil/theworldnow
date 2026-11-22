# Data build scripts

One-time build of the static region dataset used by the runtime model (issue #1).

## Requirements

- Python 3.12+
- `pip install -r scripts/requirements.txt` (rasterio/GDAL, shapely, numpy)

## Run

```bash
python scripts/build_regions.py                                   # full build -> public/data/
python scripts/build_regions.py --countries USA,NOR,AUS,RUS --fixture   # fixture -> test/fixtures/
python scripts/build_activities.py                               # activities.json (issue #2)
python scripts/build_curves.py                                    # curves.json (issue #3)
python -m unittest discover -s scripts -p "test_*.py"            # validate datasets
```

## Activity catalog (issue #2)

`scripts/build_activities.py` generates `public/data/activities.json` from a hand-curated table: one entry per counter with `nPerDay` (events per person per day, or hours per day for `kind: "state"` counters with `durationSec: 86400`), `durationSec`, `demographic` (`all` / `adults15plus` / `male15plus` / `female15plus`), `sources` (cited per counter), a human-readable `formula`, and `estimate: true`. Rates follow the table in the idea (`notes:docs/ideas/theworldnow.md`): peeing 6-7/day ~25 s, pooping ~1/day ~5 min, eating 60-135 min/day by country, sex ~7% of adults on an average day for a median 5.4 min (Waldinger 2005; Durex/Natsal/GSS/NSFG), births ~4.3/s and deaths ~1.9/s (UN WPP 2024), Google ~99,000 searches/s, coffee ~2.25 bn cups/day (NCA/ICO), ~1-2 M people airborne (ICAO/FlightRadar24), ~5.5 bn online (DataReportal). Sex-related counters are scoped to the 15+ population from `regions.json`; per-country sex-rate weighting and uncertainty communication remain an open question tracked in issue #10.

Downloads are cached under `data/raw/` (gitignored, ~900 MB); delete that directory to force a re-download. A full build takes ~1 minute.

## Inputs (pinned)

| Input                                     | Source                                                                                                                                | Pinned version                                    |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Country polygons (ISO3)                   | Natural Earth `ne_110m_admin_0_countries.geojson` via [nvkelso/natural-earth-vector](https://github.com/nvkelso/natural-earth-vector) | commit `9380cca83db5f9aef52d5e762765100745f84b27` |
| Timezone polygons (IANA tzid)             | [timezone-boundary-builder](https://github.com/evansiroky/timezone-boundary-builder) release asset `timezones.geojson.zip`            | tag `2024a`                                       |
| Population raster (30 arc-sec, EPSG:4326) | JRC GHSL `GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.zip`                                                                              | R2023A, epoch 2020, V1-0                          |
| Age/sex structure                         | UN WPP 2024 `WPP2024_PopulationByAge5GroupSex_Medium.csv.gz`                                                                          | WPP 2024 (interim update), year <= 2025           |

GPWv4 (NASA SEDAC) or WorldPop rasters can replace GHSL; the zonal-stats code only assumes an EPSG:4326 raster. GHSL was chosen because it needs no Earthdata login and ships as a single global file.

## Method

1. Region = country polygon intersected with each overlapping IANA timezone polygon (`STRtree` + shapely). Countries spanning multiple time zones (USA, Russia, France, Australia, Brazil, Canada, ...) therefore get one region per tzid automatically.
2. Population per region = zonal sum of the GHSL raster over the region polygon (cell centers, windowed block reads).
3. `lon`/`lat` = population-weighted centroid of the region (raster cells weighted by pop); polygon representative point if the region has zero population.
4. `popM15plus`/`popF15plus` = the country's UN WPP 15+ male/female population distributed across its regions proportionally to raster population (the fallback allowed by the issue; WorldPop age/sex rasters can replace this), capped so adults never exceed the region's population.
5. Bands: each region is assigned to its 1-degree longitude band via `floor(lon) + 180`; `bands.json` sums population per band and lists region ids (`iso3|tzid`).

Notes: Natural Earth uses `ISO_A3 = -99` for a few countries (Norway, France, Kosovo, ...); the builder falls back to `ADM0_A3` in that case. At 110m resolution, coastal/fjord population is slightly undercounted (global raster sums to ~7.84 bn, regions to ~7.66 bn) — acceptable for weighting, documented here.

## Outputs (measured)

| File                                | Size     | Content                                              |
| ----------------------------------- | -------- | ---------------------------------------------------- |
| `public/data/regions.json`          | 140.7 KB | 1034 regions, 177 countries, total pop 7,657,885,833 |
| `public/data/bands.json`            | 40.2 KB  | 360 bands                                            |
| `test/fixtures/regions.sample.json` | 14.6 KB  | 102 regions (USA, NOR, AUS, RUS)                     |
| `test/fixtures/bands.sample.json`   | 19.4 KB  | 360 bands for the fixture regions                    |

Both files are far below any static-hosting limit, so they are committed as plain JSON — no gzip/brotli pre-compression or splitting needed.

### `regions.json` schema

```json
[
  {
    "iso3": "NOR",
    "name": "Norway",
    "tzid": "Europe/Oslo",
    "pop": 4510932,
    "popM15plus": 2362738,
    "popF15plus": 2341073,
    "lon": 9.9349,
    "lat": 61.1012
  }
]
```

### `bands.json` schema

```json
[
  {
    "band": 293,
    "lonMin": 113,
    "pop": 1410144614,
    "regions": ["CHN|Asia/Shanghai", "CHN|Asia/Urumqi"]
  }
]
```

`band` is 0..359 covering `[lonMin, lonMin+1)`.
