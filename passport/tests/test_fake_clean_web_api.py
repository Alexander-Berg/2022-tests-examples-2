# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.clean_web_api import (
    CleanWebAPI,
    CleanWebPermanentError,
)
from passport.backend.core.builders.clean_web_api.faker.fake_clean_web_api import (
    clean_web_api_bunch_response,
    clean_web_api_response_bad_verdicts,
    clean_web_api_simple_response,
    FakeCleanWebAPI,
)
from passport.backend.core.test.test_utils import with_settings


TEST_TEXT = 'abcde'
TEST_KEY = 'KEY'


@with_settings(
    CLEAN_WEB_API_URL='http://localhost/',
    CLEAN_WEB_API_TIMEOUT=1,
    CLEAN_WEB_API_RETRIES=1,
)
class FakeCleanWebAPITestCase(TestCase):
    def setUp(self):
        self.faker = FakeCleanWebAPI()
        self.faker.start()
        self.clean_web_api = CleanWebAPI()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_ok(self):
        expected_simple = True
        expected_full = clean_web_api_simple_response(expected_simple)
        self.faker.set_response_value('', expected_full)
        eq_(
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY),
            json.loads(expected_full),
        )
        eq_(
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY, simple_response=True),
            expected_simple,
        )

    def test_bunch_ok(self):
        expected_simple = [False, None, True]
        expected_full = clean_web_api_bunch_response(expected_simple)
        self.faker.set_response_value('', expected_full)
        eq_(
            self.clean_web_api.check_text_bunch([TEST_TEXT] * 3, [TEST_KEY] * 3),
            json.loads(expected_full),
        )
        eq_(
            self.clean_web_api.check_text_bunch([TEST_TEXT] * 3, [TEST_KEY] * 3, simple_response=True),
            expected_simple,
        )

    def test_ok_bad_verdicts(self):
        expected_simple = ['full_name']
        expected_full = clean_web_api_response_bad_verdicts(expected_simple)
        self.faker.set_response_value('', expected_full)
        eq_(
            self.clean_web_api.check_user_data(TEST_KEY, first_name=TEST_TEXT, full_name=TEST_TEXT),
            json.loads(expected_full),
        )
        eq_(
            self.clean_web_api.check_user_data(TEST_KEY, first_name=TEST_TEXT, full_name=TEST_TEXT, simple_response=True),
            expected_simple,
        )

    @raises(CleanWebPermanentError)
    def test_error(self):
        self.faker.set_response_side_effect('', CleanWebPermanentError)
        self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)
