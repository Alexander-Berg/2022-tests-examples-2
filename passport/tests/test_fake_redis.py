# -*- coding: utf-8 -*-

from time import time
import unittest

from nose.tools import assert_raises
from passport.backend.core.redis_manager.faker.fake_redis import FakeRedis
from passport.backend.core.test.time_utils.time_utils import TimeNow
from redis import ResponseError


class TestFakeRedis(unittest.TestCase):
    def setUp(self):
        self.redis = FakeRedis('localhost', 6379)
        self.data = {'a': 'b', 'c': 'd'}

    def tearDown(self):
        del self.redis

    def test_get_set_expire(self):
        assert self.redis.get('k1') is None
        self.redis.set('k1', 'v1')
        self.redis.expire('k1', -1)
        assert self.redis.get('k1') is None
        self.redis.set('k1', 'v1')
        assert self.redis.get('k1') == b'v1'

    def test_setex(self):
        assert self.redis.get('k1') is None
        self.redis.setex('k1', -1, 'v1')
        assert self.redis.get('k1') is None

        assert self.redis.get('k2') is None
        self.redis.setex('k2', 999, 'v2')
        assert self.redis.get('k2') == b'v2'

    def test_incr(self):
        assert self.redis.incr('k1') == 1
        assert self.redis.get('k1') == '1'
        assert self.redis.incr('k1') == 2
        assert self.redis.get('k1') == '2'

    def test_bad_incr(self):
        self.redis.set('k1', '#')
        with assert_raises(ResponseError):
            self.redis.incr('k1')

    def test_hmset(self):
        assert self.redis.hmset('k1', self.data)
        assert self.redis._redis[b'k1'] == {b'a': b'b', b'c': b'd'}
        assert self.redis.hmset('k1', {'c': 'e'})
        assert self.redis._redis[b'k1'] == {b'a': b'b', b'c': b'e'}

    def test_hgetall(self):
        assert not self.redis.hgetall('k1')
        self.redis.hmset('k1', self.data)
        assert self.redis.hgetall('k1') == {b'a': b'b', b'c': b'd'}

    def test_hget(self):
        assert not self.redis.hget('k1', 'a')
        self.redis.hmset('k1', self.data)
        assert self.redis.hget('k1', 'a') == self.data['a'].encode('utf-8')
        assert self.redis.hget('k1', 'ab') is None

    def test_exists(self):
        assert not self.redis.exists('no-key')
        self.redis.hmset('k1', self.data)
        assert self.redis.exists('k1')

        self.redis._key_expiration_map[b'k1'] = time() + 100
        assert self.redis.exists('k1')

        self.redis._key_expiration_map[b'k1'] = time() - 100
        assert not self.redis.exists('k1')
        assert b'k1 'not in self.redis._redis

    def test_expire_on_hash(self):
        assert not self.redis.expire('no-key', 10)
        self.redis.hmset('k1', self.data)
        assert self.redis.expire('k1', 10)
        assert self.redis._key_expiration_map[b'k1'] == TimeNow(delta=10)

    def test_expire_on_list(self):
        self.redis.lpush('l1', 1, 2, 3)
        assert self.redis.expire('l1', 10)
        assert self.redis._key_expiration_map[b'l1'] == TimeNow(delta=10)

    def test_delete(self):
        assert not self.redis.delete('no-key', 'no-key-2')
        self.redis.hmset('k1', self.data)
        self.redis.hmset('k2', self.data)
        assert self.redis.delete('k1', 'k2')
        assert b'k1' not in self.redis._redis
        assert b'k2' not in self.redis._redis

    def test_hincrby(self):
        assert self.redis.hincrby('k1', 'f1', 15) == 15
        self.redis.hincrby('k1', 'f1', 10)
        assert self.redis._redis[b'k1'][b'f1'] == '25'

    def test_bad_key_hincrby(self):
        self.redis.hmset('k1', {'f1': '#'})
        with assert_raises(ResponseError):
            self.redis.hincrby('k1', 'f1', 10)

    def test_bad_value_hincrby(self):
        self.redis.hmset('k1', {'f1': '1'})
        with assert_raises(ResponseError):
            self.redis.hincrby('k1', 'f1', '#')

    def test_rpush(self):
        assert self.redis.rpush('k1', 'v1', 'v2') == 2
        assert self.redis._redis[b'k1'] == [b'v1', b'v2']
        assert self.redis.rpush('k1', 'v3') == 3
        assert self.redis._redis[b'k1'] == [b'v1', b'v2', b'v3']

    def test_lpush(self):
        assert self.redis.lpush('k1', 'v1', 'v2') == 2
        assert self.redis._redis[b'k1'] == [b'v2', b'v1']
        assert self.redis.lpush('k1', 'v3') == 3
        assert self.redis._redis[b'k1'] == [b'v3', b'v2', b'v1']

    def test_lpush_error(self):
        with assert_raises(ResponseError):
            self.redis.lpush('k1')

    def test_rpush_error(self):
        with assert_raises(ResponseError):
            self.redis.rpush('k1')

    def test_lrange(self):
        assert self.redis.lrange('k1', 0, -1) == []

        self.redis.rpush('k1', 'v1', 'v2', 'v3', 'v4')

        assert self.redis.lrange('k1', 1, -1) == [b'v2', b'v3', b'v4']
        assert self.redis.lrange('k1', 0, 2) == [b'v1', b'v2', b'v3']
        assert self.redis.lrange('k1', 1, 2) == [b'v2', b'v3']

    def test_lrange_error(self):
        self.redis.lpush('k1', 'v1', 'v2', 'v3')
        with assert_raises(ValueError):
            self.redis.lrange('k1', 0, -2)

    def test_llen(self):
        assert self.redis.llen('no-key') == 0
        self.redis.rpush('k1', 'v1', 'v2', 'v3')
        assert self.redis.llen('k1') == 3

    def test_ltrim(self):
        assert self.redis.ltrim('no-key', 100, 500)

        self.redis.rpush('k1', 'v1', 'v2', 'v3', 'v4')
        assert self.redis.ltrim('k1', 0, 1)
        assert self.redis._redis[b'k1'] == [b'v1', b'v2']

    def test_ltrim_error(self):
        self.redis.lpush('k1', 'v1', 'v2', 'v3')
        with assert_raises(ValueError):
            self.redis.ltrim('k1', 0, -2)

    def test_ttl(self):
        assert self.redis.ttl('no-key') is None
        self.redis.hmset('k1', self.data)
        assert self.redis.ttl('k1') is None
        self.redis.expire('k1', 10)
        assert time() + self.redis.ttl('k1') == TimeNow(delta=10)
        self.redis._key_expiration_map[b'k1'] -= 5
        assert time() + self.redis.ttl('k1') == TimeNow(delta=5)
        self.redis._key_expiration_map[b'k1'] -= 10
        assert self.redis.ttl('k1') is None
        self.redis.expire('k1', 10)

    def test_hset(self):
        assert self.redis.hset('k1', 'f1', 15) == 1
        assert self.redis.hset('k1', 'f1', 15) == 0
        self.redis.hset('k1', 'f1', 10)
        assert self.redis._redis[b'k1'][b'f1'] == b'10'

    def test_hdel(self):
        assert self.redis.hset('k1', 'f1', 15) == 1

        assert self.redis.hdel('k2') == 0
        assert self.redis.hdel('k1', 'f2') is False

        assert self.redis.hdel('k1', 'f1') == 1
        assert b'f1' not in self.redis._redis[b'k1']

    def test_sadd(self):
        assert not self.redis.sismember('key', 'item1')
        assert self.redis.smembers('key') == set()

        self.redis.sadd('key', 'item1', 'item2')

        assert self.redis.sismember('key', 'item1')
        assert self.redis.smembers('key') == {b'item1', b'item2'}

    def test_ping(self):
        assert self.redis.ping() is None

    def test_watch_unwatch(self):
        assert self.redis.watch('some_key', 'some_other_key') is None
        assert self.redis.unwatch() is None

    def test_transaction(self):
        pipe = self.redis.pipeline()
        pipe.multi()
        pipe.hset('k1', 'f1', 15)
        assert b'k1' not in self.redis._redis
        assert pipe.execute() == [1, ]
        assert self.redis._redis[b'k1'][b'f1'] == b'15'

    def test_transaction_discard(self):
        pipe = self.redis.pipeline()
        pipe.multi()
        pipe.hset('k1', 'f1', 15)
        pipe.discard()

    def test_transaction_rollback(self):
        pipe = self.redis.pipeline()
        pipe.multi()
        pipe.hset('k1', 'f1', 15)
        pipe.hincrby('k1', 'f1', 'not-an-integer')
        with assert_raises(ResponseError):
            pipe.execute()
        assert b'k1' not in self.redis._redis, self.redis._redis

    def test_pipeline_rollback(self):
        pipe = self.redis.pipeline()
        pipe.hset('k1', 'f1', 15)
        pipe.hincrby('k1', 'f1', 'not-an-integer')
        with assert_raises(ResponseError):
            pipe.execute()
        assert self.redis._redis[b'k1'][b'f1'] == b'15'

    def test_double_pipeline(self):
        pipe = self.redis.pipeline()
        assert pipe.pipeline() is pipe
