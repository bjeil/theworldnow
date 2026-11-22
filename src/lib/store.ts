import { get, writable } from "svelte/store";
import { loadModel, type Model, type TickResult } from "./model";

export const model = writable<Model | null>(null);
export const tickResult = writable<TickResult | null>(null);
export const selectedIso3 = writable<string | null>(null);
export const selectedActivity = writable<string | null>(null);

let timer: ReturnType<typeof setInterval> | null = null;

export async function start(): Promise<void> {
  const m = await loadModel(import.meta.env.BASE_URL);
  model.set(m);
  const run = () => {
    tickResult.set(m.tick(new Date(), get(selectedIso3)));
  };
  run();
  timer = setInterval(run, 100);
}

export function stop(): void {
  if (timer !== null) clearInterval(timer);
  timer = null;
}
