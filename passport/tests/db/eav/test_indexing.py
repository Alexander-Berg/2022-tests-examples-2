# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.oauth.core.common.utils import make_hash
from passport.backend.oauth.core.db.eav.context_managers import CREATE
from passport.backend.oauth.core.test.fake_db import FakeDB
from passport.backend.oauth.core.test.framework import BaseTestCase
from passport.backend.utils.time import unixtime_to_datetime

from .base_test_data import (
    ClientForTest,
    TokenForTest,
)


class TestTokenIndexing(BaseTestCase):
    def setUp(self):
        super(TestTokenIndexing, self).setUp()
        self.fake_db = FakeDB()
        self.fake_db.start()

        with CREATE(TokenForTest()) as token:
            token.uid = 1
            token.access_token = 'foo'
            token.scope_ids = [1, 2]
            token.client_id = 1
            token.device_id = 'apple'

        with CREATE(TokenForTest()) as token:
            token.uid = 1
            token.access_token = 'bar'
            token.scope_ids = [2, 3]
            token.client_id = 2
            token.device_id = 'apple'

        with CREATE(TokenForTest()) as token:
            token.uid = 1
            token.access_token = 'zar'
            token.scope_ids = [3, 4]
            token.client_id = 2
            token.device_id = 'android'

        with CREATE(TokenForTest()) as token:
            token.uid = 2
            token.access_token = 'zarr'
            token.scope_ids = [3, 4]
            token.client_id = 2
            token.device_id = 'android'

        self.fake_db.reset_mocks()

    def tearDown(self):
        self.fake_db.stop()
        super(TestTokenIndexing, self).tearDown()

    def test_select_by_uid(self):
        tokens = TokenForTest.by_index('params', uid=1)
        eq_(len(tokens), 3)

        tokens = TokenForTest.by_index('params', uid=2)
        eq_(len(tokens), 1)

    def test_select_by_params(self):
        tokens = TokenForTest.by_index('params', uid=1, client_id=2)
        eq_(len(tokens), 2)

        tokens = TokenForTest.by_index('params', uid=1, client_id=2, scope_ids=b'|2|3|', device_id=b'apple')
        eq_(len(tokens), 1)

    def test_select_by_access_token(self):
        tokens = TokenForTest.by_index('access_token', access_token=make_hash('foo'))
        eq_(len(tokens), 1)

    def test_select_with_limits(self):
        tokens = TokenForTest.by_index('params', uid=[1, 2])
        eq_(len(tokens), 4)
        eq_(TokenForTest.count_by_index('params', uid=[1, 2]), 4)

        tokens = TokenForTest.by_index('params', uid=[1, 2], limit=2)
        eq_(len(tokens), 2)
        eq_(tokens[0].id, 1)
        eq_(tokens[1].id, 2)

        tokens = TokenForTest.by_index('params', uid=[1, 2], limit=2, offset=2)
        eq_(len(tokens), 2)
        eq_(tokens[0].id, 3)
        eq_(tokens[1].id, 4)


class TestClientIndexing(BaseTestCase):
    def setUp(self):
        super(TestClientIndexing, self).setUp()
        self.fake_db = FakeDB()
        self.fake_db.start()

        with CREATE(ClientForTest()) as client:
            client.uid = 1
            client.display_id = 'foo_1'
            client.approval_status = 0
            client.services = ['test']

        with CREATE(ClientForTest()) as client:
            client.uid = 1
            client.display_id = 'foo_2'
            client.approval_status = 1
            client.services = ['test']

        with CREATE(ClientForTest()) as client:
            client.uid = 2
            client.display_id = 'foo_3'
            client.approval_status = 0
            client.services = ['prod']

        with CREATE(ClientForTest()) as client:
            client.uid = 2
            client.display_id = 'foo_4'
            client.approval_status = 1
            client.services = ['test']

        with CREATE(ClientForTest()) as client:
            client.uid = 1
            client.display_id = 'foo_deleted'
            client.approval_status = 1
            client.services = ['test']
            client.deleted = unixtime_to_datetime(1)

    def tearDown(self):
        self.fake_db.stop()
        super(TestClientIndexing, self).tearDown()

    def test_select_by_uid(self):
        clients = ClientForTest.by_index('uid', uid=1)
        eq_(len(clients), 2)

        clients = ClientForTest.by_index('uid', uid=2)
        eq_(len(clients), 2)

    def test_select_by_display_id(self):
        clients = ClientForTest.by_index('params', display_id=b'foo_1')
        eq_(len(clients), 1)

    def test_select_deleted_by_display_id(self):
        clients = ClientForTest.by_index('params', display_id=b'foo_deleted')
        eq_(clients, [])

        clients = ClientForTest.by_index('params', display_id=b'foo_deleted', allow_deleted=True)
        eq_(len(clients), 1)

    def test_select_by_approval_status(self):
        clients = ClientForTest.by_index('params', approval_status=[0, 1])
        eq_(len(clients), 4)

        clients = ClientForTest.by_index('params', approval_status=1)
        eq_(len(clients), 2)

    def test_select_by_approval_services(self):
        clients = ClientForTest.by_index('params', services=['test', 'prod'])
        eq_(len(clients), 4)

        clients = ClientForTest.by_index('params', services=['test'])
        eq_(len(clients), 3)

    def test_select_by_params(self):
        clients = ClientForTest.by_index('params', services=['test', 'prod'], approval_status=[0, 1], uid=[1, 2])
        eq_(len(clients), 4)

        clients = ClientForTest.by_index('params', services='test', approval_status=[0, 1], uid=2)
        eq_(len(clients), 1)

        clients = ClientForTest.by_index('params', services=['prod'], approval_status=1, uid=2)
        eq_(len(clients), 0)

    def test_select_with_limits(self):
        clients = ClientForTest.by_index('params', uid=[1, 2], limit=10)
        eq_(len(clients), 4)
        eq_(ClientForTest.count_by_index('params', uid=[1, 2], limit=10), 5)  # тут удалённые тоже считаем

        clients = ClientForTest.by_index('params', uid=[1, 2], limit=2)
        eq_(len(clients), 2)
        eq_(clients[0].id, 1)
        eq_(clients[1].id, 2)

        clients = ClientForTest.by_index('params', uid=[1, 2], limit=2, offset=2)
        eq_(len(clients), 2)
        eq_(clients[0].id, 3)
        eq_(clients[1].id, 4)

    def test_select_deleted_by_params(self):
        clients = ClientForTest.by_index(
            'params',
            allow_deleted=True,
            services=['test', 'prod'],
            approval_status=[0, 1],
            uid=[1, 2],
        )
        eq_(len(clients), 5)
