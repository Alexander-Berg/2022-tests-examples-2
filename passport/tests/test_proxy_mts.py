# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from functools import partial

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.social.common import oauth2
from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import (
    BadParametersProxylibError,
    InvalidTokenProxylibError,
    UnexpectedResponseProxylibError,
)
from passport.backend.social.common.providers.Mts import Mts
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN3,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    UNIXTIME1,
)
from passport.backend.social.common.test.test_case import TestCase
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import mts as mts_test


class BaseMtsV2TestCase(TestCase):
    def setUp(self):
        super(BaseMtsV2TestCase, self).setUp()
        passport.backend.social.proxylib.init()
        self._proxy = mts_test.FakeProxy().start()
        self.get_proxy = partial(
            get_proxy,
            Mts.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                id=EXTERNAL_APPLICATION_ID1,
                secret=APPLICATION_SECRET1,
                request_from_intranet_allowed=True,
            ),
        )

    def tearDown(self):
        self._proxy.stop()
        super(BaseMtsV2TestCase, self).tearDown()


class TestMtsV2GetProfile(BaseMtsV2TestCase):
    def test_ok(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV2.get_profile(),
        )

        rv = self.get_proxy().get_profile()

        self.assertEqual(
            rv,
            {
                'phone': '+79123456789',
                'userid': '9123456789:123456789000',
            },
        )


class TestMtsV2GetTokenInfo(BaseMtsV2TestCase):
    def test_ok(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV2.get_profile({'exp': str(UNIXTIME1)}),
        )

        rv = self.get_proxy().get_token_info()

        eq_(
            rv,
            {
                'scopes': [
                    'sub',
                    'mobile:phone',
                    'mobile:account',
                    'sso',
                ],
                'client_id': EXTERNAL_APPLICATION_ID1,
                'expires': UNIXTIME1,
            },
        )

    @raises(BadParametersProxylibError)
    def test_other_app(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV2.get_profile({
                'aud': EXTERNAL_APPLICATION_ID2,
            }),
        )

        self.get_proxy().get_token_info()


class TestMtsV2RefreshToken(BaseMtsV2TestCase):
    def test_ok(self):
        self._proxy.set_response_value(
            'refresh_token',
            mts_test.MtsApiV2.refresh_token(
                access_token=APPLICATION_TOKEN1,
                expires_in=APPLICATION_TOKEN_TTL1,
                refresh_token=APPLICATION_TOKEN2,
            ),
        )

        rv = self.get_proxy().refresh_token(APPLICATION_TOKEN3)

        self.assertEqual(
            rv,
            {
                'access_token': APPLICATION_TOKEN1,
                'expires_in': APPLICATION_TOKEN_TTL1,
                'refresh_token': APPLICATION_TOKEN2,
            },
        )

        self.assertEqual(
            self._proxy.requests,
            [
                dict(
                    url='https://login.mts.ru/amserver/oauth2/token',
                    headers=None,
                    data={
                        'client_id': EXTERNAL_APPLICATION_ID1,
                        'client_secret': APPLICATION_SECRET1,
                        'grant_type': 'refresh_token',
                        'refresh_token': APPLICATION_TOKEN3,
                    },
                ),
            ],
        )

    def test_invalid_refresh_token(self):
        self._proxy.set_response_value(
            'refresh_token',
            oauth2.test.build_error('invalid_grant'),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self.get_proxy().refresh_token(APPLICATION_TOKEN3)


class BaseMtsV3TestCase(TestCase):
    def setUp(self):
        super(BaseMtsV3TestCase, self).setUp()
        passport.backend.social.proxylib.init()
        self._proxy = mts_test.FakeProxy().start()
        self.get_proxy = partial(
            get_proxy,
            Mts.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                engine_id='mts_v3',
                id=EXTERNAL_APPLICATION_ID1,
                request_from_intranet_allowed=True,
                secret=APPLICATION_SECRET1,
            ),
        )

    def tearDown(self):
        self._proxy.stop()
        super(BaseMtsV3TestCase, self).tearDown()


class TestMtsV3GetProfile(BaseMtsV3TestCase):
    def test_ok(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV3.get_profile(),
        )

        rv = self.get_proxy().get_profile()

        self.assertEqual(
            rv,
            {
                'birthday': '1986-01-01',
                'firstname': 'Иван',
                'lastname': 'Иванов',
                'phone': '+79123456789',
                'userid': '9123456789:123456789000',
            },
        )

    def test_organization(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV3.get_profile(
                user=dict(
                    is_organization='Organization',
                    organization='ООО «МТС ИТ»',
                ),
                exclude_attrs=['given_name'],
            ),
        )

        rv = self.get_proxy().get_profile()

        self.assertEqual(
            rv,
            {
                'birthday': '1986-01-01',
                'firstname': 'ООО «МТС ИТ»',
                'phone': '+79123456789',
                'userid': '9123456789:123456789000',
            },
        )

    def test_organization_with_leader(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV3.get_profile(
                user=dict(
                    is_organization='Organization',
                    organization='ООО «МТС ИТ»',
                ),
            ),
        )

        rv = self.get_proxy().get_profile()

        self.assertEqual(
            rv,
            {
                'birthday': '1986-01-01',
                'firstname': 'Иван',
                'lastname': 'Иванов',
                'phone': '+79123456789',
                'userid': '9123456789:123456789000',
            },
        )

    def test_invalid_phone_number(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV3.get_profile({'phone': '12345'}),
        )

        with self.assertRaises(UnexpectedResponseProxylibError):
            self.get_proxy().get_profile()

    def test_invalid_token(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV3.build_invalid_token_error(),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self.get_proxy().get_profile()

    def test_no_account_number(self):
        self._proxy.set_response_value(
            'get_profile',
            mts_test.MtsApiV3.get_profile(exclude_attrs=['account:number']),
        )

        rv = self.get_proxy().get_profile()

        self.assertEqual(
            rv,
            {
                'birthday': '1986-01-01',
                'firstname': 'Иван',
                'lastname': 'Иванов',
                'phone': '+79123456789',
                'userid': '9123456789:OTEyMzQ1Njc4OQ==',
            },
        )


class TestMtsV3RefreshToken(BaseMtsV3TestCase):
    def test_ok(self):
        self._proxy.set_response_value(
            'refresh_token',
            mts_test.MtsApiV3.refresh_token(
                access_token=APPLICATION_TOKEN1,
                expires_in=APPLICATION_TOKEN_TTL1,
            ),
        )

        rv = self.get_proxy().refresh_token(APPLICATION_TOKEN2)

        self.assertEqual(
            rv,
            {
                'access_token': APPLICATION_TOKEN1,
                'expires_in': APPLICATION_TOKEN_TTL1,
            },
        )

        self.assertEqual(
            self._proxy.requests,
            [
                dict(
                    url='https://login.mts.ru/amserver/oauth2/realms/root/realms/users/access_token',
                    headers=None,
                    data={
                        'client_id': EXTERNAL_APPLICATION_ID1,
                        'client_secret': APPLICATION_SECRET1,
                        'grant_type': 'refresh_token',
                        'refresh_token': APPLICATION_TOKEN2,
                    },
                ),
            ],
        )

    def test_invalid_refresh_token(self):
        self._proxy.set_response_value(
            'refresh_token',
            oauth2.test.build_error('invalid_grant'),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self.get_proxy().refresh_token(APPLICATION_TOKEN2)
