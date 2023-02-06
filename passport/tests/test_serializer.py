# -*- coding: utf-8 -*-
from copy import deepcopy
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    raises,
)
from passport.backend.core.test.test_utils import iterdiff
from passport.backend.core.tracks.exceptions import ConcurrentTrackOperationError
from passport.backend.core.tracks.serializer import (
    LIST_ROOT,
    Serializer,
)
from six import iteritems


eq_ = iterdiff(eq_)


class BaseSerializerTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_pipe = mock.Mock()
        self.fake_redis = mock.Mock()
        self.fake_redis.pipeline.return_value = self.fake_pipe
        self.fake_pipe.parent = self.fake_redis
        self.serializer = Serializer()
        self.track = self.make_track(
            data={
                'field': 'value',
                'another_field': 'another_value',
                'empty_field': '',
                'protected_field': 'some_value',
            },
            counters={
                'counter': 1,
                'another_counter': 2,
                'empty_counter': 0,
            },
            lists={
                'list': ['1'],
                'empty_list': [],
            },
        )
        self.fake_redis.get.return_value = self.track.track_version
        self.fake_redis.hgetall.return_value = deepcopy(self.track._data)

    def tearDown(self):
        del self.fake_pipe
        del self.fake_redis
        del self.track

    def make_track(self, track_id='id', version=1, data=None, counters=None, lists=None):
        track = mock.Mock()
        track.track_id = track_id
        track.track_version = version
        track._data = data or {}
        track._counters = counters or {}
        track._lists = lists or {}
        track.list_names = list(lists.keys()) if lists else list()
        track.ttl = 60
        track.concurrent_protected_fields = {'protected_field'}
        for field, value in iteritems(track._data):
            setattr(track, field, value)
        return track

    def pipe_call_args_list(self):
        return [
            (name, args)  # kwargs нигде не используются
            for name, args, kwargs in self.fake_pipe.method_calls
        ]


class TestSerializerCreate(BaseSerializerTestCase):
    def try_serialize(self):
        self.serializer.execute(old_track=None, new_track=self.track, redis_node=self.fake_redis)

    def test_ok(self):
        self.try_serialize()
        eq_(
            self.pipe_call_args_list(),
            [
                ('multi', ()),
                ('set', ('track:id:version', 1)),
                ('expire', ('track:id:version', 60)),
                ('hmset', ('track:id', {'field': 'value', 'another_field': 'another_value', 'empty_field': '', 'protected_field': 'some_value'})),
                ('expire', ('track:id', 60)),
                ('rpush', ('track:id:empty_list', LIST_ROOT)),
                ('expire', ('track:id:empty_list', 60)),
                ('rpush', ('track:id:list', LIST_ROOT, '1')),
                ('expire', ('track:id:list', 60)),
                ('execute', ()),
            ],
        )


class TestSerializerChange(BaseSerializerTestCase):
    def try_serialize(self, changing_func):
        snapshot = deepcopy(self.track)
        changing_func(self.track)
        self.serializer.execute(old_track=snapshot, new_track=self.track, redis_node=self.fake_redis)

    def test_nothing_changed(self):
        self.try_serialize(lambda x: None)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('execute', ()),
            ],
        )

    def test_change_field(self):
        def change(track):
            track._data['field'] = 'another_value'
            track._data['another_field'] = 'another_value'

        self.try_serialize(change)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('hmset', ('track:id', {'field': 'another_value'})),
                ('execute', ()),
            ],
        )

    def test_concurrent_change_allowed(self):
        self.fake_redis.hgetall.return_value['field'] = 'weird_value'

        def change(track):
            track._data['another_field'] = 'value'

        self.try_serialize(change)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('hmset', ('track:id', {'another_field': 'value'})),
                ('execute', ()),
            ],
        )

    @raises(ConcurrentTrackOperationError)
    def test_concurrent_field_change_forbidden(self):
        self.fake_redis.hgetall.return_value['protected_field'] = 'weird_value'

        def change(track):
            track._data['another_field'] = 'value'

        self.try_serialize(change)

    @raises(ConcurrentTrackOperationError)
    def test_concurrent_version_change_forbidden(self):
        self.fake_redis.get.return_value = str(self.track.track_version + 1)

        def change(track):
            track._data['another_field'] = 'value'

        self.try_serialize(change)

    def test_delete_field(self):
        def change(track):
            del track._data['field']

        self.try_serialize(change)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('hdel', ('track:id', 'field')),
                ('execute', ()),
            ],
        )

    def test_set_field_to_none(self):
        def change(track):
            track._data['field'] = None

        self.try_serialize(change)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('hdel', ('track:id', 'field')),
                ('execute', ()),
            ],
        )

    def test_counters(self):
        def change(track):
            track._counters['counter'] = 2
            track._counters['another_counter'] = 1
            track._counters['empty_counter'] += 2
            del track._counters['counter2']

        self.track = self.make_track(
            counters={
                'counter': 1,
                'counter2': 2,
                'another_counter': 2,
                'empty_counter': 0,
            },
        )
        self.fake_redis.hgetall.return_value = deepcopy(self.track._data)

        self.try_serialize(change)

        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('hset', ('track:id', 'another_counter', 1)),
                ('hincrby', ('track:id', 'counter', 1)),
                ('hincrby', ('track:id', 'empty_counter', 2)),
                ('hdel', ('track:id', 'counter2')),
                ('execute', ()),
            ],
        )

    def test_list_add(self):
        def change(track):
            track._lists['list'].append('2')

        self.try_serialize(change)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('rpush', ('track:id:list', '2')),
                ('execute', ()),
            ],
        )

    def test_truncate_list_on_overflow(self):
        new_items = list(range(400, 1100))
        def change(track):
            track._lists['list'].extend(new_items)

        self.track = self.make_track(lists={'list': list(range(400))})
        self.fake_redis.hgetall.return_value = deepcopy(self.track._data)

        self.try_serialize(change)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('rpush', ('track:id:list',) + tuple(new_items)),
                ('ltrim', ('track:id:list', 100, -1)),
                ('lpush', ('track:id:list', LIST_ROOT)),
                ('execute', ()),
            ],
        )
        eq_(self.track._lists['list'], list(range(100, 1100)))

    def test_list_change(self):
        def change(track):
            track._lists['list'][:] = ['3', '4']

        self.try_serialize(change)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('ltrim', ('track:id:list', 0, 0)),
                ('rpush', ('track:id:list', '3', '4')),
                ('execute', ()),
            ],
        )

    def test_error_in_serializer(self):
        self.fake_pipe.hmset.side_effect = ValueError

        def change(track):
            track._data['field'] = 'another_value'
            track._data['another_field'] = 'another_value'

        with assert_raises(ValueError):
            self.try_serialize(change)
        eq_(
            self.pipe_call_args_list(),
            [
                ('watch', ('track:id:version',)),
                ('multi', ()),
                ('hmset', ('track:id', {'field': 'another_value'})),
                ('discard', ()),
            ],
        )


class TestSerializerDelete(BaseSerializerTestCase):
    def try_delete(self, track=None):
        track = track or self.track
        self.serializer.execute(old_track=track, new_track=None, redis_node=self.fake_redis)

    def test_ok(self):
        self.try_delete()
        eq_(
            self.pipe_call_args_list(),
            [
                ('multi', ()),
                ('delete', ('track:id',)),
                ('delete', ('track:id:version',)),
                ('delete', ('track:id:empty_list',)),
                ('delete', ('track:id:list',)),
                ('execute', ()),
            ],
        )

    def test_error_in_serializer(self):
        self.fake_pipe.delete.side_effect = ValueError
        with assert_raises(ValueError):
            self.try_delete()
        eq_(
            self.pipe_call_args_list(),
            [
                ('multi', ()),
                ('delete', ('track:id',)),
                ('discard', ()),
            ],
        )
