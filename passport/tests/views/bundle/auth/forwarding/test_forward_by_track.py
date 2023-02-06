# -*- coding: utf-8 -*-

from time import time

import mock
from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_FORWARD_AUTH_TO_MOBILE_BY_TRACK
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_DEVICE_INFO,
    TEST_FIRSTNAME,
    TEST_HOST,
    TEST_LOGIN,
    TEST_OAUTH_TOKEN,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP1,
    TEST_YANDEXUID_VALUE,
    TRACK_ID1,
)
from passport.backend.core import useragent
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth.faker import (
    oauth_bundle_successful_response,
    token_error_response,
    token_response,
)
from passport.backend.core.redis_manager.redis_manager import RedisError
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.tracks.utils import get_model_by_type as get_track_model_by_type


CLIENT_ID1 = 'client_id1'
CLIENT_SECRET1 = 'client_secret1'
DEVICE_NAME1 = 'Fyr-fyr-fyr'
TOKEN_REISSUE_INTERVAL1 = 30
TTL1 = 60
USER_AGENT2 = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Installed by Symantec Package)'


class BaseByTrackAuthForwardingTestCase(EmailTestMixin, BaseBundleTestViews):
    def build_authorization_forwarding_track(self, track_type='authorize', created_at=None):
        if created_at is None:
            created_at = time()
        track_class = get_track_model_by_type(track_type)
        track = track_class(
            track_id=TRACK_ID1,
            data=dict(
                track_type=track_type,
                process_name=PROCESS_FORWARD_AUTH_TO_MOBILE_BY_TRACK,
                created=created_at,
            ),
            ttl=TTL1,
            version=1,
        )
        track.allow_oauth_authorization = True
        track.oauth_token_created_at = None
        track.uid = TEST_UID1
        return track

    def assert_tracks_equal(self, actual, expected):
        eq_(str(actual.uid), str(expected.uid))
        eq_(actual.ttl, TimeSpan(expected.ttl))
        eq_(actual.created, TimeSpan(expected.created))

        if expected.oauth_token_created_at is None:
            self.assertIsNone(actual.oauth_token_created_at)
        else:
            eq_(actual.oauth_token_created_at, TimeSpan(expected.oauth_token_created_at))

        AUTHORIZATION_FORWARDING_TRACK_FIELDS = [
            'allow_oauth_authorization',
            'process_name',
            'track_id',
            'track_type',
        ]
        track_to_dict = lambda t: {f: getattr(t, f) for f in AUTHORIZATION_FORWARDING_TRACK_FIELDS}
        iterdiff(eq_)(track_to_dict(actual), track_to_dict(expected))

    def save_track(self, source_track):
        manager = self.env.track_manager.get_manager()
        track = manager.create(
            track_type=source_track.track_type,
            created=source_track.created,
            consumer=TEST_CONSUMER1,
            ttl=source_track.ttl,
            process_name=source_track.process_name,
        )
        AUTHORIZATION_FORWARDING_TRACK_FIELDS = [
            'allow_oauth_authorization',
            'oauth_token_created_at',
            'uid',
        ]
        with manager.transaction(track=track).rollback_on_error() as track:
            for field in AUTHORIZATION_FORWARDING_TRACK_FIELDS:
                if hasattr(source_track, field):
                    value = getattr(source_track, field)
                    setattr(track, field, value)

    def setup_existing_track(self, track):
        if track is None:
            track = self.build_authorization_forwarding_track()
        self.track_id_generator.set_side_effect([track.track_id])
        self.save_track(track)

    def build_blackbox_response(self, **kwargs):
        kwargs.setdefault('login', TEST_LOGIN)
        emails = [
            self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
        ]
        kwargs.setdefault('emails', emails)
        kwargs.setdefault('uid', TEST_UID1)
        kwargs.setdefault('firstname', TEST_FIRSTNAME)
        return kwargs

    def build_invalid_sessionid_blackbox_response(self):
        return dict(
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
        )

    def build_account_not_found_blackbox_response(self):
        return dict(
            item_id=TEST_UID1,
            uid=None,
        )

    def build_global_logout_blackbox_response(self, timestamp):
        return dict(
            attributes={
                'account.global_logout_datetime': str(timestamp),
            },
        )


@with_settings_hosts(
    AUTH_FORWARDING_TRACK_TTL=TTL1,
    BLACKBOX_RETRIES=1,
    BLACKBOX_URL='https://blackbox',
)
class TestCreateTrackByTrackForwarding(BaseByTrackAuthForwardingTestCase):
    default_url = '/1/bundle/auth/forward_by_track/create_track/'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP1,
        'cookie': TEST_USER_COOKIE,
        'user_agent': TEST_USER_AGENT,
        'host': TEST_HOST,
        'consumer_ip': TEST_CONSUMER_IP1,
    }
    consumer = TEST_CONSUMER1

    def setUp(self):
        super(TestCreateTrackByTrackForwarding, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.track_id_generator = FakeTrackIdGenerator().start()

        self.assign_grants()
        self.setup_blackbox()
        self.setup_track_manager()
        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        del self.track_id_generator
        self.env.stop()
        del self.env
        super(TestCreateTrackByTrackForwarding, self).tearDown()

    def assign_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'auth_forwarding_by_track': ['create_track'],
                    },
                ),
            },
        )

    def setup_blackbox(self, blackbox_response=None, exception=None):
        if blackbox_response is None and exception is None:
            blackbox_response = self.build_blackbox_response()
        if blackbox_response is not None:
            response = blackbox_sessionid_multi_response(**blackbox_response)
            self.env.blackbox.set_response_side_effect('sessionid', [response])
        else:
            self.env.blackbox.set_response_side_effect('sessionid', [exception])

    def setup_track_manager(self):
        self.track_id_generator.set_side_effect([TRACK_ID1])

    def assert_track_forwards_authorization(self):
        actual = self.env.track_manager.get_manager().read(TRACK_ID1)
        expected = self.build_authorization_forwarding_track()
        self.assert_tracks_equal(actual, expected)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'create_track',
            mode='auth_forwarding_by_track',
            action='create_track',
            host=TEST_HOST,
            uid=str(TEST_UID1),
            track_id=TRACK_ID1,
            ip=TEST_USER_IP1,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_VALUE,
            consumer=TEST_CONSUMER1,
        )

    def assert_create_track_ok_response(self, rv):
        track_expire_at = TimeNow(offset=TTL1)
        self.assert_ok_response(
            rv,
            track_id=TRACK_ID1,
            track_expire_at=track_expire_at,
        )

    def assert_userinfo_blackbox_request_ok(self, request):
        request.assert_properties_equal(method='GET')
        request.assert_url_starts_with('https://blackbox/blackbox/?')
        request.assert_query_contains(
            {
                'method': 'sessionid',
                'userip': TEST_USER_IP1,
            },
        )
        request.assert_contains_attributes(
            {
                'account.is_disabled',
                'account.2fa_on',
            },
        )
        request.assert_contains_dbfields({'subscription.suid.67'})

    def test_ok(self):
        rv = self.make_request()

        self.assert_create_track_ok_response(rv)
        self.assert_track_forwards_authorization()
        self.env.statbox_logger.assert_has_written(
            [
                self.env.statbox.entry('check_cookies'),
                self.env.statbox.entry('create_track'),
            ],
        )

        eq_(len(self.env.blackbox.requests), 1)
        self.assert_userinfo_blackbox_request_ok(self.env.blackbox.requests[0])

    def test_invalid_sessionid(self):
        self.setup_blackbox(self.build_invalid_sessionid_blackbox_response())

        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_account_disabled(self):
        self.setup_blackbox(self.build_blackbox_response(enabled=False))

        rv = self.make_request()

        self.assert_error_response(rv, ['account.disabled'])
        self.env.blackbox.requests[0].assert_query_contains({'full_info': 'yes'})
        self.env.blackbox.requests[0].assert_contains_attributes({'account.is_disabled'})

    def test_blackbox_network_failed(self):
        self.setup_blackbox(exception=useragent.RequestError)

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.blackbox_failed'])

    def test_redis_failed(self):
        with mock.patch.object(
            self.env.track_manager.get_redis(),
            'pipeline',
            mock.Mock(side_effect=RedisError()),
        ):
            rv = self.make_request()

        self.assert_error_response(rv, ['backend.redis_failed'])

    def test_strong_password_policy(self):
        self.setup_blackbox(self.build_blackbox_response(subscribed_to=[67]))

        rv = self.make_request()

        self.assert_error_response(rv, ['account.strong_password_policy_enabled'])
        self.env.blackbox.requests[0].assert_contains_dbfields({'subscription.suid.67'})

    def test_require_password_when_totp_enabled(self):
        self.setup_blackbox(
            self.build_blackbox_response(
                attributes={'account.2fa_on': '1'},
                age=-1
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['password.required'])

    def test_dont_require_password_when_totp_disabled(self):
        self.setup_blackbox(self.build_blackbox_response(age=-1))

        rv = self.make_request()

        self.assert_create_track_ok_response(rv)

    def test_dont_require_password_when_entered_recently(self):
        self.setup_blackbox(
            self.build_blackbox_response(
                attributes={'account.2fa_on': '1'},
            ),
        )

        rv = self.make_request()

        self.assert_create_track_ok_response(rv)


@with_settings_hosts(
    AUTH_FORWARDING_TRACK_TTL=TTL1,
    BLACKBOX_RETRIES=1,
    BLACKBOX_URL='https://blackbox',
    OAUTH_RETRIES=1,
    OAUTH_URL='https://oauth',
    TOKEN_REISSUE_INTERVAL=TOKEN_REISSUE_INTERVAL1,
)
class TestExchangeByTrackAuthForwarding(BaseByTrackAuthForwardingTestCase):
    default_url = '/1/bundle/auth/forward_by_track/exchange/'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP1,
        'consumer_ip': TEST_CONSUMER_IP1,
        'host': None,
        'user_agent': USER_AGENT2,
    }
    http_query_args = {
        'track_id': TRACK_ID1,
        'client_id': CLIENT_ID1,
        'client_secret': CLIENT_SECRET1,
    }
    http_query_args.update(TEST_DEVICE_INFO)
    consumer = TEST_CONSUMER1

    def setUp(self):
        super(TestExchangeByTrackAuthForwarding, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_id_generator = FakeTrackIdGenerator().start()

        self.assign_grants()
        self.setup_blackbox()
        self.setup_oauth()
        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        del self.track_id_generator
        self.env.stop()
        del self.env
        super(TestExchangeByTrackAuthForwarding, self).tearDown()

    def assign_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'auth_forwarding_by_track': ['exchange'],
                    },
                ),
            },
        )

    def setup_track_manager(self, track=None):
        self.setup_existing_track(track)

    def setup_blackbox(self, blackbox_response=None, exception=None):
        if blackbox_response is None and exception is None:
            blackbox_response = self.build_blackbox_response()
        if blackbox_response is not None:
            blackbox_response = self.sessionid_to_userinfo_response(blackbox_response)
            response = blackbox_userinfo_response(**blackbox_response)
            self.env.blackbox.set_response_side_effect('userinfo', [response])
        else:
            self.env.blackbox.set_response_side_effect('userinfo', [exception])

    def sessionid_to_userinfo_response(self, blackbox_response):
        blackbox_response = dict(blackbox_response)
        if 'item_id' in blackbox_response:
            blackbox_response['id'] = blackbox_response.pop('item_id')
        blackbox_response.pop('secure', 0)
        return blackbox_response

    def setup_oauth(
        self,
        token_timeout=False,
        device_status_timeout=False,
        device_known=False,
        _token_response=None,
    ):
        if _token_response is None:
            if token_timeout:
                _token_response = useragent.RequestError
            else:
                _token_response = token_response(access_token=TEST_OAUTH_TOKEN)
        self.env.oauth.set_response_side_effect('_token', [_token_response])

        if device_status_timeout:
            device_status_response = useragent.RequestError
        else:
            device_status_response = oauth_bundle_successful_response(
                has_auth_on_device=device_known,
                device_id='device-id',
                device_name=DEVICE_NAME1,
            )
        self.env.oauth.set_response_side_effect('device_status', [device_status_response])

    def assert_track_not_forwards_authorization(self):
        expected = self.build_authorization_forwarding_track()
        expected.oauth_token_created_at = time()

        actual = self.env.track_manager.get_manager().read(TRACK_ID1)
        self.assert_tracks_equal(actual, expected)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base',
            mode='auth_forwarding_by_track',
            host='localhost',
            uid=str(TEST_UID1),
            track_id=TRACK_ID1,
            ip=TEST_USER_IP1,
            consumer=TEST_CONSUMER1,
            user_agent=USER_AGENT2,
        )
        self.env.statbox.bind_entry(
            'exchange',
            _inherit_from=['base'],
            action='exchange',
        )
        self.env.statbox.bind_entry(
            'notify',
            _inherit_from=['base'],
            action='auth_notification',
            counter_exceeded='0',
            email_sent='1',
            device_name=DEVICE_NAME1,
            is_challenged='0',
        )

    def build_email(self, address):
        masked_login = TEST_LOGIN[:2] + '***' if 'yandex' not in address else TEST_LOGIN
        return {
            'language': 'ru',
            'addresses': [address],
            'subject': 'auth_challenge.lite.subject',
            'tanker_keys': {
                'logo_url': {},
                'greeting': {'FIRST_NAME': TEST_FIRSTNAME},
                'auth_challenge.lite.notice': {'MASKED_LOGIN': masked_login},
                'auth_challenge.we_know': {},
                'user_meta_data.location': {'LOCATION': u'Мекильтео'},
                'user_meta_data.browser': {'BROWSER': 'MSIE 5.5 (Windows 98)'},
                'auth_challenge.device_name': {'DEVICE_NAME': DEVICE_NAME1},
                'auth_challenge.if_hacked.with_url': {
                    'SUPPORT_URL': "<a href='https://yandex.ru/support/passport/troubleshooting/hacked.html'>https://yandex.ru/support/passport/troubleshooting/hacked.html</a>",
                },
                'auth_challenge.support_url': {},
                'signature.secure': {},
                'feedback': {
                    'FEEDBACK_URL_BEGIN': "<a href='https://feedback2.yandex.ru/'>",
                    'FEEDBACK_URL_END': '</a>',
                },
                'feedback_url': {},
            },
        }

    def assert_passport_assertion_oauth_request_ok(self, request):
        request.assert_properties_equal(method='POST')
        request.assert_url_starts_with('https://oauth/token?')
        expected_oauth_query = dict(TEST_DEVICE_INFO, user_ip=TEST_USER_IP1)
        request.assert_query_equals(expected_oauth_query)
        expected_oauth_data = {
            'grant_type': 'passport_assertion',
            'client_id': CLIENT_ID1,
            'client_secret': CLIENT_SECRET1,
            'assertion': str(TEST_UID1),
            'password_passed': False,
            'passport_track_id': TRACK_ID1,
        }
        request.assert_post_data_equals(expected_oauth_data)

    def assert_device_status_oauth_request_ok(self, request):
        request.assert_properties_equal(method='GET')
        request.assert_url_starts_with('https://oauth/api/1/device/status?')
        expected_oauth_query = dict(
            TEST_DEVICE_INFO,
            uid=str(TEST_UID1),
            consumer='passport',
        )
        request.assert_query_equals(expected_oauth_query)

    def assert_exchange_ok_response(self, rv):
        self.assert_ok_response(
            rv,
            token=TEST_OAUTH_TOKEN,
        )

    def assert_userinfo_blackbox_request_ok(self, request):
        request.assert_properties_equal(
            method='POST',
            url='https://blackbox/blackbox/',
        )
        request.assert_post_data_contains(
            {
                'method': 'userinfo',
                'userip': TEST_USER_IP1,
                'uid': str(TEST_UID1),
                'emails': 'getall',
                'regname': 'yes',
            },
        )
        request.assert_contains_attributes(
            {
                'person.firstname',
                'person.country',
                'person.language',
                'account.is_disabled',
                'account.global_logout_datetime',
                'revoker.tokens',
                'revoker.app_passwords',
                'revoker.web_sessions',
            },
        )

    def test_ok(self):
        self.setup_track_manager()

        rv = self.make_request()

        self.assert_exchange_ok_response(rv)
        self.assert_track_not_forwards_authorization()
        self.env.statbox_logger.assert_has_written(
            [
                self.env.statbox.entry('notify'),
                self.env.statbox.entry('exchange'),
            ],
        )
        self.assert_emails_sent(
            [
                self.build_email(TEST_LOGIN + '@gmail.com'),
                self.build_email(TEST_LOGIN + '@yandex.ru'),
            ],
        )

        eq_(len(self.env.oauth.requests), 2)
        self.assert_device_status_oauth_request_ok(self.env.oauth.requests[0])
        self.assert_passport_assertion_oauth_request_ok(self.env.oauth.requests[1])

        eq_(len(self.env.blackbox.requests), 1)
        self.assert_userinfo_blackbox_request_ok(self.env.blackbox.requests[0])

    def test_retry(self):
        track = self.build_authorization_forwarding_track()
        track.oauth_token_created_at = int(time())
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_exchange_ok_response(rv)
        self.assert_track_not_forwards_authorization()

        updated_track = self.env.track_manager.get_manager().read(track.track_id)
        eq_(updated_track.oauth_token_created_at, str(track.oauth_token_created_at))

    def test_track_not_found(self):
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_invalid_track_process_name(self):
        track = self.build_authorization_forwarding_track()
        track.process_name = 'hack'
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_invalid_track_type(self):
        track = self.build_authorization_forwarding_track(track_type='complete')
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_track_not_allow_oauth_authorization(self):
        track = self.build_authorization_forwarding_track()
        track.allow_oauth_authorization = False
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_used_track(self):
        track = self.build_authorization_forwarding_track()
        track.oauth_token_created_at = time() - TOKEN_REISSUE_INTERVAL1 - 1
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_blackbox_network_failed(self):
        self.setup_track_manager()
        self.setup_blackbox(exception=useragent.RequestError)

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])

    def test_account_not_found(self):
        self.setup_track_manager()
        self.setup_blackbox(self.build_account_not_found_blackbox_response())

        rv = self.make_request()

        self.assert_error_response(rv, ['account.not_found'])
        self.env.blackbox.requests[0].assert_post_data_contains({'uid': str(TEST_UID1)})

    def test_account_disabled(self):
        self.setup_track_manager()
        self.setup_blackbox(self.build_blackbox_response(enabled=False))

        rv = self.make_request()

        self.assert_error_response(rv, ['account.disabled'])
        self.env.blackbox.requests[0].assert_contains_attributes({'account.is_disabled'})

    def test_global_logout(self):
        track_created_at = int(time() - TTL1 / 2.)
        track = self.build_authorization_forwarding_track(created_at=track_created_at)
        self.setup_track_manager(track)

        global_logout_at = int(track_created_at + 1)
        self.setup_blackbox(self.build_global_logout_blackbox_response(global_logout_at))

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])
        self.env.blackbox.requests[0].assert_contains_attributes({'account.global_logout_datetime'})

    def test_oauth_token_timeout(self):
        self.setup_track_manager()
        self.setup_oauth(token_timeout=True)

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])

    def test_oauth_token_invalid_grant(self):
        self.setup_track_manager()
        self.setup_oauth(_token_response=token_error_response())

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])

    def test_redis_failed(self):
        self.setup_track_manager()

        with mock.patch.object(
            self.env.track_manager.get_redis(),
            'pipeline',
            mock.Mock(side_effect=RedisError()),
        ):
            rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])

    def test_oauth_device_status_timeout(self):
        self.setup_track_manager()
        self.setup_oauth(device_status_timeout=True)

        rv = self.make_request()

        self.assert_exchange_ok_response(rv)
        self.assert_track_not_forwards_authorization()
        self.env.statbox_logger.assert_has_written(
            [
                self.env.statbox.entry('exchange'),
            ],
        )
        self.assert_emails_sent(list())

        eq_(len(self.env.oauth.requests), 2)
        self.assert_device_status_oauth_request_ok(self.env.oauth.requests[0])
        self.assert_passport_assertion_oauth_request_ok(self.env.oauth.requests[1])

    def test_known_device(self):
        self.setup_track_manager()
        self.setup_oauth(device_known=True)

        rv = self.make_request()

        self.assert_exchange_ok_response(rv)
        self.assert_track_not_forwards_authorization()
        self.env.statbox_logger.assert_has_written(
            [
                self.env.statbox.entry('exchange'),
            ],
        )
        self.assert_emails_sent(list())

        eq_(len(self.env.oauth.requests), 2)
        self.assert_device_status_oauth_request_ok(self.env.oauth.requests[0])
        self.assert_passport_assertion_oauth_request_ok(self.env.oauth.requests[1])


@with_settings_hosts(
    AUTH_FORWARDING_TRACK_TTL=TTL1,
    BLACKBOX_RETRIES=1,
)
class TestGetStatusByTrackAuthForwarding(BaseByTrackAuthForwardingTestCase):
    default_url = '/1/bundle/auth/forward_by_track/get_status/'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP1,
        'cookie': TEST_USER_COOKIE,
        'user_agent': TEST_USER_AGENT,
        'host': TEST_HOST,
        'consumer_ip': TEST_CONSUMER_IP1,
    }
    http_query_args = {
        'track_id': TRACK_ID1,
    }
    consumer = TEST_CONSUMER1

    def setUp(self):
        super(TestGetStatusByTrackAuthForwarding, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_id_generator = FakeTrackIdGenerator().start()

        self.assign_grants()
        self.setup_blackbox()

    def tearDown(self):
        self.track_id_generator.stop()
        del self.track_id_generator
        self.env.stop()
        del self.env
        super(TestGetStatusByTrackAuthForwarding, self).tearDown()

    def assign_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'auth_forwarding_by_track': ['get_status'],
                    },
                ),
            },
        )

    def setup_track_manager(self, track=None):
        self.setup_existing_track(track)

    def setup_blackbox(self, blackbox_response=None, exception=None):
        if blackbox_response is None and exception is None:
            blackbox_response = self.build_blackbox_response()
        if blackbox_response is not None:
            response = blackbox_sessionid_multi_response(**blackbox_response)
            self.env.blackbox.set_response_side_effect('sessionid', [response])
        else:
            self.env.blackbox.set_response_side_effect('sessionid', [exception])

    def assert_get_status_ok_response(self, rv, token_issued=False):
        track_expire_at = TimeNow(offset=TTL1)
        self.assert_ok_response(
            rv,
            token_issued=token_issued,
            track_expire_at=track_expire_at,
            track_id=TRACK_ID1,
        )

    def test_token_not_issued(self):
        self.setup_track_manager()

        rv = self.make_request()

        self.assert_get_status_ok_response(rv)

    def test_token_issued(self):
        track = self.build_authorization_forwarding_track()
        track.oauth_token_created_at = int(time())
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_get_status_ok_response(
            rv,
            token_issued=True,
        )

    def test_redis_failed(self):
        self.setup_track_manager()

        with mock.patch.object(
            self.env.track_manager.get_redis(),
            'pipeline',
            mock.Mock(side_effect=RedisError()),
        ):
            rv = self.make_request()

        self.assert_error_response(rv, ['backend.redis_failed'])

    def test_track_not_found(self):
        rv = self.make_request()
        self.assert_error_response(rv, ['track.not_found'])

    def test_invalid_track_process_name(self):
        track = self.build_authorization_forwarding_track()
        track.process_name = 'hack'
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_invalid_track_type(self):
        track = self.build_authorization_forwarding_track(track_type='complete')
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_track_not_allow_oauth_authorization(self):
        track = self.build_authorization_forwarding_track()
        track.allow_oauth_authorization = False
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_blackbox_network_failed(self):
        self.setup_track_manager()
        self.setup_blackbox(exception=useragent.RequestError)

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.blackbox_failed'])

    def test_invalid_sessionid(self):
        self.setup_track_manager()
        self.setup_blackbox(self.build_invalid_sessionid_blackbox_response())

        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_account_disabled(self):
        self.setup_track_manager()
        self.setup_blackbox(self.build_blackbox_response(enabled=False))

        rv = self.make_request()

        self.assert_error_response(rv, ['account.disabled'])
        self.env.blackbox.requests[0].assert_query_contains({'full_info': 'yes'})
        self.env.blackbox.requests[0].assert_contains_attributes({'account.is_disabled'})

    def test_track_account_not_match_session(self):
        track = self.build_authorization_forwarding_track()
        track.uid = TEST_UID2
        self.setup_track_manager(track)

        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.no_uid'])
