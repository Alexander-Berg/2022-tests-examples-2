# -*- coding: utf-8 -*-
import unittest

from mock import mock
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HOST,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_oauth_tokens_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.logbroker.exceptions import TransportError
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.utils.common import noneless_dict
from passport.backend.utils.string import smart_bytes


TEST_TRACK_ID = 'abcd123456'
TEST_APP_ID = 'ru.yandex.test'
TEST_LOGIN_ID = 'login-id1'
TEST_LOGIN_ID2 = 'login-id2'
TEST_PUSH_ID1 = '3d372a68-eb95-4803-ad4b-b35d0a34a220'
TEST_RANDOM_CODE = '153413'
TEST_OAUTH_TOKEN = 'test-x-token'
TEST_OAUTH_HEADER = 'OAuth %s' % TEST_OAUTH_TOKEN


@with_settings_hosts(
    PUSH_2FA_CODE_URL_TEMPLATE='https://passport.yandex.%(tld)s/am/push/getcode?track_id=%(track_id)s',
)
class _BaseTestPush2faControllers(BaseBundleTestViews):
    consumer = 'dev'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
    )
    grants_mock = None

    def setUp(self):
        super(_BaseTestPush2faControllers, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants=self.grants_mock))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.bind_statbox_templates()

    def tearDown(self):
        self.env.stop()
        super(_BaseTestPush2faControllers, self).tearDown()

    def setup_bb_account_response(self, uid=TEST_UID):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=uid),
        )

    def setup_bb_sessionid_response(self, uid=TEST_UID, login_id=TEST_LOGIN_ID, additional_uid=None):
        response = blackbox_sessionid_multi_response(uid=uid, login_id=login_id)
        if additional_uid:
            response = blackbox_sessionid_multi_append_user(
                response,
                uid=additional_uid,
            )
        self.env.blackbox.set_blackbox_response_value('sessionid', response)

    def bind_statbox_templates(self):
        self.env.statbox.bind_base(
            host=TEST_HOST,
            uid=str(TEST_UID),
            track_id=self.track_id,
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            consumer=self.consumer,
        )
        self.env.statbox.bind_entry(
            'push_2fa_send',
            mode='push_2fa_send',
        )
        self.env.statbox.bind_entry(
            'push_2fa_get_code',
            mode='push_2fa_get_code',
            yandexuid='yandexuid',
        )

    def assert_statbox_empty(self):
        self.env.statbox.assert_equals([])


class TestSendPush2faView(_BaseTestPush2faControllers):
    default_url = '/1/bundle/push/2fa/send/'
    http_method = 'POST'
    grants_mock = {'push_2fa': ['send']}

    def setUp(self):
        super(TestSendPush2faView, self).setUp()

        self._uuid_patch = mock.patch('uuid.uuid4', lambda: TEST_PUSH_ID1)
        self._uuid_patch.start()

        self._random_code_patch = mock.patch(
            'passport.backend.api.views.bundle.push.push_2fa.controllers.generate_random_code',
            lambda x: TEST_RANDOM_CODE,
        )
        self._random_code_patch.start()

    def tearDown(self):
        self._random_code_patch.stop()
        self._uuid_patch.stop()
        super(TestSendPush2faView, self).tearDown()

    def setup_kolmogor(self, rate=2):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def assert_push_sent(self):
        translations = settings.translations.NOTIFICATIONS['ru']
        message = dict(
            push_service='2fa',
            event_name='2fa_code',
            recipients=[
                dict(
                    uid=str(TEST_UID),
                    app_targeting_type='ONE_APP_PER_DEVICE',
                    required_am_capabilities=['push:passport_protocol'],
                    require_trusted_device=True,
                    context='{"track": "%s"}' % self.track_id,
                ),
            ],
            text_body=dict(
                title=smart_bytes(translations['2fa.push.title']),
                body=smart_bytes(translations['2fa.push.text']),
            ),
            webview_body=dict(
                webview_url='https://passport.yandex.ru/am/push/getcode?track_id={}'.format(self.track_id),
                require_web_auth=True,
            ),
            push_id=TEST_PUSH_ID1,
        )
        self.env.lbw_challenge_pushes.assert_message_sent(
            dict(push_message_request=message),
        )

    def assert_statbox_ok(self, status='ok'):
        self.env.statbox.assert_equals(
            self.env.statbox.entry(
                'push_2fa_send',
                status=status,
            ),
        )

    def test_send__ok(self):
        self.setup_bb_account_response()
        self.setup_kolmogor()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        rv = self.make_request(query_args=dict(track_id=self.track_id))

        self.assert_ok_response(rv)
        self.assert_push_sent()
        self.assert_statbox_ok()
        track = self.track_manager.read(self.track_id)
        self.assertEqual(track.push_otp, TEST_RANDOM_CODE)

    def test_send__logbroker_exception__error(self):
        self.setup_bb_account_response()
        self.setup_kolmogor()
        self.env.lbw_challenge_pushes.set_send_side_effect(TransportError('some error'))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        rv = self.make_request(query_args=dict(track_id=self.track_id))

        self.assert_error_response(rv, ['backend.logbroker_failed'])
        self.assert_statbox_ok(status='failed')

    def test_send__wrong_track__error(self):
        self.setup_bb_account_response()
        self.setup_kolmogor()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        rv = self.make_request(query_args=dict(track_id='non-existent'))

        self.assert_error_response(rv, ['track_id.invalid'])
        self.assert_statbox_empty()

    def test_send__no_uid_in_track(self):
        self.setup_bb_account_response()
        self.setup_kolmogor()

        rv = self.make_request(query_args=dict(track_id=self.track_id))

        self.assert_error_response(rv, ['track.invalid_state'])
        self.assert_statbox_empty()

    def test_send__push_limit_exceed__error(self):
        self.setup_bb_account_response()
        self.setup_kolmogor(rate=50)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        rv = self.make_request(query_args=dict(track_id=self.track_id))

        self.assert_error_response(rv, ['rate.limit_exceeded'])
        self.assert_statbox_empty()


@with_settings_hosts()
class TestGetAuthCodePush2faView(_BaseTestPush2faControllers):
    default_url = '/1/bundle/push/2fa/get_code/'
    http_method = 'GET'
    grants_mock = {'push_2fa': ['get_code']}

    def setup_bb_get_tokens_response(self, trusted_login_ids=None):
        trusted_login_ids = trusted_login_ids or []
        tokens_with_login_id = [
            noneless_dict(
                login_id=login_id,
                is_xtoken_trusted=(login_id in trusted_login_ids or None),
            ) for login_id in [TEST_LOGIN_ID, TEST_LOGIN_ID2]
        ]
        tokens_without_login_id = [
            dict(is_xtoken_trusted=True),
            dict(),
        ]
        self.env.blackbox.set_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response(
                tokens_with_login_id + tokens_without_login_id,
            ),
        )

    def build_headers(self, cookie=TEST_USER_COOKIE):
        headers = dict(self.http_headers)
        if cookie:
            headers.update(cookie=cookie)
        return headers

    def assert_statbox_ok(self, status='ok', with_check_cookies=False, **kwargs):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(
            self.env.statbox.entry(
                'push_2fa_get_code',
                status=status,
                **kwargs
            )
        )
        self.env.statbox.assert_equals(entries)

    def test_get_code__ok(self):
        self.setup_bb_get_tokens_response(trusted_login_ids=[TEST_LOGIN_ID])
        self.setup_bb_sessionid_response()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.push_otp = TEST_RANDOM_CODE

        rv = self.make_request(
            query_args=dict(track_id=self.track_id),
            headers=self.build_headers(),
        )

        self.assert_ok_response(rv, otp=TEST_RANDOM_CODE)
        self.assert_statbox_ok(with_check_cookies=True)

    def test_get_code__multisession__ok(self):
        self.setup_bb_get_tokens_response(trusted_login_ids=[TEST_LOGIN_ID])
        self.setup_bb_sessionid_response(additional_uid=TEST_UID2)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID2
            track.push_otp = TEST_RANDOM_CODE

        rv = self.make_request(
            query_args=dict(track_id=self.track_id),
            headers=self.build_headers(),
        )

        self.assert_ok_response(rv, otp=TEST_RANDOM_CODE)
        self.assert_statbox_ok(uid=str(TEST_UID2), with_check_cookies=True)

    def test_get_code__wrong_track_id__error(self):
        self.setup_bb_sessionid_response()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.push_otp = TEST_RANDOM_CODE

        rv = self.make_request(
            query_args=dict(track_id='wrong'),
            headers=self.build_headers(),
        )

        self.assert_error_response(rv, ['track_id.invalid'])

    def test_get_code__no_user_cookie__error(self):
        self.setup_bb_sessionid_response()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.push_otp = TEST_RANDOM_CODE

        rv = self.make_request(
            query_args=dict(track_id=self.track_id),
            headers=self.build_headers(cookie=None),
        )

        self.assert_error_response(rv, ['cookie.empty'])

    def test_get_code__no_track_uid__error(self):
        self.setup_bb_sessionid_response()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.push_otp = TEST_RANDOM_CODE

        rv = self.make_request(
            query_args=dict(track_id=self.track_id),
            headers=self.build_headers(),
        )

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_get_code__wrong_track_uid__error(self):
        self.setup_bb_sessionid_response()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID2
            track.push_otp = TEST_RANDOM_CODE

        rv = self.make_request(
            query_args=dict(track_id=self.track_id),
            headers=self.build_headers(),
        )

        self.assert_error_response(rv, ['sessionid.no_uid'])

    def test_get_code__no_otp_code__error(self):
        self.setup_bb_sessionid_response()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        rv = self.make_request(
            query_args=dict(track_id=self.track_id),
            headers=self.build_headers(),
        )

        self.assert_error_response(rv, ['track.invalid_state'])

    @unittest.skip(u'Отключен, пока не сделали PASSP-33827')
    def test_get_code__device_not_trusted__error(self):
        self.setup_bb_sessionid_response()
        self.setup_bb_get_tokens_response(trusted_login_ids=[TEST_LOGIN_ID2])
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.push_otp = TEST_RANDOM_CODE

        rv = self.make_request(
            query_args=dict(track_id=self.track_id),
            headers=self.build_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.device_not_trusted'])

    @unittest.skip(u'Отключен, пока не сделали PASSP-33827')
    def test_get_code__device_not_trusted__multisession__error(self):
        self.setup_bb_sessionid_response(additional_uid=TEST_UID2)
        self.setup_bb_get_tokens_response(trusted_login_ids=[TEST_LOGIN_ID2])
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID2
            track.push_otp = TEST_RANDOM_CODE

        rv = self.make_request(
            query_args=dict(track_id=self.track_id),
            headers=self.build_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.device_not_trusted'])
