from unittest.mock import patch

from django import test
from parameterized import parameterized

from ...utils.ip_reservation import IPCache

FAKE_IP = "2a02:6b8:0:3400:ffff::4c9"


class IPReservationTest(test.SimpleTestCase):
    @parameterized.expand(
        [
            ("my_key", "my_key", True),
            ("my_key", "other_key", False),
        ]
    )
    def test_ip_is_free(self, generated_cache_key, collected_cache_key, expected):
        with patch("l3mgr.utils.ip_reservation.cache.get_or_set") as mocked_get_or_set:
            IPCache._get_cache_key = lambda *args: generated_cache_key
            mocked_get_or_set.return_value = collected_cache_key

            self.assertEqual(IPCache.ip_is_free(FAKE_IP), expected)

    @parameterized.expand([("my_key", "my_key", True)])
    def test_ip_is_free_retries(self, generated_cache_key, collected_cache_key, expected):
        with patch("l3mgr.utils.ip_reservation.cache.get_or_set") as mocked_get_or_set:
            IPCache._get_cache_key = lambda *args: generated_cache_key
            mocked_get_or_set.side_effect = [Exception, collected_cache_key]

            # Setting small retry timeout to avoid a delay in tests
            IPCache._cache_if_not_already.__closure__[3].cell_contents = 0.0001

            result = IPCache.ip_is_free(FAKE_IP)

            self.assertEqual(result, expected)
            self.assertEqual(mocked_get_or_set.call_count, 2)
