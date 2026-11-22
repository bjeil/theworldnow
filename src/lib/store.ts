import { get, writable } from "svelte/store";
import { createModel, loadModel, type Model, type TickResult } from "./model";

export const model = writable<Model | null>(null);
export const tickResult = writable<TickResult | null>(null);
export const worldResult = writable<TickResult | null>(null);
export const selectedIso3 = writable<string | null>(null);
export const selectedActivity = writable<string | null>(null);

let timer: ReturnType<typeof setInterval> | null = null;
let worker: Worker | null = null;

export async function start(): Promise<void> {
  const baseUrl = import.meta.env.BASE_URL;
  if (typeof Worker !== "undefined") {
    worker = new Worker(new URL("./worker.ts", import.meta.url), { type: "module" });
    worker.onmessage = (e: MessageEvent) => {
      const msg = e.data;
      if (msg.type === "ready") {
        model.set(
          createModel({ regions: msg.regions, activities: msg.activities, curves: msg.curves }),
        );
      } else if (msg.type === "tick") {
        worldResult.set(msg.world);
        tickResult.set(msg.result);
      }
    };
    worker.postMessage({ type: "init", baseUrl });
    timer = setInterval(() => {
      worker?.postMessage({ type: "tick", utc: Date.now(), selectedIso3: get(selectedIso3) });
    }, 100);
    return;
  }
  const m = await loadModel(baseUrl);
  model.set(m);
  timer = setInterval(() => {
    const now = new Date();
    const sel = get(selectedIso3);
    worldResult.set(m.tick(now, null));
    tickResult.set(m.tick(now, sel));
  }, 100);
}

export function stop(): void {
  if (timer !== null) clearInterval(timer);
  timer = null;
  worker?.terminate();
  worker = null;
}
