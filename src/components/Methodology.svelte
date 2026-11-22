<script lang="ts">
  import { lang, langs } from "../lib/i18n";

  $: d = langs[$lang];
</script>

<section class="methodology">
  <h2>{d.methodology}</h2>
  <p>
    Each counter is a model estimate, computed in your browser every 100 ms —{" "}
    <strong>{d.estimateNote}</strong>
  </p>
  <ul>
    <li>
      Regions are <strong>country × IANA time zone</strong> intersections (1034 regions), each with population
      from the JRC GHSL 2020 raster (30 arc-sec) and 15+ male/female shares from UN WPP 2024.
    </li>
    <li>
      Per region and activity: <code
        >rate = pop × nPerDay × dayCurve(localTime, weekday) / 86400</code
      >, where local time comes from the region's <code>tzid</code> (DST and weekends automatic) and the
      day curve is a normalized 24-point weekday/weekend curve.
    </li>
    <li>
      "Right now" (stock) = rate × duration (Little's law) for events; for states, pop × hours/24 ×
      curve. "So far today" integrates each region's curve from its local midnight.
    </li>
    <li>
      Filtering by country just re-sums the same per-region numbers for that country's regions — no
      extra requests.
    </li>
  </ul>
  <p>
    Sources: UN WPP 2024, JRC GHSL, NASA SEDAC GPW, WorldPop, IANA tz database /
    timezone-boundary-builder, Natural Earth, OECD Time Use / HETUS / Our World in Data, and the
    per-counter study sources shown on each card. Full write-up: <code>docs/methodology.md</code> in the
    repo.
  </p>
</section>

<style>
  .methodology {
    border: 1px solid #223041;
    border-radius: 0.75rem;
    padding: 1rem 1.25rem;
    background: #111826;
    font-size: 0.9rem;
  }

  .methodology code {
    color: var(--accent);
  }
</style>
