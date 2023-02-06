# -*- coding: utf-8 -*-
from time import time

from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    TEST_AUTH_ID,
    TEST_DEVICE_ID,
    TEST_DIFFERENT_PHONE_NUMBER,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_OTHER_DEVICE_ID,
    TEST_PHONE_NUMBER,
    TEST_REFERER,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HINT_ANSWER,
    TEST_HINT_QUESTION,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_oauth_tokens_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.push_api.faker import (
    push_api_app_subscription_info,
    push_api_list_response,
)
from passport.backend.core.builders.push_api.push_api import make_extra_data
from passport.backend.core.builders.trust_api.faker import TEST_PAYMETHOD_ID
from passport.backend.core.counters import auth_challenge_per_ip
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import deep_merge


TEST_CREDENTIAL_EXTERNAL_ID = 'cred-id'
TEST_DEVICE_NAME = 'device-name'
TEST_COOKIES_WITH_WCID = 'Session_id=foo; wcid=%s; yandexuid=%s' % (
    TEST_CREDENTIAL_EXTERNAL_ID,
    TEST_YANDEXUID_COOKIE,
)

TEST_USER_AGENT_SUITABLE_FOR_WEBAUTHN = 'Mozilla/5.0 (Linux; Android 6.0; LG-H818 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.95 Mobile Safari/537.36'
TEST_BROWSER_ID = 83  # соответствует юзерагенту
TEST_OS_FAMILY_ID = 433  # соответствует юзерагенту

TEST_ANTIFRAUD_EXTERNAL_ID = 'external-id'
TEST_CARD_ID = TEST_PAYMETHOD_ID


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    SEND_AUTH_EMAILS_INTERVAL=100,
    AUTH_CHALLENGE_MAX_ATTEMPTS=5,
    **mock_counters()
)
class BaseTestCase(BaseBundleTestViews, EmailTestMixin):
    http_method = 'POST'
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'cookie': 'Session_id=foo; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'user_ip': TEST_IP,
        'referer': TEST_REFERER,
    }
    consumer = 'dev'

    def setUp(self):
        self.patches = []

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.setup_trackid_generator()
        self.start_patches()

        self.setup_blackbox_response()

    def tearDown(self):
        self.stop_patches()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches

    def start_patches(self):
        for patch in self.patches:
            patch.start()

    def stop_patches(self):
        for patch in reversed(self.patches):
            patch.stop()

    def setup_trackid_generator(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)
        self.patches.append(self.track_id_generator)

    def setup_blackbox_response(
        self, has_emails=True, challenge_email_only=False, challenge_email='Gmail.com',
        has_phones=True, is_easily_hacked=False, attempts=0, alias=TEST_LOGIN, alias_type='portal',
        secured_phone_confirmed=None, has_sms_2fa=False, has_webauthn_credentials=True,
        has_secret_question=True, has_trusted_xtokens=False, bank_phonenumber_alias=None,
        simple_phone=None, native_email_only=False,
    ):
        attributes = {}
        if is_easily_hacked:
            attributes['account.is_easily_hacked'] = '1'
        if has_sms_2fa:
            attributes['account.sms_2fa_on'] = '1'
        if attempts:
            attributes['account.failed_auth_challenge_checks_counter'] = '%s:%s' % (
                attempts,
                int(time() + 100),
            )

        aliases = {alias_type: alias}
        if bank_phonenumber_alias:
            aliases['bank_phonenumber'] = bank_phonenumber_alias

        bb_kwargs = {
            'uid': TEST_UID,
            'login': alias,
            'aliases': aliases,
            'attributes': attributes,
            'dbfields': {},
        }

        if has_emails:
            emails = []
            if not challenge_email_only:
                emails.extend([
                    self.create_validated_external_email(TEST_LOGIN, 'google-mail.com'),
                    self.create_validated_external_email(TEST_LOGIN, u'google-почта.com'.encode('idna')),
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                ])
            # вставляем не в начало или в конец, чтобы проверить в том числе, что почтовый адрес
            # выбирается по правильному критерию - времени подтверждения
            emails.insert(
                1,
                self.create_validated_external_email(
                    TEST_LOGIN,
                    challenge_email.encode('idna'),
                    born_date='2010-01-01 23:59:59',
                ),
            )
            if native_email_only:
                emails = [
                    self.create_native_email(TEST_LOGIN, 'yandex.ru')
                ]
            bb_kwargs.update(emails=emails)

        if has_phones:
            phone_secured_args = {}
            if secured_phone_confirmed is not None:
                phone_secured_args['phone_confirmed'] = secured_phone_confirmed
            phone_secured = build_phone_secured(
                1,
                TEST_PHONE_NUMBER.e164,
                **phone_secured_args
            )
            phone_bound = build_phone_bound(
                2,
                TEST_DIFFERENT_PHONE_NUMBER.e164,
            )
            bb_kwargs = deep_merge(bb_kwargs, phone_secured, phone_bound)

        if simple_phone:
            phone_simple_bound = build_phone_bound(
                3,
                simple_phone.e164,
            )
            bb_kwargs = deep_merge(bb_kwargs, phone_simple_bound)

        if has_webauthn_credentials:
            bb_kwargs.update(
                webauthn_credentials=[
                    {
                        'id': 1,
                        'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                        'public_key': '1:pub-key',
                        'device_name': TEST_DEVICE_NAME,
                        'os_family_id': TEST_OS_FAMILY_ID,
                        'browser_id': TEST_BROWSER_ID,
                        'relying_party_id': TEST_HOST,
                    },
                    {
                        'id': 2,
                        'external_id': TEST_CREDENTIAL_EXTERNAL_ID + '2',
                        'public_key': '1:pub-key2',
                        'device_name': TEST_DEVICE_NAME + '2',
                        'relying_party_id': 'some-other-host.yandex.ru',
                    },
                ]
            )

        if has_secret_question:
            bb_kwargs['dbfields'].update({
                'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
                'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
            })

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**bb_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                authid=TEST_AUTH_ID,
                login_id=TEST_LOGIN_ID,
                **bb_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response([
                dict(is_xtoken_trusted=False, login_id=TEST_LOGIN_ID + '-2', device_id=TEST_OTHER_DEVICE_ID),
                dict(is_xtoken_trusted=False),
                dict(is_xtoken_trusted=has_trusted_xtokens, login_id=TEST_LOGIN_ID, device_id=TEST_DEVICE_ID),
            ]),
        )

    def setup_push_api_list_response(self, with_trusted_subscription=False):
        _s = push_api_app_subscription_info
        device_id = TEST_DEVICE_ID if with_trusted_subscription else TEST_OTHER_DEVICE_ID
        extra = make_extra_data(
            login_id=(TEST_LOGIN_ID if with_trusted_subscription else 'other-id'),
            am_version='6.5.0',
        )
        subscriptions = [
            _s(1, '12345', 'ru.yandex.test', 'apns', device_id, extra=extra),
            _s(2, '123456', 'ru.yandex.test', 'fcm', TEST_OTHER_DEVICE_ID),
        ]
        self.env.push_api.set_response_value('list', push_api_list_response(subscriptions))

    def assert_xunistater(self, condition_set_id, expected_signal, total_messages=1):
        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            [condition_set_id],
            {expected_signal: total_messages}
        )

    @property
    def common_response_values(self):
        return {
            'track_id': self.track_id,
        }


class BaseAuthTestCase(BaseTestCase):
    @property
    def http_query_args(self):
        return {
            'track_id': self.track_id,
        }

    def setUp(self):
        super(BaseAuthTestCase, self).setUp()

        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.is_auth_challenge_shown = True

        self.setup_statbox_templates()

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
            track_id=self.track_id,
            mode='auth_challenge',
            consumer='dev',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'shown',
            action='shown',
            challenges='phone,email',
        )
        self.env.statbox.bind_entry(
            'failed',
            action='failed',
        )
        self.env.statbox.bind_entry(
            'passed',
            action='passed',
        )


class BaseStandaloneTestCase(BaseTestCase):
    def setUp(self):
        super(BaseStandaloneTestCase, self).setUp()

        self.env.grants.set_grants_return_value(mock_grants(grants={'challenge': ['base']}))

        self.setup_statbox_templates()

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
            track_id=self.track_id,
            mode='challenge',
            consumer='dev',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'shown',
            action='shown',
            challenges='phone_confirmation',
            default_challenge='phone_confirmation',
        )
        self.env.statbox.bind_entry(
            'failed',
            action='failed',
        )
        self.env.statbox.bind_entry(
            'passed',
            action='passed',
        )


class CommonChallengeTests(object):
    def test_limit_exceeded_for_ip(self):
        limit = 10
        counter = auth_challenge_per_ip.get_counter()
        for _ in range(limit):
            counter.incr(TEST_IP)

        resp = self.make_request()
        self.assert_error_response(resp, ['challenge.limit_exceeded'], **self.common_response_values)

    def test_limit_exceeded_for_user(self):
        limit = 5
        self.setup_blackbox_response(attempts=limit)
        resp = self.make_request()
        self.assert_error_response(resp, ['challenge.limit_exceeded'], **self.common_response_values)

    def test_no_challenges_error(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.paymethod_id = None
        self.setup_blackbox_response(has_phones=False, has_emails=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'], **self.common_response_values)


class CommonAuthChallengeTests(CommonChallengeTests):
    def test_track_missing(self):
        resp = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(resp, ['track_id.empty'])

    def test_track_invalid_state(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.is_auth_challenge_shown = False

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], **self.common_response_values)

    def test_captcha_required(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.is_captcha_required = True

        resp = self.make_request()
        self.assert_error_response(resp, ['captcha.required'], **self.common_response_values)


class CommonStandaloneChallengeTests(CommonChallengeTests):
    pass
