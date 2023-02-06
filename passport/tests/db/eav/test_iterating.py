# -*- coding: utf-8 -*-
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.oauth.core.db.eav.context_managers import CREATE
from passport.backend.oauth.core.test.fake_db import FakeDB
from passport.backend.oauth.core.test.framework import BaseTestCase

from .base_test_data import (
    ClientForTest,
    TokenForTest,
)


class TestTokenIterating(BaseTestCase):
    def setUp(self):
        super(TestTokenIterating, self).setUp()
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
        super(TestTokenIterating, self).tearDown()

    def test_iterate_equal_chunks(self):
        iterator = TokenForTest.iterate_by_chunks(chunk_size=2)
        chunk1 = next(iterator)
        eq_(len(chunk1), 2)
        chunk2 = next(iterator)
        eq_(len(chunk2), 2)
        assert_raises(StopIteration, next, iterator)

    def test_iterate_inequal_chunks(self):
        iterator = TokenForTest.iterate_by_chunks(chunk_size=3)
        chunk1 = next(iterator)
        eq_(len(chunk1), 3)
        chunk2 = next(iterator)
        eq_(len(chunk2), 1)
        assert_raises(StopIteration, next, iterator)

    def test_iterate_large_chunk(self):
        iterator = TokenForTest.iterate_by_chunks(chunk_size=100)
        chunk1 = next(iterator)
        eq_(len(chunk1), 4)
        assert_raises(StopIteration, next, iterator)

    def test_iterate_by_one(self):
        iterator = TokenForTest.iterate_by_chunks(chunk_size=1)
        for i in range(4):
            chunk = next(iterator)
            eq_(len(chunk), 1)
        assert_raises(StopIteration, next, iterator)

    def test_iterate_from_id(self):
        iterator = TokenForTest.iterate_by_chunks(chunk_size=10, last_processed_id=2)
        chunk = next(iterator)
        eq_(len(chunk), 2)


class TestClientIterating(BaseTestCase):
    def setUp(self):
        super(TestClientIterating, self).setUp()
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

    def tearDown(self):
        self.fake_db.stop()
        super(TestClientIterating, self).tearDown()

    def test_iterate_equal_chunks(self):
        iterator = ClientForTest.iterate_by_chunks(chunk_size=2)
        chunk1 = next(iterator)
        eq_(len(chunk1), 2)
        chunk2 = next(iterator)
        eq_(len(chunk2), 2)
        assert_raises(StopIteration, next, iterator)

    def test_iterate_inequal_chunks(self):
        iterator = ClientForTest.iterate_by_chunks(chunk_size=3)
        chunk1 = next(iterator)
        eq_(len(chunk1), 3)
        chunk2 = next(iterator)
        eq_(len(chunk2), 1)
        assert_raises(StopIteration, next, iterator)

    def test_iterate_large_chunk(self):
        iterator = ClientForTest.iterate_by_chunks(chunk_size=100)
        chunk1 = next(iterator)
        eq_(len(chunk1), 4)
        assert_raises(StopIteration, next, iterator)

    def test_iterate_by_one(self):
        iterator = ClientForTest.iterate_by_chunks(chunk_size=1)
        for i in range(4):
            chunk = next(iterator)
            eq_(len(chunk), 1)
        assert_raises(StopIteration, next, iterator)

    def test_iterate_from_id(self):
        iterator = ClientForTest.iterate_by_chunks(chunk_size=10, last_processed_id=2)
        chunk = next(iterator)
        eq_(len(chunk), 2)
