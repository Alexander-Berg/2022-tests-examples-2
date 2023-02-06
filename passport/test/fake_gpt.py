# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import (
    Mock,
    patch,
)
from passport.backend.social.common.gpt import Gpt


class FakeGpt(object):
    def __init__(self):
        self._time_mock = Mock(name='fake_time', return_value=0)
        self._randomizer_mock = Mock(name='fake_randomizer')
        self._randomizer_mock.randrange = Mock(return_value=0)

        def fake_init(*args, **kwargs):
            return self._fake_init(self, *args, **kwargs)

        self._patch = patch.object(Gpt, '__init__', fake_init)

    @staticmethod
    def _fake_init(self, gpt, *args, **kwargs):
        gpt._timer = self._time_mock
        gpt._randomizer = self._randomizer_mock

    def start(self):
        self._patch.start()
        return self

    def stop(self):
        self._patch.stop()
