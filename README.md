# theworldnow

Real-time, population-weighted counters of what people around the world are doing right now — sleeping, peeing, eating, having sex, googling, being born, dying, and more. Planned from the idea in `bjeil/notes:docs/ideas/theworldnow.md`.

**Static, local-first: no backend. All computation happens in the browser.** Data is prebuilt as static JSON and hosted alongside the app.

## Run

```bash
npm ci
npm run dev        # local dev server
npm run build      # static build -> dist/
npm run preview    # preview the production build
npm test           # vitest unit tests
npm run check      # svelte-check + types
npm run lint       # eslint
npm run format     # prettier --check
```

## Data

Static datasets live in `public/data/` and are built by the scripts in `scripts/` (Python, see `scripts/README.md`):

- `regions.json` — one region per (country × IANA timezone) with population, 15+ male/female population, and centroid (`scripts/build_regions.py`, issue #1)
- `activities.json` — counter catalog: rate, duration, demographic, sources, formula (issue #2)
- `curves.json` — per-country 24×7 weekday/weekend day curves (issue #3)
- `bands.json` — 360 one-degree longitude bands for the map (issue #1)

Rebuild all data with:

```bash
pip install -r scripts/requirements.txt
python scripts/build_regions.py
python scripts/build_curves.py
```

## Architecture

```
scripts/ (Python, one-time)          browser (runtime, every 100 ms)
  raw sources -> public/data/*.json    fetch JSON once -> model.tick(utc, country?)
  regions / bands / activities /       -> per-activity rate (λ), stock ("right now"),
  curves                                so-far-today, per-country breakdown
                                       -> counter grid, country filter, map
```

Model: `λ_A,r(t) = pop_r × n_A × f_A(local_time_r, weekday_r) / 86400` per region `r = (country, tzid)`, summed per activity; stock `S_A = λ_A × duration_A` (Little's law). Local time comes from `Intl.DateTimeFormat` with the region's IANA `tzid`, so DST, weekends and multi-timezone countries (USA, Russia, France, ...) are handled automatically. Everything is an **estimate, not a measurement** — every counter links to its source and formula (see `docs/methodology.md`, issue #10).

## Tech decisions

- Svelte 5 + Vite + TypeScript, hand-written CSS, no UI framework (same pattern as `bjeil/notes:docs/ideas/okonomi.md`)
- Map: Leaflet + `world-atlas` TopoJSON country polygons (issue #8)
- Tests: vitest for the app, `unittest` for the data pipeline
- CI: `.github/workflows/ci.yml`; deploy: GitHub Pages via `.github/workflows/deploy.yml`
- Domain candidates (checked when the idea was written): `theworldnow.net` / `.live` / `.world` available; `.com` taken

## Deploy

Pushes to `main` build and deploy to GitHub Pages (`.github/workflows/deploy.yml`). One-time setup: repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Issues

The work is tracked as issues #1–#10 (see the issue tracker).
