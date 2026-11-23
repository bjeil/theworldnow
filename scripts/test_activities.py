import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GROUPS = {"sleep", "body", "food", "sex", "screen", "transport", "vital"}
DEMOGRAPHICS = {"all", "adults15plus", "male15plus", "female15plus"}


class TestActivities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROOT / "public" / "data" / "activities.json") as f:
            cls.activities = json.load(f)

    def test_schema(self):
        self.assertGreater(len(self.activities), 20)
        for a in self.activities:
            self.assertEqual(
                set(a),
                {"id", "label", "group", "kind", "nPerDay", "demographic", "maxOf", "ratePrimary", "explanation", "durationSec", "unit", "sources", "formula", "estimate"},
            )
            self.assertIn(a["group"], GROUPS)
            self.assertIn(a["kind"], {"event", "state"})
            self.assertIn(a["demographic"], DEMOGRAPHICS)
            self.assertGreater(a["nPerDay"], 0)
            self.assertGreater(a["durationSec"], 0)
            self.assertTrue(a["estimate"])
            self.assertTrue(a["formula"])
            self.assertGreater(len(a["explanation"]), 40)
            self.assertGreaterEqual(len(a["sources"]), 1)
            for s in a["sources"]:
                self.assertIn("title", s)
                self.assertTrue(s["url"].startswith("https://"))

    def test_unique_ids(self):
        ids = [a["id"] for a in self.activities]
        self.assertEqual(len(ids), len(set(ids)))

    def test_state_counters_use_whole_day(self):
        for a in self.activities:
            if a["kind"] == "state":
                self.assertEqual(a["durationSec"], 86400)

    def test_sex_counters_scoped_to_adults(self):
        by_id = {a["id"]: a for a in self.activities}
        self.assertEqual(by_id["sex"]["demographic"], "adults15plus")
        self.assertEqual(by_id["male-ejaculation"]["demographic"], "male15plus")
        self.assertEqual(by_id["female-orgasm"]["demographic"], "female15plus")

    def test_all_groups_covered(self):
        self.assertEqual({a["group"] for a in self.activities}, GROUPS)


if __name__ == "__main__":
    unittest.main()
