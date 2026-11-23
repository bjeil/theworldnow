<script lang="ts">
  import type { Activity, ActivityTick } from "../lib/model";
  import { fmtBig, fmtPct, fmtRate } from "../lib/format";
  import { en } from "../lib/i18n";

  let {
    activity,
    value,
    worldValue,
    share,
    top10,
    open,
    onToggle,
  }: {
    activity: Activity;
    value: ActivityTick | undefined;
    worldValue: ActivityTick | undefined;
    share: number | null;
    top10: { name: string; rate: number }[];
    open: boolean;
    onToggle: () => void;
  } = $props();

  const d = en;
</script>

<div class="wrap">
  <button class="card" class:open aria-expanded={open} onclick={onToggle}>
    <span class="label">{activity.label}</span>
    {#if activity.ratePrimary}
      <span class="stock">{fmtRate(value?.rate ?? 0)} /s</span>
      <span class="sub">
        {fmtBig(value?.stock ?? 0)} right now · {fmtBig(value?.soFarToday ?? 0)}
        {d.today}{#if share !== null}
          · {fmtPct(share)} {d.ofWorld}{/if}
      </span>
    {:else}
      <span class="stock">{fmtBig(value?.stock ?? 0)}</span>
      <span class="sub">
        {fmtRate(value?.rate ?? 0)} /s · {fmtBig(value?.soFarToday ?? 0)}
        {d.today}{#if share !== null}
          · {fmtPct(share)} {d.ofWorld}{/if}
      </span>
    {/if}
  </button>
  {#if open}
    <div class="popover">
      <strong>{d.howCalculated}</strong>
      <p>{activity.explanation}</p>
      <strong>{d.howEstimated}</strong>
      <code>{activity.formula}</code>
      <em>{d.estimateNote}</em>
      {#if share !== null}
        <span
          >{activity.label} in the selected country is {fmtPct(share)} of the world total ({fmtRate(
            worldValue?.rate ?? 0,
          )}/s worldwide).</span
        >
      {/if}
      {#if top10.length > 0}
        <strong>{d.top10}</strong>
        <ol>
          {#each top10 as t (t.name)}
            <li>{t.name}: {fmtRate(t.rate)} /s</li>
          {/each}
        </ol>
      {/if}
      <strong>{d.sources}</strong>
      <ul>
        {#each activity.sources as s (s.url)}
          <li><a href={s.url} target="_blank" rel="noreferrer">{s.title}</a></li>
        {/each}
      </ul>
    </div>
  {/if}
</div>

<style>
  .wrap {
    position: relative;
  }

  .card {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    width: 100%;
    padding: 1rem;
    border: 1px solid #223041;
    border-radius: 0.75rem;
    background: #111826;
    color: var(--fg);
    text-align: left;
    cursor: pointer;
    font: inherit;
  }

  .card:hover,
  .card.open {
    border-color: var(--accent);
  }

  .label {
    color: var(--muted);
    font-size: 0.85rem;
  }

  .stock {
    font-size: 1.6rem;
    font-variant-numeric: tabular-nums;
    font-weight: 600;
  }

  .sub {
    color: var(--muted);
    font-size: 0.8rem;
    font-variant-numeric: tabular-nums;
  }

  .popover {
    position: absolute;
    z-index: 1100;
    top: 100%;
    left: 0;
    width: 20rem;
    max-width: 80vw;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    padding: 0.75rem;
    border: 1px solid var(--accent);
    border-radius: 0.5rem;
    background: #0b0f14;
    font-size: 0.8rem;
  }

  .popover code {
    display: block;
    white-space: normal;
    word-break: break-word;
    color: var(--accent);
  }

  .popover ul,
  .popover ol {
    margin: 0;
    padding-left: 1.2rem;
  }
</style>
