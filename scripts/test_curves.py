import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestCurves(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROOT / "public" / "data" / "curves.json") as f:
            cls.curves = json.load(f)
        with open(ROOT / "public" / "data" / "activities.json") as f:
            cls.activities = json.load(f)
        with open(ROOT / "test" / "fixtures" / "curves.sample.json") as f:
            cls.fixture = json.load(f)

    def test_every_activity_has_default_curve(self):
        ids = {a["id"] for a in self.activities}
        self.assertEqual(set(self.curves), ids)
        for aid, entry in self.curves.items():
            self.assertIn("_default", entry)
            for day in ("weekday", "weekend"):
                c = entry["_default"][day]
                self.assertEqual(len(c), 24)
                self.assertTrue(all(v >= 0 for v in c))
                self.assertAlmostEqual(sum(c), 24.0, places=2)

    def test_fixture_has_country_overrides(self):
        sleeping = self.fixture["sleeping"]
        self.assertIn("_default", sleeping)
        self.assertIn("USA", sleeping)
        self.assertIn("NOR", sleeping)
        for iso3 in ("USA", "NOR"):
            self.assertEqual(len(sleeping[iso3]["weekday"]), 24)
            self.assertAlmostEqual(sum(sleeping[iso3]["weekend"]), 24.0, places=2)


if __name__ == "__main__":
    unittest.main()
