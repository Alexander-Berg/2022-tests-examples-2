# -*- coding: utf-8 -*-
import json

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.phone_squatter import (
    PhoneSquatter,
    PhoneSquatterPermanentError,
    PhoneSquatterPhoneNumberNotTrackedError,
    PhoneSquatterPhoneNumberUntrackableError,
    PhoneSquatterTemporaryError,
)
from passport.backend.core.builders.phone_squatter.faker import (
    FakePhoneSquatter,
    phone_squatter_get_change_status_response,
    phone_squatter_start_tracking_response,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.useragent.sync import RequestError


TEST_PHONE_NUMBER = '+78001234567'
TEST_REQUEST_ID = 'req-id'


@with_settings(
    PHONE_SQUATTER_URL='http://localhost/',
    PHONE_SQUATTER_TIMEOUT=1,
    PHONE_SQUATTER_RETRIES=2,
)
class TestPhoneSquatter(PassportTestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'phone_squatter',
                        'ticket': TEST_TICKET,
                    },
                },
            )
        )
        self.fake_tvm_credentials_manager.start()

        self.faker = FakePhoneSquatter()
        self.faker.start()

        self.phone_squatter = PhoneSquatter()

    def tearDown(self):
        self.faker.stop()
        self.fake_tvm_credentials_manager.stop()

    def test_server_error(self):
        self.faker.set_response_value('get_change_status', 'Server error', 500)
        with assert_raises(PhoneSquatterPermanentError):
            self.phone_squatter.get_change_status(TEST_PHONE_NUMBER, TEST_REQUEST_ID)
        eq_(len(self.faker.requests), 1)

    def test_request_error(self):
        self.faker.set_response_side_effect('get_change_status', RequestError)
        with assert_raises(PhoneSquatterTemporaryError):
            self.phone_squatter.get_change_status(TEST_PHONE_NUMBER, TEST_REQUEST_ID)
        eq_(len(self.faker.requests), 2)

    def test_get_change_status_ok(self):
        self.faker.set_response_value('get_change_status', phone_squatter_get_change_status_response())

        rv = self.phone_squatter.get_change_status(TEST_PHONE_NUMBER, TEST_REQUEST_ID)
        eq_(rv, json.loads(phone_squatter_get_change_status_response()))

        eq_(len(self.faker.requests), 1)
        req = self.faker.requests[0]
        req.assert_url_starts_with('http://localhost/phone/change/status?')
        req.assert_properties_equal(
            method='POST',
            json_data={
                'phone': TEST_PHONE_NUMBER,
            },
        )
        req.assert_query_equals({
            'reqid': TEST_REQUEST_ID,
            'allow_cached': 'false',
        })
        req.assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
        })

    def test_get_change_status_allow_cached_ok(self):
        self.faker.set_response_value('get_change_status', phone_squatter_get_change_status_response())

        rv = self.phone_squatter.get_change_status(TEST_PHONE_NUMBER, TEST_REQUEST_ID, allow_cached=True)
        eq_(rv, json.loads(phone_squatter_get_change_status_response()))

        eq_(len(self.faker.requests), 1)
        req = self.faker.requests[0]
        req.assert_url_starts_with('http://localhost/phone/change/status?')
        req.assert_properties_equal(
            method='POST',
            json_data={
                'phone': TEST_PHONE_NUMBER,
            },
        )
        req.assert_query_equals({
            'reqid': TEST_REQUEST_ID,
            'allow_cached': 'true',
        })
        req.assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
        })

    def test_get_change_status_not_tracked(self):
        self.faker.set_response_value('get_change_status', '{}', 402)

        with assert_raises(PhoneSquatterPhoneNumberNotTrackedError):
            self.phone_squatter.get_change_status(TEST_PHONE_NUMBER, TEST_REQUEST_ID)

    def test_get_change_status_untrackable(self):
        self.faker.set_response_value('get_change_status', '{}', 422)

        with assert_raises(PhoneSquatterPhoneNumberUntrackableError):
            self.phone_squatter.get_change_status(TEST_PHONE_NUMBER, TEST_REQUEST_ID)

    def test_start_tracking_ok(self):
        self.faker.set_response_value('start_tracking', phone_squatter_start_tracking_response())

        rv = self.phone_squatter.start_tracking(TEST_PHONE_NUMBER, TEST_REQUEST_ID)
        eq_(rv, json.loads(phone_squatter_start_tracking_response()))

        eq_(len(self.faker.requests), 1)
        req = self.faker.requests[0]
        req.assert_url_starts_with('http://localhost/phone/tracking/start?')
        req.assert_properties_equal(
            method='POST',
            json_data={
                'phone': TEST_PHONE_NUMBER,
            },
        )
        req.assert_query_equals({
            'reqid': TEST_REQUEST_ID,
            'draft': 'false',
        })
        req.assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
        })

    def test_start_tracking_draft_ok(self):
        self.faker.set_response_value('start_tracking', phone_squatter_start_tracking_response())

        rv = self.phone_squatter.start_tracking(TEST_PHONE_NUMBER, TEST_REQUEST_ID, is_draft=True)
        eq_(rv, json.loads(phone_squatter_start_tracking_response()))

        eq_(len(self.faker.requests), 1)
        req = self.faker.requests[0]
        req.assert_url_starts_with('http://localhost/phone/tracking/start?')
        req.assert_properties_equal(
            method='POST',
            json_data={
                'phone': TEST_PHONE_NUMBER,
            },
        )
        req.assert_query_equals({
            'reqid': TEST_REQUEST_ID,
            'draft': 'true',
        })
        req.assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
        })

    def test_start_tracking_draft__already_tracking(self):
        response = phone_squatter_start_tracking_response(status='ALREADY_TRACKING')
        self.faker.set_response_value('start_tracking', response, 202)

        rv = self.phone_squatter.start_tracking(TEST_PHONE_NUMBER, TEST_REQUEST_ID)
        eq_(rv, json.loads(response))
