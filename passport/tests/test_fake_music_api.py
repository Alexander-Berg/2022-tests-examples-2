# -*- coding: utf-8 -*-
import json
from unittest import TestCase

import mock
from nose.tools import eq_
from passport.backend.core.builders.music_api.faker import (
    FakeMusicApi,
    music_account_status_response,
)
from passport.backend.core.builders.music_api.music_api import MusicApi
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 123
TEST_IP = '192.168.1.1'


@with_settings(
    MUSIC_API_URL='http://localhost/',
    MUSIC_API_TIMEOUT=0.5,
    MUSIC_API_RETRIES=2,
)
class FakeMusicApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakeMusicApi()
        self.faker.start()
        self.music_api = MusicApi(tvm_credentials_manager=mock.Mock())

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.music_api

    def test_account_status(self):
        self.faker.set_response_value(
            'account_status',
            music_account_status_response(),
        )
        eq_(
            self.music_api.account_status(uid=TEST_UID, user_ticket='ticket', country_id=123, user_ip=TEST_IP),
            json.loads(music_account_status_response())['result'],
        )

    def test_account_status_with_plus_info(self):
        self.faker.set_response_value(
            'account_status',
            music_account_status_response(plus_info={'migrated': True}),
        )
        eq_(
            self.music_api.account_status(uid=TEST_UID, user_ticket='ticket', country_id=123, user_ip=TEST_IP),
            json.loads(music_account_status_response(plus_info={'migrated': True}))['result'],
        )
