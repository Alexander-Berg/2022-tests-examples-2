import datetime
from unittest.mock import patch, Mock

import pytz
from django import test
from parameterized import parameterized

from l3mgr.utils.throttling import ServiceOperationsThrottle, RateLimitValueError

RATE_LIMIT_NOT_SET = {}
VALID_RATE_LIMIT = {"num_allowed": 1, "interval_seconds": 1}

INVALID_RATE_LIMIT0 = (0, 0)
INVALID_RATE_LIMIT1 = (0, 10)
INVALID_RATE_LIMIT2 = ("invalid type", 10)
INVALID_RATE_LIMIT3 = ("invalid type", "invalid type")
SET_VALID_RATE_LIMIT = (10, 100)

ONE_CONFIG_PER_TWO_SECONDS = (1, 2)
TWO_CONFIGS_PER_TWO_SECONDS = (2, 2)
THREE_CONFIGS_PER_MINUTE = (3, 60)
NO_RATE_LIMIT = (0, 0)

TIME_NOW = datetime.datetime(2021, 3, 17, 7, 0, 59, 0, tzinfo=pytz.UTC)


def get_last_config_creation_time(before_now_seconds):
    return TIME_NOW.replace(second=TIME_NOW.second - before_now_seconds)


class ServiceOperationsThrottleTest(test.SimpleTestCase):
    @parameterized.expand(
        [
            (RATE_LIMIT_NOT_SET, (0, 0)),
            (VALID_RATE_LIMIT, (VALID_RATE_LIMIT["num_allowed"], VALID_RATE_LIMIT["interval_seconds"])),
        ]
    )
    @patch("l3mgr.models.Service.objects.get", return_value=Mock())
    def test_get_rate_limit(self, rate_limit_in_db, expected, mocked_service_get):
        mocked_service_get.return_value.rate_limit = rate_limit_in_db

        self.assertEqual(expected, ServiceOperationsThrottle(0).rate_limit)

    @parameterized.expand(
        [
            (
                SET_VALID_RATE_LIMIT,
                {"rate_limit": {"num_allowed": SET_VALID_RATE_LIMIT[0], "interval_seconds": SET_VALID_RATE_LIMIT[1]}},
            ),
        ]
    )
    @patch("l3mgr.models.Service.objects.filter", return_value=Mock())
    def test_set_rate_limit(self, set_rate_limit_args, expected_call_args, mocked_service_filter):
        ServiceOperationsThrottle(0).set_rate_limit(*set_rate_limit_args)

        self.assertEqual(mocked_service_filter.return_value.update.call_args_list[0].kwargs, expected_call_args)

    @parameterized.expand(
        [
            (INVALID_RATE_LIMIT0, RateLimitValueError),
            (INVALID_RATE_LIMIT1, RateLimitValueError),
            (INVALID_RATE_LIMIT2, RateLimitValueError),
            (INVALID_RATE_LIMIT3, RateLimitValueError),
        ]
    )
    @patch("l3mgr.models.Service.objects.filter", return_value=Mock())
    def test_set_invalid_rate_limit(self, set_rate_limit_args, expected_exception, mocked_service_filter):
        with self.assertRaises(expected_exception):
            ServiceOperationsThrottle(0).set_rate_limit(*set_rate_limit_args)

    @parameterized.expand(
        [
            (ONE_CONFIG_PER_TWO_SECONDS, 0, None, ServiceOperationsThrottle.NO_LIMIT),
            (ONE_CONFIG_PER_TWO_SECONDS, 1, get_last_config_creation_time(1), ONE_CONFIG_PER_TWO_SECONDS[1] - 1),
            (TWO_CONFIGS_PER_TWO_SECONDS, 1, None, ServiceOperationsThrottle.NO_LIMIT),
            (TWO_CONFIGS_PER_TWO_SECONDS, 5, TIME_NOW, TWO_CONFIGS_PER_TWO_SECONDS[1]),
            (TWO_CONFIGS_PER_TWO_SECONDS, 5, get_last_config_creation_time(1), TWO_CONFIGS_PER_TWO_SECONDS[1] - 1),
            (THREE_CONFIGS_PER_MINUTE, 2, None, ServiceOperationsThrottle.NO_LIMIT),
            (THREE_CONFIGS_PER_MINUTE, 3, get_last_config_creation_time(30), THREE_CONFIGS_PER_MINUTE[1] - 30),
            (THREE_CONFIGS_PER_MINUTE, 10, get_last_config_creation_time(55), THREE_CONFIGS_PER_MINUTE[1] - 55),
            # (NO_RATE_LIMIT, None, None, ServiceOperationsThrottle.NO_LIMIT),
        ]
    )
    @patch("l3mgr.models.Configuration.objects.filter", return_value=Mock())
    def test_request_throttling_seconds(
        self, rate_limit, config_count, last_config_time, expected_throttling_seconds, mocked_config_filter
    ):
        mocked_config_filter.return_value.count.return_value = config_count
        mocked_config_filter.return_value.order_by.return_value.only.return_value.first.return_value.timestamp = (
            last_config_time
        )

        with patch("l3mgr.utils.throttling.ServiceOperationsThrottle.rate_limit", rate_limit):
            with patch("django.utils.timezone.now") as dt_now:
                dt_now.return_value = TIME_NOW
                self.assertEqual(expected_throttling_seconds, ServiceOperationsThrottle(0).request_throttling_seconds)

    @patch("l3mgr.models.Service.objects.filter", return_value=Mock())
    def test_reset_rate_limit(self, mocked_config_filter):
        expected_call_args = {"rate_limit": {}}
        ServiceOperationsThrottle(0).reset_rate_limit()

        self.assertEqual(mocked_config_filter.return_value.update.call_args_list[0].kwargs, expected_call_args)
