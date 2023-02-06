# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.mail_apis import (
    Collie,
    CollieInvalidResponseError,
    CollieTemporaryError,
)
from passport.backend.core.builders.mail_apis.collie import DEFAULT_LIMIT
from passport.backend.core.builders.mail_apis.faker import (
    collie_item,
    collie_response,
    FakeCollie,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.useragent.sync import RequestError


TEST_UID = 1
TEST_REQUEST_ID = 'rid'


@with_settings_hosts(
    COLLIE_API_URL='http://localhost/',
    COLLIE_API_RETRIES=10,
    COLLIE_API_TIMEOUT=1,
)
class TestCollie(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'collie',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.collie = Collie()

        self.fake_collie = FakeCollie()
        self.fake_collie.start()

        self.methods = [
            ('search_contacts', self.collie.search_contacts),
        ]

    def tearDown(self):
        self.fake_collie.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_collie
        del self.collie
        del self.methods
        del self.fake_tvm_credentials_manager

    def test_search_contacts(self):
        self.fake_collie.set_response_value(
            'search_contacts',
            collie_response(items=[collie_item()]),
        )

        contacts = self.collie.search_contacts(TEST_UID, request_id=TEST_REQUEST_ID)

        eq_(contacts, [collie_item()])

        requests = self.fake_collie.requests
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/v1/users/%d/contacts/[]?offset=0&limit=%s' % (TEST_UID, DEFAULT_LIMIT),
            headers={
                'X-Ya-Service-Ticket': TEST_TICKET,
                'X-Request-Id': TEST_REQUEST_ID,
            },
        )

    def test_retries_error(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_collie.set_response_side_effect(method_name, RequestError)
            with assert_raises(CollieTemporaryError):
                method(TEST_UID)
        eq_(len(self.fake_collie.requests), 10 * (i + 1))

    def test_bad_status_code(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_collie.set_response_value(method_name, b'{}', status=500)
            with assert_raises(CollieInvalidResponseError):
                method(TEST_UID)
        eq_(len(self.fake_collie.requests), i + 1)

    def test_invalid_json(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_collie.set_response_value(method_name, b'invalid json')
            with assert_raises(CollieInvalidResponseError):
                method(TEST_UID)
        eq_(len(self.fake_collie.requests), i + 1)
