# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.bot_api import (
    BotApi,
    BotApiPermanentError,
)
from passport.backend.core.builders.bot_api.faker.fake_bot_api import (
    bot_api_response,
    FakeBotApi,
)
from passport.backend.core.test.test_utils import with_settings_hosts


TEST_UID = 1
TEST_MESSAGE_ID = 123
TEST_TEXT = u'Hej!'


@with_settings_hosts(
    BOT_API_URL='http://bot-api/',
    BOT_API_TIMEOUT=1,
    BOT_API_RETRIES=2,
    BOT_API_TOKEN='test',
)
class FakeBotApiTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_bot_api = FakeBotApi()
        self.fake_bot_api.start()

    def tearDown(self):
        self.fake_bot_api.stop()
        del self.fake_bot_api

    def test_send_message_response(self):
        ok_(not self.fake_bot_api._mock.request.called)

        bot_resp = bot_api_response(121)
        self.fake_bot_api.set_response_value('send_message', bot_resp)

        bot_api = BotApi()
        result = bot_api.send_message(uid=TEST_UID, text=TEST_TEXT)
        eq_(result, json.loads(bot_resp))

        eq_(len(self.fake_bot_api.requests), 1)

    def test_send_message_side_effect(self):
        ok_(not self.fake_bot_api._mock.request.called)

        self.fake_bot_api.set_response_side_effect('send_message', BotApiPermanentError)

        bot_api = BotApi()
        with assert_raises(BotApiPermanentError):
            bot_api.send_message(uid=TEST_UID, text=TEST_TEXT)

        eq_(len(self.fake_bot_api.requests), 1)

    def test_edit_message(self):
        ok_(not self.fake_bot_api._mock.request.called)

        bot_resp = bot_api_response(121)
        self.fake_bot_api.set_response_value('edit_message', bot_resp)

        bot_api = BotApi()
        result = bot_api.edit_message(uid=TEST_UID, message_id=TEST_MESSAGE_ID, text=TEST_TEXT)
        eq_(result, json.loads(bot_resp))

        eq_(len(self.fake_bot_api.requests), 1)
