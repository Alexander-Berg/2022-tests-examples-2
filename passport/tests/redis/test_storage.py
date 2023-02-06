# -*- coding: utf-8 -*-
import mock
from passport.backend.perimeter.auth_api.redis.storage import RedisStorage
from passport.backend.perimeter.auth_api.test import BaseTestCase
from redis import RedisError


class TestStorageCommon(BaseTestCase):
    def setUp(self):
        self.storage = RedisStorage(
            host='host',
            port=123,
            expire_time=10,
            password='foo',
            timeout=1,
            connect_timeout=2,
        )

    def test_params(self):
        assert self.storage._conn is None
        assert self.storage._host == 'host'
        assert self.storage._port == 123
        assert self.storage._expire_time == 10
        assert self.storage._timeout == 1
        assert self.storage._connect_timeout == 2

    def test_connect(self):
        assert self.storage._conn is None
        self.storage.connect()
        assert self.storage._conn is not None


class TestStorageGetSet(BaseTestCase):
    def setUp(self):
        self.storage = RedisStorage(
            host='host',
            port=123,
            expire_time=10,
            password='foo',
            timeout=1,
            connect_timeout=2,
        )
        self.pipe_mock = mock.Mock()
        self.pipe_mock.execute = mock.Mock(return_value=None)
        self.connection_mock = mock.Mock()
        self.connection_mock.pipeline = mock.Mock(return_value=self.pipe_mock)
        self.connect_mock = mock.Mock()

        self.storage.connect = self.connect_mock
        self.storage._conn = self.connection_mock

    def test_get__ok(self):
        self.pipe_mock.execute.return_value = [{b'a': b'321'}, 10]
        assert self.storage.get('some-key') == {'a': '321'}

        assert not self.connect_mock.called
        assert self.pipe_mock.execute.call_count == 1

    def test_set__ok(self):
        self.pipe_mock.execute.return_value = [1, None]
        assert self.storage.set('some-key', 123)

        assert not self.connect_mock.called
        assert self.pipe_mock.execute.call_count == 1

    def test_set__error(self):
        self.pipe_mock.execute.return_value = [0, None]

        assert not self.storage.set('some-other-key', 2)

        assert self.connect_mock.call_count == 0
        assert self.pipe_mock.execute.call_count == 1

    def test_connect_and_set__error(self):
        self.storage._conn = None
        self.storage.connect = lambda: setattr(self.storage, '_conn', self.connection_mock)
        self.pipe_mock.execute.return_value = [0, None]

        assert not self.storage.set('some-other-key', 2)

        assert self.storage._conn is not None
        assert self.pipe_mock.execute.call_count == 1

    def test_get_set__redis_error(self):
        self.pipe_mock.execute.side_effect = RedisError
        assert not self.storage.get('key')
        assert not self.storage.set('key', 1)

    def test_push_to_list__ok(self):
        self.pipe_mock.execute.return_value = [1, None, None]
        assert self.storage.push_to_list('some-key', 123, 10)

        assert not self.connect_mock.called
        assert self.pipe_mock.execute.call_count == 1

    def test_push_to_list__redis_error(self):
        self.pipe_mock.execute.side_effect = RedisError
        assert not self.storage.push_to_list('some-key', 123, 10)

    def test_get_lists__ok(self):
        self.pipe_mock.execute.return_value = [[b'1', b'2'], 10, [], 10, [b'3', b'4'], 0]
        assert self.storage.get_lists('key1', 'key2', 'key3') == {
            'key1': ['1', '2'],
            'key2': [],
            'key3': [],
        }

        assert not self.connect_mock.called
        assert self.pipe_mock.execute.call_count == 1

    def test_get_lists__redis_error(self):
        self.pipe_mock.execute.side_effect = RedisError
        assert self.storage.get_lists('key1', 'key2', 'key3') == {}
