# -*- coding: utf-8 -*-

from mock import (
    Mock,
    patch,
)
from nose.tools import eq_
from passport.backend.social.common.redis_client import (
    RedisClient,
    RedisError,
)
from passport.backend.social.common.social_config import social_config
from passport.backend.social.common.test.test_case import TestCase
import redis


class TestRedisClient(TestCase):
    def setUp(self):
        super(TestRedisClient, self).setUp()

        self._redis_conn = Mock()
        self._redis_conn.connection_pool = Mock(connection_kwargs={'host': 'localhost', 'port': '1234'})
        self.patches = [
            patch('passport.backend.social.common.redis_client.redis.Redis', Mock(return_value=self._redis_conn)),
            patch('passport.backend.social.common.redis_client.redis.ConnectionPool', Mock()),
        ]

        for p in self.patches:
            p.start()
        RedisClient.init()

        self._redis = RedisClient()

    def tearDown(self):
        RedisClient.stop()
        for p in self.patches:
            p.start()
        super(TestRedisClient, self).tearDown()

    def build_settings(self):
        settings = super(TestRedisClient, self).build_settings()
        settings['social_config'].update({
            'redis_reconnect_retries': 3,
            'redis_reconnect_timeout': 0.1,
        })
        return settings

    def _single_call(self, method_name, args):
        self._redis._execute = Mock(return_value='response')
        response = getattr(self._redis, method_name)(**args)
        eq_(response, 'response')
        eq_(self._redis._execute.call_count, 1)

    def test_execute_ok(self):
        self._redis._master.some_method = Mock(return_value='response')
        response = self._redis._execute(
            self._redis._master,
            'undefined',
            lambda conn: conn.some_method('key', 'val'),
        )
        eq_(response, 'response')
        eq_(self._redis._master.some_method.call_count, 1)

    def test_execute_retry(self):
        def _foo(key, val, counter=[0]):
            counter[0] += 1
            if counter[0] == 1:
                raise redis.RedisError()
            return 'response'

        self._redis._master.some_method = Mock(side_effect=_foo)
        response = self._redis._execute(
            self._redis._master,
            'undefined',
            lambda conn: conn.some_method('key', 'val'),
        )
        eq_(response, 'response')
        eq_(self._redis._master.some_method.call_count, 2)

    def test_execute_retry_fail(self):
        self._redis._master.some_method = Mock(side_effect=redis.RedisError)
        with self.assertRaises(RedisError):
            self._redis._execute(
                self._redis._master,
                'undefined',
                lambda conn: conn.some_method('key', 'val'),
            )
        eq_(self._redis._master.some_method.call_count, social_config.redis_reconnect_retries)

    def test_hgetall(self):
        self._single_call('hgetall', {'key': 'key'})

    def test_hmset(self):
        self._single_call('hmset', {'key': 'key', 'data': 'data'})

    def test_expire(self):
        self._single_call('expire', {'key': 'key', 'time': 123})
