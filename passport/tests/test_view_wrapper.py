# -*- coding: utf-8 -*-

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Facebook import Facebook
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.task import (
    build_provider_for_task,
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.web_service import Request
from passport.backend.social.proxy2.exception import InvalidParametersError
from passport.backend.social.proxy2.misc import FakeProfile
from passport.backend.social.proxy2.test import TestCase
from passport.backend.social.proxy2.views.v1.request_processors import (
    AccessTokenRequestProcessor,
    ApplicationRequestProcessor,
    choose_request_processor,
    ProfileRequestProcessor,
    TaskRequestProcessor,
)

from .base_proxy2_test_data import (
    TEST_APPLICATION_ID,
    TEST_APPLICATION_NAME,
    TEST_PROFILE_ID,
    TEST_PROVIDER,
    TEST_TASK_ID,
    TEST_TOKEN_VALUE,
    TEST_UID,
    TEST_USERID,
    TEST_USERNAME,
)


TEST_METHOD_NAME = 'existing_method'


# TODO Переписать: одна и та же логинка тестируется по несколько раз, много копипасты
class TestViewWrapper(TestCase):
    def setUp(self):
        super(TestViewWrapper, self).setUp()

        self.get_tokens_mock = Mock()
        self.get_profile_mock = Mock()

        self.existing_proxy_method_mock = Mock()
        self.get_proxy_response = Mock(**{TEST_METHOD_NAME: self.existing_proxy_method_mock})

        self.__patches = [
            patch('passport.backend.social.proxy2.views.v1.request_processors.get_tokens', self.get_tokens_mock),
            patch('passport.backend.social.proxy2.views.v1.request_processors.get_profile', self.get_profile_mock),
            patch('passport.backend.social.proxy2.views.v1.request_processors.get_proxy', self.get_proxy_response),
        ]

        for p in self.__patches:
            p.start()

        self._fake_grants_config.add_consumer(
            consumer=CONSUMER1,
            grants=['no-cred-use-token'],
            networks=[CONSUMER_IP1],
        )

    def tearDown(self):
        for p in reversed(self.__patches):
            p.stop()
        super(TestViewWrapper, self).tearDown()

    def build_request(self, **kwargs):
        defaults = dict(
            method='GET',
            consumer_ip=CONSUMER_IP1,
            args=dict(),
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return Request.create(**kwargs)

    def build_settings(self):
        settings = super(TestViewWrapper, self).build_settings()
        settings.update(
            dict(
                applications=[
                    dict(
                        provider_id=Vkontakte.id,
                        application_id=10,
                        application_name='vkontakte',
                        provider_client_id='vkontakte',
                        secret='',
                    ),
                    dict(
                        provider_id=Facebook.id,
                        application_id=TEST_APPLICATION_ID,
                        application_name=TEST_APPLICATION_NAME,
                        provider_client_id='facebook',
                        secret='',
                    ),
                ],
            ),
        )
        return settings

    def test_wrapper_chooses_processor(self):
        """
        Если в kwargs есть profile_id - должен быть выбран ProfileRequestProcessor.
        Если task_id - TaskRequestProcessor.
        Если app_name - ApplicationRequestProcessor.
        При наличии токена в хедерах - AccessTokenRequestProcessor.
        """
        choosing_method = choose_request_processor._get_processor_class

        request = self.build_request()

        eq_(choosing_method(request, profile_id='100'), ProfileRequestProcessor)
        eq_(choosing_method(request, task_id=TEST_TASK_ID), TaskRequestProcessor)
        eq_(choosing_method(request, app_name=TEST_APPLICATION_NAME), ApplicationRequestProcessor)

        # Такого не бывает, но все же:
        eq_(
            choosing_method(
                request,
                profile_id='100',
                task_id=TEST_TASK_ID,
                app_name=TEST_APPLICATION_NAME,
            ),
            ProfileRequestProcessor,
        )

        with self.assertRaises(InvalidParametersError):
            choosing_method(request)

        # Начнем передавать токен
        request = self.build_request(header_provider_token=TEST_TOKEN_VALUE)
        eq_(choosing_method(request), AccessTokenRequestProcessor)

        eq_(choosing_method(request, profile_id='100'), ProfileRequestProcessor)
        eq_(choosing_method(request, task_id=TEST_TASK_ID), TaskRequestProcessor)
        eq_(choosing_method(request, app_name=TEST_APPLICATION_NAME), ApplicationRequestProcessor)

    def get_profile_response(self):
        return Mock(
            profile_id=TEST_PROFILE_ID,
            uid=TEST_UID,
            provider_id=TEST_PROVIDER['id'],
            userid=TEST_USERID,
            username=TEST_USERNAME,
            allow_auth=0,
            created='',
            verified='',
            confirmed='',
            referer=0,
            yandexuid='',
        )

    def get_tokens_response(self):
        return [Token(
            application=providers.get_application_by_id(TEST_APPLICATION_ID),
            profile_id=TEST_PROFILE_ID,
            scopes=['user_birthday', 'email', 'public_profile'],
            token_id=100,
            value=TEST_TOKEN_VALUE,
        )]

    @staticmethod
    def check_response_ok(response, profile_id_in_state=True, tokens=None, profile=None, simple_userid=TEST_USERID):
        task_expected = {'state': 'success', 'provider': TEST_PROVIDER['name']}
        if profile_id_in_state:
            task_expected['profile_id'] = TEST_PROFILE_ID
        eq_(response['task'], task_expected)

        eq_(
            sorted(response['result'].keys()),
            sorted([
                'consumer',
                'profile',
                'tokens',
                'simple_userid',
                'provider',
                'request',
                'method',
                'kwargs',
            ]),
        )
        eq_(response['result']['profile'], profile)
        eq_(response['result']['simple_userid'], simple_userid)
        eq_(response['result']['provider']['id'], TEST_PROVIDER['id'])

        eq_(len(response['result']['tokens']), len(tokens))
        for expected_token, found_token in zip(tokens, response['result']['tokens']):
            for key in ['application', 'value', 'secret']:
                eq_(
                    getattr(found_token, key),
                    expected_token[key],
                    [getattr(found_token, key), expected_token[key], key],
                )

            assert sorted(found_token.scopes) == sorted(expected_token['scopes'])

    def _save_task_to_redis(self, task_id, application_id, consumer, userid, username,
                            token_scope, token_value, token_secret):
        task = Task()
        task.profile = dict(
            username=username,
            userid=userid,
        )

        application = providers.get_application_by_id(application_id)
        task.application = application

        provider_info = providers.get_provider_info_by_id(application.provider['id'])
        task.provider = build_provider_for_task(
            provider_info['code'],
            provider_info['name'],
            provider_info['id'],
        )

        task.access_token = dict(
            value=token_value,
            scope=token_scope,
            secret=token_secret,
        )
        task.task_id = task_id
        task.consumer = consumer
        save_task_to_redis(self._fake_redis, task_id, task)
        return task

    def test_processor_profile_basic(self):
        profile = self.get_profile_response()
        tokens = self.get_tokens_response()
        self.get_profile_mock.return_value = profile
        self.get_tokens_mock.return_value = tokens

        request = self.build_request()

        request_processor = choose_request_processor(lambda context: context, TEST_METHOD_NAME, [])
        response = request_processor(request, profile_id='100')
        self.check_response_ok(
            response,
            profile=profile,
            tokens=[dict(
                application=providers.get_application_by_id(TEST_APPLICATION_ID),
                scopes=['email', 'public_profile', 'user_birthday'],
                value=TEST_TOKEN_VALUE,
                secret=None,
            )],
        )

    def test_processor_profile_allowed_applications(self):
        """
        Проверим, что работает параметр allowed_applications.
        """
        profile = self.get_profile_response()
        tokens = self.get_tokens_response()
        self.get_profile_mock.return_value = profile
        self.get_tokens_mock.return_value = tokens

        request = self.build_request(
            args={
                'allowed_applications': 'facebook,vkontakte',
            },
        )
        request_processor = choose_request_processor(lambda context: context, TEST_METHOD_NAME, [])
        response = request_processor(request, profile_id='100')

        self.check_response_ok(
            response,
            profile=profile,
            tokens=[dict(
                application=providers.get_application_by_id(TEST_APPLICATION_ID),
                scopes=['email', 'public_profile', 'user_birthday'],
                value=TEST_TOKEN_VALUE,
                secret=None,
            )],
        )
        eq_(set(self.get_tokens_mock.call_args_list[0][1]['application_ids']), set([10, 20]))

    @raises(InvalidParametersError)
    def test_processor_profile_allowed_applications_invalid_app(self):
        """
        Неправильное имя приложение должно приводить к ошибке.
        """
        self.get_profile_mock.return_value = self.get_profile_response()
        request = self.build_request(
            args={
                'allowed_applications': 'invalid_application',
            },
        )

        request_processor = choose_request_processor(lambda context: context, TEST_METHOD_NAME, [])
        request_processor(request, profile_id='100')

    def test_processor_task_basic(self):
        task = self._save_task_to_redis(
            task_id=TEST_TASK_ID,
            consumer=CONSUMER1,
            userid=TEST_USERID,
            username=TEST_USERNAME,
            application_id=TEST_APPLICATION_ID,
            token_scope='user_birthday,email,public_profile',
            token_value=TEST_TOKEN_VALUE,
            token_secret=None,
        )
        request = self.build_request(args={'consumer': CONSUMER1})

        request_processor = choose_request_processor(lambda context: context, TEST_METHOD_NAME, [])
        response = request_processor(request, task_id=TEST_TASK_ID)

        self.check_response_ok(
            response,
            profile_id_in_state=False,
            profile=FakeProfile(
                provider_id=TEST_PROVIDER['id'],
                userid=TEST_USERID,
                username=TEST_USERNAME,
                uid=None,
                profile_id=None,
            ),
            tokens=[dict(
                application=task.application,
                scopes=['email', 'public_profile', 'user_birthday'],
                value=TEST_TOKEN_VALUE,
                secret=None,
            )],
        )

    def test_processor_access_token_basic(self):
        request = self.build_request(
            args={
                'application': TEST_APPLICATION_NAME,
            },
            header_provider_token=TEST_TOKEN_VALUE,
        )

        request_processor = choose_request_processor(lambda context: context, TEST_METHOD_NAME, [])
        response = request_processor(request)

        self.check_response_ok(
            response,
            profile_id_in_state=False,
            profile=None,
            tokens=[dict(
                application=providers.get_application_by_id(TEST_APPLICATION_ID),
                scopes=[],
                value=TEST_TOKEN_VALUE,
                secret=None,
            )],
            simple_userid=None,
        )

    @raises(InvalidParametersError)
    def test_processor_access_token_requires_application(self):
        request = self.build_request(header_provider_token=TEST_TOKEN_VALUE)

        request_processor = choose_request_processor(lambda context: context, TEST_METHOD_NAME, [])
        request_processor(request)

    def test_processor_application(self):
        request = self.build_request()
        request_processor = choose_request_processor(lambda context: context, TEST_METHOD_NAME, [])
        response = request_processor(request, app_name=TEST_APPLICATION_NAME)

        self.check_response_ok(
            response,
            profile_id_in_state=False,
            profile=None,
            tokens=[dict(
                application=providers.get_application_by_id(TEST_APPLICATION_ID),
                scopes=[],
                value=None,
                secret=None,
            )],
            simple_userid=None,
        )
