# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common import oauth2
from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import InvalidTokenProxylibError
from passport.backend.social.common.providers.Yahoo import Yahoo
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    REFRESH_TOKEN1,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.token.domain import Token
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import yahoo as yahoo_test


class BaseYahooTestCase(TestCase):
    def setUp(self):
        super(BaseYahooTestCase, self).setUp()
        self._fake_yahoo = yahoo_test.FakeProxy().start()
        passport.backend.social.proxylib.init()
        self._proxy = self.build_proxy()

    def tearDown(self):
        self._fake_yahoo.stop()
        super(BaseYahooTestCase, self).tearDown()

    def build_proxy(self, token=None):
        if token is None:
            token = Token(value=APPLICATION_TOKEN1)
        app = Application()
        return get_proxy(Yahoo.code, token.to_dict_for_proxy(), app)


class TestYahooRefreshToken(BaseYahooTestCase):
    def test_yahoo__ok(self):
        self._fake_yahoo.set_response_value(
            'refresh_token',
            yahoo_test.YahooApi.refresh_token(),
        )

        rv = self._proxy.refresh_token(APPLICATION_TOKEN1)

        self.assertEqual(
            rv,
            {
                'access_token': APPLICATION_TOKEN1,
                'expires_in': APPLICATION_TOKEN_TTL1,
                'refresh_token': REFRESH_TOKEN1,
            },
        )

    def test_yahoo__invalid_reshresh_token(self):
        self._fake_yahoo.set_response_value(
            'refresh_token',
            oauth2.test.build_error(
                error='INVALID_REFRESH_TOKEN',
                error_description='Failed to decode/encode refresh token',
            ),
        )

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            self._proxy.refresh_token(APPLICATION_TOKEN1)

        self.assertEqual(assertion.exception.message, 'Failed to decode/encode refresh token')


class TestYahooGetProfile(BaseYahooTestCase):
    def test_ok(self):
        self._fake_yahoo.set_response_value(
            'userinfo',
            yahoo_test.YahooApi.userinfo(),
        )

        rv = self._proxy.get_profile()

        self.assertEqual(
            rv,
            {
                'avatar': {
                    '0x0': 'https://s.yimg.com/ag/images/18598556-0dda-42c5-bb78-ddbb6cc833c8_192sq.jpg',
                },
                'email': 'averagejoe@yahoo.com',
                'firstname': 'Joe',
                'lastname': 'Average',
                'locale': 'ru-RU',
                'userid': 'ABCDEFGH1JKLMNOPQRSTUVWXY7',
                'username': 'Joe',
            },
        )

    def test_unverified_email(self):
        self._fake_yahoo.set_response_value(
            'userinfo',
            yahoo_test.YahooApi.userinfo(
                {
                    'email_verified': False,
                },
            ),
        )

        rv = self._proxy.get_profile()

        self.assertNotIn('email', rv)

    def test_dont_use_default_avatar(self):
        self._fake_yahoo.set_response_value(
            'userinfo',
            yahoo_test.YahooApi.userinfo(
                {
                    'picture': 'https://s.yimg.com/ag/images/default_user_profile_pic_192sq.jpg',
                },
            ),
        )

        rv = self._proxy.get_profile()

        self.assertEqual(rv['avatar'], dict())

    def test_token_invalid(self):
        self._fake_yahoo.set_response_value(
            'userinfo',
            yahoo_test.YahooApi.build_invalid_token_error(),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._proxy.get_profile()

    def test_request(self):
        self._fake_yahoo.set_response_value(
            'userinfo',
            yahoo_test.YahooApi.userinfo(),
        )

        proxy = self.build_proxy(token=Token(value=APPLICATION_TOKEN1))
        proxy.get_profile()

        self.assertEqual(
            self._fake_yahoo.requests,
            [
                dict(
                    url='https://api.login.yahoo.com/openid/v1/userinfo?format=json',
                    headers={
                        'Authorization': 'Bearer ' + APPLICATION_TOKEN1,
                    },
                    data=None,
                ),
            ],
        )
