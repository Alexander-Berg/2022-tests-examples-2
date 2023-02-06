# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64

from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import InvalidTokenProxylibError
from passport.backend.social.common.providers.MosRu import MosRu
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.test_case import TestCase
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import mos_ru as mos_ru_test


class MosRuTestCase(TestCase):
    def setUp(self):
        super(MosRuTestCase, self).setUp()
        self._proxy = mos_ru_test.FakeProxy().start()
        passport.backend.social.proxylib.init()

        self._p = get_proxy(
            MosRu.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                id=EXTERNAL_APPLICATION_ID1,
                secret=APPLICATION_SECRET1,
            ),
        )

    def tearDown(self):
        self._proxy.stop()
        super(MosRuTestCase, self).tearDown()

    def build_settings(self):
        settings = super(MosRuTestCase, self).build_settings()
        settings['social_config'].update(
            dict(
                mos_ru_get_profile_url='https://oauth20.mos.ru/auth/authenticationWS/getUserData',
                mos_ru_refresh_token_url='https://oauth20.mos.ru/sps/oauth/oauth20/token',
            ),
        )
        return settings


class TestGetProfile(MosRuTestCase):
    def test_person(self):
        self._proxy.set_response_value(
            'get_user_data',
            mos_ru_test.MosRuApi.get_user_data_for_person(),
        )

        rv = self._p.get_profile()

        self.assertEqual(
            rv,
            {
                'userid': '9843497619896145379',
                'firstname': 'Иван',
                'lastname': 'Иванов',
            },
        )

        self.assertEqual(
            self._proxy.requests,
            [
                {
                    'url': u'https://oauth20.mos.ru/auth/authenticationWS/getUserData',
                    'data': None,
                    'headers': {u'Authorization': u'Bearer %s' % APPLICATION_TOKEN1},
                },
            ],
        )

    def test_invalid_token(self):
        self._proxy.set_response_value(
            'get_user_data',
            mos_ru_test.MosRuApi.build_error(401),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._p.get_profile()


class TestRefreshToken(MosRuTestCase):
    def test_token_valid(self):
        self._proxy.set_response_value(
            'refresh_token',
            mos_ru_test.MosRuApi.refresh_token(),
        )

        rv = self._p.refresh_token(APPLICATION_TOKEN1)

        self.assertEqual(
            rv,
            {
                'access_token': APPLICATION_TOKEN1,
                'expires_in': APPLICATION_TOKEN_TTL1,
                'refresh_token': APPLICATION_TOKEN1,
            },
        )

        auth_basic = 'Basic %s' % base64.b64encode('%s:%s' % (
            EXTERNAL_APPLICATION_ID1,
            APPLICATION_SECRET1,
        ))

        self.assertEqual(
            self._proxy.requests,
            [
                {
                    'url': 'https://oauth20.mos.ru/sps/oauth/oauth20/token',
                    'data': {'grant_type': 'refresh_token', 'refresh_token': APPLICATION_TOKEN1},
                    'headers': {'Authorization': auth_basic},
                },
            ],
        )

    def test_token_invalid(self):
        self._proxy.set_response_value(
            'refresh_token',
            mos_ru_test.MosRuApi.build_invalid_token_error(),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._p.refresh_token(APPLICATION_TOKEN1)
