# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.oauth.core.db.eav.context_managers import CREATE
from passport.backend.oauth.core.test.fake_db import FakeDB
from passport.backend.oauth.core.test.framework import BaseTestCase
from passport.backend.utils.time import unixtime_to_datetime

from .base_test_data import (
    ClientForTest,
    TokenForTest,
)


class TestTokenBulkLoad(BaseTestCase):
    def setUp(self):
        super(TestTokenBulkLoad, self).setUp()
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
        super(TestTokenBulkLoad, self).tearDown()

    def test_select_by_ids(self):
        tokens = TokenForTest.by_ids([1, 2])
        eq_(list(tokens.keys()), [1, 2])

        tokens = TokenForTest.by_ids(range(2, 10))
        eq_(list(tokens.keys()), [2, 3, 4])

    def test_select_by_empty_ids(self):
        tokens = TokenForTest.by_ids([])
        eq_(tokens, {})


class TestClientBulkLoad(BaseTestCase):
    def setUp(self):
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

    def test_select_by_ids(self):
        clients = ClientForTest.by_ids([1, 2])
        eq_(list(clients.keys()), [1, 2])

        clients = ClientForTest.by_ids(range(2, 10))
        eq_(list(clients.keys()), [2, 3, 4])

    def test_select_by_empty_ids(self):
        clients = ClientForTest.by_ids([])
        eq_(clients, {})
