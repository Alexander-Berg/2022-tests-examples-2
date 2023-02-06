# -*- coding: utf-8 -*-

from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.social.broker.test import InternalBrokerHandlerV1TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.exception import NetworkProxylibError
from passport.backend.social.common.misc import X_TOKEN_SCOPE
from passport.backend.social.common.providers.Apple import Apple
from passport.backend.social.common.providers.Google import Google
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.task import Task
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_NAME1,
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN_TTL1,
    CONSUMER1,
    CONSUMER_IP1,
    EMAIL1,
    EXTERNAL_APPLICATION_ID1,
    FIRSTNAME1,
    GOOGLE_APPLICATION_ID1,
    GOOGLE_APPLICATION_NAME1,
    LASTNAME1,
    NICKNAME1,
    SIMPLE_USERID1,
    TASK_ID1,
    UID1,
    USERNAME1,
    VKONTAKTE_APPLICATION_ID1,
    VKONTAKTE_APPLICATION_NAME1,
    YANDEX_APPLICATION_ID1,
    YANDEX_APPLICATION_ID2,
    YANDEX_APPLICATION_NAME1,
    YANDEX_APPLICATION_NAME2,
)
import passport.backend.social.proxylib.test.apple as apple_test
from passport.backend.social.proxylib.test.google import (
    FakeProxy as GoogleFakeProxy,
    GoogleApi,
)
from passport.backend.social.proxylib.test.vkontakte import (
    FakeProxy as VkontakteFakeProxy,
    VkontakteApi,
)
from passport.backend.social.proxylib.test.yandex import (
    FakeProxy as YandexFakeProxy,
    YandexApi,
)


KINOPOISK_CLIENT_ID1 = 'kinopoisk_client_id1'


class TestTaskByTokenGoogle(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/task_by_token'
    REQUEST_HEADERS = {'X-Real-Ip': CONSUMER_IP1}
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'provider': 'gg',
        'application': EXTERNAL_APPLICATION_ID1,
    }
    REQUEST_DATA = {
        'provider_token': APPLICATION_TOKEN1,
        'scope': ' '.join([
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
        ]),
    }

    def setUp(self):
        super(TestTaskByTokenGoogle, self).setUp()
        self._fake_google = GoogleFakeProxy().start()

    def tearDown(self):
        self._fake_google.stop()
        super(TestTaskByTokenGoogle, self).tearDown()

    def _setup_environment(self,
                           client_token_valid=True,
                           server_token_valid_on_get_token_info=True,
                           server_token_valid_on_get_profile=True,
                           network_fail_on_exchange_code=False,
                           network_fail_on_get_token_info=False,
                           network_fail_on_get_profile=False,
                           unknown_fail_on_exchange_code=False,
                           unknown_fail_on_get_token_info=False,
                           unknown_fail_on_get_profile=False):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['task-by-token'],
        )

        self._fake_generate_task_id.set_retval(TASK_ID1)

        if network_fail_on_exchange_code:
            self._fake_google.set_response_value(
                'exchange_authorization_code_to_token',
                NetworkProxylibError(),
            )
        elif unknown_fail_on_exchange_code:
            self._fake_google.set_response_value(
                'exchange_authorization_code_to_token',
                GoogleApi.build_error('unknown'),
            )
        elif client_token_valid:
            self._fake_google.set_response_value(
                'exchange_authorization_code_to_token',
                GoogleApi.exchange_auth_code_to_token(
                    access_token=APPLICATION_TOKEN2,
                    expires_in=APPLICATION_TOKEN_TTL1,
                ),
            )
        else:
            self._fake_google.set_response_value(
                'exchange_authorization_code_to_token',
                GoogleApi.build_invalid_grant_error(),
            )

        if network_fail_on_get_token_info:
            self._fake_google.set_response_value(
                'get_token_info',
                NetworkProxylibError(),
            )
        elif unknown_fail_on_get_token_info:
            self._fake_google.set_response_value(
                'get_token_info',
                GoogleApi.build_error('unknown'),
            )
        elif server_token_valid_on_get_token_info:
            self._fake_google.set_response_value(
                'get_token_info',
                GoogleApi.get_token_info({
                    'aud': EXTERNAL_APPLICATION_ID1,
                    'azp': EXTERNAL_APPLICATION_ID1,
                    'scope': ' '.join([
                        'https://www.googleapis.com/auth/userinfo.profile',
                        'https://www.googleapis.com/auth/userinfo.email',
                    ]),
                    'expires_in': str(APPLICATION_TOKEN_TTL1),
                }),
            )
        else:
            self._fake_google.set_response_value(
                'get_token_info',
                GoogleApi.get_token_info__fail(),
            )

        if network_fail_on_get_profile:
            self._fake_google.set_response_value(
                'get_profile',
                NetworkProxylibError(),
            )
        elif unknown_fail_on_get_profile:
            self._fake_google.set_response_value(
                'get_profile',
                GoogleApi.build_error('unknown'),
            )
        elif server_token_valid_on_get_profile:
            self._fake_google.set_response_value(
                'get_profile',
                GoogleApi.get_profile({
                    'sub': SIMPLE_USERID1,
                }),
            )
        else:
            self._fake_google.set_response_value(
                'get_profile',
                GoogleApi.build_invalid_token_error(),
            )

    def _build_ok_response(self):
        return {
            'consumer': CONSUMER1,
            'task_id': TASK_ID1,
            'created': now.f(),
            'finished': now.f(),
            'profile': {
                'userid': SIMPLE_USERID1,
                'provider': {
                    'id': Google.id,
                    'code': Google.code,
                    'name': 'google',
                },
                'links': Google.profile_link(SIMPLE_USERID1),
            },
            'token': {
                'application': GOOGLE_APPLICATION_NAME1,
                'application_attributes': {
                    'id': GOOGLE_APPLICATION_NAME1,
                    'third_party': False,
                },
                'expires': now.i() + APPLICATION_TOKEN_TTL1,
                'scope': ','.join(
                    sorted([
                        'https://www.googleapis.com/auth/userinfo.profile',
                        'https://www.googleapis.com/auth/userinfo.email',
                    ]),
                ),
                'value': APPLICATION_TOKEN2,
                'token_id': None,
                'secret': None,
            },
        }

    def _build_task(self):
        task = Task()
        task.task_id = TASK_ID1
        task.consumer = CONSUMER1
        task.created = now.f()
        task.finished = now.f()
        task.in_redis = True
        task.profile = {
            'userid': SIMPLE_USERID1,
            'links': Google.profile_link(SIMPLE_USERID1),
            'provider': {
                'id': Google.id,
                'code': Google.code,
                'name': 'google',
                'retries': 1,
                'timeout': 1,
                'display_name': {
                    'default': 'Google',
                    'en': 'Google',
                    'ru': 'Google',
                },
            },
        }
        task.provider = {
            'id': Google.id,
            'code': Google.code,
            'name': 'google',
        }
        task.application = Application(
            identifier=GOOGLE_APPLICATION_ID1,
            id=EXTERNAL_APPLICATION_ID1,
            name=GOOGLE_APPLICATION_NAME1,
            is_third_party=False,
        )
        task.access_token = dict(
            value=APPLICATION_TOKEN2,
            expires=now.i() + APPLICATION_TOKEN_TTL1,
            scope=','.join(
                sorted([
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'https://www.googleapis.com/auth/userinfo.email',
                ]),
            ),
            secret=None,
            token_id=None,
            application=GOOGLE_APPLICATION_ID1,
        )
        return task

    def _assert_task_by_token_error_response(self, rv, error):
        self._assert_error_response(
            rv,
            errors=[error],
            response={
                'provider': {
                    'id': Google.id,
                    'code': Google.code,
                    'name': 'google',
                },
            },
            retpath=None,
        )

    def test_ok(self):
        self._setup_environment()

        rv = self._make_request()

        self._assert_ok_response(rv, self._build_ok_response())
        self._assert_task_equals(TASK_ID1, self._build_task())

    def test_client_token_invalid(self):
        self._setup_environment(client_token_valid=False)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'OAuthTokenInvalidError')

    def test_get_token_info_responses_server_token_invalid(self):
        self._setup_environment(server_token_valid_on_get_token_info=False)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'OAuthTokenInvalidError')

    def test_get_profile_responses_server_token_invalid(self):
        self._setup_environment(server_token_valid_on_get_profile=False)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'OAuthTokenInvalidError')

    def test_network_fail_on_exchange_code(self):
        self._setup_environment(network_fail_on_exchange_code=True)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'CommunicationFailedError')

    def test_network_fail_on_get_token_info(self):
        self._setup_environment(network_fail_on_get_token_info=True)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'CommunicationFailedError')

    def test_network_fail_on_get_profile(self):
        self._setup_environment(network_fail_on_get_profile=True)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'CommunicationFailedError')

    def test_unknown_fail_on_exchange_code(self):
        self._setup_environment(unknown_fail_on_exchange_code=True)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'CommunicationFailedError')

    def test_unknown_fail_on_get_token_info(self):
        self._setup_environment(unknown_fail_on_get_token_info=True)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'CommunicationFailedError')

    def test_unknown_fail_on_get_profile(self):
        self._setup_environment(unknown_fail_on_get_profile=True)
        rv = self._make_request()
        self._assert_task_by_token_error_response(rv, 'CommunicationFailedError')


class TestTaskByTokenVkontakte(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/task_by_token'
    REQUEST_HEADERS = {'X-Real-Ip': CONSUMER_IP1}
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'provider': 'vk',
        'application': EXTERNAL_APPLICATION_ID1,
    }
    REQUEST_DATA = {
        'provider_token': APPLICATION_TOKEN1,
        'scope': 'offline',
    }

    def setUp(self):
        super(TestTaskByTokenVkontakte, self).setUp()
        self._fake_vkontakte = VkontakteFakeProxy().start()

    def tearDown(self):
        self._fake_vkontakte.stop()
        super(TestTaskByTokenVkontakte, self).tearDown()

    def _setup_environment(self,
                           rate_limit_on_apps_get=False,
                           rate_limit_on_get_apps_permissions=False,
                           rate_limit_on_users_get=False):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['task-by-token'],
        )

        if rate_limit_on_apps_get:
            self._fake_vkontakte.set_response_value(
                'apps.get',
                VkontakteApi.build_rate_limit_exceeded_error(),
            )
        else:
            self._fake_vkontakte.set_response_value(
                'apps.get',
                VkontakteApi.apps_get([{'id': int(EXTERNAL_APPLICATION_ID1)}]),
            )

        if rate_limit_on_get_apps_permissions:
            self._fake_vkontakte.set_response_value(
                'account.getAppPermissions',
                VkontakteApi.build_rate_limit_exceeded_error(),
            )
        else:
            self._fake_vkontakte.set_response_value(
                'account.getAppPermissions',
                VkontakteApi.account_get_app_permissions(65536),
            )

        if rate_limit_on_users_get:
            self._fake_vkontakte.set_response_value(
                'users.get',
                VkontakteApi.build_rate_limit_exceeded_error(),
            )
        else:
            self._fake_vkontakte.set_response_value(
                'users.get',
                VkontakteApi.users_get(
                    user={
                        'domain': USERNAME1,
                        'nickname': NICKNAME1,
                    },
                    exclude_attrs=[
                        # Исключаю некоторые поля для упрощения теста
                        'bdate',
                        'sex',
                        'first_name',
                        'last_name',
                        'mobile_phone',
                        'home_phone',
                        'photo_50',
                        'photo_100',
                        'photo_200',
                        'photo_200_orig',
                        'photo_400_orig',
                        'photo_max_orig',
                        'universities',
                        'country',
                        'city',
                    ],
                ),
            )

    def _build_ok_response(self):
        return {
            'consumer': CONSUMER1,
            'task_id': TASK_ID1,
            'created': now.f(),
            'finished': now.f(),
            'profile': {
                'userid': SIMPLE_USERID1,
                'username': USERNAME1,
                'provider': {
                    'id': Vkontakte.id,
                    'code': Vkontakte.code,
                    'name': 'vkontakte',
                },
                'links': Vkontakte.profile_link(SIMPLE_USERID1, USERNAME1),
            },
            'token': {
                'application': VKONTAKTE_APPLICATION_NAME1,
                'application_attributes': {
                    'id': VKONTAKTE_APPLICATION_NAME1,
                    'third_party': False,
                },
                'expires': None,
                'scope': 'offline',
                'value': APPLICATION_TOKEN1,
                'token_id': None,
                'secret': None,
            },
        }

    def _assert_task_by_token_error_response(self, rv, error):
        self._assert_error_response(
            rv,
            errors=[error],
            response={
                'provider': {
                    'id': Vkontakte.id,
                    'code': Vkontakte.code,
                    'name': 'vkontakte',
                },
            },
            retpath=None,
        )

    def _build_task(self):
        task = Task()
        task.task_id = TASK_ID1
        task.consumer = CONSUMER1
        task.created = now.f()
        task.finished = now.f()
        task.in_redis = True
        task.profile = {
            'userid': SIMPLE_USERID1,
            'username': USERNAME1,
            'nickname': NICKNAME1,
            'links': Vkontakte.profile_link(SIMPLE_USERID1, USERNAME1),
            'provider': {
                'id': Vkontakte.id,
                'code': Vkontakte.code,
                'name': 'vkontakte',
                'retries': 1,
                'timeout': 1,
                'display_name': {'default': 'Vkontakte'},
            },
        }
        task.provider = {
            'id': Vkontakte.id,
            'code': Vkontakte.code,
            'name': 'vkontakte',
        }
        task.application = Application(
            identifier=VKONTAKTE_APPLICATION_ID1,
            id=EXTERNAL_APPLICATION_ID1,
            name=VKONTAKTE_APPLICATION_NAME1,
            is_third_party=False,
        )
        task.access_token = dict(
            value=APPLICATION_TOKEN1,
            expires=None,
            scope='offline',
            secret=None,
            token_id=None,
            application=VKONTAKTE_APPLICATION_ID1,
        )
        return task

    def test_ok(self):
        self._setup_environment()

        rv = self._make_request()

        self._assert_ok_response(rv, self._build_ok_response())
        self._assert_task_equals(TASK_ID1, self._build_task())

    def test_rate_limit_exceeded_on_apps_get(self):
        self._setup_environment(rate_limit_on_apps_get=True)

        rv = self._make_request()

        self._assert_task_by_token_error_response(rv, 'RateLimitExceededError')

    def test_rate_limit_exceeded_on_get_app_permissions(self):
        self._setup_environment(rate_limit_on_get_apps_permissions=True)

        rv = self._make_request()

        self._assert_task_by_token_error_response(rv, 'RateLimitExceededError')

    def test_rate_limit_exceeded_on_users_get(self):
        self._setup_environment(rate_limit_on_users_get=True)

        rv = self._make_request()

        self._assert_task_by_token_error_response(rv, 'RateLimitExceededError')


class TestTaskByTokenYandex(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/task_by_token'
    REQUEST_HEADERS = {'X-Real-Ip': CONSUMER_IP1}
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'provider': 'ya',
        'application': EXTERNAL_APPLICATION_ID1,
    }
    REQUEST_DATA = {
        'provider_token': APPLICATION_TOKEN1,
    }

    def setUp(self):
        super(TestTaskByTokenYandex, self).setUp()
        self._fake_yandex = YandexFakeProxy()
        self._fake_blackbox = FakeBlackbox()

        self.__patches = [
            self._fake_blackbox,
            self._fake_yandex,
        ]
        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestTaskByTokenYandex, self).tearDown()

    def build_settings(self):
        settings = super(TestTaskByTokenYandex, self).build_settings()
        settings['social_config'].update(
            dict(
                yandex_get_profile_url='https://login.yandex.ru/info',
                yandex_avatar_url_template='https://avatars.mds.yandex.net/get-yapic/%s/',
            ),
        )
        settings['applications'] = [
            {
                'provider_id': Yandex.id,
                'application_id': YANDEX_APPLICATION_ID1,
                'application_name': YANDEX_APPLICATION_NAME1,
                'provider_client_id': EXTERNAL_APPLICATION_ID1,
                'secret': APPLICATION_SECRET1,
                'domain': '.yandex.ru',
                'request_from_intranet_allowed': '1',
            },
            {
                'provider_id': Yandex.id,
                'application_id': YANDEX_APPLICATION_ID2,
                'application_name': YANDEX_APPLICATION_NAME2,
                'provider_client_id': KINOPOISK_CLIENT_ID1,
                'secret': APPLICATION_SECRET1,
                'domain': '.yandex.ru',
                'request_from_intranet_allowed': '1',
            },
        ]
        return settings

    def _setup_environment(self, **kwargs):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['task-by-token'],
        )

        self._fake_generate_task_id.set_retval(TASK_ID1)

        oauth_kwargs = self._build_oauth_token(**kwargs)
        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**oauth_kwargs),
            ],
        )

        get_profile_response = YandexApi.get_profile(
            {
                'id': str(UID1),
                'is_avatar_empty': True,
            },
            exclude_attrs=[
                'birthday',
                'default_email',
                'display_name',
                'emails',
                'first_name',
                'last_name',
                'sex',
            ],
        )
        self._fake_yandex.set_response_value('get_profile', get_profile_response)

    def _build_oauth_token(self, token_scope=Undefined, token_client_id=EXTERNAL_APPLICATION_ID1, **kwargs):
        if token_scope is Undefined:
            token_scope = X_TOKEN_SCOPE
        oauth = dict(
            scope=token_scope,
            client_id=token_client_id,
        )
        return oauth

    def _build_ok_response(self, token_scope=X_TOKEN_SCOPE):
        return {
            'consumer': CONSUMER1,
            'task_id': TASK_ID1,
            'created': now.f(),
            'finished': now.f(),
            'profile': {
                'userid': str(UID1),
                'provider': {
                    'id': Yandex.id,
                    'code': Yandex.code,
                    'name': 'yandex',
                },
                'links': list(),
            },
            'token': {
                'application': YANDEX_APPLICATION_NAME1,
                'application_attributes': {
                    'id': YANDEX_APPLICATION_NAME1,
                    'third_party': False,
                },
                'expires': None,
                'scope': token_scope,
                'value': APPLICATION_TOKEN1,
                'token_id': None,
                'secret': None,
            },
        }

    def _assert_task_by_token_error_response(self, rv, error):
        self._assert_error_response(
            rv,
            errors=[error],
            response={
                'provider': {
                    'id': Yandex.id,
                    'code': Yandex.code,
                    'name': 'yandex',
                },
            },
            retpath=None,
        )

    def test_x_token(self):
        self._setup_environment(token_scope=X_TOKEN_SCOPE)

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            self._build_ok_response(token_scope=X_TOKEN_SCOPE),
        )

    def test_social_broker_token(self):
        self._setup_environment(token_scope='social:broker')

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            self._build_ok_response(token_scope='social:broker'),
        )

    def test_unknown_application_client_id(self):
        self._setup_environment()

        rv = self._make_request(query={'application': 'unknown'})

        self._assert_error_response(
            rv,
            errors=['ApplicationUnknownError'],
            retpath=None,
        )

    def test_unknown_token_client_id__x_token(self):
        self._setup_environment(token_client_id='unknown', token_scope=X_TOKEN_SCOPE)

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            self._build_ok_response(token_scope=X_TOKEN_SCOPE),
        )

    def test_unknown_token_client_id__social_broker_token(self):
        self._setup_environment(token_client_id='unknown', token_scope='social:broker')

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            self._build_ok_response(token_scope='social:broker'),
        )

    def test_unknown_token_client_id__unknown_token_scope(self):
        self._setup_environment(token_client_id='unknown', token_scope='unknown')

        rv = self._make_request()

        self._assert_task_by_token_error_response(rv, 'OAuthTokenInvalidError')

    def test_known_token_client_id__unknown_token_scope(self):
        # Регрессионный тесты (костыль для Кинопоиска, потому что у приложения
        # Кинопоиска нет ни скоупа oauth:grant_xtoken, ни скоупа social:broker).
        self._setup_environment(token_client_id=KINOPOISK_CLIENT_ID1, token_scope='unknown')

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            self._build_ok_response(token_scope='unknown'),
        )

    def test_known_client_id__unknown_token_client_id_and_token_scope(self):
        self._setup_environment(token_client_id='unknown', token_scope='unknown')

        rv = self._make_request(query={'application': KINOPOISK_CLIENT_ID1})

        self._assert_task_by_token_error_response(rv, 'OAuthTokenInvalidError')


class TestTaskByTokenApple(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/task_by_token'
    REQUEST_HEADERS = {'X-Real-Ip': CONSUMER_IP1}
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'provider': 'apl',
        'application': EXTERNAL_APPLICATION_ID1,
    }

    @property
    def REQUEST_DATA(self):
        return {
            'provider_token': self._build_token(),
        }

    def setUp(self):
        super(TestTaskByTokenApple, self).setUp()
        self._fake_apple = apple_test.FakeProxy()

        self.__patches = [
            self._fake_apple,
        ]
        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestTaskByTokenApple, self).tearDown()

    def build_settings(self):
        settings = super(TestTaskByTokenApple, self).build_settings()
        settings['providers'] = [self._build_provider_info()]
        settings['applications'] = [
            {
                'provider_id': Apple.id,
                'application_id': APPLICATION_ID1,
                'application_name': APPLICATION_NAME1,
                'provider_client_id': EXTERNAL_APPLICATION_ID1,
                'domain': 'social.yandex.net',
                'request_from_intranet_allowed': '1',
            },
        ]
        return settings

    def _setup_environment(self):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['task-by-token'],
        )

        public_keys_response = apple_test.AppleApi.get_public_keys()
        self._fake_apple.set_response_values(
            'get_public_keys',
            [
                public_keys_response,
                public_keys_response,
                public_keys_response,
            ],
        )

    def _build_ok_response(self, id_token):
        return {
            'consumer': CONSUMER1,
            'task_id': TASK_ID1,
            'created': now.f(),
            'finished': now.f(),
            'profile': {
                'userid': SIMPLE_USERID1,
                'email': EMAIL1,
                'firstname': FIRSTNAME1,
                'lastname': LASTNAME1,
                'provider': {
                    'id': Apple.id,
                    'code': Apple.code,
                    'name': 'apple',
                },
                'links': list(),
            },
            'token': {
                'application': APPLICATION_NAME1,
                'application_attributes': {
                    'id': APPLICATION_NAME1,
                    'third_party': False,
                },
                'expires': now.i() + APPLICATION_TOKEN_TTL1,
                'scope': '',
                'value': id_token,
                'token_id': None,
                'secret': None,
            },
        }

    def _build_task(self, id_token):
        task = Task()
        task.task_id = TASK_ID1
        task.consumer = CONSUMER1
        task.created = now.f()
        task.finished = now.f()
        task.in_redis = True
        task.profile = {
            'userid': SIMPLE_USERID1,
            'email': EMAIL1,
            'firstname': FIRSTNAME1,
            'lastname': LASTNAME1,
            'links': list(),
            'provider': {
                'id': Apple.id,
                'code': Apple.code,
                'name': 'apple',
                'timeout': 1,
                'retries': 1,
                'display_name': {
                    'default': 'apple',
                },
            },
        }

        task.provider = {
            'id': Apple.id,
            'code': Apple.code,
            'name': 'apple',
        }
        task.application = Application(
            identifier=APPLICATION_ID1,
            id=EXTERNAL_APPLICATION_ID1,
            name=APPLICATION_NAME1,
            is_third_party=False,
        )
        task.access_token = dict(
            value=id_token,
            expires=now.i() + APPLICATION_TOKEN_TTL1,
            scope='',
            secret=None,
            token_id=None,
            application=APPLICATION_ID1,
        )
        return task

    def _build_provider_info(self):
        return {
            'id': Apple.id,
            'code': Apple.code,
            'name': 'apple',
            'timeout': 1,
            'retries': 1,
            'display_name': {
                'default': 'apple',
            },
        }

    def _build_token(self, id_token=None):
        if id_token is None:
            id_token = self._build_id_token()
        return apple_test.build_client_token_v1(
            dict(
                id_token=id_token,
                firstname=FIRSTNAME1,
                lastname=LASTNAME1,
            ),
        )

    def _build_id_token(self):
        id_token = dict(
            aud=EXTERNAL_APPLICATION_ID1,
            email=EMAIL1,
            exp=now.i() + APPLICATION_TOKEN_TTL1,
            sub=SIMPLE_USERID1,
        )
        return apple_test.build_id_token(id_token)

    def test_ok(self):
        self._setup_environment()
        id_token = self._build_id_token()
        token = self._build_token(id_token)

        rv = self._make_request(data={'provider_token': token})

        self._assert_ok_response(
            rv,
            self._build_ok_response(id_token),
        )
        self._assert_task_equals(
            TASK_ID1,
            self._build_task(id_token),
        )
