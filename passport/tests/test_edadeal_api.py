# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import (
    assert_raises,
    ok_,
)
from passport.backend.core.builders.edadeal import (
    EdadealApi,
    EdadealPermanentError,
)
from passport.backend.core.builders.edadeal.faker import FakeEdadealApi
from passport.backend.core.test.test_utils import with_settings


TEST_EDADEAL_TOKEN = '123-qwe'
TEST_UID = 1


@with_settings(
    EDADEAL_URL='http://localhost',
    EDADEAL_TIMEOUT=1,
    EDADEAL_RETRIES=2,
    EDADEAL_TOKEN=TEST_EDADEAL_TOKEN,
)
class TestEdadealCommon(unittest.TestCase):
    def setUp(self):
        self.edadeal = EdadealApi()
        self.edadeal.useragent = mock.Mock()

        self.response = mock.Mock()
        self.edadeal.useragent.request.return_value = self.response
        self.edadeal.useragent.request_error_class = self.edadeal.temporary_error_class
        self.response.content = b''
        self.response.status_code = 200

    def tearDown(self):
        del self.edadeal
        del self.response

    def test_ok(self):
        ok_(not self.edadeal.update_plus_status(TEST_UID, is_active=True))

    def test_bad_request(self):
        self.response.status_code = 400
        self.response.content = b'JSON decoding failure(passport)'
        with assert_raises(EdadealPermanentError):
            self.edadeal.update_plus_status(TEST_UID, is_active=False)

    def test_auth_error(self):
        self.response.status_code = 401
        self.response.content = b'Wrong authorization header(passport)'
        with assert_raises(EdadealPermanentError):
            self.edadeal.update_plus_status(TEST_UID, is_active=True)

    def test_server_error(self):
        self.response.status_code = 500
        with assert_raises(EdadealPermanentError):
            self.edadeal.update_plus_status(TEST_UID, is_active=False)


@with_settings(
    EDADEAL_URL='http://localhost',
    EDADEAL_TIMEOUT=1,
    EDADEAL_RETRIES=2,
    EDADEAL_TOKEN=TEST_EDADEAL_TOKEN,
)
class TestEdadealMethods(unittest.TestCase):
    def setUp(self):
        self.fake_edadeal = FakeEdadealApi()
        self.fake_edadeal.start()
        self.fake_edadeal.set_response_value('update_plus_status', b'')
        self.edadeal = EdadealApi()

    def tearDown(self):
        self.fake_edadeal.stop()
        del self.fake_edadeal

    def test_update_plus_ok(self):
        response = self.edadeal.update_plus_status(TEST_UID, is_active=False)
        ok_(not response)
        self.fake_edadeal.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/auth/v1/plus',
            headers={
                'Authorization': 'Bearer %s' % TEST_EDADEAL_TOKEN,
                'Content-Type': 'application/json',
            },
            json_data={'yuid': TEST_UID, 'is_active': False},
        )

    def test_update_plus_error(self):
        self.fake_edadeal.set_response_value('update_plus_status', b'', status=500)
        with assert_raises(EdadealPermanentError):
            self.edadeal.update_plus_status(TEST_UID, is_active=False)
