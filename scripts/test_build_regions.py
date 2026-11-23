import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "test" / "fixtures"


class TestRegionsFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FIXTURES / "regions.sample.json") as f:
            cls.regions = json.load(f)
        with open(FIXTURES / "bands.sample.json") as f:
            cls.bands = json.load(f)

    def test_schema_and_types(self):
        self.assertGreater(len(self.regions), 0)
        for r in self.regions:
            self.assertEqual(set(r), {"iso3", "name", "tzid", "pop", "popM15plus", "popF15plus", "lon", "lat"})
            self.assertRegex(r["iso3"], r"^[A-Z]{3}$")
            self.assertIsInstance(r["name"], str)
            self.assertIsInstance(r["tzid"], str)
            self.assertGreater(len(r["tzid"]), 0)
            for k in ("pop", "popM15plus", "popF15plus"):
                self.assertIsInstance(r[k], int)
                self.assertGreaterEqual(r[k], 0)
            self.assertLessEqual(r["popM15plus"], r["pop"])
            self.assertLessEqual(r["popF15plus"], r["pop"])
            self.assertGreaterEqual(r["lon"], -180.0)
            self.assertLessEqual(r["lon"], 180.0)
            self.assertGreaterEqual(r["lat"], -90.0)
            self.assertLessEqual(r["lat"], 90.0)

    def test_regions_unique(self):
        keys = [(r["iso3"], r["tzid"]) for r in self.regions]
        self.assertEqual(len(keys), len(set(keys)))

    def test_multi_timezone_country_present(self):
        by_country = {}
        for r in self.regions:
            by_country.setdefault(r["iso3"], set()).add(r["tzid"])
        self.assertIn("USA", by_country)
        self.assertGreater(len(by_country["USA"]), 1)

    def test_bands_cover_360_degrees(self):
        self.assertEqual(len(self.bands), 360)
        for i, b in enumerate(self.bands):
            self.assertEqual(b["band"], i)
            self.assertEqual(b["lonMin"], i - 180)
            self.assertIsInstance(b["pop"], int)
            self.assertGreaterEqual(b["pop"], 0)

    def test_bands_partition_regions(self):
        ids = []
        for b in self.bands:
            ids.extend(b["regions"])
        expected = [f"{r['iso3']}|{r['tzid']}" for r in self.regions]
        self.assertEqual(sorted(ids), sorted(expected))
        self.assertEqual(sum(b["pop"] for b in self.bands), sum(r["pop"] for r in self.regions))

    def test_bands_have_lat_range(self):
        for b in self.bands:
            self.assertIn("latMin", b)
            self.assertIn("latMax", b)
            self.assertLessEqual(b["latMin"], b["latMax"])
            self.assertGreaterEqual(b["latMin"], -85)
            self.assertLessEqual(b["latMax"], 85)

    def test_band_assignment_matches_lon(self):
        import math

        for r in self.regions:
            b = min(359, max(0, int(math.floor(r["lon"])) + 180))
            self.assertIn(f"{r['iso3']}|{r['tzid']}", self.bands[b]["regions"])


    def test_small_countries_present(self):
        import json as _json

        with open(ROOT / "public" / "data" / "regions.json") as f:
            isos = {r["iso3"] for r in _json.load(f)}
        for small in ("SGP", "LUX", "MCO", "VAT", "MLT", "AND", "LIE", "SMR", "BRB", "VUT"):
            self.assertIn(small, isos)
        self.assertGreaterEqual(len(isos), 230)

    def test_meta_matches_population_sum(self):
        import json as _json

        for base in (ROOT / "public" / "data", ROOT / "test" / "fixtures"):
            meta = _json.load(open(base / "meta.json"))
            regions_file = "regions.json" if base.name == "data" else "regions.sample.json"
            regions = _json.load(open(base / regions_file))
            total = sum(r["pop"] for r in regions)
            self.assertAlmostEqual(total / meta["worldPopulation"], 1.0, places=3)
            self.assertEqual(meta["regions"], len(regions))


if __name__ == "__main__":
    unittest.main()
