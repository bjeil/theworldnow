# Performance

Budget from the idea: a few thousand regions (country × tzid) × ~30 activities is under 100,000
operations per tick, so per-second updates — and even 10×/s for smooth animation — are free in JS,
also with a country filter active. Even 64,800 one-degree cells would fit in a Web Worker.

## Implementation

- The tick runs in a **Web Worker** (`src/lib/worker.ts`); the UI receives `{world, result}`
  messages every 100 ms and renders from `requestAnimationFrame`/store updates. If `Worker` is
  unavailable, the store falls back to running the tick on the main thread.
- The model loads the static JSON once (`regions.json` 140 KB, `activities.json` 23 KB,
  `curves.json` 16 KB); `Intl.DateTimeFormat` formatters are cached per tzid; curve lookups are
  cached per (activity, iso3).
- The map heatmap refreshes at 1 Hz, the counter grid at 10 Hz.

## Measured

`src/lib/perf.test.ts` runs 50 ticks over the full dataset (1034 regions × 42 activities, world +
USA-filtered) in CI and asserts the average tick is under 100 ms. Local measurement: see the test
output (`avg tick with full dataset: … ms`).
