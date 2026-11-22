import { describe, expect, it } from "vitest";
import { createModel, type ModelData } from "./model";
import regions from "../../public/data/regions.json";
import activities from "../../public/data/activities.json";
import curves from "../../public/data/curves.json";

describe("performance budget", () => {
  it("a full tick over all regions x activities stays well under 100 ms", () => {
    const m = createModel({
      regions: regions as ModelData["regions"],
      activities: activities as ModelData["activities"],
      curves: curves as ModelData["curves"],
    });
    const n = 50;
    const t0 = performance.now();
    for (let i = 0; i < n; i++) {
      m.tick(new Date(Date.now() + i * 1000), i % 2 === 0 ? "USA" : null);
    }
    const avg = (performance.now() - t0) / n;
    console.log(`avg tick with full dataset: ${avg.toFixed(2)} ms over ${n} ticks`);
    expect(avg).toBeLessThan(100);
  });
});
