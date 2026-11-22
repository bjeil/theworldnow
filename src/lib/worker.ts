import { createModel, type Model, type ModelData } from "./model";

let model: Model | null = null;

interface InitMessage {
  type: "init";
  baseUrl: string;
}

interface TickMessage {
  type: "tick";
  utc: number;
  selectedIso3: string | null;
}

const ctx = self as unknown as Worker;

ctx.onmessage = async (e: MessageEvent<InitMessage | TickMessage>) => {
  const msg = e.data;
  if (msg.type === "init") {
    const [regions, activities, curves] = await Promise.all([
      fetch(`${msg.baseUrl}data/regions.json`).then((r) => r.json()),
      fetch(`${msg.baseUrl}data/activities.json`).then((r) => r.json()),
      fetch(`${msg.baseUrl}data/curves.json`).then((r) => r.json()),
    ]);
    const data: ModelData = { regions, activities, curves };
    model = createModel(data);
    ctx.postMessage({ type: "ready", ...data });
  } else if (msg.type === "tick" && model) {
    const utc = new Date(msg.utc);
    ctx.postMessage({
      type: "tick",
      world: model.tick(utc, null),
      result: model.tick(utc, msg.selectedIso3),
    });
  }
};
