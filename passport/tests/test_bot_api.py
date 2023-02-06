# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_headers_equal
from passport.backend.core.builders.bot_api import (
    BotApi,
    BotApiAuthError,
    BotApiInvalidRequestError,
    BotApiPermanentError,
    BotApiTemporaryError,
)
from passport.backend.core.builders.bot_api.faker.fake_bot_api import (
    bot_api_response,
    FakeBotApi,
)
from passport.backend.core.test.test_utils import with_settings_hosts


TEST_UID = 1
TEST_MESSAGE_ID = 456
TEST_TEXT = 'Your link: https://pass.com/auth?track_id=1'
TEST_CARD = {'key': 'value'}
TEST_NOTIFICATION_TEXT = 'Sign in'


@with_settings_hosts(
    BOT_API_URL='http://localhost/',
    BOT_API_TIMEOUT=0.5,
    BOT_API_RETRIES=2,
    BOT_API_TOKEN='test',
)
class TestBotApiCommon(unittest.TestCase):
    def setUp(self):
        self.bot_api = BotApi()
        self.bot_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.bot_api.useragent.request.return_value = self.response
        self.bot_api.useragent.request_error_class = self.bot_api.temporary_error_class
        self.response.content = json.dumps({}).encode('utf-8')
        self.response.status_code = 200

    def tearDown(self):
        del self.bot_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = 'not a json'
        with assert_raises(BotApiPermanentError):
            self.bot_api.send_message(uid=TEST_UID, text=TEST_TEXT)

    def test_temporary_error(self):
        self.response.status_code = 500
        with assert_raises(BotApiTemporaryError):
            self.bot_api.send_message(uid=TEST_UID, text=TEST_TEXT)

    def test_bad_status_code(self):
        self.response.status_code = 418
        self.response.content = b'IAmATeapot'
        with assert_raises(BotApiPermanentError):
            self.bot_api.send_message(uid=TEST_UID, text=TEST_TEXT)

    def test_bad_auth(self):
        self.response.status_code = 401
        self.response.content = b'Bot is not authorized'
        with assert_raises(BotApiAuthError):
            self.bot_api.send_message(uid=TEST_UID, text=TEST_TEXT)

    def test_invalid_request(self):
        self.response.status_code = 400
        with assert_raises(BotApiInvalidRequestError):
            self.bot_api.send_message(uid=TEST_UID, text=TEST_TEXT)


@with_settings_hosts(
    BOT_API_URL='http://localhost/',
    BOT_API_TIMEOUT=0.5,
    BOT_API_RETRIES=2,
    BOT_API_TOKEN='test',
)
class TestBotApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_bot_api = FakeBotApi()
        self.fake_bot_api.start()

        self.bot_api = BotApi()

    def tearDown(self):
        self.fake_bot_api.stop()
        del self.fake_bot_api

    def test_send_ok(self):
        self.fake_bot_api.set_response_value('send_message', bot_api_response(message_id=TEST_MESSAGE_ID))
        resp = self.bot_api.send_message(uid=TEST_UID, text=TEST_TEXT, card=TEST_CARD, notification_text=TEST_NOTIFICATION_TEXT)
        eq_(resp, {'message': {'message_id': TEST_MESSAGE_ID}})
        self.fake_bot_api.requests[0].assert_properties_equal(
            url='http://localhost/bot/sendMessage/',
            method='POST',
            json_data={
                'user_uid': TEST_UID,
                'text': TEST_TEXT,
                'card': TEST_CARD,
                'notification': TEST_NOTIFICATION_TEXT,
            },
        )

    def test_send_auth_error(self):
        self.fake_bot_api.set_response_side_effect('send_message', BotApiAuthError)
        with assert_raises(BotApiPermanentError):
            self.bot_api.send_message(uid=TEST_UID, text=TEST_TEXT)

    def test_send_req_id(self):
        self.fake_bot_api.set_response_value('send_message', bot_api_response())
        resp = self.bot_api.send_message(uid=TEST_UID, text=TEST_TEXT, request_id=1)
        eq_(resp, {'message': {'message_id': 123}})
        assert_builder_headers_equal(
            self.fake_bot_api,
            {
                'Authorization': 'OAuth test',
                'Content-Type': 'application/json',
                'X-Request-Id': 1,
            },
        )

    def test_edit_ok(self):
        self.fake_bot_api.set_response_value('edit_message', bot_api_response())
        self.bot_api.edit_message(
            uid=TEST_UID,
            message_id=TEST_MESSAGE_ID,
            text=TEST_TEXT,
            card=TEST_CARD,
            notification_text=TEST_NOTIFICATION_TEXT,
        )
        self.fake_bot_api.requests[0].assert_properties_equal(
            url='http://localhost/bot/editMessage/',
            method='POST',
            json_data={
                'user_uid': TEST_UID,
                'message_id': TEST_MESSAGE_ID,
                'text': TEST_TEXT,
                'card': TEST_CARD,
                'notification': TEST_NOTIFICATION_TEXT,
            },
        )
