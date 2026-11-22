<script lang="ts">
  import { onMount } from "svelte";
  import { SvelteMap } from "svelte/reactivity";
  import CounterCard from "./components/CounterCard.svelte";
  import CountryFilter from "./components/CountryFilter.svelte";
  import Methodology from "./components/Methodology.svelte";
  import WorldMap from "./components/WorldMap.svelte";
  import { fmtInt, fmtLocalTime } from "./lib/format";
  import { lang, langs } from "./lib/i18n";
  import {
    model,
    selectedActivity,
    selectedIso3,
    start,
    stop,
    tickResult,
    worldResult,
  } from "./lib/store";

  const groupTitles: Record<string, Record<string, string>> = {
    en: {
      sleep: "Sleep & circadian",
      body: "Toilet & body",
      food: "Food & drink",
      sex: "Sex & intimacy",
      screen: "Screen & internet",
      transport: "Transport & work",
      vital: "Birth, death & emotion",
    },
    no: {
      sleep: "Søvn & døgnrytme",
      body: "Do og kropp",
      food: "Mat og drikke",
      sex: "Sex og intimitet",
      screen: "Skjerm og nett",
      transport: "Transport og jobb",
      vital: "Fødsel, død og følelser",
    },
  };

  let showMethodology = $state(false);

  onMount(() => {
    start();
    return stop;
  });

  let d = $derived(langs[$lang]);

  let groups = $derived(
    $model
      ? [...new Set($model.activities.map((a) => a.group))].map((g) => ({
          group: g,
          title: groupTitles[$lang]?.[g] ?? g,
          activities: $model.activities.filter((a) => a.group === g),
        }))
      : [],
  );

  let tzids = $derived(
    $selectedIso3
      ? [
          ...new Set(
            ($model?.regions ?? []).filter((r) => r.iso3 === $selectedIso3).map((r) => r.tzid),
          ),
        ]
      : [],
  );

  let top10 = $derived(
    $selectedActivity && $worldResult && $model
      ? Object.entries($worldResult.activities[$selectedActivity]?.byCountry ?? {})
          .map(([iso3, rate]) => ({
            name: $model!.regions.find((r) => r.iso3 === iso3)?.name ?? iso3,
            rate,
          }))
          .sort((a, b) => b.rate - a.rate)
          .slice(0, 10)
      : [],
  );

  let shares = $derived.by(() => {
    const out = new SvelteMap<string, number>();
    if (!$selectedIso3 || !$worldResult || !$tickResult) return out;
    for (const [id, w] of Object.entries($worldResult.activities)) {
      const v = $tickResult.activities[id]?.rate ?? 0;
      if (w.rate > 0) out.set(id, v / w.rate);
    }
    return out;
  });

  let liveText = $derived.by(() => {
    if (!$tickResult || !$model) return "";
    const sec = Math.floor($tickResult.utc / 1000);
    const label = $model.activities.find((a) => a.id === "sleeping")?.label ?? "sleeping";
    return `${label}: ${fmtInt($tickResult.activities["sleeping"]?.stock ?? 0)} (${sec})`;
  });
</script>

<main>
  <h1>theworldnow</h1>
  <p class="muted">{d.tagline}</p>
  <div class="toolbar">
    <CountryFilter />
    <button class="tool" onclick={() => (showMethodology = !showMethodology)}>
      {showMethodology ? d.hideMethodology : d.methodology}
    </button>
    <button class="tool" onclick={() => lang.set($lang === "en" ? "no" : "en")}>
      {$lang === "en" ? "Norsk" : "English"}
    </button>
    {#if tzids.length > 0 && $tickResult}
      <span class="tz-times">
        {#each tzids as tz (tz)}
          <span class="tz">{tz.replace(/_/g, " ")} {fmtLocalTime($tickResult.utc, tz)}</span>
        {/each}
      </span>
    {/if}
  </div>
  <div class="sr-only" aria-live="polite">{liveText}</div>
  {#if showMethodology}
    <Methodology />
  {/if}
  {#if !$model}
    <p>{d.loading}</p>
  {:else}
    <WorldMap />
    {#each groups as g (g.group)}
      <section>
        <h2>{g.title}</h2>
        <div class="grid">
          {#each g.activities as a (a.id)}
            <CounterCard
              activity={a}
              value={$tickResult?.activities[a.id]}
              worldValue={$worldResult?.activities[a.id]}
              share={shares.get(a.id) ?? null}
              {top10}
              open={$selectedActivity === a.id}
              onToggle={() => selectedActivity.set($selectedActivity === a.id ? null : a.id)}
            />
          {/each}
        </div>
      </section>
    {/each}
  {/if}
</main>

<style>
  h1 {
    font-size: 2rem;
    margin-bottom: 0.25rem;
  }

  h2 {
    font-size: 1.1rem;
    color: var(--accent);
    margin: 1.5rem 0 0.5rem;
  }

  .toolbar {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 1rem 0;
  }

  .tool {
    padding: 0.5rem 0.9rem;
    border: 1px solid #223041;
    border-radius: 0.5rem;
    background: #111826;
    color: var(--fg);
    font: inherit;
    cursor: pointer;
  }

  .tool:hover {
    border-color: var(--accent);
  }

  .tz-times {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    color: var(--muted);
    font-size: 0.85rem;
    font-variant-numeric: tabular-nums;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr));
    gap: 0.75rem;
  }
</style>
