# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.octopus import (
    Octopus,
    OctopusPermanentError,
    OctopusSessionNotFound,
)
from passport.backend.core.builders.octopus.faker import (
    FakeOctopus,
    octopus_response,
    octopus_session_log_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_CALL_SESSION_ID = '123-qwe'
TEST_CODE_HALF = '123'
TEST_CALLER = '+79000010101'
TEST_CALLEE = '+79000020202'
TEST_LANGUAGE = 'ru'


@with_settings(
    OCTOPUS_URL='http://localhost/',
    OCTOPUS_TIMEOUT=1,
    OCTOPUS_RETRIES=1,
    OCTOPUS_AUTH_TOKEN='123',
    TELEPHONY_OK_STATUSES=[
        'InProgress',
    ],
)
class FakeOctopusTestCase(TestCase):
    def setUp(self):
        self.faker = FakeOctopus()
        self.faker.start()
        self.octopus = Octopus()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_create_session(self):
        self.faker.set_response_value('create_session', octopus_response(TEST_CALL_SESSION_ID))
        eq_(
            self.octopus.create_session(
                TEST_CODE_HALF,
                TEST_CODE_HALF,
                TEST_CALLER,
                TEST_CALLEE,
                TEST_LANGUAGE,
            ),
            TEST_CALL_SESSION_ID,
        )

    @raises(OctopusPermanentError)
    def test_create_session_error(self):
        self.faker.set_response_side_effect('create_session', OctopusPermanentError)
        self.octopus.create_session(
            TEST_CODE_HALF,
            TEST_CODE_HALF,
            TEST_CALLER,
            TEST_CALLEE,
            TEST_LANGUAGE,
        )

    def test_get_session_log(self):
        self.faker.set_response_value('get_session_log', octopus_session_log_response())
        eq_(
            self.octopus.get_session_log(TEST_CALL_SESSION_ID),
            json.loads(octopus_session_log_response()),
        )

    @raises(OctopusSessionNotFound)
    def test_get_session_log_error(self):
        self.faker.set_response_side_effect('get_session_log', OctopusSessionNotFound)
        self.octopus.get_session_log(TEST_CALL_SESSION_ID)

    def test_create_flash_call_session(self):
        self.faker.set_response_value('create_flash_call_session', octopus_response(TEST_CALL_SESSION_ID))
        eq_(
            self.octopus.create_flash_call_session(
                TEST_CALLER,
                TEST_CALLEE,
            ),
            TEST_CALL_SESSION_ID,
        )

    @raises(OctopusPermanentError)
    def test_create_flash_call_session_error(self):
        self.faker.set_response_side_effect('create_flash_call_session', OctopusPermanentError)
        self.octopus.create_flash_call_session(
            TEST_CALLER,
            TEST_CALLEE,
        )
