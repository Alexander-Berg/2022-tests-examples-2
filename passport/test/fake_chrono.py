# -*- coding: utf-8 -*-

import datetime

import mock


class FakeChrono(object):
    def __init__(self):
        self._timestamp = datetime.datetime.now()

    def now(self, tz=None):
        timestamp = self._timestamp
        if tz is not None:
            timestamp = tz.localize(timestamp)
        return timestamp


class FakeChronoManager(object):
    def __init__(self):
        self.chrono = FakeChrono()

        fake_lazy_loader = mock.Mock(name='fake_lazy_loader')
        fake_lazy_loader.get_instance.return_value = self.chrono
        self._patch = mock.patch('passport.backend.social.common.chrono.LazyLoader', fake_lazy_loader)

    def start(self):
        self._patch.start()

    def stop(self):
        self._patch.stop()

    def set_timestamp(self, timestamp):
        if not isinstance(timestamp, datetime.datetime):
            timestamp = datetime.datetime.fromtimestamp(timestamp)
        self.chrono._timestamp = timestamp
