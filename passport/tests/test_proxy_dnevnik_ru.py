# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64

from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import InvalidTokenProxylibError
from passport.backend.social.common.providers.DnevnikRu import DnevnikRu
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.test_case import TestCase
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import dnevnik_ru as dnevnik_ru_test


TEST_REFRESH_TOKEN_URL = u'https://api.dnevnik.ru/v2.0/authorizations'
TEST_GET_PROFILE_URL = u'https://api.dnevnik.ru/v2.0/users/me'


class DnevnikRuTestCase(TestCase):
    def setUp(self):
        super(DnevnikRuTestCase, self).setUp()
        self._proxy = dnevnik_ru_test.FakeProxy().start()
        passport.backend.social.proxylib.init()

        self._p = get_proxy(
            DnevnikRu.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                id=EXTERNAL_APPLICATION_ID1,
                secret=APPLICATION_SECRET1,
            ),
        )

    def tearDown(self):
        self._proxy.stop()
        super(DnevnikRuTestCase, self).tearDown()

    def build_settings(self):
        settings = super(DnevnikRuTestCase, self).build_settings()
        settings['social_config'].update(
            dict(
                dnevnik_ru_get_profile_url=TEST_GET_PROFILE_URL,
                dnevnik_ru_refresh_token_url=TEST_REFRESH_TOKEN_URL,
            ),
        )
        return settings


class TestGetProfile(DnevnikRuTestCase):
    def test_person(self):
        self._proxy.set_response_value(
            'get_user_data',
            dnevnik_ru_test.DnevnikRuApi.get_user_data_for_person(),
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
                    'url': TEST_GET_PROFILE_URL,
                    'data': None,
                    'headers': {
                        u'Access-Token': APPLICATION_TOKEN1,
                        u'Authorization': u'Bearer %s' % APPLICATION_TOKEN1,
                    },
                },
            ],
        )

    def test_person__no_first_last_name__shortname_fallback(self):
        self._proxy.set_response_value(
            'get_user_data',
            dnevnik_ru_test.DnevnikRuApi.get_user_data_for_person(
                exclude_attrs=['firstName', 'lastName'],
            ),
        )

        rv = self._p.get_profile()

        self.assertEqual(
            rv,
            {
                'userid': '9843497619896145379',
                'firstname': 'ИваИва',
            },
        )

    def test_person__got_only_last_name__no_shortname_fallback(self):
        self._proxy.set_response_value(
            'get_user_data',
            dnevnik_ru_test.DnevnikRuApi.get_user_data_for_person(
                exclude_attrs=['firstName'],
            ),
        )

        rv = self._p.get_profile()

        self.assertEqual(
            rv,
            {
                'userid': '9843497619896145379',
                'lastname': 'Иванов',
            },
        )

    def test_invalid_token(self):
        self._proxy.set_response_value(
            'get_user_data',
            dnevnik_ru_test.DnevnikRuApi.build_error(401),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._p.get_profile()


class TestRefreshToken(DnevnikRuTestCase):
    def test_token_valid(self):
        self._proxy.set_response_value(
            'refresh_token',
            dnevnik_ru_test.DnevnikRuApi.refresh_token(),
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
                    'url': TEST_REFRESH_TOKEN_URL,
                    'data': {'grant_type': 'RefreshToken', 'RefreshToken': APPLICATION_TOKEN1},
                    'headers': {'Authorization': auth_basic},
                },
            ],
        )

    def test_token_invalid(self):
        self._proxy.set_response_value(
            'refresh_token',
            dnevnik_ru_test.DnevnikRuApi.build_invalid_token_error(),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._p.refresh_token(APPLICATION_TOKEN1)
