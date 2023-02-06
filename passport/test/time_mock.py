# -*- coding: utf-8 -*-

import calendar
from datetime import datetime
import time

import mock


class TimeMock(object):
    range = 1000000

    def __init__(self, base_value=None, offset=0, incrementing=False):
        if base_value is None:
            base_value = int(calendar.timegm(datetime(2015, 10, 21, 0, 0, 0).timetuple()))

        self.base_value = base_value
        self.base_value += offset

        if incrementing is not False:
            increment_value = 1
            if type(incrementing) is int:
                increment_value = incrementing
            self.base_value = range(self.base_value, self.base_value + self.range, increment_value)
            self.mock = mock.patch.object(
                time,
                'time',
                mock.Mock(side_effect=self.base_value),
            )
        else:
            self.mock = mock.patch.object(
                time,
                'time',
                mock.Mock(side_effect=lambda: self.base_value),
            )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        self.mock.start()

    def stop(self):
        self.mock.stop()

    def tick(self, tick_value=1):
        self.base_value += tick_value
