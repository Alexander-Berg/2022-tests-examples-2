# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import NetworkProxylibError
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.test.conf import settings_context
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
)
from passport.backend.social.common.test.fake_useragent import (
    FakeUseragent,
    FakeZoraUseragent,
)
from passport.backend.social.common.test.types import FakeResponse
from passport.backend.social.common.useragent import (
    build_http_pool_manager,
    ZoraUseragent,
)
import passport.backend.social.proxylib
from passport.backend.social.proxylib.repo.common import Repo
from passport.backend.social.proxylib.test.test_case import TestCase
from urllib3.exceptions import ReadTimeoutError


class TestExecuteRequestBasic(TestCase):
    def setUp(self):
        super(TestExecuteRequestBasic, self).setUp()

        self._HTTP = self._fake_http_pool_manager
        self._r = Repo('xx')
        self._r.access_token = {'value': APPLICATION_TOKEN1}
        self._r.app = Application(request_from_intranet_allowed=True)

    def _get_configuration(self, useragent_retries=None, provider_retries=None,
                           useragent_timeout=None, provider_timeout=None):
        social_config = dict(
            broker_stress_emulator_provider_url='http://social-u2.yandex.net:11956/api/',
        )

        if useragent_retries is not None:
            social_config['useragent_default_retries'] = useragent_retries

        if useragent_timeout is not None:
            social_config['useragent_default_timeout'] = useragent_timeout

        provider = dict(id=1, code='xx', name='xx')

        if provider_retries is not None:
            provider['retries'] = provider_retries

        if provider_timeout is not None:
            provider['timeout'] = provider_timeout

        return dict(
            fake_db=self._fake_db,
            social_config=social_config,
            providers=[provider],
            applications=[
                {
                    'application_id': 1,
                    'provider_id': 1,
                    'provider_client_id': 'xx1',
                    'application_name': 'xx1',
                },
            ],
        )

    def test_basic(self):
        self._HTTP.urlopen.side_effect = [FakeResponse('', status_code=200)]

        self._r.compose_request(base_url='http://www.yandex.ru/hello/')
        with settings_context(**self._get_configuration()):
            self._r.execute_request_basic()

        eq_(
            self._HTTP.urlopen.call_args_list,
            [
                mock.call(
                    method='GET',
                    url='http://www.yandex.ru/hello/?access_token=abcdef',
                    headers={'User-Agent': 'yandex-social-useragent/0.1'},
                    body=None,
                    pool_timeout=1,
                    redirect=False,
                    # Повторения исполняются на уровне Useragent и поэтому
                    # в urllib3 нужно передать False, чтобы он не делал
                    # повторений.
                    retries=False,
                    timeout=1,
                ),
            ],
        )

    def test_global_retries(self):
        for retry_count in [2, 3]:
            self._HTTP.urlopen.side_effect = [ReadTimeoutError(None, None, None)] * retry_count
            self._r.compose_request(base_url='http://www.yandex.ru/hello/')

            with settings_context(**self._get_configuration(useragent_retries=retry_count)):
                with self.assertRaises(NetworkProxylibError):
                    self._r.execute_request_basic()

                eq_(self._HTTP.urlopen.call_count, retry_count)
                ok_(self._HTTP.urlopen.call_args_list[0][1]['retries'] is False)
                self._HTTP.reset_mock()

    def test_provider_retries(self):
        for retry_count in [2, 3]:
            self._HTTP.urlopen.side_effect = [ReadTimeoutError(None, None, None)] * retry_count
            self._r.compose_request(base_url='http://www.yandex.ru/hello/')

            with settings_context(**self._get_configuration(useragent_retries=10, provider_retries=retry_count)):
                with self.assertRaises(NetworkProxylibError):
                    self._r.execute_request_basic()

            eq_(self._HTTP.urlopen.call_count, retry_count)
            ok_(self._HTTP.urlopen.call_args_list[0][1]['retries'] is False)
            self._HTTP.reset_mock()

    def test_specified_retries(self):
        for retry_count in [2, 3]:
            self._HTTP.urlopen.side_effect = [ReadTimeoutError(None, None, None)] * retry_count
            self._r.compose_request(base_url='http://www.yandex.ru/hello/')

            with settings_context(**self._get_configuration(useragent_retries=10, provider_retries=15)):
                with self.assertRaises(NetworkProxylibError):
                    self._r.execute_request_basic(retries=retry_count)

            eq_(self._HTTP.urlopen.call_count, retry_count)
            ok_(self._HTTP.urlopen.call_args_list[0][1]['retries'] is False)
            self._HTTP.reset_mock()

    def test_global_timeout(self):
        for timeout in [2, 3]:
            self._HTTP.urlopen.side_effect = [ReadTimeoutError(None, None, None)]
            self._r.compose_request(base_url='http://www.yandex.ru/hello/')

            with settings_context(**self._get_configuration(useragent_timeout=timeout)):
                with self.assertRaises(NetworkProxylibError):
                    self._r.execute_request_basic()

            eq_(self._HTTP.urlopen.call_args[1]['timeout'], timeout)
            self._HTTP.reset_mock()

    def test_provider_timeout(self):
        for timeout in [2, 3]:
            self._HTTP.urlopen.side_effect = [ReadTimeoutError(None, None, None)]
            self._r.compose_request(base_url='http://www.yandex.ru/hello/')

            with settings_context(**self._get_configuration(useragent_timeout=10, provider_timeout=timeout)):
                with self.assertRaises(NetworkProxylibError):
                    self._r.execute_request_basic()

            eq_(self._HTTP.urlopen.call_args[1]['timeout'], timeout)
            self._HTTP.reset_mock()

    def test_specified_timeout(self):
        for timeout in [2, 3]:
            self._HTTP.urlopen.side_effect = [ReadTimeoutError(None, None, None)]
            self._r.compose_request(base_url='http://www.yandex.ru/hello/')

            with settings_context(**self._get_configuration(useragent_timeout=10, provider_timeout=15)):
                with self.assertRaises(NetworkProxylibError):
                    self._r.execute_request_basic(timeout=timeout)

            eq_(self._HTTP.urlopen.call_args[1]['timeout'], timeout)
            self._HTTP.reset_mock()

    def test_additional_headers(self):
        self._HTTP.urlopen.side_effect = [FakeResponse('', status_code=200)]
        self._r.compose_request(
            base_url='http://www.yandex.ru/hello/',
            additional_headers={'Header1': 'Value1'},
        )
        with settings_context(**self._get_configuration()):
            self._r.execute_request_basic()
        eq_(
            self._HTTP.urlopen.call_args_list,
            [
                mock.call(
                    method='GET',
                    url='http://www.yandex.ru/hello/?access_token=abcdef',
                    headers={
                        'User-Agent': 'yandex-social-useragent/0.1',
                        'Header1': 'Value1',
                    },
                    body=None,
                    pool_timeout=1,
                    redirect=False,
                    retries=False,
                    timeout=1,
                ),
            ],
        )


class TestExecuteRequestBasic2(TestCase):
    def setUp(self):
        super(TestExecuteRequestBasic2, self).setUp()
        passport.backend.social.proxylib.init()

        LazyLoader.register('http_pool_manager', build_http_pool_manager)

        self.fake_useragent = FakeUseragent()
        self.fake_useragent.start()

        self.base_url = 'http://base.url/me'
        self.repo = self.build_repo()
        self.fake_useragent.set_response_values([FakeResponse('ok', 200)])

    def tearDown(self):
        self.fake_useragent.stop()
        super(TestExecuteRequestBasic2, self).tearDown()

    def build_repo(self, app=None):
        if app is None:
            app = self.build_application()
        rep = Repo('xx')
        rep.access_token = dict(value=APPLICATION_TOKEN1)
        rep.app = app
        rep.settings = dict()
        return rep

    def build_application(self):
        return Application(
            id=EXTERNAL_APPLICATION_ID1,
            request_from_intranet_allowed=True,
        )

    def test_add_app_id(self):
        self.repo.settings.update(add_app_id=True)
        self.repo.compose_request(base_url=self.base_url)
        self.repo.execute_request_basic()

        assert len(self.fake_useragent.requests) == 1
        assert self.fake_useragent.requests[0].query.get('app_id') == EXTERNAL_APPLICATION_ID1

    def test_add_custom_provider_client_id(self):
        app = self.build_application()
        app.custom_provider_client_id = EXTERNAL_APPLICATION_ID2
        self.repo.app = app
        self.repo.settings.update(add_app_id=True)
        self.repo.compose_request(base_url=self.base_url)
        self.repo.execute_request_basic()

        assert len(self.fake_useragent.requests) == 1
        assert self.fake_useragent.requests[0].query.get('app_id') == EXTERNAL_APPLICATION_ID2


class TestRepoUsesZora(TestCase):
    def setUp(self):
        super(TestRepoUsesZora, self).setUp()

        self._fake_zora_useragent = FakeZoraUseragent()

        self.__patches = [
            self._fake_zora_useragent,
        ]
        for patch in self.__patches:
            patch.start()

        zora_useragent = ZoraUseragent(mock.Mock(name='tvm_credentials_manager'))
        LazyLoader.register('zora_useragent', lambda: zora_useragent)

        providers.init()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestRepoUsesZora, self).tearDown()

    def _build_repo(self, request_from_intranet_allowed=False):
        repo = Repo('xx')
        repo.app = Application(request_from_intranet_allowed=request_from_intranet_allowed)
        return repo

    def test_execute_request_basic(self):
        def make_request(repo):
            repo.compose_request(base_url='https://hello/', add_access_token=False)
            repo.execute_request_basic(http_method='POST')

        self._fake_zora_useragent.set_response_value(FakeResponse('ok', 200))

        make_request(self._build_repo())

        self.assertEqual(len(self._fake_zora_useragent.requests), 1)
        self.assertEqual(self._fake_zora_useragent.requests[0].url, 'https://hello/')
        self.assertEqual(len(self._fake_useragent.requests), 0)

        self._fake_useragent.set_response_value(FakeResponse('ok', 200))

        make_request(self._build_repo(request_from_intranet_allowed=True))

        self.assertEqual(len(self._fake_useragent.requests), 1)
        self.assertEqual(self._fake_useragent.requests[0].url, 'https://hello/')
        self.assertEqual(len(self._fake_zora_useragent.requests), 1)
