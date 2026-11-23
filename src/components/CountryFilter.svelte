<script lang="ts">
  import { model, selectedIso3 } from "../lib/store";
  import { en } from "../lib/i18n";

  let query = $state("");

  const d = en;
  let open = $state(false);

  let countries = $derived(
    [
      ...new Map(
        ($model?.regions ?? []).map((r) => [r.iso3, { iso3: r.iso3, name: r.name }]),
      ).values(),
    ].sort((a, b) => a.name.localeCompare(b.name)),
  );

  let q = $derived(query.trim().toLowerCase());
  let filtered = $derived(
    q
      ? countries.filter(
          (c) => c.name.toLowerCase().includes(q) || c.iso3.toLowerCase().includes(q),
        )
      : countries,
  );

  let selectedName = $derived(
    $selectedIso3
      ? (countries.find((c) => c.iso3 === $selectedIso3)?.name ?? $selectedIso3)
      : "World",
  );

  function pick(iso3: string | null) {
    selectedIso3.set(iso3);
    query = "";
    open = false;
  }
</script>

<div class="filter">
  <button
    class="toggle"
    aria-expanded={open}
    aria-haspopup="listbox"
    onclick={() => (open = !open)}
  >
    {selectedName} ▾
  </button>
  {#if open}
    <div class="panel">
      <input
        type="search"
        placeholder={d.searchCountry}
        bind:value={query}
        aria-label={d.searchCountry}
        onkeydown={(e) => e.key === "Escape" && (open = false)}
      />
      <ul role="listbox" aria-label="Countries">
        <li role="option" aria-selected={$selectedIso3 === null}>
          <button onclick={() => pick(null)}>{d.world}</button>
        </li>
        {#each filtered.slice(0, 50) as c (c.iso3)}
          <li role="option" aria-selected={$selectedIso3 === c.iso3}>
            <button onclick={() => pick(c.iso3)}>{c.name} ({c.iso3})</button>
          </li>
        {/each}
        {#if filtered.length === 0}
          <li class="empty">No match</li>
        {/if}
      </ul>
    </div>
  {/if}
</div>

<style>
  .filter {
    position: relative;
    display: inline-block;
  }

  .toggle {
    padding: 0.5rem 0.9rem;
    border: 1px solid #223041;
    border-radius: 0.5rem;
    background: #111826;
    color: var(--fg);
    font: inherit;
    cursor: pointer;
  }

  .toggle:hover {
    border-color: var(--accent);
  }

  .panel {
    position: absolute;
    z-index: 20;
    top: 100%;
    left: 0;
    width: 18rem;
    max-height: 20rem;
    overflow: auto;
    border: 1px solid var(--accent);
    border-radius: 0.5rem;
    background: #0b0f14;
    padding: 0.5rem;
  }

  input {
    width: 100%;
    padding: 0.4rem 0.6rem;
    margin-bottom: 0.4rem;
    border: 1px solid #223041;
    border-radius: 0.4rem;
    background: #111826;
    color: var(--fg);
    font: inherit;
  }

  ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  li button {
    width: 100%;
    text-align: left;
    padding: 0.35rem 0.5rem;
    border: 0;
    border-radius: 0.3rem;
    background: none;
    color: var(--fg);
    font: inherit;
    cursor: pointer;
  }

  li button:hover {
    background: #1a2433;
  }

  .empty {
    color: var(--muted);
    padding: 0.35rem 0.5rem;
  }
</style>
