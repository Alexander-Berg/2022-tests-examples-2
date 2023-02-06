# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.application import (
    Application,
    ApplicationGroupId,
)
from passport.backend.social.common.exception import (
    InvalidTokenProxylibError,
    UnexpectedResponseProxylibError,
)
from passport.backend.social.common.providers.Xiaomi import Xiaomi
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.test_case import TestCase
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import xiaomi as xiaomi_test


class XiaomiTestCase(TestCase):
    def setUp(self):
        super(XiaomiTestCase, self).setUp()
        self._proxy = xiaomi_test.FakeProxy().start()
        passport.backend.social.proxylib.init()

        self._p = get_proxy(
            Xiaomi.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                group_id=ApplicationGroupId.station,
                id=EXTERNAL_APPLICATION_ID1,
                secret=APPLICATION_SECRET1,
                refresh_token_url='https://api.xiao.mi/oauth2/refresh',
            ),
        )

    def tearDown(self):
        self._proxy.stop()
        super(XiaomiTestCase, self).tearDown()


class TestRefreshToken(XiaomiTestCase):
    def test_token_valid(self):
        self._proxy.set_response_value(
            'refresh_token',
            xiaomi_test.XiaomiApi.refresh_token(),
        )

        rv = self._p.refresh_token(APPLICATION_TOKEN1)

        self.assertEqual(
            rv,
            {
                'access_token': APPLICATION_TOKEN1,
                'refresh_token': APPLICATION_TOKEN2,
            },
        )

    def test_token_invalid(self):
        self._proxy.set_response_value(
            'refresh_token',
            xiaomi_test.XiaomiApi.build_invalid_token_error(),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            self._p.refresh_token(APPLICATION_TOKEN1)

    def test_invalid_error_response(self):
        self._proxy.set_response_value(
            'refresh_token',
            xiaomi_test.XiaomiApi.build_invalid_error_response(),
        )

        with self.assertRaises(UnexpectedResponseProxylibError):
            self._p.refresh_token(APPLICATION_TOKEN1)
