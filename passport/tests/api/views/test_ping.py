# -*- coding: utf-8 -*-
import unittest

import mock
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.takeout.api.app import create_app
from passport.backend.takeout.test_utils.fake_redis import FakeRedis
import redis
from redis.sentinel import MasterNotFoundError


class BaseTaskTestCase(unittest.TestCase):
    def setUp(self):
        self.patches = []
        self.os_access_mock = mock.Mock(return_value=True)
        self.os_access_patch = mock.patch('os.access', self.os_access_mock)
        self.patches.append(self.os_access_patch)

        self.redis_faker = FakeRedis()
        self.patches.append(self.redis_faker)

        self.grants_faker = FakeGrants()
        self.grants_faker._mock.return_value = {}
        self.patches.append(self.grants_faker)

        for patch in self.patches:
            patch.start()

        self.client = create_app().test_client()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()

        del self.grants_faker
        del self.redis_faker
        del self.os_access_patch
        del self.os_access_mock
        del self.client

    def test_ping_simple_ok(self):
        rv = self.client.get('/ping')
        assert rv.status_code == 200
        assert rv.data == b'Pong\n'

        assert self.os_access_mock.called
        assert not self.redis_faker.called

    def test_ping_full_ok(self):
        with mock.patch('passport.backend.takeout.api.views.ping.get_config') as get_config_mock:
            get_config_mock.return_value = {
                'common': {'ping_file': 'ping-file.html'},
            }
            rv = self.client.get('/ping?check=db')
        assert rv.status_code == 200
        assert rv.data == b'Pong\n'

        assert self.os_access_mock.called
        assert self.redis_faker.called

    def test_ping_service_shut_down(self):
        self.os_access_mock.return_value = False

        rv = self.client.get('/ping')
        assert rv.status_code == 521
        assert rv.json == {'error': 'service.shut_down'}

        assert self.os_access_mock.called

    def test_ping_db_unavailable_connection_error(self):
        self.redis_faker.sentinel_mock.return_value.discover_master.side_effect = redis.ConnectionError('some error')

        with mock.patch('passport.backend.takeout.api.views.ping.get_config') as get_config_mock:
            get_config_mock.return_value = {
                'common': {'ping_file': 'ping-file.html'},
            }
            rv = self.client.get('/ping?check=db')
        assert rv.status_code == 521
        assert rv.json == {'error': 'redis.unavailable', 'description': 'some error'}

        assert self.os_access_mock.called
        assert self.redis_faker.called

    def test_ping_db_unavailable_master_not_found(self):
        self.redis_faker.sentinel_mock.return_value.discover_master.side_effect = MasterNotFoundError('some error')

        with mock.patch('passport.backend.takeout.api.views.ping.get_config') as get_config_mock:
            get_config_mock.return_value = {
                'common': {'ping_file': 'ping-file.html'},
            }
            rv = self.client.get('/ping?check=db')
        assert rv.status_code == 521
        assert rv.json == {'error': 'redis.unavailable', 'description': 'some error'}

        assert self.os_access_mock.called
        assert self.redis_faker.called
