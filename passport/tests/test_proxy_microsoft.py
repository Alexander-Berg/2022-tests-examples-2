# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from nose.tools import eq_
from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import ProviderTemporaryUnavailableProxylibError
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.test_case import TestCase
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import microsoft as microsoft_test

from . import TestProxy


class TestProxyMicrosoft(TestProxy):
    provider_code = 'ms'
    error_profile_response = '{"error":{"code":"request_token_invalid","message": "The access token isn\'t valid."}}'

    def test_profile_ok(self):
        decoded_data = '''{
           "id": "d8f534746436bd2d",
           "name": "Vasya Poupkine",
           "first_name": "Vasya",
           "last_name": "Poupkine",
           "link": "https://profile.live.com/",
           "birth_day": 28,
           "birth_month": 4,
           "birth_year": 1990,
           "gender": null,
           "emails": {
               "account": "user@foo.bar"
           },
           "locale": "ru_RU",
           "updated_time": "2015-09-21T13:17:40+0000"
        }'''

        expected_dict = {
            'username': 'user@foo.bar',
            'firstname': 'Vasya',
            'locale': 'ru_RU',
            'lastname': 'Poupkine',
            'userid': 'd8f534746436bd2d',
            'birthday': '1990-04-28',
            'avatar': {
                '180x180': u'https://apis.live.net/v5.0/d8f534746436bd2d/picture?type=medium',
                '360x360': u'https://apis.live.net/v5.0/d8f534746436bd2d/picture?type=large',
                '96x96': u'https://apis.live.net/v5.0/d8f534746436bd2d/picture?type=small',
            },
            'email': 'user@foo.bar',
            "updated": "2015-09-21T13:17:40+0000",
        }

        self._process_single_test(
            'get_profile',
            decoded_data,
            expected_dict=expected_dict,
        )

    def test_profile_error(self):
        self._tst_profile_error()

    def test_get_profile_links(self):
        links = self.proxy.get_profile_links('12345', 'some_user')
        eq_(links, [u'https://profile.live.com/cid-12345'])


class TestMicrosoft(TestCase):
    def setUp(self):
        super(TestMicrosoft, self).setUp()
        passport.backend.social.proxylib.init()
        self._proxy = microsoft_test.FakeProxy().start()

        self.provider_code = 'ms'
        self.app = Application(id=EXTERNAL_APPLICATION_ID1)
        self.access_token = {'value': APPLICATION_TOKEN1}

    def tearDown(self):
        self._proxy.stop()
        super(TestMicrosoft, self).tearDown()

    def test_refresh_token_server_error(self):
        self._proxy.set_response_value(
            'refresh_token',
            microsoft_test.MicrosoftApi.build_server_error()
        )

        with self.assertRaises(ProviderTemporaryUnavailableProxylibError):
            get_proxy(self.provider_code, self.access_token, self.app).refresh_token(APPLICATION_TOKEN1)
