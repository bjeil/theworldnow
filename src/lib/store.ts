import { get, writable } from "svelte/store";
import { loadModel, type Model, type TickResult } from "./model";

export const model = writable<Model | null>(null);
export const tickResult = writable<TickResult | null>(null);
export const worldResult = writable<TickResult | null>(null);
export const selectedIso3 = writable<string | null>(null);
export const selectedActivity = writable<string | null>(null);

let timer: ReturnType<typeof setInterval> | null = null;

export async function start(): Promise<void> {
  const m = await loadModel(import.meta.env.BASE_URL);
  model.set(m);
  const run = () => {
    const now = new Date();
    const sel = get(selectedIso3);
    worldResult.set(m.tick(now, null));
    tickResult.set(m.tick(now, sel));
  };
  run();
  timer = setInterval(run, 100);
}

export function stop(): void {
  if (timer !== null) clearInterval(timer);
  timer = null;
}
