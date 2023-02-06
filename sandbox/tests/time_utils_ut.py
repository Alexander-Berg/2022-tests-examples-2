import unittest

import datetime as dt
from sandbox.projects.common import time_utils


class DatetimeToTimestamp(unittest.TestCase):
    def test_only_date(self):
        self.assertEqual(1578873600.0, time_utils.datetime_to_timestamp(dt.datetime(year=2020, month=1, day=13)))

    def test_datetime(self):
        self.assertEqual(1578935102.0, time_utils.datetime_to_timestamp(dt.datetime(year=2020, month=1, day=13, hour=17, minute=5, second=2)))

    def test_zero_time(self):
        self.assertEqual(0.0, time_utils.datetime_to_timestamp(time_utils.ZERO_TIME_UTC))


if __name__ == '__main__':
    unittest.main()
