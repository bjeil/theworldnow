import { describe, expect, it } from "vitest";
import { createModel, interp, localHour, popFor, type ModelData } from "./model";
import regions from "../../test/fixtures/regions.sample.json";
import curves from "../../test/fixtures/curves.sample.json";
import activities from "../../public/data/activities.json";
import realRegions from "../../public/data/regions.json";

const fixtureData: ModelData = {
  regions: regions as ModelData["regions"],
  activities: activities as ModelData["activities"],
  curves: curves as ModelData["curves"],
};

describe("interp", () => {
  it("interpolates linearly and wraps at 24", () => {
    const c = Array(24).fill(0);
    c[10] = 10;
    c[0] = 10;
    expect(interp(c, 10)).toBeCloseTo(10);
    expect(interp(c, 10.5)).toBeCloseTo(5);
    expect(interp(c, 23.5)).toBeCloseTo(5);
  });
});

describe("localHour", () => {
  it("gives different local hours per timezone at the same UTC instant", () => {
    const utc = new Date("2025-06-15T12:00:00Z");
    const ny = localHour(utc, "America/New_York");
    const la = localHour(utc, "America/Los_Angeles");
    expect(ny.hour - la.hour).toBeCloseTo(3);
  });

  it("handles DST transitions via the IANA tz database", () => {
    const before = localHour(new Date("2025-03-08T12:00:00Z"), "America/New_York");
    const after = localHour(new Date("2025-03-10T12:00:00Z"), "America/New_York");
    expect(after.hour - before.hour).toBeCloseTo(1);
  });

  it("detects weekend vs weekday locally", () => {
    const sat = localHour(new Date("2025-06-14T12:00:00Z"), "Europe/Oslo");
    const mon = localHour(new Date("2025-06-16T12:00:00Z"), "Europe/Oslo");
    expect(sat.weekday === 0 || sat.weekday === 6).toBe(true);
    expect(mon.weekday >= 1 && mon.weekday <= 5).toBe(true);
  });
});

describe("popFor", () => {
  it("maps demographics to region populations", () => {
    const r = {
      iso3: "X",
      name: "X",
      tzid: "UTC",
      pop: 100,
      popM15plus: 40,
      popF15plus: 35,
      lon: 0,
      lat: 0,
    };
    expect(popFor(r, "all")).toBe(100);
    expect(popFor(r, "adults15plus")).toBe(75);
    expect(popFor(r, "male15plus")).toBe(40);
    expect(popFor(r, "female15plus")).toBe(35);
  });
});

describe("model.tick", () => {
  const model = createModel(fixtureData);
  const utc = new Date("2025-06-16T12:00:00Z");

  it("returns every activity with rate, stock and soFarToday", () => {
    const res = model.tick(utc);
    for (const a of model.activities) {
      const t = res.activities[a.id]!;
      expect(t.rate).toBeGreaterThanOrEqual(0);
      expect(t.stock).toBeCloseTo(t.rate * (a.kind === "state" ? 3600 : a.durationSec), 6);
      expect(t.soFarToday).toBeGreaterThanOrEqual(0);
      expect(t.soFarToday).toBeLessThanOrEqual(sumPop(fixtureData) * a.nPerDay * 1.01);
    }
  });

  it("country filter reduces to that country's regions and never exceeds world", () => {
    const world = model.tick(utc);
    const usa = model.tick(utc, "USA");
    for (const a of model.activities) {
      expect(usa.activities[a.id]!.rate).toBeLessThanOrEqual(world.activities[a.id]!.rate * 1.0001);
      expect(usa.activities[a.id]!.byCountry["USA"]).toBeCloseTo(usa.activities[a.id]!.rate, 6);
    }
    expect(Object.keys(usa.activities["sleeping"]!.byCountry)).toEqual(["USA"]);
    const byRegionSum = Object.values(world.activities["sleeping"]!.byRegion).reduce(
      (s, v) => s + v,
      0,
    );
    expect(byRegionSum).toBeCloseTo(world.activities["sleeping"]!.rate, 6);
  });

  it("multi-timezone country gets different local hours per region (USA)", () => {
    const res = model.tick(utc, "USA");
    expect(res.activities["sleeping"]!.rate).toBeGreaterThan(0);
    const ny = localHour(utc, "America/New_York");
    const la = localHour(utc, "America/Los_Angeles");
    expect(ny.hour).not.toBeCloseTo(la.hour);
  });

  it("falls back to _default curve for countries without overrides", () => {
    expect(model.curveFor("sleeping", "FRA")).toBe(curves["sleeping"]!._default);
    expect(model.curveFor("sleeping", "USA")).toBe(curves["sleeping"]!["USA"]);
  });

  it("state counters never exceed their parent (no paradoxes)", () => {
    const model = createModel(fixtureData);
    const worldPop = sumPop(fixtureData);
    const usaPop = fixtureData.regions
      .filter((r) => r.iso3 === "USA")
      .reduce((s, r) => s + r.pop, 0);
    for (let hh = 0; hh < 24; hh++) {
      const utc = new Date(Date.UTC(2025, 5, 16, hh, 0, 0));
      for (const [sel, pop] of [
        [null, worldPop],
        ["USA", usaPop],
      ] as const) {
        const res = model.tick(utc, sel);
        const a = res.activities;
        expect(a["online"]!.stock).toBeLessThanOrEqual(a["awake"]!.stock + 1e-6);
        expect(a["awake"]!.stock).toBeLessThanOrEqual(pop + 1e-6);
        expect(a["scrolling-social"]!.stock).toBeLessThanOrEqual(a["awake"]!.stock + 1e-6);
        expect(a["working"]!.stock).toBeLessThanOrEqual(a["awake"]!.stock + 1e-6);
        expect(a["dreaming"]!.stock).toBeLessThanOrEqual(a["sleeping"]!.stock + 1e-6);
        expect(a["peeing"]!.stock).toBeLessThanOrEqual(a["on-toilet"]!.stock + 1e-6);
        expect(a["pooping"]!.stock).toBeLessThanOrEqual(a["on-toilet"]!.stock + 1e-6);
        expect(a["sleeping"]!.stock + a["awake"]!.stock).toBeCloseTo(pop, -2);
      }
    }
  });

  it("breathing and heartbeat differ and stay within population", () => {
    const model = createModel(fixtureData);
    const res = model.tick(new Date("2025-06-16T12:00:00Z"));
    const b = res.activities["breathing"]!;
    const h = res.activities["heartbeat"]!;
    const pop = sumPop(fixtureData);
    expect(b.stock).not.toBeCloseTo(h.stock, 3);
    expect(b.stock).toBeLessThanOrEqual(pop);
    expect(h.stock).toBeLessThanOrEqual(pop);
    expect(h.stock).toBeCloseTo((pop * 100000 * 0.8) / 86400, -3);
    expect(b.rate).toBeLessThan(h.rate);
  });

  it("worldPopulation matches the dataset near mid-year and grows at the net rate", () => {
    const model = createModel(fixtureData);
    const midYear = new Date(Date.UTC(2025, 5, 1));
    const res0 = model.tick(midYear);
    expect(res0.worldPopulation).toBeCloseTo(sumPop(fixtureData), -4);
    const res1 = model.tick(new Date(midYear.getTime() + 1000 * 1000));
    const net = (res0.activities["born"]?.rate ?? 0) - (res0.activities["died"]?.rate ?? 0);
    expect(res1.worldPopulation - res0.worldPopulation).toBeCloseTo(net * 1000, 3);
  });

  it("world totals are plausible against the full regions dataset", () => {
    const full = createModel({
      regions: realRegions as ModelData["regions"],
      activities: activities as ModelData["activities"],
      curves: curves as ModelData["curves"],
    });
    const res = full.tick(new Date("2025-06-16T12:00:00Z"));
    expect(res.activities["born"]!.rate).toBeGreaterThan(3);
    expect(res.activities["born"]!.rate).toBeLessThan(6);
    expect(res.activities["died"]!.rate).toBeGreaterThan(1);
    expect(res.activities["sleeping"]!.stock).toBeGreaterThan(3e8);
    expect(res.activities["sleeping"]!.stock).toBeLessThan(8.5e9);
  });
});

function sumPop(data: ModelData): number {
  return data.regions.reduce((s, r) => s + r.pop, 0);
}
