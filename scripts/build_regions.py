"""Build regions.json (country x timezone) and bands.json (1-degree longitude bands) from pinned public datasets."""

import argparse
import csv
import gzip
import json
import sys
from datetime import datetime
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parent.parent

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/9380cca83db5f9aef52d5e762765100745f84b27/geojson/ne_110m_admin_0_countries.geojson"
TZ_URL = "https://github.com/evansiroky/timezone-boundary-builder/releases/download/2024a/timezones.geojson.zip"
GHSL_URL = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/GHS_POP_E2020_GLOBE_R2023A_4326_30ss/V1-0/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.zip"
WPP_URL = "https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_PopulationByAge5GroupSex_Medium.csv.gz"

WPP_MAX_YEAR = 2025
BLOCK_ROWS = 1024


def download(url, dest):
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"cached: {dest}")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    tmp.rename(dest)
    print(f"saved: {dest} ({dest.stat().st_size / 1e6:.1f} MB)")
    return dest


def load_countries(path):
    with open(path) as f:
        gj = json.load(f)
    out = []
    for feat in gj["features"]:
        props = feat["properties"]
        iso3 = (props.get("ISO_A3") or "").strip()
        if iso3 == "-99":
            iso3 = (props.get("ADM0_A3") or "").strip()
        if not iso3 or iso3 == "-99":
            continue
        name = props.get("NAME_EN") or props.get("NAME") or iso3
        out.append({"iso3": iso3, "name": name, "geom": shape(feat["geometry"]).buffer(0)})
    return out


def load_timezones(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.lower().endswith((".geojson", ".json")) and not n.endswith("/")]
        if not names:
            raise RuntimeError(f"no geojson in {path}")
        with z.open(names[0]) as f:
            gj = json.load(f)
    out = []
    for feat in gj["features"]:
        tzid = feat["properties"].get("tzid")
        if not tzid:
            continue
        g = shape(feat["geometry"]).buffer(0)
        if not g.is_empty:
            out.append((tzid, g))
    return out


def polygonal(g):
    if g.is_empty:
        return g
    if g.geom_type == "Polygon":
        return g
    if g.geom_type == "MultiPolygon":
        return g
    parts = [p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")]
    polys = []
    for p in parts:
        if p.geom_type == "Polygon":
            polys.append(p)
        else:
            polys.extend(p.geoms)
    if not polys:
        return Polygon()
    return MultiPolygon(polys) if len(polys) > 1 else polys[0]


def build_regions(countries, timezones, only=None):
    tz_geoms = [g for _, g in timezones]
    tree = STRtree(tz_geoms)
    regions = []
    for c in countries:
        if only and c["iso3"] not in only:
            continue
        for idx in tree.query(c["geom"]):
            tzid, tzgeom = timezones[idx]
            inter = polygonal(c["geom"].intersection(tzgeom))
            if inter.is_empty or inter.area <= 1e-12:
                continue
            regions.append({"iso3": c["iso3"], "name": c["name"], "tzid": tzid, "geom": inter})
    regions.sort(key=lambda r: (r["iso3"], r["tzid"]))
    return regions


def zonal_pop(src, geom):
    t = src.transform
    minx, miny, maxx, maxy = geom.bounds
    col0 = max(0, int(np.floor((minx - t.c) / t.a)))
    col1 = min(src.width, int(np.ceil((maxx - t.c) / t.a)))
    row0 = max(0, int(np.floor((maxy - t.f) / t.e)))
    row1 = min(src.height, int(np.ceil((miny - t.f) / t.e)))
    if col1 <= col0 or row1 <= row0:
        c = geom.representative_point()
        return 0.0, c.x, c.y
    bw = col1 - col0
    pop = 0.0
    lon_sum = 0.0
    lat_sum = 0.0
    for r0 in range(row0, row1, BLOCK_ROWS):
        bh = min(BLOCK_ROWS, row1 - r0)
        win = Window(col0, r0, bw, bh)
        arr = src.read(1, window=win, masked=True)
        bt = src.window_transform(win)
        mask = rasterize(
            [(geom, 1)], out_shape=(bh, bw), transform=bt, fill=0, dtype="uint8", all_touched=False
        ).astype(bool)
        filled = np.nan_to_num(arr.filled(0.0), nan=0.0, posinf=0.0, neginf=0.0)
        filled = np.clip(filled, 0.0, None)
        m = filled * mask * (~arr.mask)
        if m.any():
            pop += float(m.sum())
            xs = bt.c + (np.arange(bw) + 0.5) * bt.a
            ys = bt.f + (np.arange(bh) + 0.5) * bt.e
            lon_sum += float(m.sum(axis=0) @ xs)
            lat_sum += float(m.sum(axis=1) @ ys)
    if pop > 0:
        return pop, lon_sum / pop, lat_sum / pop
    c = geom.representative_point()
    return 0.0, c.x, c.y


def load_age_sex(path):
    per_iso = {}
    with gzip.open(path, "rt", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["LocTypeID"] != "4":
                continue
            try:
                year = int(row["Time"])
                age_start = int(row["AgeGrpStart"])
            except ValueError:
                continue
            if year > WPP_MAX_YEAR or age_start < 15:
                continue
            iso3 = (row["ISO3_code"] or "").strip()
            if not iso3:
                continue
            m = float(row["PopMale"]) * 1000.0
            fe = float(row["PopFemale"]) * 1000.0
            d = per_iso.setdefault(iso3, {})
            cur = d.get(year, (0.0, 0.0))
            d[year] = (cur[0] + m, cur[1] + fe)
    out = {}
    for iso3, years in per_iso.items():
        best = max(years)
        out[iso3] = years[best]
    return out


def load_total_pop(path, year):
    totals = {}
    with gzip.open(path, "rt", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["LocTypeID"] != "4":
                continue
            try:
                if int(row["Time"]) != year:
                    continue
                totals[row["ISO3_code"].strip()] = totals.get(row["ISO3_code"].strip(), 0.0) + float(row["PopTotal"]) * 1000.0
            except ValueError:
                continue
    return totals


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw-dir", default=str(ROOT / "data" / "raw"))
    ap.add_argument("--out-dir", default=str(ROOT / "public" / "data"))
    ap.add_argument("--countries", default="", help="comma-separated ISO3 subset (for fixtures)")
    ap.add_argument("--fixture", action="store_true", help="write regions.sample.json / bands.sample.json to test/fixtures")
    args = ap.parse_args()

    raw = Path(args.raw_dir)
    ne_path = download(NE_URL, raw / "ne_110m_admin_0_countries.geojson")
    tz_path = download(TZ_URL, raw / "timezones-2024a.geojson.zip")
    ghsl_zip = download(GHSL_URL, raw / "GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.zip")
    wpp_path = download(WPP_URL, raw / "WPP2024_PopulationByAge5GroupSex_Medium.csv.gz")

    tif_path = raw / "ghl_pop_e2020_4326_30ss.tif"
    if not tif_path.exists():
        with zipfile.ZipFile(ghsl_zip) as z:
            tifs = [n for n in z.namelist() if n.lower().endswith(".tif")]
            biggest = max(tifs, key=lambda n: z.getinfo(n).file_size)
            with z.open(biggest) as srcf, open(tif_path, "wb") as dstf:
                while True:
                    chunk = srcf.read(1 << 22)
                    if not chunk:
                        break
                    dstf.write(chunk)
        print(f"extracted: {tif_path}")

    countries = load_countries(ne_path)
    timezones = load_timezones(tz_path)
    only = {c.strip().upper() for c in args.countries.split(",") if c.strip()} or None
    regions = build_regions(countries, timezones, only=only)
    print(f"regions (country x tz): {len(regions)}")

    age_sex = load_age_sex(wpp_path)

    with rasterio.open(tif_path) as src:
        for i, r in enumerate(regions):
            pop, lon, lat = zonal_pop(src, r["geom"])
            r["pop"] = pop
            r["lon"] = lon
            r["lat"] = lat
            if (i + 1) % 200 == 0:
                print(f"  zonal stats {i + 1}/{len(regions)}")

    year = datetime.now().year
    total_pop = load_total_pop(wpp_path, year)

    country_raster = {}
    for r in regions:
        country_raster[r["iso3"]] = country_raster.get(r["iso3"], 0.0) + r["pop"]
    scaled = 0
    for r in regions:
        target = total_pop.get(r["iso3"], 0.0)
        base = country_raster.get(r["iso3"], 0.0)
        if target > 0 and base > 0:
            r["pop"] *= target / base
            scaled += 1

    country_pop = {}
    for r in regions:
        country_pop[r["iso3"]] = country_pop.get(r["iso3"], 0.0) + r["pop"]
    country_adult = {}
    for r in regions:
        m15, f15 = age_sex.get(r["iso3"], (0.0, 0.0))
        country_adult[r["iso3"]] = (m15, f15)
    for r in regions:
        cp = country_pop.get(r["iso3"], 0.0)
        m15, f15 = country_adult.get(r["iso3"], (0.0, 0.0))
        adults = m15 + f15
        scale = min(1.0, cp / adults) if adults > 0 and cp > 0 else 0.0
        if r["pop"] > 0:
            r["popM15plus"] = m15 * scale * r["pop"] / cp if cp > 0 else 0.0
            r["popF15plus"] = f15 * scale * r["pop"] / cp if cp > 0 else 0.0
        else:
            r["popM15plus"] = 0.0
            r["popF15plus"] = 0.0

    out_regions = []
    for r in regions:
        pop = int(round(r["pop"]))
        m = int(round(r["popM15plus"]))
        f = int(round(r["popF15plus"]))
        if m + f > pop:
            over = m + f - pop
            if m >= over:
                m -= over
            else:
                f -= over - m
                m = 0
        out_regions.append(
            {
                "iso3": r["iso3"],
                "name": r["name"],
                "tzid": r["tzid"],
                "pop": pop,
                "popM15plus": m,
                "popF15plus": f,
                "lon": round(r["lon"], 4),
                "lat": round(r["lat"], 4),
            }
        )

    bands = []
    for b in range(360):
        bands.append({"band": b, "lonMin": b - 180, "pop": 0, "regions": []})
    for r in out_regions:
        b = int(np.floor(r["lon"])) + 180
        b = min(359, max(0, b))
        bands[b]["pop"] += r["pop"]
        bands[b]["regions"].append(f"{r['iso3']}|{r['tzid']}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "populationYear": year,
        "worldPopulation": int(round(sum(r["pop"] for r in regions))),
        "regions": len(regions),
    }
    meta_dir = ROOT / "test" / "fixtures" if args.fixture else out_dir
    meta_dir.mkdir(parents=True, exist_ok=True)
    with open(meta_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")
    print(f"population scaled to UN WPP {year} for {scaled} countries; world pop {meta['worldPopulation']:,}")
    if args.fixture:
        fixture_dir = ROOT / "test" / "fixtures"
        fixture_dir.mkdir(parents=True, exist_ok=True)
        regions_file = fixture_dir / "regions.sample.json"
        bands_file = fixture_dir / "bands.sample.json"
    else:
        regions_file = out_dir / "regions.json"
        bands_file = out_dir / "bands.json"

    with open(regions_file, "w") as f:
        json.dump(out_regions, f, separators=(",", ":"))
    with open(bands_file, "w") as f:
        json.dump(bands, f, separators=(",", ":"))

    total = sum(r["pop"] for r in out_regions)
    print(f"wrote {regions_file} ({regions_file.stat().st_size / 1e3:.1f} KB, {len(out_regions)} regions, total pop {total:,.0f})")
    print(f"wrote {bands_file} ({bands_file.stat().st_size / 1e3:.1f} KB, {len(bands)} bands)")


if __name__ == "__main__":
    sys.exit(main())
