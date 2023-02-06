# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import ProviderTemporaryUnavailableProxylibError
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.fake_useragent import FakeUseragent
from passport.backend.social.common.test.test_case import (
    TestCase,
    TvmTestCaseMixin,
)
from passport.backend.social.common.useragent import (
    build_http_pool_manager,
    RequestError,
)
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import yandex as yandex_test


class _BaseYandexTestCase(TvmTestCaseMixin, TestCase):
    def setUp(self):
        super(_BaseYandexTestCase, self).setUp()
        self._fake_useragent = FakeUseragent()
        self._fake_blackbox = FakeBlackbox()

        self.__patches = [
            self._fake_useragent,
            self._fake_blackbox,
        ]
        for patch in self.__patches:
            patch.start()

        LazyLoader.register('http_pool_manager', build_http_pool_manager)

        passport.backend.social.proxylib.init()

        self._p = get_proxy(
            Yandex.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                id=EXTERNAL_APPLICATION_ID1,
                secret=APPLICATION_SECRET1,
                request_from_intranet_allowed=True,
            ),
        )

    def tearDown(self):
        LazyLoader.flush()
        for patch in reversed(self.__patches):
            patch.stop()
        super(_BaseYandexTestCase, self).tearDown()

    def build_settings(self):
        settings = super(_BaseYandexTestCase, self).build_settings()
        settings['social_config'].update(
            dict(
                yandex_get_profile_url='https://login.yandex.ru/info',
                yandex_avatar_url_template='https://avatars.mds.yandex.net/get-yapic/%s/',
            ),
        )
        return settings


class TestYandex(_BaseYandexTestCase):
    def setUp(self):
        super(TestYandex, self).setUp()
        self._fake_proxy = yandex_test.FakeProxy().start()

    def tearDown(self):
        self._fake_proxy.stop()
        super(TestYandex, self).tearDown()

    def test_get_profile__backend_failed(self):
        self._fake_proxy.set_response_value(
            'get_profile',
            yandex_test.YandexApi.build_backend_error(),
        )

        with self.assertRaises(ProviderTemporaryUnavailableProxylibError):
            self._p.get_profile()

    def test_get_token_info__network_fail(self):
        self._fake_blackbox.set_response_side_effect('oauth', RequestError())
        with self.assertRaises(ProviderTemporaryUnavailableProxylibError):
            self._p.get_token_info()


class TestYandexRetriesOn5xx(_BaseYandexTestCase):
    def build_settings(self):
        settings = super(TestYandexRetriesOn5xx, self).build_settings()
        settings['providers'] = [
            {
                'id': Yandex.id,
                'code': Yandex.code,
                'name': 'yandex',
                'timeout': 1,
                'retries': 2,
                'display_name': {'default': 'Яндекс'},
            },
        ]
        return settings

    def test_get_profile__backend_failed(self):
        self._fake_useragent.set_response_values(
            [
                yandex_test.YandexApi.build_backend_error(),
                yandex_test.YandexApi.build_backend_error(),
            ],
        )

        with self.assertRaises(ProviderTemporaryUnavailableProxylibError):
            self._p.get_profile()

        self.assertEqual(len(self._fake_useragent.requests), 2)
