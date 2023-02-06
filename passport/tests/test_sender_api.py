# -*- coding: utf-8 -*-
import json
import unittest

from nose_parameterized import parameterized
from passport.backend.core.builders.sender_api.exceptions import (
    SenderApiInvalidRequestError,
    SenderApiTemporaryError,
)
from passport.backend.core.builders.sender_api.faker.sender_api import (
    FakeSenderApi,
    sender_api_reply_error,
    sender_api_reply_ok,
)
from passport.backend.core.builders.sender_api.sender_api import SenderApi
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_ALIAS,
    TEST_TICKET,
)
from passport.backend.utils.string import (
    smart_bytes,
    smart_text,
)


TEST_EMAIL1 = 'test@test.com'
TEST_EMAIL2 = 'test2@test.com'
TEST_LIST_ID1 = 123
TEST_LIST_ID2 = 124
TEST_LIST_ID3 = 124


@with_settings(
    SENDER_API_URL='http://test_api',
    SENDER_API_RETRIES=2,
    SENDER_API_UNSUBSCRIBE_EXT_ACCOUNT='passport-ext',
    SENDER_API_TIMEOUT=1,
)
class TestSenderApi(unittest.TestCase):
    def setUp(self):
        self.fake_sender_api = FakeSenderApi()
        self.fake_sender_api.start()
        self.fake_tvm_manager = FakeTvmCredentialsManager()
        self.fake_tvm_manager.set_data(fake_tvm_credentials_data())
        self.fake_tvm_manager.start()
        self.sender_api = SenderApi(tvm_dst_alias=TEST_ALIAS)

    def tearDown(self):
        self.fake_sender_api.stop()
        self.fake_tvm_manager.stop()

    def _error_reply(self, is_json):
        if is_json:
            return json.dumps(sender_api_reply_error(email=TEST_EMAIL1))
        else:
            return smart_bytes(u'какая-то ошибка')

    def assert_request_params(self, method='POST', query=None, post_data=None):
        assert method == 'POST' or post_data is None
        self.assertEqual(len(self.fake_sender_api.requests), 1)
        req = self.fake_sender_api.requests[0]
        req.assert_properties_equal(method=method)
        req.assert_headers_contain({'X-Ya-Service-Ticket': TEST_TICKET})
        if query is not None:
            req.assert_query_equals(query)
        if post_data is not None:
            req.assert_post_data_equals(post_data)

    def test_set_unsubscriptions__unsubscribe_list__ok(self):
        reply_ok = sender_api_reply_ok(email=TEST_EMAIL1)
        self.fake_sender_api.set_response_value('set_unsubscriptions', json.dumps(reply_ok))
        res = self.sender_api.set_unsubscriptions(TEST_EMAIL1, [TEST_LIST_ID1, TEST_LIST_ID2], [])
        self.assertEqual(res, reply_ok)
        self.assert_request_params(
            query={'email': TEST_EMAIL1},
            post_data=dict(
                state=json.dumps([
                    {'list_id': TEST_LIST_ID1, 'unsubscribed': True},
                    {'list_id': TEST_LIST_ID2, 'unsubscribed': True},
                ]),
            ),
        )

    def test_set_unsubscriptions__subscribe_list__ok(self):
        reply_ok = sender_api_reply_ok(email=TEST_EMAIL1)
        self.fake_sender_api.set_response_value('set_unsubscriptions', json.dumps(reply_ok))
        res = self.sender_api.set_unsubscriptions(TEST_EMAIL1, [], [TEST_LIST_ID1, TEST_LIST_ID2])
        self.assertEqual(res, reply_ok)
        self.assert_request_params(
            query={'email': TEST_EMAIL1},
            post_data=dict(
                state=json.dumps([
                    {'list_id': TEST_LIST_ID1, 'unsubscribed': False},
                    {'list_id': TEST_LIST_ID2, 'unsubscribed': False},
                ]),
            ),
        )

    def test_set_unsubscriptions__both_lists__ok(self):
        reply_ok = sender_api_reply_ok(email=TEST_EMAIL1)
        self.fake_sender_api.set_response_value('set_unsubscriptions', json.dumps(reply_ok))
        res = self.sender_api.set_unsubscriptions(TEST_EMAIL1, [TEST_LIST_ID1, TEST_LIST_ID2], [TEST_LIST_ID3])
        self.assertEqual(res, reply_ok)
        self.assert_request_params(
            query={'email': TEST_EMAIL1},
            post_data=dict(
                state=json.dumps([
                    {'list_id': TEST_LIST_ID1, 'unsubscribed': True},
                    {'list_id': TEST_LIST_ID2, 'unsubscribed': True},
                    {'list_id': TEST_LIST_ID3, 'unsubscribed': False},
                ]),
            ),
        )

    @parameterized.expand([(True,), (False,)])
    def test_set_unsubscriptions__400__exception(self, json_reply):
        reply = self._error_reply(json_reply)
        self.fake_sender_api.set_response_value('set_unsubscriptions', reply, status=400)
        with self.assertRaises(SenderApiInvalidRequestError) as e:
            self.sender_api.set_unsubscriptions(TEST_EMAIL1, [TEST_LIST_ID1], [])
        self.assertRegexpMatches(smart_text(e.exception), u'code=400.+какая-то ошибка')

    @parameterized.expand([(True,), (False,)])
    def test_set_unsubscriptions__500__exception(self, json_reply):
        reply = self._error_reply(json_reply)
        self.fake_sender_api.set_response_value('set_unsubscriptions', reply, status=500)
        with self.assertRaises(SenderApiTemporaryError) as e:
            self.sender_api.set_unsubscriptions(TEST_EMAIL1, [TEST_LIST_ID1], [])
        self.assertRegexpMatches(smart_text(e.exception), u'code=500.+какая-то ошибка')

    def test_copy_unsubscriptions__ok(self):
        reply_ok = sender_api_reply_ok(src=TEST_EMAIL1, dst=TEST_EMAIL2)
        self.fake_sender_api.set_response_value('copy_unsubscriptions', json.dumps(reply_ok))
        res = self.sender_api.copy_unsubscriptions(TEST_EMAIL1, TEST_EMAIL2)
        self.assertEqual(res, reply_ok)
        self.assert_request_params(query={'src': TEST_EMAIL1, 'dst': TEST_EMAIL2})

    @parameterized.expand([(True,), (False,)])
    def test_copy_unsubscriptions__400__exception(self, json_reply):
        reply = self._error_reply(json_reply)
        self.fake_sender_api.set_response_value('set_unsubscriptions', reply, status=400)
        with self.assertRaises(SenderApiInvalidRequestError) as e:
            self.sender_api.set_unsubscriptions(TEST_EMAIL1, [TEST_LIST_ID1], [])
        self.assertRegexpMatches(smart_text(e.exception), u'code=400.+какая-то ошибка')

    @parameterized.expand([(True,), (False,)])
    def test_copy_unsubscriptions__500__exception(self, json_reply):
        reply = self._error_reply(json_reply)
        self.fake_sender_api.set_response_value('set_unsubscriptions', reply, status=500)
        with self.assertRaises(SenderApiTemporaryError) as e:
            self.sender_api.set_unsubscriptions(TEST_EMAIL1, [TEST_LIST_ID1], [])
        self.assertRegexpMatches(smart_text(e.exception), u'code=500.+какая-то ошибка')
