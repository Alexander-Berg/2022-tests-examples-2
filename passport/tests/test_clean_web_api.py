# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.clean_web_api import (
    CleanWebAPI,
    CleanWebInvalidResponse,
    CleanWebPermanentError,
    CleanWebTemporaryError,
)
from passport.backend.core.builders.clean_web_api.faker.fake_clean_web_api import (
    clean_web_api_bunch_response,
    clean_web_api_response,
    clean_web_api_response_bad_verdicts,
    clean_web_api_simple_response,
    FakeCleanWebAPI,
)
from passport.backend.core.test.test_utils import with_settings


TEST_TEXT = 'abcde'
TEST_TEXT2 = '123456'
TEST_TEXT3 = 'XYZ'
TEST_RESULT = [{
    'name': 'text_auto_yandex_mentioned',
    'subsource': 'tmu',
    'value': True,
    'entity': 'text',
    'source': 'clean-web',
    'key': 'None',
}]
TEST_KEY = 'KEY'
TEST_KEY2 = 'KEY2'
TEST_VERDICT_DATA = 'ABCDEFG'
TEST_UID = '12345'


@with_settings(
    CLEAN_WEB_API_URL='http://localhost/',
    CLEAN_WEB_API_TIMEOUT=1,
    CLEAN_WEB_API_RETRIES=2,
)
class TestCleanWebAPICommon(unittest.TestCase):
    def setUp(self):
        self.clean_web_api = CleanWebAPI()
        self.clean_web_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.clean_web_api.useragent.request.return_value = self.response
        self.clean_web_api.useragent.request_error_class = self.clean_web_api.temporary_error_class
        self.response.content = clean_web_api_response()
        self.response.status_code = 200

    def tearDown(self):
        del self.clean_web_api
        del self.response

    def test_ok(self):
        eq_(
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY),
            json.loads(clean_web_api_response()),
        )

    def test_bad_request(self):
        self.response.status_code = 400
        self.response.content = b'Invalid code'
        with assert_raises(CleanWebPermanentError):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)

    def test_unusual_status(self):
        self.response.status_code = 418
        with assert_raises(CleanWebPermanentError):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)

    def test_temporary(self):
        self.response.status_code = 503
        with assert_raises(CleanWebTemporaryError):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)


@with_settings(
    CLEAN_WEB_API_URL='http://localhost/',
    CLEAN_WEB_API_TIMEOUT=1,
    CLEAN_WEB_API_RETRIES=2,
)
class TestCleanWebAPIMethods(unittest.TestCase):
    def setUp(self):
        self.fake_clean_web_api = FakeCleanWebAPI()
        self.fake_clean_web_api.start()
        self.fake_clean_web_api.set_response_value('', clean_web_api_response(TEST_RESULT))
        self.clean_web_api = CleanWebAPI()

    def tearDown(self):
        self.fake_clean_web_api.stop()
        del self.fake_clean_web_api

    def test_check_text_ok(self):
        response = self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)
        eq_(response, json.loads(clean_web_api_response(TEST_RESULT)))
        self.fake_clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=dict(
                jsonrpc='2.0',
                method='process',
                id=1234,
                params={
                    'type': 'text',
                    'service': 'passport',
                    'key': TEST_KEY,
                    'body': {
                        'auto_only': True,
                        'text': TEST_TEXT,
                    },
                },
            ),
        )

    def test_check_text_bunch_ok(self):
        expected_response = clean_web_api_bunch_response([False, True])
        self.fake_clean_web_api.set_response_value('', expected_response)
        response = self.clean_web_api.check_text_bunch([TEST_TEXT, TEST_TEXT2], [TEST_KEY, TEST_KEY2])
        eq_(response, json.loads(expected_response))
        self.fake_clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=[
                dict(
                    jsonrpc='2.0',
                    method='process',
                    id=1234,
                    params={
                        'type': 'text',
                        'service': 'passport',
                        'key': key,
                        'body': {
                            'auto_only': True,
                            'text': text,
                        },
                    },
                ) for key, text in zip([TEST_KEY, TEST_KEY2], [TEST_TEXT, TEST_TEXT2])
            ]
        )

    def test_check_media_ok(self):
        response = self.clean_web_api.check_media(TEST_TEXT, TEST_KEY)
        eq_(response, json.loads(clean_web_api_response(TEST_RESULT)))
        self.fake_clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=dict(
                jsonrpc='2.0',
                method='process',
                id=1234,
                params={
                    'type': 'image',
                    'service': 'passport',
                    'key': TEST_KEY,
                    'body': {
                        'auto_only': True,
                        'image_url': TEST_TEXT,
                    },
                },
            ),
        )

    def test_check_media_bunch_ok(self):
        expected_response = clean_web_api_bunch_response([False, True])
        self.fake_clean_web_api.set_response_value('', expected_response)
        response = self.clean_web_api.check_media_bunch([TEST_TEXT, TEST_TEXT2], [TEST_KEY, TEST_KEY2])
        eq_(response, json.loads(expected_response))
        self.fake_clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=[
                dict(
                    jsonrpc='2.0',
                    method='process',
                    id=1234,
                    params={
                        'type': 'image',
                        'service': 'passport',
                        'key': key,
                        'body': {
                            'auto_only': True,
                            'image_url': url,
                        },
                    },
                ) for key, url in zip([TEST_KEY, TEST_KEY2], [TEST_TEXT, TEST_TEXT2])
            ],
        )

    def test_check_text_ok_with_auto_only_False(self):
        response = self.clean_web_api.check_text(TEST_TEXT, TEST_KEY, auto_only=False)
        eq_(response, json.loads(clean_web_api_response(TEST_RESULT)))
        self.fake_clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=dict(
                jsonrpc='2.0',
                method='process',
                id=1234,
                params={
                    'type': 'text',
                    'service': 'passport',
                    'key': TEST_KEY,
                    'body': {
                        'auto_only': False,
                        'text': TEST_TEXT,
                    },
                },
            ),
        )

    def test_check_text_ok_with_verdict_data(self):
        response = self.clean_web_api.check_text(TEST_TEXT, TEST_KEY, verdict_data=TEST_VERDICT_DATA)
        eq_(response, json.loads(clean_web_api_response(TEST_RESULT)))
        self.fake_clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=dict(
                jsonrpc='2.0',
                method='process',
                id=1234,
                params={
                    'type': 'text',
                    'service': 'passport',
                    'key': TEST_KEY,
                    'body': {
                        'auto_only': True,
                        'text': TEST_TEXT,
                        'verdict_data': TEST_VERDICT_DATA,
                    },
                },
            ),
        )

    def test_check_text_ok_with_puid(self):
        response = self.clean_web_api.check_text(TEST_TEXT, TEST_KEY, uid=TEST_UID)
        eq_(response, json.loads(clean_web_api_response(TEST_RESULT)))
        self.fake_clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=dict(
                jsonrpc='2.0',
                method='process',
                id=1234,
                params={
                    'type': 'text',
                    'service': 'passport',
                    'key': TEST_KEY,
                    'body': {
                        'auto_only': True,
                        'text': TEST_TEXT,
                    },
                    'puid': TEST_UID,
                },
            ),
        )

    def test_invalid_response_not_json(self):
        self.fake_clean_web_api.set_response_value('', b'not a json')
        with assert_raises(CleanWebPermanentError):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)

    def test_invalid_response_malformed_result(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_response(TEST_TEXT))
        with assert_raises(CleanWebInvalidResponse):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)

    def test_invalid_response_malformed_result_no_value(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_response([{}]))
        with assert_raises(CleanWebInvalidResponse):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)

    def test_invalid_response_malformed_result_wrong_value_type(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_response([{'value': ''}]))
        with assert_raises(CleanWebInvalidResponse):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)

    def test_invalid_response_no_result(self):
        self.fake_clean_web_api.set_response_value('', b'{}')
        with assert_raises(CleanWebInvalidResponse):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)

    def test_temporary(self):
        self.fake_clean_web_api.set_response_side_effect('', CleanWebTemporaryError())
        with assert_raises(CleanWebTemporaryError):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)
        eq_(len(self.fake_clean_web_api.requests), 2)

    def test_check_text_simple_response(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_simple_response(True))
        eq_(self.clean_web_api.check_text(TEST_TEXT, TEST_KEY, True), True)
        self.fake_clean_web_api.set_response_value('', clean_web_api_simple_response(False))
        eq_(self.clean_web_api.check_text(TEST_TEXT, TEST_KEY, True), False)

    def test_check_text_bunch_simple_response(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_bunch_response([False, True]))
        eq_(self.clean_web_api.check_text_bunch([TEST_TEXT, TEST_TEXT2], [TEST_KEY, TEST_KEY2], True), [False, True])

    def test_invalid_response_bunch_result_for_single_request(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_bunch_response([]))
        with assert_raises(CleanWebInvalidResponse):
            self.clean_web_api.check_text(TEST_TEXT, TEST_KEY)

    def test_invalid_response_single_result_for_bunch_request(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_response())
        with assert_raises(CleanWebInvalidResponse):
            self.clean_web_api.check_text_bunch([TEST_TEXT], [TEST_KEY])

    def test_invalid_response_wrong_number_of_results_in_bunch_request(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_bunch_response([]))
        with assert_raises(CleanWebInvalidResponse):
            self.clean_web_api.check_text_bunch([TEST_TEXT], [TEST_KEY])

    def test_check_media_bunch_simple_response(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_bunch_response([True, False, None]))
        eq_(
            self.clean_web_api.check_text_bunch([TEST_TEXT] * 3, [TEST_KEY] * 3, True),
            [
                True,
                False,
                None,
            ],
        )

    @parameterized.expand(
        [
            ('any_unknown_tripped_check', True),
            ('text_passport_toloka_yandex', False)
        ]
    )
    def test_check_reject_only_blacklisted_causes(self, reject_cause, expected_response):
        self.fake_clean_web_api.set_response_value('', clean_web_api_response([{'value': True, 'name': reject_cause, 'entity': 'text'}]))
        response = self.clean_web_api.check_text(TEST_TEXT, TEST_KEY, simple_response=True)
        eq_(response, expected_response)

    def test_check_allow_emergency_cause(self):
        self.fake_clean_web_api.set_response_value(
            '',
            clean_web_api_response([
                {'value': True, 'name': "text_auto_spam", 'entity': 'full_name'},
                {'value': True, 'name': "emergency_text_auto_good", 'entity': 'full_name'},  # обеляет вердикт выше
                {'value': True, 'name': "text_auto_spam", 'entity': 'first_name'},
            ]),
        )
        response = self.clean_web_api.check_user_data(TEST_TEXT, first_name=TEST_TEXT, full_name=TEST_TEXT2, simple_response=True)
        eq_(response, ['first_name'])

    def test_check_deny_allowed_emergency_cause(self):
        self.fake_clean_web_api.set_response_value(
            '',
            clean_web_api_response([
                {'value': True, 'name': "text_auto_spam", 'entity': 'full_name'},
                {'value': True, 'name': "emergency_text_auto_good", 'entity': 'full_name'},  # обеляет вердикт выше
                {'value': True, 'name': "emergency_text_auto_delete", 'entity': 'full_name'},  # очерняет обеляющий вердикт выше
                {'value': True, 'name': "text_auto_spam", 'entity': 'first_name'},
            ]),
        )
        response = self.clean_web_api.check_user_data(TEST_TEXT, first_name=TEST_TEXT, full_name=TEST_TEXT2, simple_response=True)
        eq_(response, ['first_name'])

    def test_check_user_data_simple_response_ok(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_simple_response(True))
        response = self.clean_web_api.check_user_data(TEST_KEY, first_name=TEST_TEXT, display_name=TEST_TEXT2, simple_response=True)
        eq_(response, True)

    def test_check_user_data_simple_response(self):
        self.fake_clean_web_api.set_response_value('', clean_web_api_response_bad_verdicts(['first_name']))
        response = self.clean_web_api.check_user_data(TEST_KEY, first_name=TEST_TEXT, display_name=TEST_TEXT2, public_id=TEST_TEXT3, simple_response=True)
        eq_(response, ['first_name'])
        self.fake_clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=dict(
                jsonrpc='2.0',
                method='process',
                id=1234,
                params={
                    'type': 'user_data',
                    'service': 'passport',
                    'key': TEST_KEY,
                    'body': {
                        'auto_only': True,
                        'first_name': TEST_TEXT,
                        'display_name': TEST_TEXT2,
                        'public_id': TEST_TEXT3,
                    },
                },
            ),
        )
