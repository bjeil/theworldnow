# theworldnow — project review

**Review date: 2026-11-24.**

> **Qualification:** This is a preliminary review, not a source-verified scientific audit. Numerical benchmarks, domain pricing, source and licensing claims, and implementation estimates below require independent verification. Recommendations are proposals, not established fixes. In particular:
>
> - Integrating the linearly interpolated curve requires trapezoids for **whole hours as well as partial hours**; the formula in finding 1 is incomplete.
> - A change in the number asleep is a **net change**, not the rate of people falling asleep. Entries and exits cannot be recovered from the net alone.
> - Sex-event rates depend on whether the input is per person or per act; participant counts, acts, and duration must be defined and sourced before applying a factor of two. The numerical estimates below are not verified.
> - Online activities can overlap: each may be a subset of online without their sum being bounded by online. Do not treat the suggested sum invariant as valid.
> - Small timezone intersections are not necessarily errors; investigate boundary discrepancies before merging any regions. The statement about OSM tile-policy violation is not established by the code alone; assess the actual usage against the policy.
> - The registrar pricing below is not a quote, and Cloudflare Registrar's registration and nameserver requirements must be checked before choosing it.

Scope: model/measures, map, site presentation, new measures, other improvements, domain.
Method: read all source, data and docs; ran the model headlessly (vitest probes, not committed) at several UTC times and for single regions; ran lint/format/check/tests/build (all green: 19 tests pass; the bundle is 981 kB JS / 306 kB gzip).
Limits: the review sandbox has no outbound network, so I did not view the live site or map tiles, and **could not check the domain live** (see §7).

---

## TL;DR — top priorities

1. **Fix real bugs** (§1.1): "so far today" jumps at hour boundaries; state counters show person-hours labelled as people; `online` uses 16.3 h/day (≈ 70 % of humanity "online" at once); `sex` double-counts partners; `awake` "today" is inconsistent; China and 45 other countries never highlight on the map (name mismatch).
2. **Make countries actually different** (§1.2). Today every country has the same per-capita rates and the same day shape; only population and time zone differ. So "top 10 countries" is just a population ranking, and Nigeria has the same birth rate as Japan. Add per-country covariates (births/deaths, internet use, age structure, ...).
3. **Replace the map** (§2): the 1° longitude stripes are the wonky part. Use per-region choropleth + day/night terminator + hover/click + legend + time scrubber.
4. **Restructure the page** (§3): sticky header with world population, tabs for groups, icons, a "headline" strip, a ranked list/detail panel instead of 42 equal cards.
5. **Add ~15 well-grouped measures** (§4), mostly "world-scale" counters that can be sourced from real-time-ish rates, and hide the long tail behind tabs.

---

## 1. Measures and calculations

### 1.1 Concrete defects (verified)

| #   | Finding                                                                                                                                                                                                                                                                                                                                                         | Evidence                                                                                                    | Fix                                                                                                                                                                                                                                                                                                                              |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **"So far today" jumps every hour.** `model.ts` cumulative sum adds `c[i]` for whole hours, then adds `0.5·(lerp)` for the fraction (wrong: should be `frac × avg(c[full], interp)`). At each hour boundary the value jumps by a full `c[i]`.                                                                                                                   | Oslo, `eating`: 1.94 M at 09:59:59 UTC → 2.42 M at 10:00:01 (+25 % in 2 s); within an hour it barely moves. | Use `Σ_{i<full} c[i] + frac · (c[full] + interp(c, hour)) / 2` (trapezoid), and make the curve convention (hour-start sample vs hour-average) consistent with `interp`. Add a continuity unit test at hour boundaries.                                                                                                           |
| 2   | **State counters' "today" is person-hours, displayed as a count.** For `kind:"state"`, `soFar = pop·n·cum/24`, shown as e.g. "44 B today" next to "people sleeping" (world pop is 8.3 B).                                                                                                                                                                       | `App`/`CounterCard` show `fmtBig(soFarToday) today` for all kinds.                                          | For states show **person-hours** ("44 B person-hours of sleep today") or "% of day elapsed asleep", or hide.                                                                                                                                                                                                                     |
| 3   | **State counters' `/s` rate is meaningless.** For states `rate = stock/3600` (e.g. "sleeping: 875,707 /s").                                                                                                                                                                                                                                                     | `model.ts` tick; also `awake` rate = awakeStock/3600.                                                       | For states show the _net flow_ (Δstock/Δt: people falling asleep per second), or omit.                                                                                                                                                                                                                                           |
| 4   | **`online` = 16.3 h/day over _everyone_.** At UTC 12:00, 5.97 B (72 %) "online"; Oslo 83 % at 13:00. The explanation conflates "share of people who use the internet" (~68 %) with hours of use. DataReportal: ~6 h 40 min/day for _users_ ⇒ ≈ 1.5 B actively online on average (≈ 4.5 h/capita incl. non-users), or ≈ 3–4 B "connected/always-on".             | probe at UTC 0/6/12/18.                                                                                     | Decide on the definition. "Actively using the internet right now" ≈ users × (6.7 h/24) × curve; show "connected" separately if wanted. Then derive `scrolling-social` / `watching-video` / `gaming` as _subsets_ of online (currently `online` is 16.3 h but its parts sum to 4 h, and `maxOf` points at `awake`, not `online`). |
| 5   | **`sex` counts each act once per participant** (0.07/adult/day × adults, 6.2 B adults ⇒ ~434 M/day). An act involves two people; and ~45 % of adults have no active partner. Order of magnitude is ~100–200 M acts/day. Also `kissing`, `hugging`: per-person events are likewise ambiguous.                                                                    | formula in `activities.json`.                                                                               | Model `acts = partnered_adults × freq / 2`; stock of "people having sex" = 2 × acts × duration. Use per-country partnered share (UN marital status/union data).                                                                                                                                                                  |
| 6   | **Sex duration 324 s is intravaginal ejaculation latency (Waldinger 2005), not session length.** The session is typically 10–30 min incl. foreplay. Stock is therefore underestimated 2–5×.                                                                                                                                                                     | `durationSec: 324`.                                                                                         | Pick a documented "session length" source (e.g. Kinsey/Corty & Guardiani 2008 survey) and keep IELT only for the male-ejaculation counter.                                                                                                                                                                                       |
| 7   | **`male-ejaculation` (0.06/day) is below `sex` (0.07)**, yet it should include solo events (masturbation ~ weekly+). `female-orgasm` 0.05 similarly ignores partner status.                                                                                                                                                                                     | activities table                                                                                            | Define counters coherently: partnered acts, solo events, with separate sources.                                                                                                                                                                                                                                                  |
| 8   | **`awake` "so far today" disagrees with `sleeping`.** `awake` soFar uses a separate hump curve (peak 13:00) while the stock is `pop − sleeping`.                                                                                                                                                                                                                | `model.ts` `raw.set("awake", soFar: raw.get("awake")?.soFar)`                                               | Derive `awake` soFar as `pop·cum24 − sleeping soFar`.                                                                                                                                                                                                                                                                            |
| 9   | **Sleep curve shape is questionable.** Gaussian (+baseline) normalised to 8 h; Oslo at 03:00 on a weekday: 75 % asleep (real time-use diaries: ~90 %+), while elsewhere the raw value hits the 100 % clamp and the day minimum is 1.5 % (real ~3–5 % at midday). The result depends on clamps rather than a calibrated shape.                                   | probe on `Europe/Oslo`                                                                                      | Replace with measured curves (§1.3).                                                                                                                                                                                                                                                                                             |
| 10  | **Clamps use the wrong parent.** `flying`, `peeing` etc. are clamped to `awake`, but people sleep on planes, and wake at night to urinate; `waking-now`/`going-to-bed` are transitions, not awake-states.                                                                                                                                                       | `maxOf: "awake"`                                                                                            | Remove `awake` clamp for flying/toilet; keep clamps only for true containment. Show the clamp hits in a debug view so tuning is visible.                                                                                                                                                                                         |
| 11  | **Births/deaths are the same per-capita rate everywhere** (`4.59e-5`/day for all). Japan and Nigeria have identical crude birth rates in the model.                                                                                                                                                                                                             | `activities.json`                                                                                           | Use UN WPP **CBR / CDR per country** (the pipeline already downloads WPP). Rate becomes `pop × CBR/1000/365`. Same for `crying`, etc. via age structure.                                                                                                                                                                         |
| 12  | **Time-of-day curves are synthetic** (`build_curves.py`: Gaussians). Cited sources (OECD, HETUS) do not feed the curves, and every country shares the same shape (`_default` only) — Spain eats dinner at 22:00, Japan sleeps ~7 h, the US ~8.5 h.                                                                                                              | `curves.json` has only `_default`                                                                           | Build curves from open time-use microdata: HETUS (EU), ATUS (US), MTUS (multinational), and the UN/OECD summary tables; fall back to nearest similar-culture country.                                                                                                                                                            |
| 13  | **Midnight discontinuity in `interp`.** Interpolating hour 23.x blends towards `curve[0]` of the _same_ weekday/weekend curve instead of the next day's; weekday→weekend boundaries (Fri→Sat, Sun→Mon) are visible steps. Weekday flag is the _calendar_ day, so a Friday night's sleep at 01:00 Saturday uses the weekend curve.                               | `interp`, `tick`                                                                                            | Interpolate across day boundaries with the neighbouring day's curve.                                                                                                                                                                                                                                                             |
| 14  | **World population vs sum of regions.** `meta.json` says 8.303 B, the header shows 8.340 B in Nov 2026 because it extrapolates from "mid-2026" at `(born − died)` while docs say WPP year ≤ 2025. It's fine, but the baseline year/provenance should be explicit.                                                                                               | model.ts `midYear`                                                                                          | Document baseline (GHSL 2020 raster scaled to WPP 2026?) and show "UN WPP 2024 medium, extrapolated".                                                                                                                                                                                                                            |
| 15  | **Missing 15+ data → sex counters zero** for Kosovo, Somalia, Somaliland, Northern Cyprus (and 15+ total is 6.22 B vs ~6.5 B in WPP).                                                                                                                                                                                                                           | probe                                                                                                       | Fall back to the world 15+ ratio; map ISO3 aliases (XKX, SOM, CYN).                                                                                                                                                                                                                                                              |
| 16  | **Sliver regions / data artefacts.** 597 of 1131 regions have < 20 k people, e.g. Afghanistan has regions in `Asia/Ashgabat` (5 k), `Asia/Shanghai` (0), China in `Asia/Bangkok`, `Asia/Almaty`... (tz-polygon/country-polygon boundary mismatch). Methodology says 1034 regions, `meta.json` says 1131, docs say Natural Earth 110m while the script uses 50m. | regions.json                                                                                                | Merge regions < 0.1 % of the country (or < 50 k) into the country's dominant tz; fix the docs; show region count from `meta.json`. This also cuts per-tick cost ~50 %.                                                                                                                                                           |
| 17  | **Uniform per-capita rates ignore development.** `driving`, `showering`, `coffee`, `washing-hands`, `brushing-teeth`, `online`, `gaming`, `flying` all use the same per-capita rate in every country. Coffee/day in Finland vs Nigeria differ 20×.                                                                                                              | activities                                                                                                  | Add per-country multiplier tables (see 1.2).                                                                                                                                                                                                                                                                                     |
| 18  | **`crying` 1/day (120 s) and `working` 5.5 h/adult** are high. Studies: adults cry ~1–5 times/month; employed ≈ 3.5 B of 6.5 B adults ⇒ ~3–3.5 h/adult/day averaged over 7 days. At UTC 06:00 the model has 2.1 B working (>60 % of all employed) at once.                                                                                                      | probe                                                                                                       | Recalibrate; use ILO employment-to-population ratio per country × hours/week.                                                                                                                                                                                                                                                    |
| 19  | **`kind:"event"` stocks for ~instant events are meaningless** ("2.9 B breathing right now", "7.7 B heartbeats right now").                                                                                                                                                                                                                                      | probe                                                                                                       | For `breathing`, `heartbeat`, `blinking`, `swallowing` show only rate; drop the stock.                                                                                                                                                                                                                                           |
| 20  | **Perf/arch:** every 100 ms the worker computes 2 full ticks (world + selected), each calling `Intl.formatToParts` ×1131 regions, and posts ~100 k numbers (`byRegion` for 42 activities ×2). The main thread also instantiates the model (duplicate).                                                                                                          | `worker.ts`, `store.ts`                                                                                     | Cache local hour/weekday per tz once per minute (offsets); compute selected country from the world pass; tick at 1 Hz and interpolate counters with `requestAnimationFrame`; send `byRegion` only for the active activity.                                                                                                       |

### 1.2 How to make the calculations more meaningful

- **Make the model a product of three explicit factors** per region and activity:
  `rate = population_segment(r) × base_rate(country) × timeOfDay(country, weekday, local hour)`.
  Today only the first and third (with a global default) exist. Add `base_rate(country)` via covariate multipliers: internet users (ITU/World Bank), median age and age pyramid (WPP), employment ratio (ILO), urbanisation, car ownership, GDP/capita, coffee/tea consumption (ICO), alcohol consumption (WHO), etc.
- **Distinguish stock, flow, state.** Three kinds are currently blurred: _states_ (sleeping, online → people), _events_ (googling, born → per-second flow), _instantaneous counts_ (heartbeats → flow only). The UI should render each kind differently (see §3).
- **Show uncertainty**, not only "estimate": store `low/high` per counter (a ±range from source spread) and render as "≈ 2.4 M (1.5 – 3.5 M)" in detail view; colour confidence (A: official statistics, B: survey-based, C: expert guess). `crying` is already tagged "Expert estimate".
- **Cross-checks as tests**: add invariants — world births/day ≈ WPP; `awake + sleeping = pop` per region; `online ≥ scrolling + video + gaming`; global daily mean of each state equals `nPerDay/24` ± 2 % (this would have caught the `online` issue).
- **Seasonality & calendar**: DST is handled; Ramadan (fasting-aware eating curves), school holidays, Christmas, and daylight length vs. wake time (high latitudes) are not. Add an optional per-country curve variant keyed by calendar flags.
- **So-far-today** should use _each region's_ own midnight, but the world total mixes days; label as "since local midnight (rolling)" or provide an "elapsed UTC day" alternative.

### 1.3 Recommended data work (in priority order)

1. WPP per-country CBR/CDR, age pyramid (already downloaded) → births, deaths, kids/adults split.
2. ITU/World Bank internet use → online-related counters.
3. HETUS/ATUS/MTUS → measured time-of-day curves for sleeping, eating, working, TV/video, driving, cooking, socialising (top ~30 countries; clusters for the rest).
4. ILO employment & hours → working.
5. Real-time-ish world rates (see §4) from public APIs, fetched at build time and refreshed by a scheduled GitHub Action (static site stays static).

---

## 2. The map

### 2.1 What is wrong now (from code)

- **It shows 360 vertical stripes** (`bands.json`: 1° longitude bands from −85° to 85° lat). Colour = sum over regions whose _centroid_ falls in the band. Large regions are drawn into one stripe (all of Russia's/Canada's/USA's population lands on one line), so the map is spiky and does not correspond to where people really are.
- **The activity barely changes the picture.** Because rates are `pop × global const × curve`, the heatmap is "population per band, shifted by the clock"; every activity looks nearly the same. Intensity is normalised to the max band, which is always China/India.
- **Heat is hidden:** country polygons (fill opacity 0.6) are added _above_ the bands, covering them.
- **Dead/buggy code:** `tileLayer` is declared but never assigned, so the theme `$effect` never changes tiles (always light OSM tiles, even in dark theme); `tileUrl()` and `countries110` (actually the 50 m file) are misnamed/unused; CSS `var(--…)` strings are passed as Leaflet style values (these are set as SVG attributes and may not resolve — verify in a browser).
- **Selecting a country by name fails for 46 countries** (`f.properties.name === region.name`): e.g. "People's Republic of China" vs "China", "Czech Republic", "Ivory Coast", DR Congo, Bosnia, Bahamas... China never highlights or zooms. Use ISO codes (add `iso_a3` to the topojson join or ship numeric id).
- **No interaction:** no hover tooltip, no click-to-select country, no legend, no time control, no zoom-to-region, no mobile gestures; 750 kB of country TopoJSON bundled into the main JS (981 kB total, 306 kB gzip) plus OSM raster tiles (which also violates OSM's tile usage policy for production traffic).

### 2.2 Proposed design

**Visual layers (toggle with a layer switcher):**

1. **Intensity choropleth** (default): colour each _region polygon_ (country × tz) by **share of local population doing the activity right now** (e.g. 78 % asleep) — this makes the day/night wave visible for every activity and is independent of population size.
2. **Absolute density** (dot-density / hex bins of people doing it) using a coarse GHSL grid (e.g. 0.25° ≈ 100 k cells; ship as a compact binary/PNG raster) multiplied per cell by its tz region's current share.
3. **Day/night terminator** and solar-noon line (cheap, instantly legible; `suncalc` or closed-form formulas).
4. **Time-zone bands** (optional outlines), labelled with local time.

**Interaction:** hover tooltip (country, local time, count, share, top activity), click → select country (sync with filter), double-click/zoom → region detail, legend with scale, "time machine" scrubber (±24 h, play/pause, speed ×60/×3600) that feeds the model's `tick(utc)` — the model is already pure in `utc`, so this is nearly free. Keyboard-accessible list alternative to the map for a11y.

**Technology options**

| Option                                                                                       | Pros                                                                                                                   | Cons                                                                                        | Verdict                                                        |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Keep Leaflet, fix it                                                                         | small change                                                                                                           | SVG layers with 1000+ polygons recolouring every second are slow; weak animation/projection | stop-gap only                                                  |
| **MapLibre GL JS** + vector/GeoJSON source of regions, `feature-state` for per-region colour | WebGL smooth recolour at 60 fps, globe projection, free, no API key (use OpenFreeMap/Protomaps or _no basemap at all_) | +~200 kB; need simplified region polygons                                                   | **recommended**                                                |
| **d3-geo + canvas/SVG** (Natural Earth projection or orthographic globe)                     | tiny, full control, no tiles, looks "designed", terminator trivial; spinning globe mode                                | you implement zoom/hit-testing (d3-zoom, `geoContains`/quadtree)                            | **best fit for a counter-style site** — a basemap isn't needed |
| deck.gl / Three.js globe                                                                     | wow factor                                                                                                             | heavy                                                                                       | optional later                                                 |

**How to implement (steps):**

1. `build_regions.py`: also emit **simplified region polygons** (mapshaper/`shapely.simplify(0.05)` + topojson, quantised) → `regions.topo.json` ≈ 300–500 kB (lazy-loaded). Keep ISO3 + tzid as properties. Drop `bands.json`.
2. Rendering: MapLibre with a GeoJSON source `promoteId: "rid"`; per tick (1 Hz) `setFeatureState` for the _active_ activity only (worker sends one `byRegion` array).
3. Code-split: `import()` the map component; remove the 750 kB bundled atlas.
4. Wire selection: click/hover → `selectedIso3`; legend + scrubber components; a11y list.
5. Test: unit-test the colour scale and the iso join (all 240 countries must resolve).

---

## 3. Formatting and presentation

### 3.1 Observations

- One very long scroll: header → toolbar → map → 7 sections × ≈6 cards of 42 equal-weight counters. A reader cannot tell what matters; "heartbeat" and "breathing" appear next to "sex".
- No icons or visual hierarchy; text-only cards; cards show 3–4 different numbers (rate, stock, today, % of world) with unlabelled semantics.
- The details popover is absolutely positioned (z-index 1100) and overlays neighbours; may clip on small screens; no dismiss on outside click/Escape; no deep-linking.
- Theme button text is static ("Switch to light theme" even when light); footer/credits/about are absent; tagline is long and repeats the disclaimer; the methodology panel is stale (says 1034 regions).
- Accessibility is decent (aria-expanded, reduced-motion, sr-only live region) but numbers re-render 10×/s (animating digits are hard to read/announce).
- Performance: bundle 981 kB; 10 Hz updates of 42 cards.

### 3.2 Proposed layout

```
┌ sticky header: logo · World pop (live, +2.5/s) · [Country ▾] · [24h ◀ now ▶] · ☀/☾ · ⓘ ┐
├ HERO strip (4–6 big numbers):  😴 asleep · 🌐 online · 👶 born today · 🪦 died today · ✈ airborne · 💬 searches/s ┤
├ [Tabs: Overview | Body | Food | Intimacy | Screens | Movement & Work | Life & Death | Planet ] ┤
│ left (60 %): MAP (layers, legend, scrubber)         right (40 %): Detail panel for selected counter │
│                                                     (sparkline of 24 h, top 10, source, formula)     │
├ counters grid for the active tab (compact cards: icon, label, big number, unit, ▲▼ trend, 24 h sparkline)┤
└ footer: methodology · sources · data version · GitHub · privacy (none collected)                      ┘
```

Specific upgrades:

- **Tabs / segmented control** for groups (replace 7 stacked sections) with a persistent "Overview" that shows 6–8 curated headliners. Keep search ("find a counter").
- **Icons**: one consistent SVG icon set (Lucide / Tabler, tree-shaken ≈ 1 kB each) or emoji fallback. Colour-code groups (a CSS custom property per group) and reuse it on the map layer chip.
- **Card redesign**: one primary number (state → "people now", event → "per second"), one small secondary line, a **24 h sparkline** of today's curve with a "now" marker (data already in `curves`). Move "% of world" into the detail panel, and the person-hours stats out of the card.
- **Detail panel/drawer** (side drawer on desktop, bottom sheet on mobile) instead of a floating popover; URL state (`#country=NOR&c=sleeping&tab=food`) for shareable links.
- **Tone/readability**: tabular numbers already used; add odometer-style digit animation only on the hero numbers; throttle other cards to 1 Hz; `prefers-reduced-motion` respected (already).
- **Mobile**: horizontal-scrolling tabs, 2-column cards, collapsed map (tap to expand).
- **Branding & share**: proper logo/wordmark, Open Graph image (screenshot of the hero), `theme-color`, favicon set, tagline in one sentence ("What is the world doing right now? Estimated, live, per country.").
- **Theme**: use `prefers-color-scheme` default (exists), label the toggle with ☀/☾ icon; add a third palette variant for the map.
- **i18n**: `i18n.ts` only has `en`; move all strings (group titles in `App.svelte`, "right now", etc.) into it before adding a language.
- **Trust UI**: confidence badge (A/B/C) on each card; a consistent "estimate" pill; link to the formula.

---

## 4. Additional measures (grouped so the page stays calm)

Keep the page _progressive_: Overview shows ≤ 8; each tab shows ≤ 8; the rest sit behind "Show more". Proposed groups, with new candidates in **bold**.

| Tab                                               | Existing (keep/trim)                                     | New, interesting, defensible                                                                                                                                                                                                                                                                         |
| ------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Overview**                                      | sleeping, online, born, died, flying                     | **people on Earth** (+ net/s), **people in space** (7–10, from Open Notify API-style static), **babies born today**, **CO₂ emitted today**, **trees lost**                                                                                                                                           |
| **Body**                                          | peeing, pooping, showering, brushing teeth, yawn, sneeze | **toothpaste tubes**, **hiccups**, **people with a cold/flu now** (seasonal, WHO FluNet), **hangovers** (alcohol stats), **people awake at 3 am** (insomnia ≈ 10 %), **pills/vaccines administered**                                                                                                 |
| **Food & drink**                                  | eating, coffee, cooking, bites                           | **cups of tea** (≈ 3 bn/day), **beers drunk** (≈ 5 bn L/yr ≈ 190 L/s... derive), **pizzas eaten** (~ 5 bn/yr), **Big Macs**, **bottles of water**, **food wasted** (≈ 1 bn meals/day), **people hungry** (FAO ≈ 700 M, constant)                                                                     |
| **Intimacy & feelings** (rename "Sex & intimacy") | sex, kissing, hugging, laughing, crying                  | **marriages / divorces per second** (UN Stats), **people falling in love** (soft/novelty), **text messages / emails / WhatsApp** (≈ 100 bn/day)                                                                                                                                                      |
| **Screens & internet**                            | online, social, video, gaming, googling                  | **emails sent** (~ 350 bn/day) and **spam share**, **YouTube hours watched** (≈ 1 bn h/day), **tweets/posts**, **WhatsApp messages**, **Netflix/streaming**, **photos taken** (~ 5 bn/day), **bitcoin transactions** (live via public API, optional)                                                 |
| **Movement & work**                               | driving, public transport, working, flying               | **cars on the road**, **ships at sea** (AIS stats), **trains running**, **commuters**, **people in school/class** (UNESCO enrolment × school-hours curve), **parcels delivered**, **people in hospital**                                                                                             |
| **Life & death**                                  | born, died                                               | **deaths by cause** (WHO: heart disease, cancer, road traffic ≈ 1.2 M/yr, suicide, malaria, hunger), **road deaths today**, **people turning 18 / 65 today**, **couples marrying**, **centenarians**                                                                                                 |
| **Planet** (new, "edgy"/ambient)                  | —                                                        | **sunrises happening now** (people seeing sunrise: terminator × population), **people in daylight vs darkness (%)**, **solar generation (live-ish from ENTSO-E/EIA)**, **lightning strikes/s** (~ 45/s), **earthquakes today** (USGS feed), **CO₂ ppm** (NOAA Mauna Loa), **plastic bottles bought** |

**"Edgy but safe" ideas:** _"You are here"_ personal line (your country, local time, how many people share your minute: "Right now 41 M people are brushing their teeth, 8 M of them in your time zone"); _"Everyone you share a birthday with"_; _"Where is it 3:07 am?"_; _"What the person on the opposite side of the world is doing"_ (antipode lookup — the model already has regions and time); _"Today vs 100 years ago"_ population sparkline; _"Share card"_ image export for social.

**Content/taste:** sex/ejaculation counters can get the site flagged by ad networks, school filters and some social platforms. Options: keep them but put them in an "Intimacy" tab behind a one-time "18+" toggle (default off for share links/OG image), and avoid the word list in titles/description. Decide the policy explicitly (README lists "taste boundary" as open).

**Sourcing rule for new measures:** each must have (a) a primary source with URL, (b) unit and definition, (c) the kind (state/event/flow), (d) a confidence grade, and (e) a plausibility test in `model.test.ts` against its published global total. Counters that are the same number everywhere (e.g. global CO₂) do not need the regional model — add a `scope: "global"` type that is a simple linear counter (rate × t since a published baseline) and render it in the "Planet" tab.

---

## 5. Other improvements

**Engineering**

- Split bundle: lazy-load map; use `topojson` at build time; target < 150 kB gzip initial.
- Unit-test the numerics at the level of invariants (world totals vs source totals; hour-boundary continuity; `awake+sleeping=pop`; all ISO3 in regions are joinable to map).
- Add a **data-validation script** in `scripts/` that fails CI if any activity lacks sources, a curve, or violates plausibility bounds (global 24 h integral of each counter within X % of its documented annual total).
- Per-region cache of local time; avoid `Intl.DateTimeFormat.formatToParts` every 100 ms ×1131 regions (compute offsets once/min; DST transitions are minute-scale events).
- Remove stale/dead code (`tileUrl`, `countries110` name, fixed 1000 ms throttle logic that skips recolours) and keep docs in sync (region count, Natural Earth resolution, "populationYear").
- Scheduled GitHub Action to refresh live-ish data (births/deaths unaffected; flights/earthquakes/CO₂) and commit JSON; keep the site static.
- Add an `app.test.ts` that actually renders `App` with fixture data (currently a 16-line smoke test) and a Playwright smoke test of the built site in CI.
- Pin and document GHSL vintage vs WPP year; document that the population base is 2020 raster scaled to WPP.

**Product**

- Deep links and share cards; embed mode (`?embed=1`) for blogs.
- "About / FAQ / How accurate is this?" page; data download (CSV of the current tick) for journalists/teachers.
- Analytics: privacy-friendly only (or none); consider a short "no tracking" line as a feature.
- Open Graph preview should be a real image (hero numbers), not just text; add `robots`, sitemap, `canonical` for the custom domain.
- Licence/attribution page: Natural Earth (public domain), GHSL (CC BY 4.0), UN WPP (CC BY 3.0 IGO), timezone-boundary-builder (ODbL — requires attribution and share-alike on derived DBs), OSM/basemap attribution.

---

## 6. Suggested roadmap

| Phase                                      | Work                                                                                                                                                     | Size |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| **0 – correctness (1–2 days)**             | Fix findings 1, 2, 3, 4, 5, 8, 13, 16, map name join; update docs/meta; add invariant tests                                                              | S    |
| **1 – differentiate countries (3–5 days)** | CBR/CDR, internet use, employment, age structure; per-country multipliers in `activities.json`; per-country curves for top ~30 countries from HETUS/ATUS | M    |
| **2 – new map (4–6 days)**                 | simplified region polygons, d3/MapLibre map, intensity layer, terminator, tooltip/click, legend, scrubber                                                | M    |
| **3 – page redesign (3–5 days)**           | sticky header, hero strip, tabs, icons, detail drawer, sparklines, URL state                                                                             | M    |
| **4 – new measures (ongoing)**             | 3–4 per tab; `scope: global` counters; confidence badges; scheduled data refresh                                                                         | M    |
| **5 – polish**                             | OG image, i18n, share cards, a11y audit, performance budget                                                                                              | S    |

---

## 7. Domain: theworldnow.net

**Status: could not be verified from this environment.** The sandbox blocks outbound DNS/HTTP (RDAP, WHOIS and registrar pages all failed). The README says `theworldnow.net`, `.live`, `.world` were available "when the idea was written" and `.com` was taken; that is _not_ a current confirmation.

How to check in 30 seconds (any one):

1. `https://rdap.verisign.com/net/v1/domain/theworldnow.net` → HTTP **404** = not registered; **200** = taken.
2. `whois theworldnow.net` → "No match for domain" = available.
3. Type it in a registrar search (Cloudflare, Porkbun, Namecheap).

**Expected price (typical, to be confirmed at checkout; not a live quote):** `.net` is a regulated registry with a wholesale price ≈ **US$ 13–14/yr** (Verisign has raised it ~7 %/yr in recent years). At-cost registrars (Cloudflare Registrar, Porkbun, Spaceship) typically sell it at ≈ **US$ 12–16/yr** with renewals at the same price; mainstream retail (GoDaddy/Namecheap) may show promo prices of ≈ $10–13 for year 1 and ≈ $16–22 at renewal. If the domain turns out to be **registered** (parked or aftermarket), expect a broker/aftermarket price (hundreds to thousands of dollars); then consider `theworldnow.live` / `.world` / `.app` / `.io`.

### Step-by-step: acquire and connect theworldnow.net

1. **Check availability** with the RDAP URL above or a registrar search. If taken, check _who_: if expired/pending delete, set a backorder (e.g. DropCatch/SnapNames); otherwise pick an alternative TLD.
2. **Pick a registrar.** Recommended: **Cloudflare Registrar** (at-cost pricing, no renewal markup, free WHOIS privacy, DNS built in) or **Porkbun**. Avoid auto-upsells (email, "site builder", premium DNS).
3. **Create an account** with 2FA (authenticator app or passkey) — domain hijacking is mostly account takeover.
4. **Register** `theworldnow.net` for 1 year (or several; price per year is the same at cost). Enable **auto-renew** and **registrar lock**. Keep **WHOIS privacy** on (free at Cloudflare/Porkbun/Namecheap).
5. **Add a payment backup & renewal email** to a role address (not only a personal one).
6. **Point DNS at GitHub Pages** (the site deploys from `.github/workflows/deploy.yml`):
   - Apex `theworldnow.net`: four `A` records → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` (and the IPv6 `AAAA` set from GitHub docs).
   - `www`: `CNAME` → `bjeil.github.io`.
   - If using Cloudflare DNS, set these records **DNS-only (grey cloud)** until GitHub has issued the certificate.
7. **Configure GitHub:** repo → _Settings → Pages → Custom domain_ = `theworldnow.net`; wait for the DNS check to pass, then tick **Enforce HTTPS** (certificate from Let's Encrypt, can take up to ~1 h). Optionally verify the domain at _Account settings → Pages → Add a domain_ (TXT record) to prevent subdomain takeover.
8. **Add a `public/CNAME` file** containing `theworldnow.net` (so each deploy keeps the setting; with the Actions-based Pages deploy the setting in the repo UI is what counts, but the file is harmless and documents intent). The Vite config already uses `base: "./"`, so asset paths work on the custom domain.
9. **Redirect `www` → apex** (or the reverse) — GitHub Pages handles it automatically when both are set.
10. **Update the site**: `canonical` link and Open Graph URL in `index.html`, README, and sitemap/robots.
11. **Defensive registrations (optional):** `.com` if it is available/affordable, and `theworldnow.live`/`.world` — set them to 301 to the main domain (Cloudflare redirect rules).
12. **Email (optional):** set up an alias via Cloudflare Email Routing/ImprovMX; add SPF/DKIM/DMARC records if you ever send mail from the domain.
13. **Verify:** `dig theworldnow.net +short`, `curl -I https://theworldnow.net` (200, valid cert), and re-test `www`.
