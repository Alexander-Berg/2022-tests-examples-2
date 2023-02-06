# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.octopus import (
    Octopus,
    OctopusAuthError,
    OctopusInvalidResponse,
    OctopusPermanentError,
    OctopusSessionNotFound,
    OctopusTemporaryError,
)
from passport.backend.core.builders.octopus.faker import (
    FakeOctopus,
    octopus_response,
    octopus_session_log_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_PHONE_NUMBER = '+79990010101'
TEST_CODE = 327
TEST_CALL_SESSION_ID = '123-qwe'
TEST_CALLER = '+79000010101'
TEST_CALLEE = '+79000020202'
TEST_LANGUAGE = 'ru'


@with_settings(
    OCTOPUS_URL='http://localhost/',
    OCTOPUS_TIMEOUT=1,
    OCTOPUS_RETRIES=2,
    OCTOPUS_AUTH_TOKEN='123',
    TELEPHONY_OK_STATUSES=[
        'InProgress',
    ],
)
class TestOctopusCommon(unittest.TestCase):
    def setUp(self):
        self.octopus = Octopus()
        self.octopus.useragent = mock.Mock()

        self.response = mock.Mock()
        self.octopus.useragent.request.return_value = self.response
        self.octopus.useragent.request_error_class = self.octopus.temporary_error_class
        self.response.content = octopus_response()
        self.response.status_code = 200

    def tearDown(self):
        del self.octopus
        del self.response

    def test_ok(self):
        eq_(
            self.octopus.create_session(TEST_CODE, TEST_CODE, TEST_CALLER, TEST_CALLEE, TEST_LANGUAGE),
            'fed-123-qwe',
        )
        eq_(
            self.octopus.create_flash_call_session(TEST_CALLER, TEST_CALLEE),
            'fed-123-qwe',
        )

    def test_bad_request(self):
        self.response.status_code = 400
        self.response.content = b'Invalid code'
        with assert_raises(OctopusPermanentError):
            self.octopus.create_session(TEST_CODE, TEST_CODE, TEST_CALLER, TEST_CALLEE, TEST_LANGUAGE)
        with assert_raises(OctopusPermanentError):
            self.octopus.create_flash_call_session(TEST_CALLER, TEST_CALLEE)

    def test_session_unusual_status(self):
        self.response.status_code = 418
        with assert_raises(OctopusPermanentError):
            self.octopus.create_session(TEST_CODE, TEST_CODE, TEST_CALLER, TEST_CALLEE, TEST_LANGUAGE)
        with assert_raises(OctopusPermanentError):
            self.octopus.create_flash_call_session(TEST_CALLER, TEST_CALLEE)

    def test_session_not_found(self):
        self.response.status_code = 404
        self.response.content = b'Not found'
        with assert_raises(OctopusSessionNotFound):
            self.octopus.get_session_log(TEST_CALL_SESSION_ID)

    def test_server_error(self):
        self.response.status_code = 401
        self.response.content = b'No unit for auth key'
        with assert_raises(OctopusAuthError):
            self.octopus.create_session(TEST_CODE, TEST_CODE, TEST_CALLER, TEST_CALLEE, TEST_LANGUAGE)
        with assert_raises(OctopusAuthError):
            self.octopus.create_flash_call_session(TEST_CALLER, TEST_CALLEE)

    def test_temporary(self):
        self.response.status_code = 503
        with assert_raises(OctopusTemporaryError):
            self.octopus.create_session(TEST_CODE, TEST_CODE, TEST_CALLER, TEST_CALLEE, TEST_LANGUAGE)
        with assert_raises(OctopusTemporaryError):
            self.octopus.create_flash_call_session(TEST_CALLER, TEST_CALLEE)


@with_settings(
    OCTOPUS_URL='http://localhost/',
    OCTOPUS_TIMEOUT=1,
    OCTOPUS_RETRIES=2,
    OCTOPUS_AUTH_TOKEN='123',
    TELEPHONY_OK_STATUSES=[
        'InProgress',
    ],
)
class TestOctopusMethods(unittest.TestCase):
    def setUp(self):
        self.fake_octopus = FakeOctopus()
        self.fake_octopus.start()
        self.fake_octopus.set_response_value('create_session', octopus_response(TEST_CALL_SESSION_ID))
        self.fake_octopus.set_response_value('create_flash_call_session', octopus_response(TEST_CALL_SESSION_ID))
        self.fake_octopus.set_response_value('get_session_log', octopus_session_log_response())
        self.octopus = Octopus()

    def tearDown(self):
        self.fake_octopus.stop()
        del self.fake_octopus

    def test_create_session_ok(self):
        response = self.octopus.create_session(TEST_CODE, TEST_CODE, TEST_CALLER, TEST_CALLEE, TEST_LANGUAGE)
        eq_(response, TEST_CALL_SESSION_ID)
        self.fake_octopus.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/v0/create-call',
            headers={
                'Authorization': '123',
                'Content-Type': 'application/json',
            },
        )

    def test_create_flash_call_session_ok(self):
        response = self.octopus.create_flash_call_session(TEST_CALLER, TEST_CALLEE)
        eq_(response, TEST_CALL_SESSION_ID)
        self.fake_octopus.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/v0/create-pinger-call',
            headers={
                'Authorization': '123',
                'Content-Type': 'application/json',
            },
        )

    def test_create_session__empty_session_id(self):
        self.fake_octopus.set_response_value('create_session', '')
        with assert_raises(OctopusInvalidResponse):
            self.octopus.create_session(TEST_CODE, TEST_CODE, TEST_CALLER, TEST_CALLEE, TEST_LANGUAGE)

    def test_create_flash_call_session__empty_session_id(self):
        self.fake_octopus.set_response_value('create_flash_call_session', '')
        with assert_raises(OctopusInvalidResponse):
            self.octopus.create_flash_call_session(TEST_CALLER, TEST_CALLEE)

    def test_get_session_log_ok(self):
        expected_response = octopus_session_log_response()
        self.fake_octopus.set_response_value('get_session_log', expected_response)
        response = self.octopus.get_session_log(TEST_CALL_SESSION_ID)
        eq_(response, json.loads(expected_response))
        self.fake_octopus.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/v0/call-status?sessionID=%s' % TEST_CALL_SESSION_ID,
            headers={
                'Authorization': '123',
            },
        )

    def test_get_session_log_invalid_response(self):
        self.fake_octopus.set_response_value('get_session_log', 'not a json')
        with assert_raises(OctopusPermanentError):
            self.octopus.get_session_log(TEST_CALL_SESSION_ID)

    def test_get_session_log_error_status(self):
        self.fake_octopus.set_response_value('get_session_log', octopus_session_log_response(status='error'))
        with assert_raises(OctopusInvalidResponse):
            self.octopus.get_session_log(TEST_CALL_SESSION_ID)

    def test_get_session_log_no_status(self):
        self.fake_octopus.set_response_value('get_session_log', '{}')
        with assert_raises(OctopusInvalidResponse):
            self.octopus.get_session_log(TEST_CALL_SESSION_ID)

    def test_temporary(self):
        self.fake_octopus.set_response_side_effect('create_session', OctopusTemporaryError())
        with assert_raises(OctopusTemporaryError):
            self.octopus.create_session(TEST_CODE, TEST_CODE, TEST_CALLER, TEST_CALLEE, TEST_LANGUAGE)
        eq_(len(self.fake_octopus.requests), 2)
