import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = Path("/Users/sc/katana-agent/oracle/astro-companion/scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class OracleAstrologyCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["ORACLE_STATE_DIR"] = self.temp_dir.name
        os.environ["ASTROVISOR_TOKEN"] = "test-token"

    def tearDown(self):
        self.temp_dir.cleanup()
        os.environ.pop("ORACLE_STATE_DIR", None)
        os.environ.pop("ASTROVISOR_TOKEN", None)

    def test_call_endpoint_uses_cache_on_second_request(self):
        import oracle_astrology

        with mock.patch.object(
            oracle_astrology,
            "_perform_http_request",
            return_value={"result": {"moon_phase": "Waxing Gibbous"}},
        ) as mocked:
            first = oracle_astrology.call_endpoint(
                kind="transits",
                endpoint="/api/transits/calculate",
                payload={"date": "2026-03-10"},
                ttl=3600,
            )
            second = oracle_astrology.call_endpoint(
                kind="transits",
                endpoint="/api/transits/calculate",
                payload={"date": "2026-03-10"},
                ttl=3600,
            )

        self.assertEqual(mocked.call_count, 1)
        self.assertFalse(first["cached"])
        self.assertTrue(second["cached"])
        self.assertEqual(second["data"], first["data"])


if __name__ == "__main__":
    unittest.main()
