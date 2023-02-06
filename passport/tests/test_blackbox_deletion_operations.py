# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_deletion_operations_response,
    FakeBlackbox,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.utils.time import datetime_to_integer_unixtime

from .test_blackbox import BaseBlackboxTestCase


TEST_TIMESTAMP1 = datetime(2012, 10, 1)
TEST_TIMESTAMP2 = datetime(2014, 4, 5)


@with_settings(
    BLACKBOX_URL=u'http://blackb.ox/',
)
class TestDeletionOperationsResponse(BaseBlackboxTestCase):
    def setUp(self):
        super(TestDeletionOperationsResponse, self).setUp()
        self.faker = FakeBlackbox()
        self.faker.start()
        self.blackbox = Blackbox()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        super(TestDeletionOperationsResponse, self).tearDown()

    def test_empty(self):
        self.faker.set_response_value('deletion_operations', blackbox_deletion_operations_response([]))

        response = self.blackbox.deletion_operations(
            deleted_after=TEST_TIMESTAMP1,
            deleted_before=TEST_TIMESTAMP2,
            chunk_count=1,
            chunk_no=0,
        )

        eq_(response, {'deletion_operations': []})

    def test_ok(self):
        self.faker.set_response_value('deletion_operations', blackbox_deletion_operations_response([{'uid': 51}]))

        response = self.blackbox.deletion_operations(
            deleted_after=TEST_TIMESTAMP1,
            deleted_before=TEST_TIMESTAMP2,
            chunk_count=1,
            chunk_no=0,
        )

        eq_(response, {'deletion_operations': [{'uid': 51}]})

    def test_request(self):
        self.faker.set_response_value('deletion_operations', blackbox_deletion_operations_response())

        self.blackbox.deletion_operations(
            deleted_after=TEST_TIMESTAMP1,
            deleted_before=TEST_TIMESTAMP2,
            chunk_count=10,
            chunk_no=20,
        )

        eq_(len(self.faker.requests), 1)
        self.faker.requests[0].assert_properties_equal(method='GET')
        self.faker.requests[0].assert_url_starts_with('http://blackb.ox/blackbox/?')
        self.faker.requests[0].assert_query_equals({
            'method': 'deletion_operations',
            'deleted_after': str(datetime_to_integer_unixtime(TEST_TIMESTAMP1)),
            'deleted_before': str(datetime_to_integer_unixtime(TEST_TIMESTAMP2)),
            'chunk_count': '10',
            'chunk_no': '20',
            'format': 'json',
        })
