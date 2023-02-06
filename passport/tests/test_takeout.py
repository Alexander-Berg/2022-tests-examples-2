# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.takeout import Takeout
from passport.backend.core.builders.takeout.exceptions import (
    TakeoutPermanentError,
    TakeoutTemporaryError,
)
from passport.backend.core.builders.takeout.faker import (
    FakeTakeout,
    takeout_ok_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)


TEST_UID = 1
TEST_UNIXTIME = 100000


@with_settings(
    TAKEOUT_URL='http://localhost/',
    TAKEOUT_CONSUMER='takeout',
    TAKEOUT_RETRIES=2,
    TAKEOUT_TIMEOUT=1,
)
class TestTakeoutCommon(unittest.TestCase):
    def setUp(self):
        self.takeout = Takeout(use_tvm=False)
        self.takeout.useragent = mock.Mock()

        self.response = mock.Mock()
        self.takeout.useragent.request.return_value = self.response
        self.takeout.useragent.request_error_class = self.takeout.temporary_error_class
        self.response.content = json.dumps(takeout_ok_response())
        self.response.status_code = 200

    def tearDown(self):
        del self.takeout
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 400
        self.response.content = b'not a json'
        with assert_raises(TakeoutPermanentError):
            self.takeout.prepare_archive(TEST_UID, TEST_UNIXTIME)

    def test_server_temporary_error(self):
        self.response.status_code = 503
        self.response.content = b'"server temporarily unavailable"'
        with assert_raises(TakeoutTemporaryError):
            self.takeout.prepare_archive(TEST_UID, TEST_UNIXTIME)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'"server is down"'
        with assert_raises(TakeoutPermanentError):
            self.takeout.prepare_archive(TEST_UID, TEST_UNIXTIME)


@with_settings(
    TAKEOUT_URL='http://localhost/',
    TAKEOUT_CONSUMER='takeout',
    TAKEOUT_RETRIES=2,
    TAKEOUT_TIMEOUT=1,
)
class TestTakeoutMethods(unittest.TestCase):
    def setUp(self):
        self.tvm_credentials_manager = FakeTvmCredentialsManager()
        self.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'takeout',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self.tvm_credentials_manager.start()

        self.fake_takeout = FakeTakeout()
        self.fake_takeout.start()
        self.fake_takeout.set_response_value_without_method(
            json.dumps(takeout_ok_response()).encode('utf8'),
        )

        self.takeout = Takeout()

    def tearDown(self):
        self.fake_takeout.stop()
        self.tvm_credentials_manager.stop()
        del self.fake_takeout
        del self.tvm_credentials_manager

    def test_prepare_archive(self):
        response = self.takeout.prepare_archive(TEST_UID, TEST_UNIXTIME)

        eq_(response, takeout_ok_response())
        self.fake_takeout.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/1/prepare_archive/?consumer=takeout',
            post_args={
                'uid': TEST_UID,
                'unixtime': TEST_UNIXTIME,
            },
        )
