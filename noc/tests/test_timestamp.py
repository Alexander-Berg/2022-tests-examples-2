import time
import datetime

from hbf.timestamp import Timestamp
from . import BaseTest


class TestTimestamp(BaseTest):
    def test1(self):
        ts_set = set()

        for s in [
            "Sun, 06 Nov 1994 08:49:37 GMT",
            "Sunday, 06-Nov-94 08:49:37 GMT",
            "Sun Nov  6 08:49:37 1994",
        ]:
            ts = Timestamp(s)
            self.assertEqual(str(ts), "Sun, 06 Nov 1994 08:49:37 GMT")
            self.assertEqual(int(ts), 784111777)  # date -d 'Sun, 06 Nov 1994 08:49:37 GMT' +%s

            # check if hashable
            if not ts_set:
                ts_set.add(ts)
            self.assertIn(ts, ts_set)

    def test2(self):
        now = int(time.time())
        ts = Timestamp(now)
        ts_1 = Timestamp(now + 1)
        dt = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc)

        self.assertEqual(ts, dt, repr(dt))
        self.assertGreater(ts_1, dt)
        self.assertLess(dt, ts_1)
