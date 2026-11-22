<script lang="ts">
  import { onMount } from "svelte";
  import CounterCard from "./components/CounterCard.svelte";
  import CountryFilter from "./components/CountryFilter.svelte";
  import { fmtLocalTime } from "./lib/format";
  import {
    model,
    selectedActivity,
    selectedIso3,
    start,
    stop,
    tickResult,
    worldResult,
  } from "./lib/store";

  const groupTitles: Record<string, string> = {
    sleep: "Sleep & circadian",
    body: "Toilet & body",
    food: "Food & drink",
    sex: "Sex & intimacy",
    screen: "Screen & internet",
    transport: "Transport & work",
    vital: "Birth, death & emotion",
  };

  onMount(() => {
    start();
    return stop;
  });

  $: groups = $model
    ? [...new Set($model.activities.map((a) => a.group))].map((g) => ({
        group: g,
        title: groupTitles[g] ?? g,
        activities: $model!.activities.filter((a) => a.group === g),
      }))
    : [];

  $: tzids = $selectedIso3
    ? [
        ...new Set(
          ($model?.regions ?? []).filter((r) => r.iso3 === $selectedIso3).map((r) => r.tzid),
        ),
      ]
    : [];

  $: top10 =
    $selectedActivity && $worldResult && $model
      ? Object.entries($worldResult.activities[$selectedActivity]?.byCountry ?? {})
          .map(([iso3, rate]) => ({
            name: $model!.regions.find((r) => r.iso3 === iso3)?.name ?? iso3,
            rate,
          }))
          .sort((a, b) => b.rate - a.rate)
          .slice(0, 10)
      : [];

  function shareOf(id: string): number | null {
    const w = $worldResult?.activities[id]?.rate ?? 0;
    const v = $tickResult?.activities[id]?.rate ?? 0;
    return $selectedIso3 && w > 0 ? v / w : null;
  }
</script>

<main>
  <h1>theworldnow</h1>
  <p class="muted">
    What is everyone doing right now? Population-weighted estimates per country × time zone — every
    counter is an <strong>estimate, not a measurement</strong> (click a counter for its formula and sources).
  </p>
  <div class="toolbar">
    <CountryFilter />
    {#if tzids.length > 0 && $tickResult}
      <span class="tz-times">
        {#each tzids as tz (tz)}
          <span class="tz">{tz.replace(/_/g, " ")} {fmtLocalTime($tickResult.utc, tz)}</span>
        {/each}
      </span>
    {/if}
  </div>
  {#if !$model}
    <p>Loading model…</p>
  {:else}
    {#each groups as g (g.group)}
      <section>
        <h2>{g.title}</h2>
        <div class="grid">
          {#each g.activities as a (a.id)}
            <CounterCard
              activity={a}
              value={$tickResult?.activities[a.id]}
              worldValue={$worldResult?.activities[a.id]}
              share={shareOf(a.id)}
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
