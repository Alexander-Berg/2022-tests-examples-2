# -*- coding: utf-8 -*-

from collections import namedtuple
import time
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.redis_manager.redis_manager import RedisManager
from passport.backend.core.test.test_utils import (
    iterdiff,
    with_settings,
)
from passport.backend.core.tracks.exceptions import (
    NodeNotFoundError,
    TrackNotFoundError,
)
from passport.backend.core.tracks.model import RegisterTrack
from passport.backend.core.tracks.track_manager import TrackManager
from passport.backend.core.tracks.transaction import TrackTransaction


_host = namedtuple('host', 'name id')

REDIS_TEST_PORT = 7379

TRACK_ID_1 = 's1'
TRACK_ID_2 = 's2'
BAD_TRACK_ID_1 = 'abc'

TRACK_DATA = {'1': 'aa', '2': 'bb'}


eq_ = iterdiff(eq_)


def get_redis_mock_mgrs():
    return {
        '1.yandex.net': mock.Mock(spec=RedisManager),
        '2.yandex.net': mock.Mock(spec=RedisManager),
    }


def node_id_from_track_id(track_id):
    if track_id == TRACK_ID_1:
        return '1.yandex.net'
    if track_id == TRACK_ID_2:
        return '2.yandex.net'
    return 'unknown'


@with_settings(
    TRACK_TTL=10,
    TRACK_TTL_OFFSET=2,
)
class TestTrackManager(unittest.TestCase):
    track_class = RegisterTrack

    def setUp(self):
        self.manager = TrackManager(get_redis_mock_mgrs())

        self.get_node_id_from_track_id_mock = mock.Mock(side_effect=node_id_from_track_id)
        self.create_track_id_mock = mock.Mock(side_effect=lambda: TRACK_ID_1)
        self.create_short_track_id_mock = mock.Mock(side_effect=lambda: TRACK_ID_2)
        self.pipeline_execute_mock = mock.Mock(return_value=[0, None, {}])
        self.pipeline_mock = mock.Mock()
        self.pipeline_mock.execute = self.pipeline_execute_mock

        for node_id in get_redis_mock_mgrs():
            self.manager.redis_track_managers[node_id].pipeline = mock.Mock(return_value=self.pipeline_mock)

        # Эти функции лежат в utils, но мокаем их в track_manager - они туда уже проимпортировались
        self.patches = [
            mock.patch(
                'passport.backend.core.tracks.track_manager.get_node_id_from_track_id',
                self.get_node_id_from_track_id_mock,
            ),
            mock.patch(
                'passport.backend.core.tracks.track_manager.create_track_id',
                self.create_track_id_mock,
            ),
            mock.patch(
                'passport.backend.core.tracks.track_manager.create_short_track_id',
                self.create_short_track_id_mock,
            ),
        ]

        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.patches
        del self.manager
        del self.get_node_id_from_track_id_mock
        del self.create_track_id_mock
        del self.create_short_track_id_mock
        del self.pipeline_execute_mock
        del self.pipeline_mock

    def pipe_call_args_list(self):
        return [
            (name, args)  # kwargs нигде не используются
            for name, args, kwargs in self.pipeline_mock.method_calls
        ]

    def test_read_track(self):
        self.pipeline_execute_mock.side_effect = [
            (5, 1, {'track_type': 'register'}),
            ([],),
        ]
        self.manager.read(TRACK_ID_2)

        eq_(self.manager.redis_track_managers['1.yandex.net'].pipeline.call_count, 0)
        eq_(self.manager.redis_track_managers['2.yandex.net'].pipeline.call_count, 2)  # две транзакции на трек
        eq_(
            self.pipe_call_args_list(),
            [
                ('multi', ()),
                ('ttl', ('track:%s' % TRACK_ID_2,)),
                ('get', ('track:%s:version' % TRACK_ID_2,)),
                ('hgetall', ('track:%s' % TRACK_ID_2,)),
                ('execute', ()),
                ('multi', ()),
                ('lrange', ('track:%s:phone_operation_confirmations' % TRACK_ID_2, 1, -1)),
                ('lrange', ('track:%s:restore_methods_select_order' % TRACK_ID_2, 1, -1)),
                ('lrange', ('track:%s:suggested_logins' % TRACK_ID_2, 1, -1)),
                ('lrange', ('track:%s:totp_push_device_ids' % TRACK_ID_2, 1, -1)),
                ('execute', ()),
            ],
        )

    @raises(TrackNotFoundError)
    def test_read_not_existing_track(self):
        self.manager.read(TRACK_ID_1)

    @raises(NodeNotFoundError)
    def test_read_track_from_unknown_node(self):
        self.manager.read(BAD_TRACK_ID_1)

    @raises(ValueError)
    def test_create_track_unknown_track_type(self):
        self.manager.create('unknown', 'dev')

    def test_create_track_avaliable_types(self):
        for type_ in ['register', 'complete', 'authorize']:
            ok_(self.manager.create(type_, 'dev'))

    def test_create_track_with_process_name(self):
        ok_(self.manager.create('complete', 'dev', process_name='process'))

    def test_create_track(self):
        # Этот тест проверяет трек-менеджера на примере работы с треком типа 'register'
        created = time.time()
        track = self.manager.create('register', 'dev', created)
        ok_(isinstance(track, self.track_class))
        eq_(track.track_id, TRACK_ID_1)
        eq_(track.track_version, 1)

        eq_(
            self.pipe_call_args_list(),
            [
                ('multi', ()),
                ('set', ('track:%s:version' % TRACK_ID_1, 1)),
                ('expire', ('track:%s:version' % TRACK_ID_1, 10)),
                ('hmset', ('track:%s' % TRACK_ID_1, {'track_type': 'register', 'consumer': 'dev', 'created': created})),
                ('expire', ('track:%s' % TRACK_ID_1, 10)),
                ('rpush', ('track:%s:phone_operation_confirmations' % TRACK_ID_1, '<root>')),
                ('expire', ('track:%s:phone_operation_confirmations' % TRACK_ID_1, 10)),
                ('rpush', ('track:%s:restore_methods_select_order' % TRACK_ID_1, '<root>')),
                ('expire', ('track:%s:restore_methods_select_order' % TRACK_ID_1, 10)),
                ('rpush', ('track:%s:suggested_logins' % TRACK_ID_1, '<root>')),
                ('expire', ('track:%s:suggested_logins' % TRACK_ID_1, 10)),
                ('rpush', ('track:%s:totp_push_device_ids' % TRACK_ID_1, '<root>')),
                ('expire', ('track:%s:totp_push_device_ids' % TRACK_ID_1, 10)),
                ('execute', ()),
            ],
        )

    def test_create_track_with_short_track_id(self):
        track = self.manager.create_short('complete', 'dev', process_name='process')
        eq_(track.track_id, TRACK_ID_2)

    def test_transaction(self):
        self.pipeline_execute_mock.side_effect = [
            (5, 1, {'track_type': 'register'}),
            ([],),
            (5, 1, {'track_type': 'register'}),
            ([],),
        ]
        track = self.manager.read(TRACK_ID_1)
        transaction = self.manager.transaction(TRACK_ID_1)

        ok_(isinstance(transaction, TrackTransaction))
        eq_(transaction.track.track_id, track.track_id)
        ok_(transaction.manager is self.manager)
