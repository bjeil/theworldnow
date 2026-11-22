export interface Region {
  iso3: string;
  name: string;
  tzid: string;
  pop: number;
  popM15plus: number;
  popF15plus: number;
  lon: number;
  lat: number;
}

export interface ActivitySource {
  title: string;
  url: string;
}

export type Demographic = "all" | "adults15plus" | "male15plus" | "female15plus";

export interface Activity {
  id: string;
  label: string;
  group: string;
  kind: "event" | "state";
  nPerDay: number;
  demographic: Demographic;
  durationSec: number;
  unit: string;
  sources: ActivitySource[];
  formula: string;
  estimate: boolean;
}

export interface DayCurve {
  weekday: number[];
  weekend: number[];
}

export type Curves = Record<string, Record<string, DayCurve>>;

export interface ActivityTick {
  rate: number;
  stock: number;
  soFarToday: number;
  byCountry: Record<string, number>;
  byRegion: Record<string, number>;
}

export interface TickResult {
  utc: number;
  selectedIso3: string | null;
  activities: Record<string, ActivityTick>;
}

export interface ModelData {
  regions: Region[];
  activities: Activity[];
  curves: Curves;
}

export interface Model {
  activities: Activity[];
  regions: Region[];
  tick(utc: Date, selectedIso3?: string | null): TickResult;
  curveFor(activityId: string, iso3: string): DayCurve;
  popFor(region: Region, demographic: Demographic): number;
}

const formatters = new Map<string, Intl.DateTimeFormat>();

function formatter(tzid: string): Intl.DateTimeFormat {
  let f = formatters.get(tzid);
  if (!f) {
    f = new Intl.DateTimeFormat("en-US", {
      timeZone: tzid,
      hourCycle: "h23",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
    formatters.set(tzid, f);
  }
  return f;
}

export function localHour(utc: Date, tzid: string): { hour: number; weekday: number } {
  const parts = formatter(tzid).formatToParts(utc);
  const get = (type: string) => Number(parts.find((p) => p.type === type)?.value);
  const year = get("year");
  const month = get("month");
  const day = get("day");
  const hour = get("hour") % 24;
  const minute = get("minute");
  const weekday = new Date(Date.UTC(year, month - 1, day)).getUTCDay();
  return { hour: hour + minute / 60, weekday };
}

export function interp(curve: number[], h: number): number {
  const x = Math.min(Math.max(h, 0), 24 - 1e-9);
  const i = Math.floor(x);
  const frac = x - i;
  return curve[i]! * (1 - frac) + curve[(i + 1) % 24]! * frac;
}

export function popFor(region: Region, demographic: Demographic): number {
  switch (demographic) {
    case "all":
      return region.pop;
    case "adults15plus":
      return region.popM15plus + region.popF15plus;
    case "male15plus":
      return region.popM15plus;
    case "female15plus":
      return region.popF15plus;
  }
}

export function createModel(data: ModelData): Model {
  const curveCache = new Map<string, Map<string, DayCurve>>();
  const byIso3 = new Map<string, Region[]>();
  for (const r of data.regions) {
    const list = byIso3.get(r.iso3) ?? [];
    list.push(r);
    byIso3.set(r.iso3, list);
  }

  function curveFor(activityId: string, iso3: string): DayCurve {
    let m = curveCache.get(activityId);
    if (!m) {
      m = new Map();
      curveCache.set(activityId, m);
    }
    let c = m.get(iso3);
    if (!c) {
      const entry = data.curves[activityId];
      c = entry?.[iso3] ??
        entry?._default ?? { weekday: Array(24).fill(1), weekend: Array(24).fill(1) };
      m.set(iso3, c);
    }
    return c;
  }

  function tick(utc: Date, selectedIso3: string | null = null): TickResult {
    const activities: Record<string, ActivityTick> = {};
    for (const a of data.activities) {
      activities[a.id] = { rate: 0, stock: 0, soFarToday: 0, byCountry: {}, byRegion: {} };
    }
    const regions = selectedIso3 ? (byIso3.get(selectedIso3) ?? []) : data.regions;
    for (const r of regions) {
      const { hour, weekday } = localHour(utc, r.tzid);
      const weekend = weekday === 0 || weekday === 6;
      for (const a of data.activities) {
        const pop = popFor(r, a.demographic);
        if (pop <= 0) continue;
        const c = curveFor(a.id, r.iso3)[weekend ? "weekend" : "weekday"];
        const f = interp(c, hour);
        const contribution = (pop * a.nPerDay * f) / 86400;
        const t = activities[a.id]!;
        t.rate += contribution;
        t.byCountry[r.iso3] = (t.byCountry[r.iso3] ?? 0) + contribution;
        const rid = `${r.iso3}|${r.tzid}`;
        t.byRegion[rid] = (t.byRegion[rid] ?? 0) + contribution;
        let cum = 0;
        const full = Math.min(Math.floor(hour), 23);
        for (let i = 0; i < full; i++) cum += c[i]!;
        cum += (c[full]! * (1 - (hour - full)) + c[(full + 1) % 24]! * (hour - full)) * 0.5;
        t.soFarToday += (pop * a.nPerDay * cum) / 24;
      }
    }
    for (const a of data.activities) {
      const t = activities[a.id]!;
      t.stock = t.rate * (a.kind === "state" ? 3600 : a.durationSec);
    }
    return { utc: utc.getTime(), selectedIso3, activities };
  }

  return { activities: data.activities, regions: data.regions, tick, curveFor, popFor };
}

export async function loadModel(baseUrl = ""): Promise<Model> {
  const [regions, activities, curves] = await Promise.all([
    fetch(`${baseUrl}data/regions.json`).then((r) => r.json()),
    fetch(`${baseUrl}data/activities.json`).then((r) => r.json()),
    fetch(`${baseUrl}data/curves.json`).then((r) => r.json()),
  ]);
  return createModel({ regions, activities, curves });
}
