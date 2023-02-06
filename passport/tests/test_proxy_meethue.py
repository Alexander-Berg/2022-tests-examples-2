# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import (
    InvalidTokenProxylibError,
    UnexpectedResponseProxylibError,
)
from passport.backend.social.common.providers.Meethue import Meethue
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.test_case import TestCase
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import meethue as meethue_test


class MeethueTestCase(TestCase):
    def setUp(self):
        super(MeethueTestCase, self).setUp()
        self._proxy = meethue_test.FakeProxy().start()
        passport.backend.social.proxylib.init()

        self._p = get_proxy(
            Meethue.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                id=EXTERNAL_APPLICATION_ID1,
                secret=APPLICATION_SECRET1,
            ),
        )

    def tearDown(self):
        self._proxy.stop()
        super(MeethueTestCase, self).tearDown()


class TestRefreshToken(MeethueTestCase):
    def test_token_valid(self):
        self._proxy.set_response_value(
            'refresh_token',
            meethue_test.MeethueApi.refresh_token(),
        )

        rv = self._p.refresh_token(APPLICATION_TOKEN1)

        self.assertEqual(
            rv,
            {
                'access_token': APPLICATION_TOKEN1,
                'expires_in': APPLICATION_TOKEN_TTL1,
                'refresh_token': APPLICATION_TOKEN2,
            },
        )

    def test_token_invalid(self):
        self._proxy.set_response_value(
            'refresh_token',
            meethue_test.MeethueApi.build_invalid_token_error(),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._p.refresh_token(APPLICATION_TOKEN1)

    def test_invalid_error_response(self):
        self._proxy.set_response_value(
            'refresh_token',
            meethue_test.MeethueApi.build_invalid_error_response(),
        )

        with self.assertRaises(UnexpectedResponseProxylibError):
            self._p.refresh_token(APPLICATION_TOKEN1)
