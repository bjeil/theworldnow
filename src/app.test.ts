import { describe, expect, it } from "vitest";
import regions from "../public/data/regions.json";
import bands from "../public/data/bands.json";

describe("scaffold", () => {
  it("loads the regions dataset built by scripts/build_regions.py", () => {
    expect(regions.length).toBeGreaterThan(1000);
    expect(regions[0]).toHaveProperty("iso3");
    expect(regions[0]).toHaveProperty("tzid");
    expect(regions[0]).toHaveProperty("pop");
  });

  it("loads the 360 longitude bands", () => {
    expect(bands).toHaveLength(360);
  });
});
