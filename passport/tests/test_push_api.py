# -*- coding: utf-8 -*-

import json

from nose_parameterized import parameterized
from passport.backend.core.builders.push_api import (
    PushApi,
    PushApiInvalidRequestError,
    PushApiInvalidResponseError,
    PushApiUnsupportedPlatformError,
)
from passport.backend.core.builders.push_api.faker import (
    FakePushApi,
    push_api_app_subscription_info,
)
from passport.backend.core.builders.push_api.push_api import (
    make_extra_data,
    Subscription,
    SubscriptionExtra,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
)


TEST_APP_NAME = 'ru.yandex.test_app'
TEST_CERT = 'razdva'
TEST_DEVICE_ID_1 = 'abcdef1245678a'
TEST_DEVICE_ID_2 = 'a98765abcdef'
TEST_DEVICE_TOKEN = '123'
TEST_EVENT = 'event'
TEST_PAYLOAD = dict(field1='field1')
TEST_PLATFORM_1 = 'apns'
TEST_PLATFORM_2 = 'apple'
TEST_PLATFORM_3 = 'Android 1.2.3'
TEST_TTL = '1'
TEST_TICKET = '1234567'
TEST_SERVICE_NAME = 'passport-push'
TEST_SUBSCRIPTION_ID_1 = 'mob:abcdef1234567890'
TEST_SUBSCRIPTION_ID_2 = 'mob:abc1234567890123def'
TEST_SUBSCRIPTION_ID_3 = 'mob:abavavavava'
TEST_USER = 'pasha'
TEST_UUID = '983'


class JsonMatcher(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return '<JsonMatcher {}>'.format(self.data)

    __repr__ = __str__

    def __eq__(self, other):
        return json.loads(other) == self.data


@with_settings(
    PUSH_API_URL='http://push_api',
    PUSH_API_RETRIES=2,
    PUSH_API_SERVICE_NAME=TEST_SERVICE_NAME,
    PUSH_API_TIMEOUT=1,
)
class TestPushApi(PassportTestCase):
    def setUp(self):
        self.fake_push_api = FakePushApi()
        self.fake_push_api.start()
        self.fake_tvm = FakeTvmCredentialsManager()
        self.fake_tvm.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'push_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm.start()

    def tearDown(self):
        self.fake_tvm.stop()
        self.fake_push_api.stop()

    def get_push_api(self):
        return PushApi()

    def assert_request_params(
        self, url_suffix, method='GET', query=None,
        headers=None, data=None, json_post=False,
    ):
        assert (not json_post) or (method == 'POST')

        self.assertEqual(len(self.fake_push_api.requests), 1)
        req = self.fake_push_api.requests[0]

        all_headers = {}
        if json_post:
            all_headers.update({'Content-Type': 'application/json'})
        if headers:
            all_headers.update(headers)
        if all_headers:
            req.assert_headers_contain(all_headers)
        req.assert_properties_equal(method=method)
        req.assert_url_starts_with('http://push_api/{}'.format(url_suffix))
        req.assert_query_equals(query or {})
        self.assertEqual(req.post_args, data)

    def test_invalid(self):
        self.fake_push_api.set_response_value_without_method(b'NOT OK')
        with self.assertRaises(PushApiInvalidRequestError):
            self.get_push_api().register(TEST_APP_NAME, TEST_CERT, TEST_PLATFORM_1)

    def test_register_ok(self):
        self.fake_push_api.set_response_value_without_method(b'OK')
        r = self.get_push_api().register(TEST_APP_NAME, TEST_CERT, TEST_PLATFORM_1)
        self.assertEqual(r, 'OK')
        self.assert_request_params(
            'v2/register/app/{}'.format(TEST_PLATFORM_1),
            method='POST',
            query=dict(app_name=TEST_APP_NAME, service=TEST_SERVICE_NAME),
            data=TEST_CERT.encode('utf8'),
        )

    def test_send_ok(self):
        self.fake_push_api.set_response_value_without_method(b'OK')
        r = self.get_push_api().send(TEST_EVENT, TEST_PAYLOAD, TEST_USER, TEST_TTL)
        self.assertEqual(r, 'OK')
        self.assert_request_params(
            'v2/send',
            method='POST',
            query=dict(
                event=TEST_EVENT,
                user=TEST_USER,
                ttl=TEST_TTL,
                service=TEST_SERVICE_NAME,
            ),
            headers={'X-DeliveryMode': 'queued'},
            json_post=True,
            data=json.dumps(TEST_PAYLOAD),
        )

    def test_send_sync__ok(self):
        self.fake_push_api.set_response_value_without_method(json.dumps([
            dict(code=200, id=1, body=dict(message_id='123')),
            dict(code=205, id=2, body=dict(message_id='456')),
            dict(code=500, id=3, body=dict(message_id='789')),
        ]))
        r = self.get_push_api().send(TEST_EVENT, TEST_PAYLOAD, TEST_USER, TEST_TTL, sync=True)
        self.assertEqual(r, {
            1: dict(code=200, id=1, body=dict(message_id='123')),
            2: dict(code=205, id=2, body=dict(message_id='456')),
            3: dict(code=500, id=3, body=dict(message_id='789')),
        })
        self.assert_request_params(
            'v2/send',
            method='POST',
            query=dict(
                event=TEST_EVENT,
                user=TEST_USER,
                ttl=TEST_TTL,
                service=TEST_SERVICE_NAME,
            ),
            headers={'X-DeliveryMode': 'direct'},
            json_post=True,
            data=json.dumps(TEST_PAYLOAD),
        )

    def test_send_sync__single_subscription__ok(self):
        self.fake_push_api.set_response_value_without_method(json.dumps(
            dict(code=205, id=1, body=dict(message_id='123')),
        ))
        r = self.get_push_api().send(TEST_EVENT, TEST_PAYLOAD, TEST_USER, TEST_TTL, sync=True)
        self.assertEqual(r, {
            1: dict(code=205, id=1, body=dict(message_id='123')),
        })
        self.assert_request_params(
            'v2/send',
            method='POST',
            query=dict(
                event=TEST_EVENT,
                user=TEST_USER,
                ttl=TEST_TTL,
                service=TEST_SERVICE_NAME,
            ),
            headers={'X-DeliveryMode': 'direct'},
            json_post=True,
            data=json.dumps(TEST_PAYLOAD),
        )

    @parameterized.expand([(202,), (204,), (205,)])
    def test_send_sync__no_subscriptions__ok(self, code):
        self.fake_push_api.set_response_value_without_method(json.dumps(dict(
            code=code,
            mesage='No subscriptions found',
        )))
        r = self.get_push_api().send(TEST_EVENT, TEST_PAYLOAD, TEST_USER, TEST_TTL, sync=True)
        self.assertEqual(r, {})
        self.assert_request_params(
            'v2/send',
            method='POST',
            query=dict(
                event=TEST_EVENT,
                user=TEST_USER,
                ttl=TEST_TTL,
                service=TEST_SERVICE_NAME,
            ),
            headers={'X-DeliveryMode': 'direct'},
            json_post=True,
            data=json.dumps(TEST_PAYLOAD),
        )

    def test_subscribe_ok(self):
        self.fake_push_api.set_response_value_without_method(b'OK')
        r = self.get_push_api().subscribe(
            app_name=TEST_APP_NAME,
            device_token=TEST_DEVICE_TOKEN,
            platform=TEST_PLATFORM_1,
            user=TEST_USER,
            uuid=TEST_UUID,
        )
        self.assertEqual(r, 'OK')
        self.assert_request_params(
            'v2/subscribe/app',
            method='POST',
            query=dict(
                app_name=TEST_APP_NAME,
                platform=TEST_PLATFORM_1,
                service=TEST_SERVICE_NAME,
                user=TEST_USER,
                uuid=TEST_UUID,
            ),
            data=dict(push_token=TEST_DEVICE_TOKEN),
        )

    def test_unsubscribe_ok(self):
        self.fake_push_api.set_response_value_without_method(b'OK')
        r = self.get_push_api().unsubscribe(TEST_USER, TEST_UUID)
        self.assertEqual(r, 'OK')
        self.assert_request_params(
            'v2/unsubscribe/app',
            method='POST',
            query=dict(
                service=TEST_SERVICE_NAME,
                user=TEST_USER,
                uuid=TEST_UUID,
            ),
        )

    def test_list_ok(self):
        info1 = push_api_app_subscription_info(
            id_=TEST_SUBSCRIPTION_ID_1,
            app=TEST_APP_NAME,
            uuid=TEST_UUID,
            platform=TEST_PLATFORM_1,
            device=TEST_DEVICE_ID_1,
            extra='12345',
        )
        info2 = push_api_app_subscription_info(
            id_=TEST_SUBSCRIPTION_ID_2,
            uuid=TEST_UUID,
            app=TEST_APP_NAME,
            platform=TEST_PLATFORM_1,
            device=TEST_DEVICE_ID_2,
            extra='[67890]',
        )
        info3 = push_api_app_subscription_info(
            id_=TEST_SUBSCRIPTION_ID_2,
            uuid=TEST_UUID,
            app=TEST_APP_NAME,
            platform=TEST_PLATFORM_1,
            device=TEST_DEVICE_ID_2,
            extra=make_extra_data(am_version='1.2.3'),
        )
        info4 = push_api_app_subscription_info(
            id_=TEST_SUBSCRIPTION_ID_3,
            uuid=TEST_UUID,
            app=TEST_APP_NAME,
            platform=TEST_PLATFORM_1,
            device=TEST_DEVICE_ID_2,
            extra=make_extra_data(am_version='1.2.3', login_id='123456', app_version='1.2.3-some-postfix'),
            client='client',
            session='session',
            filter='filter',
            init_time=456,
            last_sent=789,
        )
        self.fake_push_api.set_response_value('list', json.dumps([info1, info2, info3, info4]))

        r = self.get_push_api().list(TEST_USER)
        self.assertEqual(r, [
            Subscription(
                id=TEST_SUBSCRIPTION_ID_1,
                app=TEST_APP_NAME,
                uuid=TEST_UUID,
                platform=TEST_PLATFORM_1,
                device=TEST_DEVICE_ID_1,
                client='some_client',
                session='some_session',
                filter='',
                ttl=3600 * 24 * 30,
                init_time=None,
                last_sent=None,
                raw_extra='12345',
                extra=SubscriptionExtra(am_version=None, login_id=None, app_version=None),
            ),
            Subscription(
                id=TEST_SUBSCRIPTION_ID_2,
                uuid=TEST_UUID,
                app=TEST_APP_NAME,
                platform=TEST_PLATFORM_1,
                device=TEST_DEVICE_ID_2,
                client='some_client',
                session='some_session',
                filter='',
                ttl=3600 * 24 * 30,
                init_time=None,
                last_sent=None,
                raw_extra='[67890]',
                extra=SubscriptionExtra(am_version=None, login_id=None, app_version=None),
            ),
            Subscription(
                id=TEST_SUBSCRIPTION_ID_2,
                uuid=TEST_UUID,
                app=TEST_APP_NAME,
                platform=TEST_PLATFORM_1,
                device=TEST_DEVICE_ID_2,
                client='some_client',
                session='some_session',
                filter='',
                ttl=3600 * 24 * 30,
                init_time=None,
                last_sent=None,
                raw_extra=json.dumps({'0': '1.2.3'}),
                extra=SubscriptionExtra(am_version='1.2.3', login_id=None, app_version=None),
            ),
            Subscription(
                id=TEST_SUBSCRIPTION_ID_3,
                uuid=TEST_UUID,
                app=TEST_APP_NAME,
                platform=TEST_PLATFORM_1,
                device=TEST_DEVICE_ID_2,
                client='client',
                session='session',
                filter='filter',
                ttl=3600 * 24 * 30,
                init_time=456,
                last_sent=789,
                raw_extra=JsonMatcher({'0': '1.2.3', '1': '123456', '2': '1.2.3-some-postfix'}),
                extra=SubscriptionExtra(am_version='1.2.3', login_id='123456', app_version='1.2.3-some-postfix'),
            ),
        ])
        self.assert_request_params(
            url_suffix='v2/list',
            method='GET',
            query=dict(service=TEST_SERVICE_NAME, user=TEST_USER),
        )

    def test_list_http_error(self):
        self.fake_push_api.set_response_value('list', b'NOT OK', 500)
        with self.assertRaisesRegexp(
            PushApiInvalidResponseError,
            r'Request failed.+NOT OK.+500',
        ):
            self.get_push_api().list(TEST_USER)

    def test_list_not_json(self):
        self.fake_push_api.set_response_value('list', b'NOT OK')
        with self.assertRaisesRegexp(
            PushApiInvalidResponseError,
            r'Invalid JSON.+NOT OK',
        ):
            self.get_push_api().list(TEST_USER)

    def test_list_not_list(self):
        self.fake_push_api.set_response_value('list', b'null')
        with self.assertRaisesRegexp(
            PushApiInvalidResponseError,
            r'not a list',
        ):
            self.get_push_api().list(TEST_USER)

    def test_list_missing_fields(self):
        self.fake_push_api.set_response_value('list', b'[{}]')
        with self.assertRaisesRegexp(
            PushApiInvalidResponseError,
            r'Missing list result key',
        ):
            self.get_push_api().list(TEST_USER)

    def test_not_supported_platform(self):
        self.fake_push_api.set_response_value_without_method(b'NOT OK')
        with self.assertRaises(PushApiUnsupportedPlatformError):
            self.get_push_api().register(TEST_APP_NAME, TEST_CERT, 'invalid_platform')

    def test_supported_platform(self):
        self.fake_push_api.set_response_value_without_method(b'OK')
        push_api = self.get_push_api()
        push_api.register(TEST_APP_NAME, TEST_CERT, TEST_PLATFORM_2)
        push_api.register(TEST_APP_NAME, TEST_CERT, TEST_PLATFORM_3)
