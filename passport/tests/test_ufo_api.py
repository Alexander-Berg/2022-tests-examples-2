# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.ufo_api import UfoApi
from passport.backend.core.builders.ufo_api.exceptions import (
    UfoApiInvalidResponseError,
    UfoApiTemporaryError,
)
from passport.backend.core.builders.ufo_api.faker import (
    FakeUfoApi,
    ufo_api_phones_stats_response,
    ufo_api_profile_item,
    ufo_api_profile_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = 1
TEST_SID = 'mail'
TEST_TIMESTAMP = 100000

TEST_PHONE = PhoneNumber.parse('+79091234567')


@with_settings(
    UFO_API_URL='http://localhost/',
    UFO_API_TIMEOUT=1,
    UFO_API_RETRIES=2,
    UFO_API_USE_RC=False,
)
class TestUfoApiCommon(unittest.TestCase):
    def setUp(self):
        self.ufo_api = UfoApi()
        self.ufo_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.ufo_api.useragent.request.return_value = self.response
        self.ufo_api.useragent.request_error_class = self.ufo_api.temporary_error_class
        self.response.content = json.dumps(ufo_api_profile_response()).encode('utf8')
        self.response.status_code = 200

    def tearDown(self):
        del self.ufo_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = b'some kind of json'
        with assert_raises(UfoApiInvalidResponseError):
            self.ufo_api.profile(uid=TEST_UID)

    def test_server_error(self):
        self.response.status_code = 500
        with assert_raises(UfoApiTemporaryError):
            self.ufo_api.profile(uid=TEST_UID)

    def test_default_initialization(self):
        ufo_api = UfoApi()
        ok_(ufo_api.useragent is not None)
        eq_(ufo_api.url, 'http://localhost/')


@with_settings(
    UFO_API_URL='http://localhost/',
    UFO_API_TIMEOUT=1,
    UFO_API_RETRIES=2,
    UFO_API_USE_RC=False,
)
class TestUfoApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_ufo_api = FakeUfoApi()
        self.fake_ufo_api.start()
        self.fake_ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(),
            ).encode('utf8'),
        )
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            json.dumps(
                ufo_api_phones_stats_response(TEST_PHONE),
            ).encode('utf8'),
        )
        self.ufo_api = UfoApi()

    def tearDown(self):
        self.fake_ufo_api.stop()
        del self.fake_ufo_api

    def test_profile_empty_ok(self):
        response = self.ufo_api.profile(uid=TEST_UID)
        eq_(
            response,
            ufo_api_profile_response(),
        )
        self.fake_ufo_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/1/profile/?uid=%s' % TEST_UID,
        )

    def test_profile_ok(self):
        self.fake_ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=[ufo_api_profile_item()],
                ),
            ).encode('utf8'),
        )
        response = self.ufo_api.profile(uid=TEST_UID)
        eq_(
            response,
            ufo_api_profile_response(
                items=[ufo_api_profile_item()],
            ),
        )
        self.fake_ufo_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/1/profile/?uid=%s' % TEST_UID,
        )

    def test_profile_with_use_rc_ok(self):
        self.fake_ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=[ufo_api_profile_item()],
                ),
            ).encode('utf8'),
        )
        response = UfoApi(use_rc=True).profile(uid=TEST_UID)
        eq_(
            response,
            ufo_api_profile_response(
                items=[ufo_api_profile_item()],
            ),
        )
        self.fake_ufo_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/1/profile/?uid=%s&use_rc=yes' % TEST_UID,
        )

    def test_profile_invalid_response(self):
        self.fake_ufo_api.set_response_value(
            'profile',
            'Invalid response',
        )
        with assert_raises(UfoApiInvalidResponseError):
            self.ufo_api.profile(uid=TEST_UID)

    def test_phones_stats_empty_ok(self):
        response = self.ufo_api.phones_stats(phone=TEST_PHONE)
        eq_(
            response,
            ufo_api_phones_stats_response(TEST_PHONE),
        )
        self.fake_ufo_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/1/phones/stats/?phone=%s' % TEST_PHONE.digital,
        )

    def test_phones_stats_ok(self):
        stats = {'blob': 'data'}
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            json.dumps(
                ufo_api_phones_stats_response(
                    TEST_PHONE,
                    stats,
                ),
            ).encode('utf8'),
        )
        response = self.ufo_api.phones_stats(phone=TEST_PHONE)
        eq_(
            response,
            ufo_api_phones_stats_response(
                TEST_PHONE,
                stats,
            ),
        )
        self.fake_ufo_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/1/phones/stats/?phone=%s' % TEST_PHONE.digital,
        )

    def test_phones_stats_invalid_response(self):
        self.fake_ufo_api.set_response_value(
            'phones_stats',
            'Invalid response',
        )
        with assert_raises(UfoApiInvalidResponseError):
            self.ufo_api.phones_stats(phone=TEST_PHONE)
