# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import (
    Mock,
    patch,
)
from passport.backend.social.common.throttler import Throttler


class FakeThrottle(object):
    def __init__(self):
        self._mock = Mock(name='throttle', return_value=None)
        self._patches = [
            patch('passport.backend.social.common.throttler.Throttler.throttle', self._mock),
            patch('passport.backend.social.common.throttler.Throttler.from_grants_context', self._from_grants_context),
        ]

    def start(self):
        for _patch in self._patches:
            _patch.start()
        return self

    def stop(self):
        for _patch in reversed(self._patches):
            _patch.start()

    def set_response_value(self, value):
        self._mock.side_effect = [value]

    def _from_grants_context(self, request_name, grants_config, grants_context):
        return Throttler(request_name, list())
