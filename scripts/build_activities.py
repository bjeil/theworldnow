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
    {"id": "sleeping", "maxOf": "__pop__", "label": "Sleeping", "group": "sleep", "kind": "state", "nPerDay": 8.0, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd", "hetus", "owid"]},
    {"id": "awake", "label": "Awake", "group": "sleep", "kind": "state", "nPerDay": 16.0, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd", "hetus"]},
    {"id": "dreaming", "maxOf": "sleeping", "label": "Dreaming (REM)", "group": "sleep", "kind": "state", "nPerDay": 1.75, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "waking-now", "maxOf": "awake", "label": "Waking up right now", "group": "sleep", "kind": "event", "nPerDay": 1.0, "durationSec": 300, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "going-to-bed", "maxOf": "awake", "label": "Going to bed right now", "group": "sleep", "kind": "event", "nPerDay": 1.0, "durationSec": 120, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "on-toilet", "maxOf": "awake", "label": "On the toilet", "group": "body", "kind": "state", "nPerDay": 0.17, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["bach", "popcol"]},
    {"id": "peeing", "maxOf": "on-toilet", "label": "Peeing right now", "group": "body", "kind": "event", "nPerDay": 6.5, "durationSec": 25, "demographic": "all", "unit": "people", "sources": ["bach"]},
    {"id": "pooping", "maxOf": "on-toilet", "label": "Pooping right now", "group": "body", "kind": "event", "nPerDay": 1.0, "durationSec": 300, "demographic": "all", "unit": "people", "sources": ["popcol"]},
    {"id": "showering", "maxOf": "awake", "label": "Showering right now", "group": "body", "kind": "event", "nPerDay": 0.7, "durationSec": 480, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "washing-hands", "maxOf": "awake", "label": "Washing hands right now", "group": "body", "kind": "event", "nPerDay": 8.0, "durationSec": 20, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "brushing-teeth", "maxOf": "awake", "label": "Brushing teeth right now", "group": "body", "kind": "event", "nPerDay": 2.0, "durationSec": 120, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "sneezing", "maxOf": "awake", "label": "Sneezing right now", "group": "body", "kind": "event", "nPerDay": 4.0, "durationSec": 2, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "coughing", "maxOf": "awake", "label": "Coughing right now", "group": "body", "kind": "event", "nPerDay": 10.0, "durationSec": 3, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "yawning", "maxOf": "awake", "label": "Yawning right now", "group": "body", "kind": "event", "nPerDay": 8.0, "durationSec": 5, "demographic": "all", "unit": "people", "sources": ["physio"]},
    {"id": "swallowing", "maxOf": "awake", "label": "Swallowing right now", "group": "body", "kind": "event", "nPerDay": 1500.0, "durationSec": 1, "demographic": "all", "unit": "people", "sources": ["physio"]},
    {"id": "farting", "maxOf": "awake", "label": "Farting right now", "group": "body", "kind": "event", "nPerDay": 15.0, "durationSec": 3, "demographic": "all", "unit": "people", "sources": ["clinical"]},
    {"id": "blinking", "maxOf": "awake", "label": "Blinking right now", "group": "body", "kind": "event", "nPerDay": 15000.0, "durationSec": 0.3, "demographic": "all", "unit": "people", "sources": ["physio"]},
    {"id": "breathing", "label": "Breathing right now", "group": "body", "kind": "event", "nPerDay": 20000.0, "durationSec": 1.5, "ratePrimary": True, "demographic": "all", "unit": "people", "sources": ["physio"]},
    {"id": "heartbeat", "label": "Heartbeats right now", "group": "body", "kind": "event", "nPerDay": 100000.0, "durationSec": 0.8, "ratePrimary": True, "demographic": "all", "unit": "beats", "sources": ["physio"]},
    {"id": "eating", "maxOf": "awake", "label": "Eating right now", "group": "food", "kind": "state", "nPerDay": 1.5, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd", "hetus", "owid"]},
    {"id": "taking-a-bite", "maxOf": "awake", "label": "Taking a bite right now", "group": "food", "kind": "event", "nPerDay": 250.0, "durationSec": 2, "demographic": "all", "unit": "bites", "sources": ["oecd", "estimat"]},
    {"id": "sipping", "maxOf": "awake", "label": "Taking a sip right now", "group": "food", "kind": "event", "nPerDay": 50.0, "durationSec": 2, "demographic": "all", "unit": "sips", "sources": ["estimat"]},
    {"id": "drinking-coffee", "maxOf": "awake", "label": "Drinking coffee right now", "group": "food", "kind": "event", "nPerDay": 0.28, "durationSec": 1200, "demographic": "all", "unit": "people", "sources": ["nca", "ico"]},
    {"id": "cooking", "maxOf": "awake", "label": "Cooking right now", "group": "food", "kind": "event", "nPerDay": 0.5, "durationSec": 1800, "demographic": "all", "unit": "people", "sources": ["oecd", "hetus"]},
    {"id": "sex", "maxOf": "awake", "label": "Having sex right now", "group": "sex", "kind": "event", "nPerDay": 0.07, "durationSec": 324, "demographic": "adults15plus", "unit": "people", "sources": ["waldinger", "durex", "natsal", "gss", "nsfg"]},
    {"id": "male-ejaculation", "maxOf": "awake", "label": "Male ejaculation right now", "group": "sex", "kind": "event", "nPerDay": 0.06, "durationSec": 10, "demographic": "male15plus", "unit": "people", "sources": ["waldinger", "durex", "estimat"]},
    {"id": "female-orgasm", "maxOf": "awake", "label": "Female orgasm right now", "group": "sex", "kind": "event", "nPerDay": 0.05, "durationSec": 20, "demographic": "female15plus", "unit": "people", "sources": ["bhat", "durex", "natsal"]},
    {"id": "kissing", "maxOf": "awake", "label": "Kissing right now", "group": "sex", "kind": "event", "nPerDay": 2.0, "durationSec": 10, "demographic": "adults15plus", "unit": "people", "sources": ["estimat"]},
    {"id": "hugging", "maxOf": "awake", "label": "Hugging right now", "group": "sex", "kind": "event", "nPerDay": 3.0, "durationSec": 15, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "online", "maxOf": "awake", "label": "Online right now", "group": "screen", "kind": "state", "nPerDay": 16.3, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["datareportal"]},
    {"id": "scrolling-social", "maxOf": "awake", "label": "Scrolling social media right now", "group": "screen", "kind": "state", "nPerDay": 1.0, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["datareportal"]},
    {"id": "watching-video", "maxOf": "awake", "label": "Watching video/TV right now", "group": "screen", "kind": "state", "nPerDay": 2.5, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["datareportal"]},
    {"id": "googling", "maxOf": "awake", "label": "Googling right now", "group": "screen", "kind": "event", "nPerDay": 1.05, "durationSec": 20, "demographic": "all", "unit": "searches", "sources": ["google"]},
    {"id": "gaming", "maxOf": "awake", "label": "Gaming right now", "group": "screen", "kind": "state", "nPerDay": 0.5, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["datareportal"]},
    {"id": "driving", "maxOf": "awake", "label": "Driving right now", "group": "transport", "kind": "state", "nPerDay": 0.5, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd", "estimat"]},
    {"id": "public-transport", "maxOf": "awake", "label": "On public transport right now", "group": "transport", "kind": "state", "nPerDay": 0.25, "durationSec": 86400, "demographic": "all", "unit": "people", "sources": ["oecd"]},
    {"id": "flying", "maxOf": "awake", "label": "In a flight right now", "group": "transport", "kind": "event", "nPerDay": 0.00185, "durationSec": 10800, "demographic": "all", "unit": "people", "sources": ["icao", "fr24"]},
    {"id": "working", "maxOf": "awake", "label": "Doing paid work right now", "group": "transport", "kind": "state", "nPerDay": 5.5, "durationSec": 86400, "demographic": "adults15plus", "unit": "people", "sources": ["ilo", "oecd"]},
    {"id": "born", "label": "Being born right now", "group": "vital", "kind": "event", "nPerDay": 0.0000459, "durationSec": 60, "demographic": "all", "unit": "babies", "sources": ["unwpp"]},
    {"id": "died", "label": "Dying right now", "group": "vital", "kind": "event", "nPerDay": 0.0000202, "durationSec": 60, "demographic": "all", "unit": "people", "sources": ["unwpp"]},
    {"id": "crying", "maxOf": "awake", "label": "Crying right now", "group": "vital", "kind": "event", "nPerDay": 1.0, "durationSec": 120, "demographic": "all", "unit": "people", "sources": ["estimat"]},
    {"id": "laughing", "maxOf": "awake", "label": "Laughing right now", "group": "vital", "kind": "event", "nPerDay": 10.0, "durationSec": 5, "demographic": "all", "unit": "people", "sources": ["estimat"]},
]

EXPLANATIONS = {
    "sleeping": "We assume people sleep about 8 of 24 hours, concentrated at local night (per-country day curves refine this). \"Right now\" = population x the share of the day spent asleep x how deep into the local night it is.",
    "awake": "Derived as population minus sleeping, so the two always add up to the total. No separate assumption.",
    "dreaming": "REM sleep is roughly 1.5-2 h of the night. We spread it over the local sleep period and never let it exceed the sleeping counter.",
    "waking-now": "About once a day per person, in the local morning, lasting about 5 minutes.",
    "going-to-bed": "About once a day, in the local evening/night, lasting about 2 minutes.",
    "on-toilet": "People spend about 10 minutes a day on the toilet, peaking after waking and after meals. This is the parent for peeing/pooping.",
    "peeing": "The average adult urinates about 6-7 times a day (BACH study), about 25 s each, spread over waking hours with morning/evening peaks. Capped at \"on the toilet\".",
    "pooping": "About once a day, about 5 minutes (Popcol study / Heaton et al.), usually in the morning. Capped at \"on the toilet\".",
    "showering": "About 0.7 times a day, about 8 minutes, usually in the morning.",
    "washing-hands": "About 8 times a day, about 20 s each (after the toilet, before eating).",
    "brushing-teeth": "Twice a day, about 2 minutes, morning and evening.",
    "sneezing": "A few times a day, a couple of seconds each. Rough estimate.",
    "coughing": "Around 10 times a day when sick, less otherwise; a few seconds each. Rough estimate.",
    "yawning": "About 8 times a day, about 5 s, when tired (morning/afternoon/evening peaks).",
    "swallowing": "Saliva is swallowed about once a minute while awake (~1,500 times/day), about 1 s each.",
    "farting": "About 10-20 times a day (clinical literature estimate), a few seconds each.",
    "blinking": "15-20 blinks per minute while awake (~15,000/day), about 0.3 s each.",
    "breathing": "12-20 breaths per minute (~20,000/day). \"Right now\" counts people mid-inhale (~1.5 s of a ~4 s cycle, so ~35% of people); the per-second rate shown big is the more interesting number.",
    "heartbeat": "60-100 beats per minute at rest (~100,000/day), ~0.8 s per beat - so about 93% of people are mid-beat at any moment.",
    "eating": "60-135 minutes a day depending on the country (OECD time-use data), peaking at local breakfast/lunch/dinner times.",
    "taking-a-bite": "About 60-110 bites per meal, ~3 meals a day, ~2 s per bite - only while eating.",
    "sipping": "About 50 sips of a drink per day, ~2 s each.",
    "drinking-coffee": "About 2.25 billion cups of coffee are drunk worldwide per day (NCA/ICO), so ~0.28 cups per person per day; a cup takes ~20 min to drink.",
    "cooking": "About half the population cooks on a given day, ~30 min, around meal times.",
    "sex": "About 7% of adults (15+) have sex on an average day (frequency surveys: Durex, Natsal, GSS, NSFG); the median session lasts ~5.4 min (Waldinger et al. 2005). Peaks in the local evening/night.",
    "male-ejaculation": "Follows the sex rate - about 6% of adult men per day; the ejaculation itself lasts ~5-15 s.",
    "female-orgasm": "About 5% of adult women per day; the orgasm itself lasts tens of seconds (time from penetration to orgasm is ~13 min on average, Bhat & Shastry 2020).",
    "kissing": "A couple of times a day, ~10 s each, mostly in the evening. Estimate.",
    "hugging": "About 3 times a day, ~15 s each. Estimate.",
    "online": "About two thirds of the world's population is online (~5.5 bn, DataReportal); averaged over everyone that is ~16 h/day, weighted to local evenings. Never more than \"awake\".",
    "scrolling-social": "About 1 hour a day on social media (DataReportal), mostly evenings. Never more than \"awake\" or \"online\".",
    "watching-video": "About 2.5 hours a day of video/TV (DataReportal), mostly evenings.",
    "googling": "Google handles ~99,000 searches per second (~8.5 bn/day), i.e. about 1 search per person per day, ~20 s each.",
    "gaming": "About 0.5 h/day on games, mostly evenings. Estimate from games-industry usage stats.",
    "driving": "About 30 min/day per person on average including non-drivers (OECD time-use), with rush-hour peaks. Never more than \"awake\".",
    "public-transport": "About 15 min/day on buses/trains (OECD time-use), rush hours.",
    "flying": "About 100,000 commercial flights a day (~1-2 million people airborne, ICAO/FlightRadar24) - about 0.002 flights per person per day, ~3 h average flight.",
    "working": "Paid work averages ~5.5 h/day per adult (ILO/OECD), concentrated on weekdays 8-18 local time, low on weekends. Never more than \"awake\".",
    "born": "UN WPP 2024: about 4.3 babies born per second worldwide, roughly uniform over the day. This is what grows the world-population stat.",
    "died": "UN WPP 2024: about 1.9 people die per second worldwide, roughly uniform over the day.",
    "crying": "About once a day, ~2 min. Rough estimate.",
    "laughing": "About 10 times a day, ~5 s each. Rough estimate, mostly evenings."
}

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
                "maxOf": a.get("maxOf"),
                "ratePrimary": bool(a.get("ratePrimary", False)),
                "explanation": EXPLANATIONS[a["id"]],
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
