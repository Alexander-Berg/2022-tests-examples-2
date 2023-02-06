# -*- coding: utf-8 -*-

import logging
import sys
import unittest

import mock
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.conf import settings
from passport.backend.core.logging_utils.faker.fake_tskv_logger import GraphiteLoggerFaker
from passport.backend.core.redis_manager.redis_manager import (
    RedisAuthenticationError,
    RedisError,
    RedisManager,
    RedisRecoverableAuthenticationError,
    RedisWatchError,
)
from passport.backend.core.test.test_utils import with_settings_hosts
import redis


REDIS_TEST_PORT = 7379

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

redis_config = {
    'master': {
        'host': '127.0.0.1',
        'port': REDIS_TEST_PORT,
        'retries': 7,
        'retry_timeout': 0.01,
        'type': 'master',
    },
    'slave1': {
        'host': 'localhost',
        'port': REDIS_TEST_PORT + 1,
        'type': 'slave',
    },
    'slave2': {
        'host': 'localhost',
        'port': REDIS_TEST_PORT + 2,
        'type': 'slave',
    }
}


@with_settings_hosts()
class TestRedisManager(unittest.TestCase):

    def setUp(self):
        self.test_key = 'k1'
        self.redis_mock = mock.Mock()
        self.manager = RedisManager(redis_constructor=self.redis_mock)
        self.conn = mock.Mock()
        self.conn.connection_pool = mock.Mock()
        self.conn.connection_pool.connection_kwargs = dict(host='localhost', port=REDIS_TEST_PORT)
        self.redis_mock.return_value = self.conn
        self.manager.configure(redis_config)
        self._graphite_logger_faker = GraphiteLoggerFaker()
        self._graphite_logger_faker.start()

    def tearDown(self):
        self._graphite_logger_faker.stop()
        del self._graphite_logger_faker
        del self.manager
        del self.redis_mock
        del self.conn

    @raises(ValueError)
    def test_get_conn_empty_cfg(self):
        RedisManager().configure({})

    def test_config_without_master(self):
        r = RedisManager()
        r.configure({
            'slave1': {
                'host': 'localhost',
                'port': REDIS_TEST_PORT + 1,
                'type': 'slave',
            },
        })
        assert_is_none(r.master)

    def test_get_conn(self):
        conn = self.manager.get_rw_connection()
        ok_(conn.redis is not None)
        eq_(conn.retry_timeout, 0.01)
        eq_(conn.retries, 7)
        conn = self.manager.get_ro_connection()
        ok_(conn.redis is not None)
        eq_(conn.retry_timeout, settings.REDIS_RETRY_TIMEOUT)
        eq_(conn.retries, settings.REDIS_RETRY_MAX_COUNT)

    def test_hmset(self):
        data = {"a": "1", "b": "c"}
        master_conn = self.conn
        result = self.manager.hmset(self.test_key, data)
        ok_(result)
        eq_(self.redis_mock.call_count, 3)
        master_conn.hmset.assert_called_once_with(self.test_key, data)

    def test_hgetall_slave(self):
        slave_conn = self.conn
        self.manager.hgetall(self.test_key)
        eq_(self.redis_mock.call_count, 3)
        slave_conn.hgetall.assert_called_once_with(self.test_key)

    def test_hget_slave(self):
        slave_conn = self.conn
        self.manager.hget(self.test_key, 'f1')
        eq_(self.redis_mock.call_count, 3)
        slave_conn.hget.assert_called_once_with(self.test_key, 'f1')

    def test_exists(self):
        slave_conn = self.conn
        self.manager.exists(self.test_key)
        eq_(self.redis_mock.call_count, 3)
        slave_conn.exists.assert_called_once_with(self.test_key)

    def test_expire(self):
        slave_conn = self.conn
        self.manager.expire(self.test_key, 10)
        eq_(self.redis_mock.call_count, 3)
        slave_conn.expire.assert_called_once_with(self.test_key, 10)

    def test_delete(self):
        self.manager.delete("k1", "k2", "k3")
        eq_(self.redis_mock.call_count, 3)
        self.conn.delete.assert_called_once_with("k1", "k2", "k3")

    def test_incr(self):
        self.manager.incr("k1")
        eq_(self.redis_mock.call_count, 3)
        self.conn.incr.assert_called_once_with("k1")

    def test_hincrby(self):
        self.manager.hincrby("k1", "f1", 2)
        eq_(self.redis_mock.call_count, 3)
        self.conn.hincrby.assert_called_once_with("k1", "f1", 2)

    def test_rpush(self):
        self.manager.rpush("k1", "f1", "f2", "f3")
        eq_(self.redis_mock.call_count, 3)
        self.conn.rpush.assert_called_once_with("k1", "f1", "f2", "f3")

    def test_lpush(self):
        self.manager.lpush("k1", "f1", "f2", "f3")
        eq_(self.redis_mock.call_count, 3)
        self.conn.lpush.assert_called_once_with("k1", "f1", "f2", "f3")

    def test_lrange(self):
        self.manager.lrange("k1", 100, 500)
        eq_(self.redis_mock.call_count, 3)
        self.conn.lrange.assert_called_once_with("k1", 100, 500)

    def test_llen(self):
        self.manager.llen("k1")
        eq_(self.redis_mock.call_count, 3)
        self.conn.llen.assert_called_once_with("k1")

    def test_ltrim(self):
        self.manager.ltrim("k1", 0, 100)
        eq_(self.redis_mock.call_count, 3)
        self.conn.ltrim.assert_called_once_with("k1", 0, 100)

    def test_ttl(self):
        self.manager.ttl("k1")
        eq_(self.redis_mock.call_count, 3)
        self.conn.ttl.assert_called_once_with("k1")

    def test_retries(self):
        def side_effect(key, counter=[0], **kwargs):
            counter[0] += 1
            if counter[0] < 2:
                raise redis.ConnectionError()
            return mock.Mock()

        slave_conn = self.conn
        slave_conn.hgetall = mock.Mock(side_effect=side_effect)

        self.manager.hgetall('test')
        eq_(2, slave_conn.hgetall.call_count)
        slave_conn.hgetall.assert_called_with('test')

    def test_no_retries_on_watch_error(self):
        self.conn.set = mock.Mock(side_effect=redis.WatchError('Watched variable changed.'))
        with assert_raises(RedisWatchError):
            self.manager.set('test', 'value')

        eq_(1, self.conn.set.call_count)

    def test_on_redis_error(self):
        conn = self.conn
        conn.hmset = mock.Mock(side_effect=redis.ConnectionError('test conn error'))
        with assert_raises(RedisError):
            self.manager.hmset('test', {})

    def test_ping(self):
        self.manager.ping()
        self.conn.ping.assert_called_once_with()
        eq_(self.redis_mock.call_count, 3)

    def test_hset(self):
        self.manager.hset('k1', 'f1', 2)
        eq_(self.redis_mock.call_count, 3)
        self.conn.hset.assert_called_once_with('k1', 'f1', 2)

    def test_hdel(self):
        self.manager.hdel('k1', 'f1')
        eq_(self.redis_mock.call_count, 3)
        self.conn.hdel.assert_called_once_with('k1', 'f1')

    def test_pipe_execute(self):
        pipe = self.manager.pipeline()
        pipe.execute()

    def test_pipe_discard(self):
        pipe = self.manager.pipeline()
        pipe.discard()

    def test_pipeline_watch_errors(self):
        conn = self.conn
        conn.pipeline().watch = mock.Mock(side_effect=redis.ConnectionError('test conn error'))
        pipe = self.manager.pipeline()
        with assert_raises(RedisError):
            pipe.watch('k1')

    def test_pipeline_auth_error(self):
        conn = self.conn
        conn.pipeline().watch = mock.Mock(side_effect=[redis.ResponseError('WRONGPASS test auth error'), mock.Mock()])
        manager = RedisManager(redis_constructor=self.redis_mock)
        manager.configure({
            u'master': {
                u'host': u'non_local_host',
                u'type': u'master',
                u'retries': 2,
                u'passwords': [u'PSWD1', u'PSWD2']
            },
        })
        pipe = manager.pipeline()
        # Пайплайн должен ломаться при неправильном пароле, даже если есть правильный пароль
        # и при этом должно произойти переключение на следующий пароль
        with assert_raises(RedisRecoverableAuthenticationError):
            pipe.watch('k1')
        eq_(self.redis_mock.call_args.kwargs['password'], 'PSWD2')

        # Если правильных паролей нет, ошибка другая
        conn.pipeline().watch = mock.Mock(side_effect=redis.ResponseError('WRONGPASS test auth error'))
        with assert_raises(RedisAuthenticationError):
            pipe.watch('k1')

    def test_write_to_graphite_log__about_non_local_request(self):
        """
        Записываем в графитный журнал обращения к соседним службам Redis.
        """
        self.conn.connection_pool.connection_kwargs = {
            u'host': u'non_local_host',
            u'port': REDIS_TEST_PORT,
        }
        manager = RedisManager(redis_constructor=self.redis_mock)
        manager.configure({
            u'master': {
                u'host': u'non_local_host',
                u'type': u'master',
                u'retries': 2,
            },
        })
        manager.ping()
        self._graphite_logger_faker.assert_has_written([
            self._graphite_logger_faker.entry(
                'base',
                response=u'success',
                retries_left=u'1',
                service=u'redis',
                srv_ipaddress=u'non_local_host',
                srv_hostname=u'non_local_host',
                network_error=u'0',
            ),
        ])

    def test_dont_write_to_graphite_log__about_local_request(self):
        """
        Не пишем в графитный журнал обращения к локальным службам Redis.
        """
        self.conn.connection_pool.connection_kwargs = {
            u'host': u'localhost',
            u'port': REDIS_TEST_PORT,
        }
        manager = RedisManager(redis_constructor=self.redis_mock)
        manager.configure({
            u'master': {
                u'host': u'localhost',
                u'type': u'master',
            },
        })
        manager.ping()
        self._graphite_logger_faker.assert_has_written([])

    def test_change_redis_password_after_auth_error(self):
        self.redis_mock.call_count = 0
        manager = RedisManager(redis_constructor=self.redis_mock)
        manager.configure({
            u'master': {
                u'host': u'localhost',
                u'type': u'master',
                u'passwords': [u'PSWD1', u'PSWD2']
            },
        })

        # redis инициализирован один раз, с первым паролем
        eq_(self.redis_mock.call_count, 1)
        eq_(self.redis_mock.call_args.kwargs['password'], 'PSWD1')

        # redis не инициализируется еще раз при вызовах без ошибок
        manager.hmset('test', {})
        eq_(self.redis_mock.call_count, 1)

        # redis инициализируется заново при ошибочном пароле, с вторым паролем
        self.conn.hmset = mock.Mock(side_effect=[redis.ResponseError('WRONGPASS test auth error'), mock.Mock()])
        manager.hmset('test', {})
        eq_(self.redis_mock.call_count, 2)
        eq_(self.redis_mock.call_args.kwargs['password'], 'PSWD2')

        # redis не инициализируется еще раз при вызовах без ошибок
        self.conn.hmset = mock.Mock()
        manager.hmset('test', {})
        eq_(self.redis_mock.call_count, 2)

        # выпадает с ошибкой при ошибочном пароле, если других паролей нет
        self.conn.hmset = mock.Mock(side_effect=redis.ResponseError('WRONGPASS test auth error'))
        with assert_raises(RedisAuthenticationError):
            manager.hmset('test', {})
