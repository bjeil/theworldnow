import { writable } from "svelte/store";

export type Lang = "en" | "no";

export const lang = writable<Lang>("en");

export const langs: Record<Lang, Record<string, string>> = {
  en: {
    tagline:
      "What is everyone doing right now? Population-weighted estimates per country × time zone — every counter is an estimate, not a measurement (click a counter for its formula and sources).",
    world: "World",
    searchCountry: "Search country or ISO3…",
    today: "today",
    ofWorld: "of world",
    methodology: "Methodology",
    hideMethodology: "Hide methodology",
    howEstimated: "How it's estimated",
    estimateNote: "Estimate, not a measurement.",
    sources: "Sources",
    top10: "Top 10 countries right now",
    loading: "Loading model…",
    mapNote:
      "Heatmap: where the selected activity is happening most right now (1° longitude bands). Select a country to highlight and zoom.",
  },
  no: {
    tagline:
      "Hva gjør alle akkurat nå? Befolkningsveide estimater per land × tidssone — hver teller er et estimat, ikke en måling (klikk på en teller for formel og kilder).",
    world: "Verden",
    searchCountry: "Søk land eller ISO3…",
    today: "i dag",
    ofWorld: "av verden",
    methodology: "Metodikk",
    hideMethodology: "Skjul metodikk",
    howEstimated: "Slik er den estimert",
    estimateNote: "Estimat, ikke en måling.",
    sources: "Kilder",
    top10: "Topp 10 land akkurat nå",
    loading: "Laster modell…",
    mapNote:
      "Varmekart: hvor den valgte aktiviteten skjer mest akkurat nå (1°-breddegrader). Velg et land for å markere og zoome.",
  },
};
