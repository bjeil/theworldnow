<script lang="ts">
  import { onMount } from "svelte";
  import CounterCard from "./components/CounterCard.svelte";
  import { model, selectedActivity, start, stop, tickResult } from "./lib/store";

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
</script>

<main>
  <h1>theworldnow</h1>
  <p class="muted">
    What is everyone doing right now? Population-weighted estimates per country × time zone — every
    counter is an <strong>estimate, not a measurement</strong> (click a counter for its formula and sources).
  </p>
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

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr));
    gap: 0.75rem;
  }
</style>
