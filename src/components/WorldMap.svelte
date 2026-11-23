<script lang="ts">
  import { onMount } from "svelte";
  import { SvelteMap } from "svelte/reactivity";
  import L from "leaflet";
  import "leaflet/dist/leaflet.css";
  import { feature } from "topojson-client";
  import countries110 from "world-atlas/countries-50m.json";
  import { model, selectedActivity, selectedIso3, worldResult } from "../lib/store";
  import { en } from "../lib/i18n";
  import type { ActivityTick } from "../lib/model";

  interface Band {
    band: number;
    lonMin: number;
    latMin: number;
    latMax: number;
    pop: number;
    regions: string[];
  }

  let mapEl: HTMLDivElement;
  let map: L.Map;
  let bandLayers: L.Rectangle[] = [];
  let countryLayer: L.GeoJSON;
  let bands: Band[] = [];
  let lastMapUpdate = 0;

  const d = en;

  const ACCENT = "76, 194, 255";

  function bandRates(value: ActivityTick | undefined): Map<number, number> {
    const out = new SvelteMap<number, number>();
    if (!value) return out;
    for (const b of bands) {
      let sum = 0;
      for (const id of b.regions) {
        sum += value.byRegion[id] ?? 0;
      }
      out.set(b.band, sum);
    }
    return out;
  }

  function colorFor(v: number, max: number): string {
    const a = max > 0 ? 0.05 + 0.75 * (v / max) : 0.05;
    return `rgba(${ACCENT}, ${a.toFixed(3)})`;
  }

  onMount(() => {
    map = L.map(mapEl, { center: [20, 0], zoom: 2, minZoom: 2, worldCopyJump: true });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "© OpenStreetMap contributors",
    }).addTo(map);

    fetch(`${import.meta.env.BASE_URL}data/bands.json`)
      .then((r) => r.json())
      .then((b: Band[]) => {
        bands = b;
        for (const band of bands) {
          const rect = L.rectangle(
            [
              [-85, band.lonMin],
              [85, band.lonMin + 1],
            ],
            { color: "#223041", weight: 0, fillColor: `rgba(${ACCENT}, 0.05)`, fillOpacity: 1 },
          ).addTo(map);
          bandLayers[band.band] = rect;
        }
      });

    const topo = countries110 as unknown as Parameters<typeof feature>[0] & {
      objects: { countries: never };
    };
    const countries = feature(topo, topo.objects.countries);
    countryLayer = L.geoJSON(countries, {
      style: { color: "#3a4a5f", weight: 1, fillColor: "#16202e", fillOpacity: 0.6 },
    }).addTo(map);
  });

  $effect(() => {
    const res = $worldResult;
    const act = $selectedActivity ?? "sleeping";
    const value = res?.activities[act];
    if (!map || bandLayers.length === 0 || !value) return;
    const now = Date.now();
    if (now - lastMapUpdate < 1000) return;
    lastMapUpdate = now;
    const rates = bandRates(value);
    let max = 0;
    for (const v of rates.values()) max = Math.max(max, v);
    for (const band of bands) {
      bandLayers[band.band]?.setStyle({ fillColor: colorFor(rates.get(band.band) ?? 0, max) });
    }
  });

  $effect(() => {
    const iso3 = $selectedIso3;
    if (!countryLayer) return;
    const name = iso3 ? ($model?.regions.find((r) => r.iso3 === iso3)?.name ?? null) : null;
    countryLayer.eachLayer((layer) => {
      const f = (layer as L.Polygon).feature;
      const match = name !== null && f?.properties?.name === name;
      (layer as L.Polygon).setStyle(
        match
          ? { color: "#4cc2ff", weight: 2, fillColor: "#4cc2ff", fillOpacity: 0.35 }
          : { color: "#3a4a5f", weight: 1, fillColor: "#16202e", fillOpacity: 0.6 },
      );
      if (match) {
        map.fitBounds((layer as L.Polygon).getBounds(), { padding: [20, 20] });
      }
    });
  });
</script>

<div class="map-wrap">
  <div bind:this={mapEl} class="map" aria-label="World map of current activity"></div>
  <p class="muted map-note">
    {d.mapNote}
  </p>
</div>

<style>
  .map-wrap {
    margin: 1.5rem 0;
  }

  .map {
    position: relative;
    z-index: 0;
    height: 24rem;
    border: 1px solid #223041;
    border-radius: 0.75rem;
  }

  .map-note {
    font-size: 0.8rem;
  }
</style>
