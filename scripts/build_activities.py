"""Generate public/data/activities.json: the counter catalog with rates, durations, demographics, sources and formulas."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

S = {
    "oecd": {"title": "OECD Time Use Database", "url": "https://www.oecd.org/en/topics/time-use.html"},
    "hetus": {"title": "Eurostat HETUS (Harmonised European Time Use Survey)", "url": "https://ec.europa.eu/eurostat/web/time-use"},
    "owid": {"title": "Our World in Data - Time Use", "url": "https://ourworldindata.org/time-use"},
    "bach": {"title": "BACH study / clinical reference on voiding frequency (6-7x/day)", "url": "https://pubmed.ncbi.nlm.nih.gov/?term=urinary+frequency+6-7+times+per+day"},
    "popcol": {"title": "Popcol study / Heaton et al. on bowel habit (~1/day, ~5 min)", "url": "https://pubmed.ncbi.nlm.nih.gov/?term=Heaton+bowel+habit+defecation+frequency"},
    "waldinger": {"title": "Waldinger et al. 2005, J Sex Med - IELT median 5.4 min", "url": "https://pubmed.ncbi.nlm.nih.gov/15784561/"},
    "bhat": {"title": "Bhat & Shastry 2020, J Sex Med - time to female orgasm ~13 min", "url": "https://pubmed.ncbi.nlm.nih.gov/?term=Bhat+Shastry+female+orgasm+time"},
    "durex": {"title": "Durex Global Sex Survey (sex frequency by country)", "url": "https://www.durex.com"},
    "natsal": {"title": "Natsal (UK National Survey of Sexual Attitudes and Lifestyles)", "url": "https://www.natsal.ac.uk"},
    "gss": {"title": "GSS (US General Social Survey) sexual frequency", "url": "https://gss.norc.org"},
    "nsfg": {"title": "NSFG (US National Survey of Family Growth)", "url": "https://www.cdc.gov/nchs/nsfg/index.htm"},
    "datareportal": {"title": "DataReportal - Digital 2025 (online population, screen time)", "url": "https://datareportal.com"},
    "google": {"title": "Google published search volume (~99,000 searches/s, ~8.5 bn/day)", "url": "https://blog.google"},
    "icao": {"title": "ICAO air traffic statistics", "url": "https://www.icao.int"},
    "fr24": {"title": "FlightRadar24 - ~10,000-20,000 commercial flights airborne at once", "url": "https://www.flightradar24.com"},
    "nca": {"title": "National Coffee Association (US)", "url": "https://www.ncausa.org"},
    "ico": {"title": "International Coffee Organization - ~2.25 bn cups/day globally", "url": "https://www.ico-coffee.org"},
    "unwpp": {"title": "UN World Population Prospects 2024 (births ~4.3/s, deaths ~1.9/s)", "url": "https://population.un.org/wpp"},
    "ilo": {"title": "ILO - labour force and working time", "url": "https://www.ilo.org"},
    "physio": {"title": "Physiology reference (StatPearls): blink 15-20/min, breathing 12-20/min, heart rate 60-100/min", "url": "https://www.ncbi.nlm.nih.gov/books/"},
    "clinical": {"title": "Clinical literature estimate (flatulence ~10-20/day)", "url": "https://pubmed.ncbi.nlm.nih.gov/?term=flatulence+frequency+per+day"},
    "estimat": {"title": "Expert estimate (no single source)", "url": "https://en.wikipedia.org/wiki/Estimate"},
}

ACTIVITIES = [
    {"id": "sleeping", "label": "Sleeping", "group": "sleep", "kind": "state", "nPerDay": 8.0, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd", "hetus", "owid"]},
    {"id": "awake", "label": "Awake", "group": "sleep", "kind": "state", "nPerDay": 16.0, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd", "hetus"]},
    {"id": "dreaming", "label": "Dreaming (REM)", "group": "sleep", "kind": "state", "nPerDay": 1.75, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "waking-now", "label": "Waking up right now", "group": "sleep", "kind": "event", "nPerDay": 1.0, "durationSec": 300, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "going-to-bed", "label": "Going to bed right now", "group": "sleep", "kind": "event", "nPerDay": 1.0, "durationSec": 120, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "on-toilet", "label": "On the toilet", "group": "body", "kind": "state", "nPerDay": 0.17, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["bach", "popcol"]},
    {"id": "peeing", "label": "Peeing right now", "group": "body", "kind": "event", "nPerDay": 6.5, "durationSec": 25, "demographic": "all", "unit": "people", "sources": ["bach"]},
    {"id": "pooping", "label": "Pooping right now", "group": "body", "kind": "event", "nPerDay": 1.0, "durationSec": 300, "demographic": "all", "unit": "people", "sources": ["popcol"]},
    {"id": "showering", "label": "Showering right now", "group": "body", "kind": "event", "nPerDay": 0.7, "durationSec": 480, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "washing-hands", "label": "Washing hands right now", "group": "body", "kind": "event", "nPerDay": 8.0, "durationSec": 20, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "brushing-teeth", "label": "Brushing teeth right now", "group": "body", "kind": "event", "nPerDay": 2.0, "durationSec": 120, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "sneezing", "label": "Sneezing right now", "group": "body", "kind": "event", "nPerDay": 4.0, "durationSec": 2, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "coughing", "label": "Coughing right now", "group": "body", "kind": "event", "nPerDay": 10.0, "durationSec": 3, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "yawning", "label": "Yawning right now", "group": "body", "kind": "event", "nPerDay": 8.0, "durationSec": 5, "demographic": "all", "unit": "people", "sources": ["physio"]},
    {"id": "swallowing", "label": "Swallowing right now", "group": "body", "kind": "event", "nPerDay": 1500.0, "durationSec": 1, "demographic": "all", "unit": "people", "sources": ["physio"]},
    {"id": "farting", "label": "Farting right now", "group": "body", "kind": "event", "nPerDay": 15.0, "durationSec": 3, "demographic": "all", "unit": "people", "sources": ["clinical"]},
    {"id": "blinking", "label": "Blinking right now", "group": "body", "kind": "event", "nPerDay": 15000.0, "durationSec": 0.3, "demographic": "all", "unit": "people", "sources": ["physio"]},
    {"id": "breathing", "label": "Breathing right now", "group": "body", "kind": "event", "nPerDay": 20000.0, "durationSec": 4, "demographic": "all", "unit": "people", "sources": ["physio"]},
    {"id": "heartbeat", "label": "Heartbeats right now", "group": "body", "kind": "event", "nPerDay": 100000.0, "durationSec": 0.8, "demographic": "all", "unit": "beats", "sources": ["physio"]},
    {"id": "eating", "label": "Eating right now", "group": "food", "kind": "state", "nPerDay": 1.5, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd", "hetus", "owid"]},
    {"id": "taking-a-bite", "label": "Taking a bite right now", "group": "food", "kind": "event", "nPerDay": 250.0, "durationSec": 2, "demographic": "all", "unit": "bites", "sources": ["oecd", "estimat"]},
    {"id": "sipping", "label": "Taking a sip right now", "group": "food", "kind": "event", "nPerDay": 50.0, "durationSec": 2, "demographic": "all", "unit": "sips", "sources": ["estimat"]},
    {"id": "drinking-coffee", "label": "Drinking coffee right now", "group": "food", "kind": "event", "nPerDay": 0.28, "durationSec": 1200, "demographic": "all", "unit": "people", "sources": ["nca", "ico"]},
    {"id": "cooking", "label": "Cooking right now", "group": "food", "kind": "event", "nPerDay": 0.5, "durationSec": 1800, "demographic": "all", "unit": "people", "sources": ["oecd", "hetus"]},
    {"id": "sex", "label": "Having sex right now", "group": "sex", "kind": "event", "nPerDay": 0.07, "durationSec": 324, "demographic": "adults15plus", "unit": "people", "sources": ["waldinger", "durex", "natsal", "gss", "nsfg"]},
    {"id": "male-ejaculation", "label": "Male ejaculation right now", "group": "sex", "kind": "event", "nPerDay": 0.06, "durationSec": 10, "demographic": "male15plus", "unit": "people", "sources": ["waldinger", "durex", "estimat"]},
    {"id": "female-orgasm", "label": "Female orgasm right now", "group": "sex", "kind": "event", "nPerDay": 0.05, "durationSec": 20, "demographic": "female15plus", "unit": "people", "sources": ["bhat", "durex", "natsal"]},
    {"id": "kissing", "label": "Kissing right now", "group": "sex", "kind": "event", "nPerDay": 2.0, "durationSec": 10, "demographic": "adults15plus", "unit": "people", "sources": ["estimat"]},
    {"id": "hugging", "label": "Hugging right now", "group": "sex", "kind": "event", "nPerDay": 3.0, "durationSec": 15, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "online", "label": "Online right now", "group": "screen", "kind": "state", "nPerDay": 16.3, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["datareportal"]},
    {"id": "scrolling-social", "label": "Scrolling social media right now", "group": "screen", "kind": "state", "nPerDay": 1.0, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["datareportal"]},
    {"id": "watching-video", "label": "Watching video/TV right now", "group": "screen", "kind": "state", "nPerDay": 2.5, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["datareportal"]},
    {"id": "googling", "label": "Googling right now", "group": "screen", "kind": "event", "nPerDay": 1.05, "durationSec": 20, "demographic": "all", "unit": "searches", "sources": ["google"]},
    {"id": "gaming", "label": "Gaming right now", "group": "screen", "kind": "state", "nPerDay": 0.5, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["datareportal"]},
    {"id": "driving", "label": "Driving right now", "group": "transport", "kind": "state", "nPerDay": 0.5, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd", "estimat"]},
    {"id": "public-transport", "label": "On public transport right now", "group": "transport", "kind": "state", "nPerDay": 0.25, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd"]},
    {"id": "flying", "label": "In a flight right now", "group": "transport", "kind": "event", "nPerDay": 0.00185, "durationSec": 10800, "demographic": "all", "unit": "people", "sources": ["icao", "fr24"]},
    {"id": "working", "label": "Doing paid work right now", "group": "transport", "kind": "state", "nPerDay": 5.5, "durationSec": 86400, "demographic": "adults15plus", "unit": "people", "sources": ["ilo", "oecd"]},
    {"id": "born", "label": "Being born right now", "group": "vital", "kind": "event", "nPerDay": 0.0000459, "durationSec": 60, "demographic": "all", "unit": "babies", "sources": ["unwpp"]},
    {"id": "died", "label": "Dying right now", "group": "vital", "kind": "event", "nPerDay": 0.0000202, "durationSec": 60, "demographic": "all", "unit": "people", "sources": ["unwpp"]},
    {"id": "crying", "label": "Crying right now", "group": "vital", "kind": "event", "nPerDay": 1.0, "durationSec": 120, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "laughing", "label": "Laughing right now", "group": "vital", "kind": "event", "nPerDay": 10.0, "durationSec": 5, "demographic": "all", "unit": "people", "sources": ["estimat"]},
]

DEMOGRAPHIC_POP = {
    "all": "pop",
    "adults15plus": "popM15plus + popF15plus",
    "male15plus": "popM15plus",
    "female15plus": "popF15plus",
}


def main():
    out = []
    for a in ACTIVITIES:
        if a["kind"] == "state":
            formula = (
                f"right now = {DEMOGRAPHIC_POP[a['demographic']]} x {a['nPerDay']}h/24 x dayCurve(localTime, weekday)"
            )
        else:
            formula = (
                f"rate = {DEMOGRAPHIC_POP[a['demographic']]} x {a['nPerDay']}/day x dayCurve(localTime, weekday) / 86400; "
                f"right now = rate x {a['durationSec']} s"
            )
        out.append(
            {
                "id": a["id"],
                "label": a["label"],
                "group": a["group"],
                "kind": a["kind"],
                "nPerDay": a["nPerDay"],
                "demographic": a["demographic"],
                "durationSec": a["durationSec"],
                "unit": a["unit"],
                "sources": [S[k] for k in a["sources"]],
                "formula": formula,
                "estimate": True,
            }
        )
    dest = ROOT / "public" / "data" / "activities.json"
    with open(dest, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {dest} ({len(out)} activities, {dest.stat().st_size / 1e3:.1f} KB)")


if __name__ == "__main__":
    main()
