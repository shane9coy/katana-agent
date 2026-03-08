import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path("/Users/sc/katana-agent/oracle/astro-companion/scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class OracleProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ORACLE_STATE_DIR"] = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()
        os.environ.pop("ORACLE_STATE_DIR", None)

    def test_validate_profile_flags_missing_coordinates(self):
        import oracle_profile

        profile = {
            "birth_chart": {
                "date": "1991-08-21",
                "time": "16:20",
                "time_known": True,
                "location": "Sandusky, Ohio",
                "latitude": None,
                "longitude": None,
                "timezone": "America/New_York",
            }
        }

        result = oracle_profile.validate_profile(profile)
        self.assertFalse(result["ok"])
        self.assertTrue(any("latitude" in error.lower() or "coordinates" in error.lower() for error in result["errors"]))

    def test_validate_profile_allows_unknown_birth_time_with_warning(self):
        import oracle_profile

        profile = {
            "birth_chart": {
                "date": "1991-08-21",
                "time": "",
                "time_known": False,
                "location": "Sandusky, Ohio",
                "latitude": 41.29,
                "longitude": -83.15,
                "timezone": "America/New_York",
            }
        }

        result = oracle_profile.validate_profile(profile)
        self.assertTrue(result["ok"])
        self.assertTrue(any("time" in warning.lower() for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
