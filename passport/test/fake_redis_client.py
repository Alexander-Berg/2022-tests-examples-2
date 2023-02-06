# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mock
import passport.backend.social.common.redis_client as redis_client


def reset_fake_redis():
    FakeRedisClient._db = {}


class RedisPatch(object):
    def __init__(self, fake_redis):
        self._mock = mock.Mock(return_value=fake_redis)
        self._patch = mock.patch.object(redis_client, 'RedisClient', self._mock)

    def start(self):
        self._patch.start()
        return self

    def stop(self):
        reset_fake_redis()
        self._patch.stop()

    def set_redis_client(self, fake_redis):
        self._mock.return_value = fake_redis


class FakeRedisClient(object):
    _db = {}

    def __init__(self):
        pass

    def hget(self, _id, key):
        dictionary = self._db.get(_id)
        if not dictionary:
            return None
        return dictionary.get(key)

    def get(self, key):
        return self._db.get(key)

    def hgetall(self, _id):
        dictionary = self._db.get(_id)
        if not dictionary:
            return {}
        return dictionary.copy()

    def hset(self, _id, key, value):
        retval = 0
        if _id not in self._db:
            self._db[_id] = {}
            retval = 1

        if key not in self._db[_id]:
            retval = 1
        self._db[_id][key] = str(value)
        return retval

    def set(self, key, value):
        self._db[key] = str(value)
        return True

    def hsetnx(self, _id, key, value):
        retval = 0
        if _id not in self._db:
            self._db[_id] = {}
            retval = 1

        if key not in self._db[_id]:
            retval = 1
            self._db[_id][key] = str(value)
        return retval

    def hmset(self, _id, mapping):
        for key, value in mapping.iteritems():
            self.hset(_id, key, value)
        return True

    def expire(self, key, seconds):
        return True

    def delete(self, *keys):
        if not keys:
            raise redis_client.RedisError()
        deleted = 0
        for key in keys:
            if key in self._db:
                del self._db[key]
                deleted += 1
        return deleted > 0

    def lrange(self, key, start, end):
        if key not in self._db:
            return list()

        values = self._db[key]

        # В Redis диапазон включает оба крайних элемента
        if end < 0:
            end = len(values) + end
        end += 1

        return values[start:end]

    def rpush(self, key, *values):
        if not values:
            raise redis_client.RedisError()
        old_values = self._db.setdefault(key, list())
        old_values.extend(values)
        return len(old_values)

    def ltrim(self, key, start, end):
        values = self.lrange(key, start, end)
        if values:
            self._db[key] = values
        else:
            self._db.pop(key, None)
