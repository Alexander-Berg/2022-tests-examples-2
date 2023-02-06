# -*- coding: utf-8 -*-
import fakeredis
from unittest import mock

from passport.backend.core.test.test_utils.utils import single_entrant_patch


@single_entrant_patch
class FakeRedis:
    def __init__(self):
        self.sentinel_mock = mock.Mock()
        self.sentinel_mock.return_value.discover_master.return_value = 'redis-host', 456
        self.sentinel_patch = mock.patch('redis.Sentinel', self.sentinel_mock)

        self.redis_mock = mock.Mock(wraps=fakeredis.FakeRedis())
        self.redis_patch = mock.patch('redis.Redis', mock.Mock(return_value=self.redis_mock))

        self.get_redis_config_patch = mock.patch(
            'passport.backend.takeout.common.conf.db.get_redis_settings',
            return_value={
                'password': 'test-redis-password',
                'sentinel': [('test-sentinel-host', 123)],
                'socket_connect_timeout': 1,
                'socket_timeout': 2,
                'master_name': 'test-master-name',
            },
        )

        self.patches = [
            self.get_redis_config_patch,
            self.sentinel_patch,
            self.redis_patch,
        ]

    def start(self):
        for patch in self.patches:
            patch.start()

    def stop(self):
        for patch in reversed(self.patches):
            patch.stop()

    @property
    def called(self):
        return self.sentinel_mock.called

    def _method_mock(self, method):
        return getattr(self.redis_mock, method)

    def redis_set_side_effect(self, method, side_effect):
        self._method_mock(method).side_effect = side_effect

    def redis_calls_by_method(self, method):
        return self._method_mock(method).call_args_list
