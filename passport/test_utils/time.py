# -*- coding: utf-8 -*-
from contextlib import contextmanager

import mock
from passport.backend.utils.time import get_unixtime


@contextmanager
def freeze_time(timestamp):
    with mock.patch('time.time') as time_mock:
        time_mock.return_value = timestamp

        assert get_unixtime() == timestamp

        yield
