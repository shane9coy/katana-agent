import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path("/Users/sc/katana-agent/oracle/astro-companion/scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class OracleScoringTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ORACLE_STATE_DIR"] = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()
        os.environ.pop("ORACLE_STATE_DIR", None)

    def test_contract_signing_gets_retrograde_penalty(self):
        import oracle_scoring

        decision_objects = [
            {
                "id": "evt_1",
                "kind": "calendar_event",
                "title": "Contract signing with partner",
                "starts_at": "2026-03-10T15:00:00-04:00",
                "domain_tags": [],
                "urgency": 0.8,
            }
        ]
        astro = {
            "moon_phase": "waxing",
            "moon_sign": "Virgo",
            "mercury_retrograde": True,
            "void_of_course": False,
            "eclipse_window": False,
            "aspects": ["Mercury trine Jupiter"]
        }
        profile = {
            "life_domains": {
                "communication": 0.9,
                "relationships": 1.0,
                "finance": 0.8,
                "creativity": 0.7,
                "rest": 0.6,
                "decisive_action": 0.85,
                "launches": 0.9,
                "health": 0.8,
                "spiritual": 0.6,
            }
        }
        weights = {
            "communication": {"mercury_weight": 0.5, "mercury_rx_penalty": 0.8},
            "finance": {"saturn_weight": 0.2, "mercury_rx_penalty": 0.5},
            "launches": {"mercury_rx_penalty": 0.8, "moon_phase_weight": 0.3},
            "decisive_action": {"mars_weight": 0.4, "mercury_rx_penalty": 0.3},
            "relationships": {"venus_weight": 0.5},
            "creativity": {"venus_weight": 0.4},
            "rest": {"moon_weight": 0.5},
            "health": {"sun_weight": 0.35},
            "spiritual": {"neptune_weight": 0.35},
        }

        scored = oracle_scoring.score_decision_objects(decision_objects, astro, profile, weights)
        self.assertEqual(len(scored), 1)
        item = scored[0]
        self.assertTrue(any("retrograde" in caution.lower() for caution in item["cautions"]))
        self.assertLess(item["score"], 2.4)

    def test_title_tagging_detects_relationships(self):
        import oracle_scoring

        tags = oracle_scoring.infer_domain_tags({"title": "Relationship repair dinner", "kind": "calendar_event"})
        self.assertIn("relationships", tags)


if __name__ == "__main__":
    unittest.main()
