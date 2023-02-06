# -*- coding: utf-8 -*-

from passport.backend.core.test.consts import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import BaseTestCase


TEST_BROKER_CONSUMER1 = 'broker_consumer1'
TEST_PROVIDER_TOKEN1 = 'token1'
TEST_YANDEX_CLIENT_ID1 = 'yci1'
TEST_YANDEX_CLIENT_SECRET1 = 'ycs1'


@with_settings_hosts()
class TestThirdPartyNativeStart(BaseTestCase):
    default_url = '/1/bundle/auth/social/third_party_native_start/?consumer=dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP1,
        'accept_language': 'ru',
        'user_agent': 'curl',
    }
    http_query_args = {
        'provider_token': TEST_PROVIDER_TOKEN1,
        'provider': 'gg',
        'application': TEST_APPLICATION_ID1,
        'retpath': TEST_RETPATH1,
    }

    def setUp(self):
        super(TestThirdPartyNativeStart, self).setUp()
        self._builder = self.get_third_party_builder()

    def tearDown(self):
        del self._builder
        super(TestThirdPartyNativeStart, self).tearDown()

    def _setup_all(self, **kwargs):
        self._setup_task_for_token(**kwargs)
        self._setup_account(**kwargs)

    def _setup_task_for_token(self,
                              client_secret_missing=False,
                              **kwargs):
        args = dict()
        if client_secret_missing:
            args.update(dict(related_yandex_client_secret=None))
        task = self._builder.build_task(**args)
        self._builder.setup_task_for_token(task)

    def _setup_account(self, **kwargs):
        self._builder.setup_social_profiles([self._builder.build_social_profile()])
        self._builder.setup_yandex_accounts([self._builder.build_yandex_social_account()])

    def test_no_client_secret(self):
        self._setup_all(client_secret_missing=True)

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['application.invalid'],
            **self._builder.build_error_response(
                has_enabled_accounts=None,
                profile_id=None,
                account=None,
            )
        )

    def test_no_provider(self):
        rv = self.make_request(exclude_args=['provider'])
        self.assert_error_response(rv, ['provider.empty'], retpath=TEST_RETPATH1)

    def test_no_application(self):
        rv = self.make_request(exclude_args=['application'])
        self.assert_error_response(rv, ['application.empty'], retpath=TEST_RETPATH1)

    def test_no_provider_token(self):
        rv = self.make_request(exclude_args=['provider_token'])
        self.assert_error_response(rv, ['provider_token.empty'], retpath=TEST_RETPATH1)

    def test_no_retpath(self):
        rv = self.make_request(exclude_args=['retpath'])
        self.assert_error_response(rv, ['retpath.empty'])

    def test_morda_ru_retpath(self):
        self._setup_task_for_token()
        self._setup_account()
        self._builder.setup_profile_creation()
        self._builder.setup_yandex_token_generation()

        rv = self.make_request(query_args=dict(retpath='https://www.yandex.ru/'))

        self.assert_ok_response(
            rv,
            check_all=False,
            retpath='https://www.yandex.ru/',
        )

    def test_morda_com_retpath(self):
        self._setup_task_for_token()
        self._setup_account()
        self._builder.setup_profile_creation()
        self._builder.setup_yandex_token_generation()

        rv = self.make_request(query_args=dict(retpath='https://www.yandex.com/'))

        self.assert_ok_response(
            rv,
            check_all=False,
            retpath='https://www.yandex.com/?redirect=0',
        )

    def test_morda_com_retpath_with_query(self):
        self._setup_task_for_token()
        self._setup_account()
        self._builder.setup_profile_creation()
        self._builder.setup_yandex_token_generation()

        rv = self.make_request(query_args=dict(retpath='https://www.yandex.com/?foo=%D1%8F'))

        self.assert_ok_response(
            rv,
            check_all=False,
            retpath='https://www.yandex.com/?foo=%D1%8F&redirect=0',
        )

    def test_morda_com_retpath_error_response(self):
        rv = self.make_request(
            query_args=dict(retpath='https://www.yandex.com/'),
            exclude_args=['provider'],
        )

        self.assert_error_response(
            rv,
            ['provider.empty'],
            retpath='https://www.yandex.com/?redirect=0',
        )
