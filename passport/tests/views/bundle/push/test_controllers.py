# -*- coding: utf-8 -*-
import time

import mock
from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
from passport.backend.core.builders.blackbox import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_oauth_tokens_response,
    blackbox_oauth_response,
)
from passport.backend.core.builders.push_api import (
    PushApiForbiddenServiceError,
    PushApiInvalidCertError,
    PushApiInvalidTokenError,
)
from passport.backend.core.builders.push_api.faker import push_api_app_subscription_info
from passport.backend.core.builders.push_api.push_api import make_extra_data
from passport.backend.core.logbroker.exceptions import (
    ProtocolError,
    TransportError,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeSpan
from passport.backend.utils.common import noneless_dict
from passport.backend.utils.string import smart_bytes


eq_ = iterdiff(eq_)

TEST_AM_VERSION = '1.2.3'
TEST_APP_ID = 'ru.yandex.test_app'
TEST_APP_PLATFORM = 'iphone'
TEST_APP_VERSION = '6.8.9-megabuild %^!@$(!&@^!@'
TEST_CERT = 'razdva'
TEST_CLIENT = 'symbian'
TEST_DEVICE = 'old_school_device'
TEST_DEVICEID = '123-456-789'
TEST_DEVICE_TOKEN = 'poken-koken'
TEST_EVENT = 'event'
TEST_GENERATED_UUID = '0ff1ec09e904db3e2bd6178479c844e5'
TEST_HOST = 'localhost'
TEST_LOGIN = 'pasha'
TEST_LOGIN_ID = 'login-id'
TEST_OAUTH_TOKEN = '123'
TEST_TTL = 3600
TEST_USER = 'mr.kek'
TEST_USER_AGENT = 'test'
TEST_USER_IP = '1.2.3.4'
TEST_UID = 123
TEST_UUID = '12-34'
TEST_PUSH_SERVICE = 'some_service'
TEST_PUSH_TITLE = u'Это пуш'
TEST_PUSH_BODY = u'Очень классный интересный пуш, загляденье'
TEST_PUSH_SUBTITLE = u'Изумительно'
TEST_PUSH_WEBVIEW_URL = u'https://офигенно.рф'
TEST_CONTEXT = '{"TEST_CONTEXT": "TEST"}'


@with_settings_hosts(
    PUSH_API_RETRIES=1,
    PUSH_API_SERVICE_NAME='passport-push',
    PUSH_API_TIMEOUT=0.5,
    PUSH_API_URL='localhost',
)
class TestPushApiRegisterView(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/push/register/'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
    )
    http_method = 'POST'
    http_query_args = dict(
        app_id=TEST_APP_ID,
        app_platform=TEST_APP_PLATFORM,
        cert=TEST_CERT,
    )

    def setUp(self):
        super(TestPushApiRegisterView, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'push_api': ['register']}))

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestPushApiRegisterView, self).tearDown()

    def test_push_api_invalid_cert_error_fails(self):
        """Ошибка в сертификате при запросе Push API"""
        self.env.push_api.set_response_side_effect('register', PushApiInvalidCertError)
        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['push_api.cert_invalid'])

    def test_push_api_invalid_platform(self):
        """Ошибка в платформе при запросе Push API"""
        resp = self.make_request(query_args=dict(app_platform='non_existing_platform'))
        self.assert_error_response(resp, error_codes=['push_api.app_platform_unsupported'])

    def test_push_api_ok(self):
        self.env.push_api.set_response_value('register', 'OK')
        resp = self.make_request()
        self.assert_ok_response(resp)


@with_settings_hosts(
    PUSH_API_RETRIES=1,
    PUSH_API_SERVICE_NAME='passport-push',
    PUSH_API_TIMEOUT=0.5,
    PUSH_API_URL='localhost',
)
class TestPushApiSubscribeView(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/push/subscribe/'
    http_headers = dict(
        authorization='Oauth ' + TEST_OAUTH_TOKEN,
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
    )
    http_method = 'POST'
    http_query_args = dict(
        app_id=TEST_APP_ID,
        app_platform=TEST_APP_PLATFORM,
        client=TEST_CLIENT,
        device=TEST_DEVICE,
        deviceid=TEST_DEVICEID,
        device_token=TEST_DEVICE_TOKEN,
        uuid=TEST_UUID,
    )

    def setUp(self):
        super(TestPushApiSubscribeView, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'push_api': ['subscribe']}))
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_UID, login=TEST_LOGIN, scope=X_TOKEN_OAUTH_SCOPE, login_id=TEST_LOGIN_ID),
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestPushApiSubscribeView, self).tearDown()

    def test_push_api_invalid_token_error_fails(self):
        """Ошибка в токене при запросе Push API"""
        self.env.push_api.set_response_side_effect('subscribe', PushApiInvalidTokenError)
        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['push_api.token_invalid'])

    def test_push_api_forbidden_service_error_fails(self):
        """Ошибка в сервисе при запросе Push API"""
        self.env.push_api.set_response_side_effect('subscribe', PushApiForbiddenServiceError)
        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['push_api.service_forbidden'])

    def test_push_api_invalid_platform(self):
        """Ошибка в платформе при запросе Push API"""
        resp = self.make_request(query_args=dict(app_platform='non_existing_platform'))
        self.assert_error_response(resp, error_codes=['push_api.app_platform_unsupported'])

    def test_push_api_essentials_empty_1(self):
        """Ошибка в платформе при запросе Push API"""
        resp = self.make_request(query_args=dict(deviceid=None))
        self.assert_error_response(resp, error_codes=['deviceid.empty'])

    def test_push_api_essentials_empty_2(self):
        """Ошибка в платформе при запросе Push API"""
        resp = self.make_request(query_args=dict(app_id=None))
        self.assert_error_response(resp, error_codes=['app_id.empty'])

    def test_push_api_ok(self):
        self.env.push_api.set_response_value('subscribe', 'OK')
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.env.push_api.requests[0].assert_query_contains(dict(
            app_name=TEST_APP_ID,
            uuid=TEST_GENERATED_UUID,
        ))
        self.env.push_api.requests[0].assert_post_data_contains(dict(
            extra=make_extra_data(login_id=TEST_LOGIN_ID),
        ))

    @parameterized.expand([(p,) for p in ('Android 10 Super mega OS', 'android', 'Android', 'gcm', 'GCM 10')])
    def test_push_api__add_app_id_postfix__ok(self, platform):
        self.env.push_api.set_response_value('subscribe', 'OK')
        resp = self.make_request(query_args=dict(
            app_id=TEST_APP_ID,
            app_platform=platform,
        ))
        self.assert_ok_response(resp)
        self.env.push_api.requests[0].assert_query_contains(dict(
            app_name=TEST_APP_ID + '.passport',
            uuid=TEST_GENERATED_UUID,
        ))
        self.env.push_api.requests[0].assert_post_data_contains(dict(
            extra=make_extra_data(login_id=TEST_LOGIN_ID),
        ))

    @parameterized.expand([(p,) for p in ('Android 10 Super mega OS', 'android', 'Android', 'gcm', 'GCM 10')])
    def test_push_api__existing_app_id_postfix__ok(self, platform):
        self.env.push_api.set_response_value('subscribe', 'OK')
        resp = self.make_request(query_args=dict(
            app_id=TEST_APP_ID + '.1.passport',
            app_platform=platform,
        ))
        self.assert_ok_response(resp)
        self.env.push_api.requests[0].assert_query_contains(dict(
            app_name=TEST_APP_ID + '.1.passport',
            uuid='31891471220a24accb3eeddaca2aeb15',
        ))
        self.env.push_api.requests[0].assert_post_data_contains(dict(
            extra=make_extra_data(login_id=TEST_LOGIN_ID),
        ))

    def test_push_api_ok_with_am_version(self):
        self.env.push_api.set_response_value('subscribe', 'OK')
        query_args = dict(self.http_query_args)
        query_args.update(am_version=TEST_AM_VERSION)
        resp = self.make_request(query_args=query_args)
        self.assert_ok_response(resp)
        self.env.push_api.requests[0].assert_query_contains(dict(
            app_name=TEST_APP_ID,
            uuid=TEST_GENERATED_UUID,
        ))
        self.env.push_api.requests[0].assert_post_data_contains(dict(
            extra=make_extra_data(login_id=TEST_LOGIN_ID, am_version=TEST_AM_VERSION),
        ))

    def test_push_api_ok_with_app_version(self):
        self.env.push_api.set_response_value('subscribe', 'OK')
        query_args = dict(self.http_query_args)
        query_args.update(app_version=TEST_APP_VERSION)
        resp = self.make_request(query_args=query_args)
        self.assert_ok_response(resp)
        self.env.push_api.requests[0].assert_query_contains(dict(
            app_name=TEST_APP_ID,
            uuid=TEST_GENERATED_UUID,
        ))
        self.env.push_api.requests[0].assert_post_data_contains(dict(
            extra=make_extra_data(login_id=TEST_LOGIN_ID, app_version=TEST_APP_VERSION),
        ))


@with_settings_hosts(
    PUSH_API_RETRIES=1,
    PUSH_API_SERVICE_NAME='passport-push',
    PUSH_API_TIMEOUT=0.5,
    PUSH_API_URL='localhost',
)
class TestPushApiUnsubscribeView(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/push/unsubscribe/'
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
    )
    http_method = 'POST'
    http_query_args = dict(
        app_id=TEST_APP_ID,
        deviceid=TEST_DEVICEID,
        uid=TEST_UID,
    )

    def setUp(self):
        super(TestPushApiUnsubscribeView, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'push_api': ['subscribe']}))
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_UID, login=TEST_LOGIN, scope=X_TOKEN_OAUTH_SCOPE),
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestPushApiUnsubscribeView, self).tearDown()

    def test_push_api_invalid_token_error_fails(self):
        """Ошибка в токене при запросе Push API"""
        self.env.push_api.set_response_side_effect('unsubscribe', PushApiInvalidTokenError)
        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['push_api.token_invalid'])

    def test_push_api_forbidden_service_error_fails(self):
        """Ошибка в сервисе при запросе Push API"""
        self.env.push_api.set_response_side_effect('unsubscribe', PushApiForbiddenServiceError)
        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['push_api.service_forbidden'])

    def test_push_api_ok(self):
        self.env.push_api.set_response_value('unsubscribe', 'OK')
        resp = self.make_request()
        self.assert_ok_response(resp)


@with_settings_hosts(
    AM_CAPABILITIES_BY_VERSION_ANDROID={
        (1, 1, 0): {'push:passport_protocol'},
    },
)
class TestSendAMPushBundleView(BaseBundleTestViews):
    default_url = '/1/bundle/push/send/am/'
    http_method = 'POST'
    grants_mock = {'push_api': ['send']}
    consumer = 'dev'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(TestSendAMPushBundleView, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants=self.grants_mock))

        self._uuid_patch = mock.patch('uuid.uuid4', lambda: TEST_GENERATED_UUID)
        self._uuid_patch.start()

        self.bind_statbox_templates()

    def tearDown(self):
        self._uuid_patch.stop()
        self.env.stop()
        super(TestSendAMPushBundleView, self).tearDown()

    def setup_list_response(self, subscriptions):
        self.env.push_api.set_response_value('list', subscriptions)

    def setup_get_oauth_tokens_response(self, tokens):
        self.env.blackbox.set_blackbox_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response(tokens),
        )

    def bind_statbox_templates(self):
        self.env.statbox.bind_base(
            host=TEST_HOST,
            uid=str(TEST_UID),
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            consumer=self.consumer,
        )
        self.env.statbox.bind_entry(
            'send_am',
            mode='push_send_am',
            action='send',
            push_service=TEST_PUSH_SERVICE,
            event_name=TEST_EVENT,
        )

    def assert_statbox_ok(self, status='ok', check_subscriptions='no', require_trusted_device='no', **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'send_am',
                status=status,
                check_subscriptions=check_subscriptions,
                require_trusted_device=require_trusted_device,
                **kwargs
            ),
        ])

    def assert_statbox_not_written(self):
        self.env.statbox.assert_has_written([])

    def assert_push_api_called(self):
        r = self.env.push_api.get_requests_by_method('list')
        assert len(r) == 1
        r[0].assert_query_contains(dict(user=str(TEST_UID)))

    def assert_push_api_not_called(self):
        assert len(self.env.push_api.get_requests_by_method('list')) == 0

    def assert_push_sent(
        self, subtitle=None, body=None, webview_url=None, require_web_auth=False,
        require_trusted_device=False, context=None, expire_time=None,
    ):
        recipient = noneless_dict(
            uid=str(TEST_UID),
            app_targeting_type='ONE_APP_PER_DEVICE',
            required_am_capabilities=['push:passport_protocol'],
            context=context,
        )
        if require_trusted_device:
            recipient['require_trusted_device'] = True
        message = dict(
            push_service=TEST_PUSH_SERVICE,
            event_name=TEST_EVENT,
            recipients=[recipient],
            text_body=noneless_dict(
                title=smart_bytes(TEST_PUSH_TITLE),
                body=smart_bytes(body) if body else None,
                subtitle=smart_bytes(subtitle) if subtitle else None,
            ),
            push_id=TEST_GENERATED_UUID,
        )
        if webview_url:
            message['webview_body'] = noneless_dict(
                webview_url=smart_bytes(webview_url),
                require_web_auth=True if require_web_auth else None,
            )
        if expire_time:
            message['expire_time'] = expire_time
        self.env.lbw_challenge_pushes.assert_message_sent(
            dict(push_message_request=message),
        )

    def assert_push_not_sent(self):
        assert len(self.env.lbw_challenge_pushes.dict_requests) == 0

    def test__send_simple__ok(self):
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
            ),
        )
        self.assert_ok_response(rv)

        self.assert_push_api_not_called()
        assert len(self.env.blackbox.get_requests_by_method('get_oauth_tokens')) == 0
        self.assert_statbox_ok(status='ok')
        self.assert_push_sent()

    @parameterized.expand([
        (False,), (True,),
    ])
    def test__send_extended__ok(self, require_web_auth):
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
                body=TEST_PUSH_BODY,
                subtitle=TEST_PUSH_SUBTITLE,
                webview_url=TEST_PUSH_WEBVIEW_URL,
                require_web_auth=require_web_auth,
                require_trusted_device=True,
                context=TEST_CONTEXT,
                ttl=500,
            ),
        )
        self.assert_ok_response(rv)

        self.assert_push_api_not_called()
        assert len(self.env.blackbox.get_requests_by_method('get_oauth_tokens')) == 0
        self.assert_statbox_ok(
            status='ok',
            require_trusted_device='yes',
        )
        self.assert_push_sent(
            subtitle=TEST_PUSH_SUBTITLE,
            body=TEST_PUSH_BODY,
            webview_url=TEST_PUSH_WEBVIEW_URL,
            require_web_auth=require_web_auth,
            require_trusted_device=True,
            context=TEST_CONTEXT,
            expire_time=TimeSpan(time.time() + 500),
        )

    def test__check_subscriptions__no_subscriptions__not_sent(self):
        self.setup_list_response([])
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
                check_subscriptions=True,
            ),
        )
        self.assert_error_response(rv, ['push_api.no_subscriptions'])

        self.assert_push_api_called()
        assert len(self.env.blackbox.get_requests_by_method('get_oauth_tokens')) == 0
        self.assert_statbox_ok(status='error', error='no_subscriptions', check_subscriptions='yes')
        self.assert_push_not_sent()

    def test__check_subscriptions__no_compatible_subscriptions__not_sent(self):
        self.setup_list_response([
            push_api_app_subscription_info(
                id_='sub1', uuid='', app='test_app', platform='gcm',
            ),
            push_api_app_subscription_info(
                id_='sub2', uuid='', app='test_app', platform='gcm',
                extra=make_extra_data(am_version='1.0.0'),
            ),
        ])
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
                check_subscriptions=True,
            ),
        )
        self.assert_error_response(rv, ['push_api.no_subscriptions'])

        self.assert_push_api_called()
        assert len(self.env.blackbox.get_requests_by_method('get_oauth_tokens')) == 0
        self.assert_statbox_ok(status='error', error='no_subscriptions', check_subscriptions='yes')
        self.assert_push_not_sent()

    def test__check_subscriptions__got_compatible_subscriptions__ok(self):
        self.setup_list_response([
            push_api_app_subscription_info(
                id_='sub1', uuid='', app='test_app', platform='gcm',
            ),
            push_api_app_subscription_info(
                id_='sub2', uuid='', app='test_app', platform='gcm',
                extra=make_extra_data(am_version='1.1.0'),
            ),
        ])
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
                check_subscriptions=True,
            ),
        )
        self.assert_ok_response(rv)

        self.assert_push_api_called()
        assert len(self.env.blackbox.get_requests_by_method('get_oauth_tokens')) == 0
        self.assert_statbox_ok(status='ok', check_subscriptions='yes')
        self.assert_push_sent()

    def test__check_subscriptions__no_trusted_subscriptions__not_sent(self):
        self.setup_list_response([
            push_api_app_subscription_info(
                id_='sub1', uuid='', app='test_app', platform='gcm',
            ),
            push_api_app_subscription_info(
                id_='sub2', uuid='', app='test_app', platform='gcm',
                device='other_device', extra=make_extra_data(am_version='1.1.0'),
            ),
        ])
        self.setup_get_oauth_tokens_response([
            dict(device_id=TEST_DEVICEID, is_xtoken_trusted=True),
            dict(device_id='other_device'),
        ])
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
                check_subscriptions=True,
                require_trusted_device=True,
            ),
        )
        self.assert_error_response(rv, ['push_api.no_subscriptions'])

        assert len(self.env.blackbox.get_requests_by_method('get_oauth_tokens')) == 1
        self.assert_push_api_called()
        self.assert_statbox_ok(status='error', error='no_subscriptions', check_subscriptions='yes', require_trusted_device='yes')
        self.assert_push_not_sent()

    def test__check_subscriptions__got_trusted_subscriptions__ok(self):
        self.setup_list_response([
            push_api_app_subscription_info(
                id_='sub1', uuid='', app='test_app', platform='gcm',
            ),
            push_api_app_subscription_info(
                id_='sub2', uuid='', app='test_app', platform='gcm',
                device=TEST_DEVICEID, extra=make_extra_data(am_version='1.1.0'),
            ),
        ])
        self.setup_get_oauth_tokens_response([
            dict(device_id=TEST_DEVICEID, is_xtoken_trusted=True),
            dict(device_id='other_device'),
        ])
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
                check_subscriptions=True,
                require_trusted_device=True,
            ),
        )
        self.assert_ok_response(rv)

        self.assert_push_api_called()
        assert len(self.env.blackbox.get_requests_by_method('get_oauth_tokens')) == 1
        self.assert_statbox_ok(status='ok', check_subscriptions='yes', require_trusted_device='yes')
        self.assert_push_sent(require_trusted_device=True)

    def test__logbroker_temporary_failure__error(self):
        self.env.lbw_challenge_pushes.set_send_side_effect(TransportError)
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
            ),
        )
        self.assert_error_response(rv, ['backend.logbroker_failed'], 504)
        self.assert_statbox_not_written()

    def test__logbroker_permanent_failure__error(self):
        self.env.lbw_challenge_pushes.set_send_side_effect(ProtocolError)
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
            ),
        )
        self.assert_error_response(rv, ['exception.unhandled'], 500)
        self.assert_statbox_not_written()

    def test__blackbox_failure__error(self):
        self.env.blackbox.set_response_side_effect_without_method(BlackboxTemporaryError)
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT,
                title=TEST_PUSH_TITLE,
                check_subscriptions=True,
                require_trusted_device=True,
            ),
        )
        self.assert_error_response(rv, ['backend.blackbox_failed'], 504)
        self.assert_statbox_not_written()
