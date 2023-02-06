# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta
import json

from furl import furl
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_response,
)
from passport.backend.core.builders.passport.faker import passport_ok_response
from passport.backend.core.test.consts import TEST_DISPLAY_NAME1
from passport.backend.core.test.test_utils.utils import (
    check_url_contains_params,
    check_url_equals,
)
from passport.backend.social.broker.communicators.GoogleCommunicator import GoogleCommunicator
from passport.backend.social.broker.cookies import build_json_secure_cookie
from passport.backend.social.broker.handlers.profile.task_state import PROFILE_R_TO_SOC
from passport.backend.social.broker.test import InternalBrokerHandlerV1TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import PLACE_QUERY
from passport.backend.social.common.profile import ProfileCreator
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Facebook import Facebook
from passport.backend.social.common.providers.Google import Google
from passport.backend.social.common.providers.MailRu import MailRu
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.task import (
    build_provider_for_task,
    load_task_from_redis,
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    AUTHORIZATION_CODE1,
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    FACEBOOK_APPLICATION_ID1,
    FACEBOOK_APPLICATION_NAME1,
    FRONTEND_URL1,
    GOOGLE_APPLICATION_NAME1,
    MAIL_RU_APPLICATION_NAME2,
    REQUEST_ID1,
    RETPATH1,
    SIMPLE_USERID1,
    TASK_ID1,
    TASK_TTL1,
    UID1,
    UNIXTIME1,
    USER_IP1,
    USERNAME1,
    VKONTAKTE_APPLICATION_ID1,
    VKONTAKTE_APPLICATION_NAME1,
    YANDEX_APPLICATION_ID1,
    YANDEX_APPLICATION_NAME1,
)
from passport.backend.social.common.test.fake_passport import FakePassport
from passport.backend.social.common.test.types import (
    ApproximateFloat,
    FakeResponse,
)
from passport.backend.social.proxylib.test import (
    vkontakte as vkontakte_test,
    yandex as yandex_test,
)
from passport.backend.utils.string import smart_unicode


def build_continue_session(
    application=None,
    consumer=CONSUMER1,
    created=1.0,
    exchange=AUTHORIZATION_CODE1,
    place=PLACE_QUERY,
    provider=None,
    retpath=RETPATH1,
    state='r_to_cont',
    task_id=TASK_ID1,
):
    """
    Строит сессию, с которой можно прийти в continue
    """
    if application is None:
        application = Application(identifier=YANDEX_APPLICATION_ID1, name=YANDEX_APPLICATION_NAME1)
    if provider is None:
        provider = providers.get_provider_info_by_id(Yandex.id)

    task = Task()

    task.application = application
    task.consumer = consumer
    task.created = created
    task.exchange = exchange
    task.place = place
    task.provider = provider
    task.retpath = retpath

    task.start_args = {
        'consumer': consumer,
        'retpath': retpath,
        'application': application.name,
    }
    if provider is not None:
        task.start_args.update(provider=provider['code'])

    task.state = state
    task.task_id = task_id

    return task


def build_bind_session():
    """
    Строит сессию, с которой можно прийти в bind
    """
    task = build_continue_session()
    task.in_redis = True
    task.state = 'r_to_bind'
    task.uid = UID1
    task.yandexuid = ''
    return task


def build_vkontakte_task():
    task = Task()

    task.access_token = dict(
        application=None,
        expires=None,
        scope='offline',
        secret=None,
        token_id=None,
        value=APPLICATION_TOKEN1,
    )

    task.application = Application(identifier=VKONTAKTE_APPLICATION_ID1, name=VKONTAKTE_APPLICATION_NAME1)
    task.consumer = CONSUMER1
    task.created = 1.0
    task.finished = ApproximateFloat(now.f())
    task.in_redis = True
    task.profile = vkontakte_test.SocialUserinfo.default().as_dict()
    task.provider = providers.get_provider_info_by_id(Vkontakte.id)
    task.task_id = TASK_ID1

    return task


def build_yandex_task():
    task = build_vkontakte_task()
    task.access_token.update(
        client_id=EXTERNAL_APPLICATION_ID1,
        scope='login:info,login:email',
    )
    task.application = Application(identifier=YANDEX_APPLICATION_ID1, name=YANDEX_APPLICATION_NAME1)
    task.profile = yandex_test.SocialUserinfo.default().as_dict()
    task.provider = providers.get_provider_info_by_id(Yandex.id)
    return task


def build_task_cookie(task, expired_at=None):
    _now = now()
    expired_at = expired_at or (_now + timedelta(seconds=TASK_TTL1))
    expires_in = (expired_at - _now).total_seconds()

    task_json = task.dump_session_data()
    task_cookie = build_json_secure_cookie(value=task_json, expires_in=expires_in)

    return task_cookie


class ContinueTestCase(InternalBrokerHandlerV1TestCase):
    def setUp(self):
        super(ContinueTestCase, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

        self._setup_get_token()
        self._setup_proxy()

    def _setup_get_token(self):
        pass

    def _setup_proxy(self):
        pass

    def _build_task_cookie(self, session_kwargs=dict(), expired_at=None):
        return build_task_cookie(self._build_session(**session_kwargs), expired_at)

    def _build_session(
        self,
        in_redis=None,
        provider=None,
        yandexuid=None,
        **kwargs
    ):
        task = build_continue_session(**kwargs)

        task.in_redis = in_redis
        task.provider = provider

        task.start_args.pop('provider', None)
        if provider is not None:
            task.start_args.update(provider=provider['code'])

        task.yandexuid = yandexuid

        return task

    def _build_bind_session(self):
        return build_bind_session()

    def _assert_continue_ok_response(self, rv, session=None):
        self._assert_ok_response(rv, skip=['cookies', 'location'])
        self._assert_response_forwards_to_url(rv, self._build_ok_retpath(RETPATH1, TASK_ID1))

        if session is None:
            session = self._build_session(
                yandexuid='',
                in_redis=True,
            )
        self._assert_response_contains_session(rv, session)

    def _assert_continue_send_to_bind_response(self, rv):
        self._assert_ok_response(
            rv,
            response=dict(
                state='bind',
                display_name=dict(
                    display_name_empty=False,
                    name=smart_unicode(TEST_DISPLAY_NAME1['name']),
                ),
                profile=dict(
                    name='Иван Иванов',
                    userid=SIMPLE_USERID1,
                    username='ivanivanov',
                ),
                provider=build_provider_for_task(code=Vkontakte.code, name='vkontakte', id=Vkontakte.id),
            ),
            skip=[
                'bind_url',
                'cancel_url',
                'cookies',
            ],
        )

        self._assert_response_contains_session(rv, self._build_bind_session())

        response_dict = json.loads(rv.data)

        check_url_equals(response_dict.get('bind_url'), self._build_bind_url())
        check_url_equals(response_dict.get('cancel_url'), self._build_fail_retpath(RETPATH1))

    def _build_bind_url(self):
        return FRONTEND_URL1 + '/' + TASK_ID1 + '/bind'


class TestContinue(ContinueTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/continue' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        self._fake_yandex_proxy = yandex_test.FakeProxy().start()
        super(TestContinue, self).setUp()
        self._setup_blackbox()

    def _get_default_request_data(self):
        return {
            'track': self._build_task_cookie(),
            'frontend_url': FRONTEND_URL1,
            'user_ip': USER_IP1,
        }

    def _setup_get_token(self):
        response = json.dumps(
            dict(
                access_token=APPLICATION_TOKEN1,
                token_type='Bearer',
            ),
        )
        self._fake_useragent.set_response_value(
            FakeResponse(
                value=response,
                status_code=200,
            ),
        )

    def _setup_proxy(self):
        self._fake_yandex_proxy.set_response_value(
            'get_profile',
            yandex_test.YandexApi.get_profile(),
        )

    def _setup_blackbox(self):
        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(
                    scope='login:info login:email',
                    oauth_token_info={'client_id': EXTERNAL_APPLICATION_ID1},
                    client_id=EXTERNAL_APPLICATION_ID1,
                ),
            ],
        )

    def _build_task(self, finished=None):
        task = build_yandex_task()
        if finished is not None:
            task.finished = finished
        task.provider = None
        return task

    def build_settings(self):
        settings = super(TestContinue, self).build_settings()
        settings['social_config'].update(
            dict(
                yandex_oauth_token_url='https://oauth.yandex.ru/token?',
                yandex_get_profile_url='https://login.yandex.ru/info',
                yandex_avatar_url_template='https://avatars.mds.yandex.net/get-yapic/%s/',
            ),
        )
        return settings

    def test_ok(self):
        rv = self._make_request()

        self._assert_continue_ok_response(rv)
        self._assert_task_equals(TASK_ID1, self._build_task())

    def test_retry(self):
        save_task_to_redis(
            self._fake_redis,
            TASK_ID1,
            self._build_task(finished=UNIXTIME1),
        )

        rv = self._make_request(
            data=dict(
                track=self._build_task_cookie(
                    session_kwargs=dict(in_redis=True),
                ),
            ),
        )

        self._assert_continue_ok_response(rv)

        # Не пойдём менять одноразовый авторизационный код на токен, потому
        # что обменяли его в прошлый раз и сохранили в Редисе
        self.assertEqual(self._fake_useragent.requests, list())


class TestContinueRequireAuth(ContinueTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/continue' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        self._fake_vkontakte_proxy = vkontakte_test.FakeProxy().start()
        super(TestContinueRequireAuth, self).setUp()
        self._setup_blackbox()

    def _get_default_request_data(self):
        return {
            'track': self._build_task_cookie(),
            'frontend_url': FRONTEND_URL1,
            'user_ip': USER_IP1,
            'Session_id': 'sessionid',
        }

    def _setup_get_token(self):
        response = json.dumps(
            dict(
                access_token=APPLICATION_TOKEN1,
                token_type='Bearer',
            ),
        )
        self._fake_useragent.set_response_value(
            FakeResponse(
                value=response,
                status_code=200,
            ),
        )

    def _setup_proxy(self):
        self._fake_vkontakte_proxy.set_response_value(
            'account.getAppPermissions',
            vkontakte_test.VkontakteApi.account_get_app_permissions(65536),
        )
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get(),
        )

    def _setup_blackbox(self):
        self._fake_blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_response(
                    display_name=TEST_DISPLAY_NAME1,
                    uid=UID1,
                ),
            ],
        )

    DEFAULT_SESSION_APPLICATION = Application(identifier=VKONTAKTE_APPLICATION_ID1, name=VKONTAKTE_APPLICATION_NAME1)

    def _build_task(self):
        task = build_vkontakte_task()
        task.uid = UID1
        return task

    def _build_session(self):
        task = build_continue_session()
        task.application = self.DEFAULT_SESSION_APPLICATION
        task.provider = providers.get_provider_info_by_id(Vkontakte.id)
        task.start_args.update(
            application=self.DEFAULT_SESSION_APPLICATION.name,
            provider=Vkontakte.code,
            require_auth='1',
        )
        return task

    def _build_bind_session(self):
        task = build_bind_session()
        task.application = self.DEFAULT_SESSION_APPLICATION
        task.provider = providers.get_provider_info_by_id(Vkontakte.id)
        task.start_args.update(
            application=self.DEFAULT_SESSION_APPLICATION.name,
            provider=Vkontakte.code,
            require_auth='1',
        )
        return task

    def test(self):
        rv = self._make_request()

        self._assert_continue_send_to_bind_response(rv)
        self._assert_task_equals(TASK_ID1, self._build_task())


class TestBind(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/bind' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        super(TestBind, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web-bind'])
        self._setup_blackbox()
        save_task_to_redis(
            self._fake_redis,
            TASK_ID1,
            self._build_task(),
        )
        self._fake_passport = FakePassport()
        self._fake_passport.set_response_value(
            'send_account_modification_notifications',
            passport_ok_response(),
        )
        self._fake_passport.start()

    def tearDown(self):
        self._fake_passport.stop()
        super(TestBind, self).tearDown()

    def _get_default_request_data(self):
        return {
            'allow': '1',
            'frontend_url': FRONTEND_URL1,
            'Session_id': 'sessionid',
            'track': build_task_cookie(self._build_session()),
            'user_ip': USER_IP1,
        }

    def _setup_blackbox(self):
        self._fake_blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_response(
                    display_name=TEST_DISPLAY_NAME1,
                    uid=UID1,
                ),
            ],
        )

    def _assert_bind_ok_response(self, rv):
        self._assert_ok_response(rv, skip=['cookies', 'location'])
        self._assert_response_forwards_to_url(rv, self._build_ok_retpath(RETPATH1, TASK_ID1))
        self._assert_response_contains_session(rv, self._build_session())

    def _build_session(self):
        task = build_bind_session()
        task.application = Application(identifier=VKONTAKTE_APPLICATION_ID1, name=VKONTAKTE_APPLICATION_NAME1)
        task.provider = providers.get_provider_info_by_id(Vkontakte.id)
        task.start_args.update(
            application=VKONTAKTE_APPLICATION_NAME1,
            provider=Vkontakte.code,
        )
        return task

    def _build_task(self):
        task = build_vkontakte_task()
        task.finished = UNIXTIME1
        task.uid = UID1
        return task

    def _assert_notification_sent(self, hostname, user_ip, uid, event_name):
        requests = self._fake_passport.get_requests_by_method('send_account_modification_notifications')
        assert len(requests) == 1
        request = requests[0]
        request.assert_post_data_equals(dict(
            event_name=event_name,
            mail_enabled='1',
            push_enabled='1',
            social_provider='vkontakte',
            uid=uid,
        ))
        request.assert_headers_contain({
            'Ya-Client-Host': hostname,
            'Ya-Consumer-Client-Ip': user_ip,
        })

    def build_settings(self):
        settings = super(TestBind, self).build_settings()
        settings['social_config'].update(
            dict(
                passport_api_consumer='socialism',
                passport_api_retries=1,
                passport_api_timeout=1,
                passport_api_url='https://passport-internal.yandex.ru',
            ),
        )
        return settings

    def find_profile(self):
        profile_creator = ProfileCreator(
            mysql_read=self._fake_db.get_engine(),
            mysql_write=self._fake_db.get_engine(),
            uid=UID1,
            social_userinfo=vkontakte_test.SocialUserinfo.default().as_dict(),
            token=None,
            timestamp=UNIXTIME1,
        )
        return profile_creator.find_profile()

    def test_ok(self):
        rv = self._make_request()

        self._assert_bind_ok_response(rv)
        self._assert_task_equals(TASK_ID1, self._build_task())

        self.assertTrue(self.find_profile())
        self._assert_notification_sent(
            hostname='social.yandex.ru',
            user_ip=USER_IP1,
            uid=UID1,
            event_name='social_add',
        )


class TestCallbackOnRtoCont(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/callback' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        super(TestCallbackOnRtoCont, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])
        save_task_to_redis(self._fake_redis, TASK_ID1, self._build_task())

    def _get_default_request_data(self):
        return {
            'frontend_url': FRONTEND_URL1,
            'track': build_task_cookie(self._build_session()),
            'user_ip': USER_IP1,
        }

    def _build_session(self):
        task = build_continue_session()
        task.application = Application(identifier=VKONTAKTE_APPLICATION_ID1, name=VKONTAKTE_APPLICATION_NAME1)
        task.in_redis = True
        task.provider = providers.get_provider_info_by_id(Vkontakte.id)
        task.start_args.update(
            application=VKONTAKTE_APPLICATION_NAME1,
            provider=Vkontakte.code,
        )
        return task

    def _build_task(self):
        task = build_vkontakte_task()
        task.finished = UNIXTIME1
        return task

    def build_continue_url(self):
        return FRONTEND_URL1 + '/' + TASK_ID1 + '/continue'

    def test(self):
        rv = self._make_request()

        self._assert_ok_response(
            rv,
            skip=['location'],
            response=dict(
                request_id=REQUEST_ID1,
                status='redirect',
                task_id=TASK_ID1,
            ),
        )
        self._assert_response_forwards_to_url(rv, self.build_continue_url())


class TestCallbackOnRtoBind(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/callback' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        super(TestCallbackOnRtoBind, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])
        save_task_to_redis(self._fake_redis, TASK_ID1, self._build_task())

    def _get_default_request_data(self):
        return {
            'frontend_url': FRONTEND_URL1,
            'track': build_task_cookie(self._build_session()),
            'user_ip': USER_IP1,
        }

    def _build_session(self):
        task = build_bind_session()
        task.application = Application(identifier=VKONTAKTE_APPLICATION_ID1, name=VKONTAKTE_APPLICATION_NAME1)
        task.provider = providers.get_provider_info_by_id(Vkontakte.id)
        task.start_args.update(
            application=VKONTAKTE_APPLICATION_NAME1,
            provider=Vkontakte.code,
        )
        return task

    def _build_task(self):
        task = build_vkontakte_task()
        task.finished = UNIXTIME1
        task.uid = UID1
        return task

    def build_bind_url(self):
        return FRONTEND_URL1 + '/' + TASK_ID1 + '/bind'

    def test(self):
        rv = self._make_request()

        self._assert_ok_response(
            rv,
            skip=['location'],
            response=dict(
                request_id=REQUEST_ID1,
                status='redirect',
                task_id=TASK_ID1,
            ),
        )
        self._assert_response_forwards_to_url(rv, self.build_bind_url())


class TestContinueGettingTaskForYandexNotCheckSlaveTokenScope(ContinueTestCase):
    # Чтобы получить таск с информацией о яндексовом аккаунте не нужно
    # проверять скоупы токена.
    # Не путать с созданием профиля между яндексовыми аккаунтами. Для создания
    # профиля скоупы токенов от обоих яндексовых аккаунтов нужно проверять.

    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/continue' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def _get_default_request_data(self):
        return {
            'track': self._build_task_cookie(),
            'frontend_url': FRONTEND_URL1,
            'user_ip': USER_IP1,
        }

    def _setup_get_token(self):
        response = json.dumps(
            dict(
                access_token=APPLICATION_TOKEN1,
                expires_in=APPLICATION_TOKEN_TTL1,
                token_type='Bearer',
            ),
        )
        self._fake_useragent.set_response_value(
            FakeResponse(
                value=response,
                status_code=200,
            ),
        )

    def _setup_proxy(self):
        self._fake_yandex_proxy.set_response_value(
            'get_profile',
            yandex_test.YandexApi.get_profile(),
        )

    def _setup_blackbox(self):
        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(
                    scope='login:info login:email',
                    oauth_token_info={'client_id': EXTERNAL_APPLICATION_ID1},
                ),
            ],
        )

    def build_settings(self):
        settings = super(TestContinueGettingTaskForYandexNotCheckSlaveTokenScope, self).build_settings()
        settings['social_config'].update(
            dict(
                yandex_oauth_token_url='https://oauth.yandex.ru/token?',
                yandex_get_profile_url='https://login.yandex.ru/info',
                yandex_avatar_url_template='https://avatars.mds.yandex.net/get-yapic/%s/',
            ),
        )
        return settings

    def setUp(self):
        self._fake_yandex_proxy = yandex_test.FakeProxy().start()
        super(TestContinueGettingTaskForYandexNotCheckSlaveTokenScope, self).setUp()

        self._setup_blackbox()

    def tearDown(self):
        super(TestContinueGettingTaskForYandexNotCheckSlaveTokenScope, self).tearDown()
        self._fake_yandex_proxy.stop()

    def test(self):
        rv = self._make_request()

        self._assert_continue_ok_response(rv)


class TestContinueFraud(ContinueTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/continue' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        self._fake_vkontakte_proxy = vkontakte_test.FakeProxy().start()
        super(TestContinueFraud, self).setUp()

    def tearDown(self):
        super(TestContinueFraud, self).tearDown()
        self._fake_vkontakte_proxy.stop()

    FRAUD_APPLICATION = Application(identifier=VKONTAKTE_APPLICATION_ID1, name=VKONTAKTE_APPLICATION_NAME1)

    def _get_default_request_data(self):
        return {
            'track': self._build_task_cookie(),
            'frontend_url': FRONTEND_URL1,
            'user_ip': USER_IP1,
        }

    def _build_session(self, **kwargs):
        defaults = dict(
            application=self.FRAUD_APPLICATION,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return super(TestContinueFraud, self)._build_session(**kwargs)

    def _setup_get_token(self):
        response = json.dumps(
            dict(
                access_token=APPLICATION_TOKEN1,
                token_type='Bearer',
            ),
        )
        self._fake_useragent.set_response_value(
            FakeResponse(
                value=response,
                status_code=200,
            ),
        )

    def _setup_proxy(self):
        self._fake_vkontakte_proxy.set_response_value(
            'account.getAppPermissions',
            vkontakte_test.VkontakteApi.account_get_app_permissions(65536),
        )

    def test_ok_firstname(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'first_name': 'Андрей',
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertEqual(task.profile['firstname'], 'Андрей')

    def test_too_long_firstname(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'first_name': 'Андрей' * 100,
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertNotIn('firstname', task.profile)

    def test_url_firstname(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'first_name': 'Поздравляем www.bit.ly/gold',
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertNotIn('firstname', task.profile)

    def test_ok_lastname(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'last_name': 'Исаев',
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertEqual(task.profile['lastname'], 'Исаев')

    def test_too_long_lastname(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'last_name': 'Исаев' * 100,
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertNotIn('last_name', task.profile)

    def test_url_lastname(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'last_name': 'Поздравляем www.bit.ly/gold',
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertNotIn('lastname', task.profile)

    def test_ok_username(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'domain': 'glug-glug',
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertEqual(task.profile['username'], 'glug-glug')

    def test_too_long_username(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'domain': 'glug-glug' * 100,
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertNotIn('username', task.profile)

    def test_url_username(self):
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'domain': 'Поздравляем www.bit.ly/gold',
            }),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertNotIn('username', task.profile)


class TestContinueNoUserid(ContinueTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/continue' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        self._fake_vkontakte_proxy = vkontakte_test.FakeProxy().start()
        super(TestContinueNoUserid, self).setUp()

    def tearDown(self):
        super(TestContinueNoUserid, self).tearDown()
        self._fake_vkontakte_proxy.stop()

    SESSION_APPLICATION = Application(identifier=VKONTAKTE_APPLICATION_ID1, name=VKONTAKTE_APPLICATION_NAME1)

    def _get_default_request_data(self):
        return {
            'track': self._build_task_cookie(),
            'frontend_url': FRONTEND_URL1,
            'user_ip': USER_IP1,
        }

    def _build_session(self, **kwargs):
        defaults = dict(
            application=self.SESSION_APPLICATION,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return super(TestContinueNoUserid, self)._build_session(**kwargs)

    def _setup_get_token(self):
        response = json.dumps(
            dict(
                access_token=APPLICATION_TOKEN1,
                token_type='Bearer',
            ),
        )
        self._fake_useragent.set_response_value(
            FakeResponse(
                value=response,
                status_code=200,
            ),
        )

    def _setup_proxy(self):
        self._fake_vkontakte_proxy.set_response_value(
            'account.getAppPermissions',
            vkontakte_test.VkontakteApi.account_get_app_permissions(65536),
        )

    def test(self):
        # На самом деле Вконтакте всегда возвращает userid, а здесь он
        # использован, потому что кого-то нужно было использовать.
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get(exclude_attrs={'id'}),
        )

        rv = self._make_request()

        self._assert_continue_ok_response(rv)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        self.assertNotIn('userid', task.profile)


class TestContinueSocialUserDisabled(ContinueTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/continue' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        self._fake_vkontakte_proxy = vkontakte_test.FakeProxy().start()
        super(TestContinueSocialUserDisabled, self).setUp()

    def tearDown(self):
        super(TestContinueSocialUserDisabled, self).tearDown()
        self._fake_vkontakte_proxy.stop()

    SESSION_APPLICATION = Application(identifier=VKONTAKTE_APPLICATION_ID1, name=VKONTAKTE_APPLICATION_NAME1)

    def _get_default_request_data(self):
        return {
            'track': self._build_task_cookie(),
            'frontend_url': FRONTEND_URL1,
            'user_ip': USER_IP1,
        }

    def _build_session(self, **kwargs):
        defaults = dict(
            application=self.SESSION_APPLICATION,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return super(TestContinueSocialUserDisabled, self)._build_session(**kwargs)

    def _setup_get_token(self):
        response = json.dumps(
            dict(
                access_token=APPLICATION_TOKEN1,
                token_type='Bearer',
            ),
        )
        self._fake_useragent.set_response_value(
            FakeResponse(
                value=response,
                status_code=200,
            ),
        )

    def _setup_proxy(self):
        self._fake_vkontakte_proxy.set_response_value(
            'account.getAppPermissions',
            vkontakte_test.VkontakteApi.account_get_app_permissions(65536),
        )
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.build_error(code=3610),
        )

    def test(self):
        rv = self._make_request()

        self._assert_error_response(
            rv,
            errors=['CommunicationFailedError'],
            retpath=RETPATH1,
            skip=[
                'cookies',
                'provider',
                'retry_url',
            ],
        )


class TestStartLoginHintProviderSupport(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = {
        'provider': MailRu.code,
        'application': MAIL_RU_APPLICATION_NAME2,
        'consumer': CONSUMER1,
        'retpath': RETPATH1,
        'login_hint': USERNAME1,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestStartLoginHintProviderSupport, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def test_with_login_hint(self):
        rv = self._make_request()

        self.assertEqual(rv.status_code, 200)

        redirect_url = self._get_redirect_url_from_response(rv)
        check_url_contains_params(redirect_url, {'login': USERNAME1})

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('login_hint'), USERNAME1)

    def test_no_login_hint(self):
        rv = self._make_request(exclude_query=['login_hint'])

        redirect_url = self._get_redirect_url_from_response(rv)
        redirect_url = furl(redirect_url)
        self.assertNotIn('login', redirect_url.args)

        session = self._get_session_from_response(rv)
        self.assertNotIn('login_hint', session.start_args)


class TestStartForcePromptProviderSupport(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = {
        'provider': Google.code,
        'application': GOOGLE_APPLICATION_NAME1,
        'consumer': CONSUMER1,
        'retpath': RETPATH1,
        'force_prompt': '1',
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestStartForcePromptProviderSupport, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def test_with_force_prompt(self):
        rv = self._make_request()

        self.assertEqual(rv.status_code, 200)

        redirect_url = self._get_redirect_url_from_response(rv)
        check_url_contains_params(redirect_url, {'prompt': 'consent'})

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('force_prompt'), '1')

    def test_no_force_prompt(self):
        rv = self._make_request(exclude_query=['force_prompt'])

        redirect_url = self._get_redirect_url_from_response(rv)
        redirect_url = furl(redirect_url)
        self.assertNotIn('prompt', redirect_url.args)

        session = self._get_session_from_response(rv)
        self.assertNotIn('force_prompt', session.start_args)


class TestStartPassthroughErrorsSupport(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = {
        'provider': Google.code,
        'application': GOOGLE_APPLICATION_NAME1,
        'consumer': CONSUMER1,
        'retpath': RETPATH1,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestStartPassthroughErrorsSupport, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def _build_retry_url(self):
        return '/'.join([FRONTEND_URL1, TASK_ID1, 'retry'])

    def test_with_passthrough_errors(self):
        rv = self._make_request(query=dict(passthrough_errors='UserDeniedError'))

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('passthrough_errors'), 'UserDeniedError')
        self.assertEqual(session.passthrough_errors, ['userdeniederror'])

    def test_with_many_passthrough_errors(self):
        rv = self._make_request(query=dict(passthrough_errors='Foo,Bar'))

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('passthrough_errors'), 'Foo,Bar')
        self.assertEqual(session.passthrough_errors, ['bar', 'foo'])

    def test_no_passthrough_errors(self):
        rv = self._make_request()

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertNotIn('passthrough_errors', session.start_args)
        self.assertEqual(session.passthrough_errors, list())

    def test_passthrough_authorization_required(self):
        rv = self._make_request(
            query=dict(
                passthrough_errors='AuthorizationRequiredError',
                require_auth='1',
            ),
        )

        self._assert_error_response(
            rv,
            errors=['AuthorizationRequiredError'],
            retpath=RETPATH1,
            retpath_kwargs=dict(
                additional_args={
                    'code': 'AuthorizationRequiredError',
                    'request_id': REQUEST_ID1,
                },
            ),
            response=dict(
                passthrough=True,
                retry_url=self._build_retry_url(),
            ),
            skip=['cookies', 'provider'],
        )


class TestRetryPassthroughErrorsSupport(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '%s/retry' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestRetryPassthroughErrorsSupport, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def _build_task_cookie(self, session_kwargs=dict()):
        task = self._build_session(**session_kwargs)
        task_json = task.dump_session_data()
        task_cookie = build_json_secure_cookie(value=task_json, expires_in=TASK_TTL1)
        return task_cookie

    def _build_session(self, passthrough_errors=None):
        task = Task()
        task.task_id = TASK_ID1
        task.created = 0
        task.state = PROFILE_R_TO_SOC
        task.start_args = dict(
            application=VKONTAKTE_APPLICATION_NAME1,
            consumer=CONSUMER2,
            retpath=RETPATH1,
        )

        if passthrough_errors:
            task.start_args.update(
                dict(
                    passthrough_errors=','.join(passthrough_errors),
                ),
            )
        task.passthrough_errors = passthrough_errors or list()

        return task

    def test_with_passthrough_errors(self):
        task_cookie = self._build_task_cookie(
            session_kwargs=dict(
                passthrough_errors=['userdeniederror'],
            ),
        )

        rv = self._make_request(data=dict(track=task_cookie))

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('passthrough_errors'), 'userdeniederror')
        self.assertEqual(session.passthrough_errors, ['userdeniederror'])


class TestCallbackPassthroughErrors(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/%s/callback' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = dict(
        frontend_url=FRONTEND_URL1,
        user_ip=USER_IP1,
    )

    def setUp(self):
        super(TestCallbackPassthroughErrors, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def _build_task_cookie(self, session_kwargs=dict()):
        task = self._build_session(**session_kwargs)
        task_json = task.dump_session_data()
        task_cookie = build_json_secure_cookie(value=task_json, expires_in=TASK_TTL1)
        return task_cookie

    def _build_session(self, passthrough_errors=None):
        task = Task()
        task.task_id = TASK_ID1
        task.created = 0
        task.state = PROFILE_R_TO_SOC
        task.start_args = dict(
            application=VKONTAKTE_APPLICATION_NAME1,
            consumer=CONSUMER2,
            retpath=RETPATH1,
        )

        if passthrough_errors:
            task.start_args.update(
                dict(
                    passthrough_errors=','.join(passthrough_errors),
                ),
            )
        task.passthrough_errors = passthrough_errors or list()

        return task

    def _build_retry_url(self):
        return '/'.join([FRONTEND_URL1, TASK_ID1, 'retry'])

    def test_with_passthrough_user_denied_error(self):
        task_cookie = self._build_task_cookie(
            session_kwargs=dict(
                passthrough_errors=['UserDeniedError'],
            ),
        )
        rv = self._make_request(query=dict(error='access_denied'), data=dict(track=task_cookie))

        self._assert_error_response(
            rv,
            errors=['UserDeniedError'],
            retpath=RETPATH1,
            retpath_kwargs=dict(
                additional_args={
                    'code': 'UserDeniedError',
                    'request_id': REQUEST_ID1,
                },
            ),
            response=dict(
                passthrough=True,
                retry_url=self._build_retry_url(),
            ),
            skip=['cookies', 'provider'],
        )

    def test_no_passthrough_user_denied_error(self):
        task_cookie = self._build_task_cookie()
        rv = self._make_request(query=dict(error='access_denied'), data=dict(track=task_cookie))

        self._assert_error_response(
            rv,
            errors=['UserDeniedError'],
            retpath=RETPATH1,
            response=dict(
                retry_url=self._build_retry_url(),
            ),
            skip=['cookies', 'provider'],
        )


class TestStartMordaRetpath(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = {
        'provider': Google.code,
        'application': GOOGLE_APPLICATION_NAME1,
        'consumer': CONSUMER1,
        'force_prompt': '1',
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestStartMordaRetpath, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def build_settings(self):
        settings = super(TestStartMordaRetpath, self).build_settings()
        settings['social_config'].update(
            dict(
                broker_retpath_grammars=[
                    """
                    domain = 'yandex.' yandex_tld | 'www.yandex.' yandex_tld
                    """,
                ],
            ),
        )
        return settings

    def test_yandex_ru(self):
        rv = self._make_request(query=dict(retpath='https://yandex.ru/'))

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('retpath'), 'https://yandex.ru/')
        self.assertEqual(session.retpath, 'https://yandex.ru/')

    def test_yandex_com(self):
        rv = self._make_request(query=dict(retpath='https://yandex.com/?foo=bar'))

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('retpath'), 'https://yandex.com/?foo=bar')
        self.assertEqual(session.retpath, 'https://yandex.com/?foo=bar&redirect=0')

    def test_www_yandex_com(self):
        rv = self._make_request(query=dict(retpath='https://www.yandex.com/'))

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('retpath'), 'https://www.yandex.com/')
        self.assertEqual(session.retpath, 'https://www.yandex.com/?redirect=0')

    def test_yandex_com_fail(self):
        rv = self._make_request(
            query=dict(
                retpath='https://yandex.com/',
                require_auth='1',
            ),
        )

        self.assertEqual(rv.status_code, 400)
        self._assert_error_response(
            rv,
            ['AuthorizationRequiredError'],
            retpath='https://yandex.com/?redirect=0',
            skip=[
                'cookies',
                'provider',
                'retry_url',
            ],
        )


class TestRetryMordaRetpath(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '%s/retry' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestRetryMordaRetpath, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def build_settings(self):
        settings = super(TestRetryMordaRetpath, self).build_settings()
        settings['social_config'].update(
            dict(
                broker_retpath_grammars=[
                    """
                    domain = 'yandex.' yandex_tld | 'www.yandex.' yandex_tld
                    """,
                ],
            ),
        )
        return settings

    def _build_task_cookie(self, session_kwargs=dict()):
        task = self._build_session(**session_kwargs)
        task_json = task.dump_session_data()
        task_cookie = build_json_secure_cookie(value=task_json, expires_in=TASK_TTL1)
        return task_cookie

    def _build_session(self, retpath):
        task = Task()
        task.task_id = TASK_ID1
        task.created = 0
        task.state = PROFILE_R_TO_SOC
        task.start_args = dict(
            application=VKONTAKTE_APPLICATION_NAME1,
            consumer=CONSUMER2,
            retpath=retpath,
        )
        task.retpath = retpath
        return task

    def test_yandex_com(self):
        task_cookie = self._build_task_cookie(
            session_kwargs=dict(
                retpath='https://yandex.com/?foo=bar',
            ),
        )

        rv = self._make_request(data=dict(track=task_cookie))

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('retpath'), 'https://yandex.com/?foo=bar')
        self.assertEqual(session.retpath, 'https://yandex.com/?foo=bar&redirect=0')


class TestStartFacebookToloka(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = {
        'application': EXTERNAL_APPLICATION_ID2,
        'consumer': CONSUMER1,
        'provider': Facebook.code,
        'retpath': RETPATH1,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestStartFacebookToloka, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def build_settings(self):
        settings = super(TestStartFacebookToloka, self).build_settings()
        settings['social_config'].update(
            dict(
                applications=[
                    {
                        'provider_id': Facebook.id,
                        'application_id': FACEBOOK_APPLICATION_ID1,
                        'application_name': FACEBOOK_APPLICATION_NAME1,
                        'provider_client_id': EXTERNAL_APPLICATION_ID1,
                        'secret': APPLICATION_SECRET1,
                    },
                ],
                general_facebook_client_id=EXTERNAL_APPLICATION_ID1,
                not_yandex_facebook_client_ids={EXTERNAL_APPLICATION_ID2: 'toloka'},
            ),
        )
        return settings

    def test(self):
        rv = self._make_request()

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.start_args.get('application'), EXTERNAL_APPLICATION_ID1)
        self.assertEqual(session.application.id, EXTERNAL_APPLICATION_ID1)


class TestStartCallbackUrlInTask(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = {
        'provider': Google.code,
        'application': GOOGLE_APPLICATION_NAME1,
        'consumer': CONSUMER1,
        'retpath': RETPATH1,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestStartCallbackUrlInTask, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def test_with_force_prompt(self):
        rv = self._make_request()

        self.assertEqual(rv.status_code, 200)

        task = load_task_from_redis(self._fake_redis, TASK_ID1)
        assert task.callback_url == '%s/%s/callback' % (FRONTEND_URL1, TASK_ID1)


class TestStartScopeInTask(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = {
        'provider': Google.code,
        'application': GOOGLE_APPLICATION_NAME1,
        'consumer': CONSUMER1,
        'retpath': RETPATH1,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
    }

    def setUp(self):
        super(TestStartScopeInTask, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web'])

    def test(self):
        rv = self._make_request(query=dict(scope='foo bar'))

        self.assertEqual(rv.status_code, 200)

        session = self._get_session_from_response(rv)
        self.assertEqual(session.scope, ' '.join(sorted(GoogleCommunicator.default_scopes + ['foo', 'bar'])))
