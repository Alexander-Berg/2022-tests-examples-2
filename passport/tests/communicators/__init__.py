# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_response,
    FakeBlackbox,
)
from passport.backend.core.builders.passport.faker import passport_ok_response
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.time_utils.time_utils import TimeSpan
from passport.backend.social.broker.communicators.communicator import (
    Communicator,
    CommunicatorApplicationMapper,
)
from passport.backend.social.broker.exceptions import (
    CommunicationFailedError,
    UserDeniedError,
)
from passport.backend.social.broker.handlers.profile.authz_in_web import (
    BindHandler,
    CallbackHandler,
    ContinueHandler,
    StartHandler,
)
from passport.backend.social.broker.statbox import MASK_TASK_ID
from passport.backend.social.broker.test import (
    FakeBuildRequestId,
    FakeGenerateTaskId,
    FakeStatboxLogger,
)
from passport.backend.social.broker.tests.base import (
    check_final_response,
    get_callback_request,
    get_start_request,
    TimeNow,
)
from passport.backend.social.broker.tests.base_broker_test_data import (
    TEST_CONSUMER,
    TEST_FRONTEND_URL,
    TEST_PROFILE_ID,
    TEST_REQUEST_ID,
    TEST_RETPATH,
    TEST_TASK_ID,
    TEST_UID,
    TEST_USER_IP,
    TEST_YANDEX_UID,
)
from passport.backend.social.common.grants import GrantsConfig
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    AUTHORIZATION_CODE1,
    CALLBACK_URL1,
    CONSUMER1,
    CONSUMER_IP1,
)
from passport.backend.social.common.test.fake_passport import FakePassport
from passport.backend.social.common.test.fake_redis_client import (
    FakeRedisClient,
    RedisPatch,
    reset_fake_redis,
)
from passport.backend.social.common.test.fake_useragent import FakeUseragent
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import FakeResponse
from passport.backend.social.common.useragent import build_http_pool_manager


class TestCommunicator(TestCase):
    def setUp(self):
        super(TestCommunicator, self).setUp()

        self.create_profile_mock = Mock(return_value=TEST_PROFILE_ID)
        self.get_profile_mock = Mock()
        self._fake_blackbox = FakeBlackbox()

        fake_generate_task_id = FakeGenerateTaskId()
        fake_generate_task_id.set_retval(TEST_TASK_ID)

        self._fake_grants_config = FakeGrantsConfig()
        self._fake_grants_config.add_consumer(
            consumer=CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['authz-in-web', 'authz-in-web-bind'],
        )

        self._fake_statbox = FakeStatboxLogger()

        self._fake_redis = FakeRedisClient()
        redis_patch = RedisPatch(self._fake_redis)

        self._fake_useragent = FakeUseragent()

        self._fake_passport = FakePassport()
        self._fake_passport.set_response_value(
            'send_account_modification_notifications',
            passport_ok_response(),
        )

        self.__patches = [
            patch('passport.backend.social.broker.binding.create_profile', self.create_profile_mock),
            patch('passport.backend.social.broker.handlers.profile.base.get_profile', self.get_profile_mock),
            self._fake_statbox,
            patch('passport.backend.social.broker.handlers.base.Communicator._get_real_token_data', Mock(side_effect=self._get_real_token_data)),
            fake_generate_task_id,
            FakeBuildRequestId(),
            self._fake_blackbox,
            self._fake_grants_config,
            redis_patch,
            self._fake_useragent,
            self._fake_passport,
        ]
        for p in self.__patches:
            p.start()

        self._fake_blackbox.set_response_side_effect(
            'sessionid',
            [blackbox_sessionid_response(uid=TEST_UID, display_name={'name': 'Petr'}) for _ in range(5)],
        )

        LazyLoader.register('slave_db_engine', self._fake_db.get_engine)
        LazyLoader.register('master_db_engine', self._fake_db.get_engine)
        LazyLoader.register('redis', lambda: self._fake_redis)

        grants_config = GrantsConfig('social-broker', Mock(name='tvm_credentials_manager'))
        LazyLoader.register('grants_config', lambda: grants_config)

        LazyLoader.register('http_pool_manager', lambda: build_http_pool_manager())

        communicator_application_mapper = CommunicatorApplicationMapper()
        LazyLoader.register('communicator_application_mapper', lambda: communicator_application_mapper)

        providers.init()

    def tearDown(self):
        LazyLoader.flush()
        reset_fake_redis()
        for p in reversed(self.__patches):
            p.stop()
        super(TestCommunicator, self).tearDown()

    def build_settings(self):
        settings = super(TestCommunicator, self).build_settings()
        settings['social_config'].update(
            dict(
                passport_api_consumer='socialism',
                passport_api_retries=1,
                passport_api_timeout=1,
                passport_api_url='https://passport-internal.yandex.ru',
            ),
        )
        return settings

    @staticmethod
    def get_application(provider_code):
        return providers.get_application_for_provider(provider_code, tld='ru')

    def _get_real_token_data(self, token_dict, *args, **kwargs):
        return token_dict

    @property
    def communicator(self):
        return Communicator.create(self.get_application(self.provider_code))

    @property
    def auth_url(self):
        return self.communicator.OAUTH_AUTHORIZE_URL

    def check_basic(self):
        self.check_ok()
        self.check_with_auth_redirect_to_bind()
        self.check_with_auth_bound()
        self.check_access_request_parsing_ok()
        self.check_access_request_parsing_error()
        self.check_access_request_parsing_invalid_data()
        self.check_authorization_request_user_denied()

    def get_statbox_start_data(self, provider_code, application_name=None,
                               retry_mode=False, require_auth=False,
                               session_id=False):

        provider = providers.get_provider_info_by_name(provider_code)['name']

        statbox_data = {
            'session_id_passed': '1' if session_id else '0',
            'token_passed': '0',
            'ip': TEST_USER_IP,
            'yandexuid': TEST_YANDEX_UID,
            'scope': '',
        }

        if retry_mode:
            statbox_data['action'] = 'restarted'
        else:
            statbox_data.update({
                'retpath': TEST_RETPATH,
                'require_auth': '1' if require_auth else '0',
                'action': 'started',
                'provider': provider,
                'place': 'query',
                'consumer': TEST_CONSUMER,
            })
            if application_name:
                statbox_data['application'] = application_name
            else:
                application = providers.get_application_for_provider(provider_code, 'ru')
                statbox_data['application'] = application.name
        return statbox_data

    def get_statbox_callbacked_data(self, status='ok'):
        statbox_data = {
            'status': status,
            'action': 'callbacked',
        }
        return statbox_data

    def get_statbox_saved_data(self):
        statbox_data = {
            'action': 'saved',
            'userid': '100',
            'elapsed_seconds': TimeSpan(0),
        }
        return statbox_data

    def get_statbox_bind_status_data(self, requested, auth_source='session_id'):
        statbox_data = {
            'action': 'bind_status',
            'uid': str(TEST_UID),
            'requested': '1' if requested else '0',
        }
        if auth_source:
            statbox_data['auth_source'] = auth_source
        return statbox_data

    def get_statbox_bound_data(self):
        statbox_data = {
            'action': 'bound',
            'uid': str(TEST_UID),
            'profile_id': str(TEST_PROFILE_ID),
            'profile_created': '0',
        }
        return statbox_data

    def assert_statbox_line(self, expected_data, index=-1):
        expected_data.update({
            'tskv_format': 'social-broker-log',
            'unixtime': TimeNow(convert_from_string=True),
            'task_id': MASK_TASK_ID,
            'request_id': TEST_REQUEST_ID,
        })
        self._fake_statbox.assert_contains([expected_data])

    def check_ok(self):
        reset_fake_redis()
        data = start_tst_ok(self.provider_code, self.auth_url)
        self.assert_statbox_line(self.get_statbox_start_data(self.provider_code))

        request = get_callback_request(data['task_id'], code=self.code, track=data['cookies'][0])
        handler = CallbackHandler(request)
        task_id = data['task_id']
        result = handler.get(task_id)
        self.assert_statbox_line(self.get_statbox_callbacked_data())

        request_continue = get_callback_request(task_id, track=json.loads(result.data)['cookies'][0])
        handler_continue = ContinueHandler(request_continue)
        self._fake_useragent.reset()
        self._fake_useragent.set_response_value(
            FakeResponse(
                self.normal_access_token_response,
                200,
            ),
        )
        result = handler_continue.get(data['task_id'])
        self.check_request_url(self._fake_useragent.requests[0], handler, data)
        self.assert_statbox_line(self.get_statbox_saved_data())

        eq_(self.get_profile_mock.call_count, 0)
        eq_(self.create_profile_mock.call_count, 0)

        check_final_response(result, handler_continue.task)

    def check_with_auth_redirect_to_bind(self):
        reset_fake_redis()
        self.get_profile_mock.reset_mock()
        self.create_profile_mock.reset_mock()
        self.get_profile_mock.return_value = None

        data = start_tst_ok(self.provider_code, self.auth_url, with_session_id=True, require_auth=True)
        self.assert_statbox_line(self.get_statbox_start_data(
            self.provider_code,
            require_auth=True,
            session_id=True,
        ))

        request = get_callback_request(
            data['task_id'],
            code=self.code,
            track=data['cookies'][0],
            with_session_id=True,
        )
        handler = CallbackHandler(request)
        task_id = data['task_id']
        result = handler.get(task_id)

        request_continue = get_callback_request(
            task_id,
            track=json.loads(result.data)['cookies'][0],
            with_session_id=True,
        )
        handler_continue = ContinueHandler(request_continue)
        self._fake_useragent.reset()
        self._fake_useragent.set_response_value(
            FakeResponse(
                self.normal_access_token_response,
                200,
            ),
        )
        result = handler_continue.get(data['task_id'])
        self.check_request_url(self._fake_useragent.requests[0], handler, data)
        self.assert_statbox_line(self.get_statbox_saved_data(), index=-2)
        self.assert_statbox_line(self.get_statbox_bind_status_data(True))

        eq_(self.get_profile_mock.call_count, 1)
        eq_(self.create_profile_mock.call_count, 0)

        data = json.loads(result.data)

        eq_(
            data['profile'],
            dict(
                name=u'Petr Testov',
                userid='100',
                username='luigi',
            ),
        )
        eq_(data['display_name'], {u'name': u'Petr', u'display_name_empty': False})
        ok_(data['bind_url'].startswith(TEST_FRONTEND_URL), data['bind_url'])
        ok_(data['cancel_url'].startswith(TEST_RETPATH), data['bind_url'])
        ok_('status=error' in data['cancel_url'])
        eq_(data['state'], 'bind')
        eq_(data['provider']['code'], self.provider_code)

        session = handler_continue.task.dump_session_data()
        session = json.loads(session)
        eq_(session['tid'], task_id)
        for key in ['code', 'ts', 'args']:
            ok_(key in session)

        eq_(session['state'], 'r_to_bind')

        # bind
        self.get_profile_mock.reset_mock()
        self.create_profile_mock.reset_mock()
        request_bind = get_callback_request(task_id, allow_bind=True,
                                            track=data['cookies'][0], with_session_id=True)
        handler_bind = BindHandler(request_bind)
        result = handler_bind.get(task_id)
        check_final_response(result, handler_bind.task)

        eq_(self.get_profile_mock.call_count, 0)
        eq_(self.create_profile_mock.call_count, 1)

    def check_with_auth_bound(self):
        reset_fake_redis()
        self.get_profile_mock.reset_mock()
        self.create_profile_mock.reset_mock()
        self.get_profile_mock.return_value = Mock()

        data = start_tst_ok(self.provider_code, self.auth_url, with_session_id=True, require_auth=True)
        self.assert_statbox_line(self.get_statbox_start_data(
            self.provider_code,
            session_id=True,
            require_auth=True,
        ))

        request = get_callback_request(
            data['task_id'],
            code=self.code,
            track=data['cookies'][0],
            with_session_id=True,
        )
        handler = CallbackHandler(request)
        task_id = data['task_id']
        result = handler.get(task_id)

        request_continue = get_callback_request(
            task_id,
            track=json.loads(result.data)['cookies'][0],
            with_session_id=True,
        )
        handler_continue = ContinueHandler(request_continue)
        self._fake_useragent.reset()
        self._fake_useragent.set_response_value(
            FakeResponse(
                self.normal_access_token_response,
                200,
            ),
        )
        result = handler_continue.get(data['task_id'])
        self.check_request_url(self._fake_useragent.requests[0], handler, data)
        self.assert_statbox_line(self.get_statbox_saved_data(), index=-3)
        self.assert_statbox_line(self.get_statbox_bind_status_data(False), index=-2)
        self.assert_statbox_line(self.get_statbox_bound_data())

        eq_(self.get_profile_mock.call_count, 1)
        eq_(self.create_profile_mock.call_count, 1)

        check_final_response(result, handler_continue.task)

    def check_access_request_parsing_ok(self):
        self._fake_useragent.set_response_value(
            FakeResponse(
                self.normal_access_token_response,
                200,
            ),
        )
        token = self.communicator.get_access_token(
            AUTHORIZATION_CODE1,
            CALLBACK_URL1,
            scopes=None,
            request_token=APPLICATION_TOKEN1,
        )
        eq_(token['value'], self.access_token)
        if hasattr(self, 'refresh_token'):
            eq_(token['refresh'], self.refresh_token)

    def check_access_request_parsing_error(self):
        self._fake_useragent.set_response_value(
            FakeResponse(
                self.error_access_token_response[1],
                self.error_access_token_response[0],
            ),
        )
        with self.assertRaises(CommunicationFailedError):
            self.communicator.get_access_token(
                AUTHORIZATION_CODE1,
                CALLBACK_URL1,
                scopes=None,
                request_token=APPLICATION_TOKEN1,
            )

    def check_access_request_parsing_invalid_data(self):
        self._fake_useragent.set_response_value(
            FakeResponse('qwerty', 200),
        )
        with self.assertRaises(CommunicationFailedError):
            self.communicator.get_access_token(
                AUTHORIZATION_CODE1,
                CALLBACK_URL1,
                scopes=None,
                request_token=APPLICATION_TOKEN1,
            )

    def check_authorization_request_user_denied(self):
        with self.assertRaises(UserDeniedError):
            self.communicator.has_error_in_callback(self.user_denied_response)


def start_tst_ok(provider, redirect_url, require_auth=False, with_session_id=False):
    request = get_start_request(provider, require_auth=require_auth, with_session_id=with_session_id)
    handler = StartHandler(request)
    result = handler.get()
    assert result.status_code == 200
    assert result.headers['Content-Type'] == u'application/json'
    data = json.loads(result.data)
    assert data['location'].startswith(redirect_url)
    assert data['provider']['code'] == provider
    return data


def start_tst_raises(provider, scheme, exception):
    request = get_start_request(provider, scheme)
    handler = StartHandler(request)
    with raises(exception):
        handler.get()
