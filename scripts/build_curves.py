"""Generate public/data/curves.json: normalized 24-point weekday/weekend day curves per activity.

Each curve has 24 hourly values normalized to sum to 24 (average 1.0), so that
rate = pop x nPerDay x f(localHour)/86400 integrates to nPerDay events per local day.
Per-country overrides live under the country ISO3; "_default" is the fallback
(documented fallback for countries without measured data, per issue #3).
"""

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def curve(peaks, baseline=0.15):
    vals = []
    for h in range(24):
        v = baseline
        for center, width, height in peaks:
            d = min(abs(h - center), 24 - abs(h - center))
            v += height * math.exp(-((d / max(width, 0.5)) ** 2))
        vals.append(v)
    total = sum(vals)
    return [round(v * 24 / total, 4) for v in vals]


def shifted(c, hours):
    hours = int(round(hours)) % 24
    return c[-hours:] + c[:-hours] if hours else list(c)


FLAT = [1.0] * 24

NIGHT = curve([(24.5, 3.5, 4.0)], baseline=0.05)
AWAKE = curve([(13.0, 6.0, 3.0)], baseline=0.05)
MORNING = curve([(7.5, 2.0, 3.0), (12.5, 1.5, 1.2), (18.5, 2.0, 1.8)], baseline=0.25)
MEALS = curve([(8.0, 1.2, 2.5), (12.5, 1.2, 3.0), (19.0, 1.5, 3.5)], baseline=0.2)
EVENING = curve([(21.0, 2.5, 3.0), (15.0, 3.0, 1.0)], baseline=0.35)
WORK = curve([(10.0, 3.0, 3.0), (16.0, 2.5, 2.5)], baseline=0.08)
RUSH = curve([(8.0, 1.2, 3.0), (17.5, 1.5, 3.5)], baseline=0.25)
DAY = curve([(14.0, 5.0, 1.5)], baseline=0.4)

BASE = {
    "sleeping": (NIGHT, shifted(NIGHT, 1)),
    "dreaming": (curve([(3.5, 2.5, 3.0)], baseline=0.02), shifted(curve([(3.5, 2.5, 3.0)], baseline=0.02), 1)),
    "awake": (AWAKE, shifted(AWAKE, 1)),
    "waking-now": (curve([(7.0, 1.0, 4.0)], baseline=0.05), curve([(8.5, 1.2, 4.0)], baseline=0.05)),
    "going-to-bed": (curve([(23.0, 1.0, 4.0)], baseline=0.05), curve([(24.0, 1.2, 4.0)], baseline=0.05)),
    "on-toilet": (MORNING, shifted(MORNING, 0.5)),
    "peeing": (curve([(7.5, 2.5, 1.6), (13.0, 3.0, 1.0), (19.0, 3.0, 1.2)], baseline=0.45), shifted(curve([(9.0, 3.0, 1.4), (15.0, 4.0, 1.0), (21.0, 3.0, 1.0)], baseline=0.45), 1)),
    "pooping": (curve([(7.5, 1.5, 4.0)], baseline=0.1), curve([(9.0, 1.8, 3.5)], baseline=0.1)),
    "showering": (curve([(7.5, 1.5, 4.0)], baseline=0.08), curve([(9.5, 2.0, 3.0)], baseline=0.08)),
    "washing-hands": (MORNING, shifted(MORNING, 0.5)),
    "brushing-teeth": (curve([(7.5, 1.2, 4.0), (22.5, 1.2, 4.0)], baseline=0.05), curve([(8.5, 1.2, 3.5), (23.0, 1.2, 3.5)], baseline=0.05)),
    "sneezing": (DAY, DAY),
    "coughing": (DAY, DAY),
    "yawning": (curve([(8.0, 2.0, 2.0), (15.0, 2.5, 2.5), (22.5, 1.5, 2.0)], baseline=0.2), curve([(9.5, 2.5, 2.0), (16.0, 3.0, 2.0), (23.0, 1.5, 2.0)], baseline=0.2)),
    "swallowing": (DAY, DAY),
    "farting": (MORNING, shifted(MORNING, 0.5)),
    "blinking": (AWAKE, shifted(AWAKE, 1)),
    "breathing": (FLAT, FLAT),
    "heartbeat": (FLAT, FLAT),
    "eating": (MEALS, shifted(MEALS, 0.5)),
    "taking-a-bite": (MEALS, shifted(MEALS, 0.5)),
    "sipping": (MEALS, shifted(MEALS, 0.5)),
    "drinking-coffee": (curve([(8.0, 1.2, 4.0), (10.5, 1.5, 2.0)], baseline=0.1), curve([(9.5, 1.5, 3.5)], baseline=0.12)),
    "cooking": (curve([(11.5, 1.2, 2.5), (17.5, 1.5, 3.5)], baseline=0.15), curve([(11.5, 1.5, 2.0), (18.0, 1.8, 3.0)], baseline=0.2)),
    "sex": (EVENING, shifted(EVENING, 1)),
    "male-ejaculation": (EVENING, shifted(EVENING, 1)),
    "female-orgasm": (EVENING, shifted(EVENING, 1)),
    "kissing": (EVENING, shifted(EVENING, 1)),
    "hugging": (EVENING, shifted(EVENING, 1)),
    "online": (curve([(21.0, 2.5, 2.5), (14.0, 4.0, 1.2)], baseline=0.55), curve([(21.5, 3.0, 2.5), (15.0, 4.5, 1.4)], baseline=0.6)),
    "scrolling-social": (EVENING, shifted(EVENING, 0.5)),
    "watching-video": (EVENING, shifted(EVENING, 1)),
    "googling": (curve([(10.0, 4.0, 1.2), (21.0, 3.0, 1.5)], baseline=0.5), curve([(14.0, 5.0, 1.3), (21.5, 3.0, 1.4)], baseline=0.5)),
    "gaming": (EVENING, shifted(EVENING, 1)),
    "driving": (RUSH, curve([(12.0, 5.0, 1.2)], baseline=0.4)),
    "public-transport": (RUSH, curve([(12.0, 5.0, 0.9)], baseline=0.4)),
    "flying": (DAY, DAY),
    "working": (WORK, curve([(12.0, 5.0, 0.8)], baseline=0.06)),
    "born": (FLAT, FLAT),
    "died": (FLAT, FLAT),
    "crying": (curve([(9.0, 3.0, 1.5), (20.0, 2.5, 2.0)], baseline=0.3), curve([(10.0, 4.0, 1.5), (20.5, 3.0, 2.0)], baseline=0.3)),
    "laughing": (EVENING, shifted(EVENING, 0.5)),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixture", action="store_true", help="write curves.sample.json to test/fixtures")
    ap.add_argument("--countries", default="USA,NOR", help="ISO3 list for the fixture")
    args = ap.parse_args()

    with open(ROOT / "public" / "data" / "activities.json") as f:
        activities = json.load(f)

    curves = {}
    for a in activities:
        weekday, weekend = BASE[a["id"]]
        curves[a["id"]] = {"_default": {"weekday": weekday, "weekend": weekend}}

    if args.fixture:
        for iso3 in [c.strip().upper() for c in args.countries.split(",") if c.strip()]:
            for a in activities:
                wd = list(curves[a["id"]]["_default"]["weekday"])
                we = list(curves[a["id"]]["_default"]["weekend"])
                if a["group"] == "sleep":
                    shift = 1 if iso3 in ("USA", "AUS") else 0
                    wd = shifted(wd, shift)
                    we = shifted(we, shift + 1)
                curves[a["id"]][iso3] = {"weekday": wd, "weekend": we}
        dest = ROOT / "test" / "fixtures" / "curves.sample.json"
    else:
        dest = ROOT / "public" / "data" / "curves.json"

    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w") as f:
        json.dump(curves, f, separators=(",", ":"))
    print(f"wrote {dest} ({len(curves)} activities, {dest.stat().st_size / 1e3:.1f} KB)")


if __name__ == "__main__":
    main()
