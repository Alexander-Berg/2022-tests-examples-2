# -*- coding: utf-8 -*-
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator

from .base_test_data import (
    TEST_COOKIE,
    TEST_COOKIE_AGE,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_PDD_DOMAIN,
    TEST_UID,
    TEST_USER_AGENT,
)


@with_settings_hosts()
class BaseOtpMigrateTestCase(BaseBundleTestViews, EmailTestMixin):
    url = None

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        self.patches = [
            self.track_id_generator,
        ]
        for patch in self.patches:
            patch.start()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
        self.setup_blackbox()
        self.setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches

    def get_account_kwargs(self, uid=TEST_UID, login=TEST_LOGIN, alias_type='portal',
                           password_verification_age=TEST_COOKIE_AGE, **kwargs):
        base_kwargs = dict(
            uid=uid,
            login=login,
            aliases={
                alias_type: login,
            },
            attributes={
                'account.2fa_on': '1',
                'account.totp.secret': 'secret',
                'account.totp.secret_ids': '0:0',
                'account.totp.pin_length': '4',
            },
            emails=[
                self.create_validated_external_email(login, 'gmail.com'),
                self.create_validated_external_email(login, 'mail.ru', rpop=True),
                self.create_validated_external_email(login, 'silent.ru', silent=True),
                self.create_native_email(login, 'yandex.ru'),
            ],
            age=password_verification_age,
        )
        return dict(base_kwargs, **kwargs)

    def setup_blackbox(self, **kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.get_account_kwargs(**kwargs)
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, domain=TEST_PDD_DOMAIN, can_users_change_password='1'),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base',
            ip=TEST_IP,
            uid=str(TEST_UID),
            consumer='dev',
            track_id=self.track_id,
            mode='migrate_otp',
            yandexuid='testyandexuid',
            user_agent=TEST_USER_AGENT,
        )

    def default_headers(self, cookie=TEST_COOKIE):
        return mock_headers(
            host=TEST_HOST,
            cookie=cookie,
            user_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )

    def default_params(self):
        return {
            'track_id': self.track_id,
        }

    def make_request(self, headers=None, exclude=None, **kwargs):
        data = dict(self.default_params(), **kwargs)
        for param in (exclude or []):
            data.pop(param, None)
        return self.env.client.post(
            self.url,
            data=data,
            headers=headers or self.default_headers(),
        )

    def assert_statbox_empty(self):
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def assert_statbox_check_cookies(self):
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry(
                    'check_cookies',
                    ['ip', 'track_id', 'user_agent', 'yandexuid', 'uid'],
                    host='passport.yandex.ru'
                )
            ]
        )

    def assert_statbox_logged(self, with_check_cookies=False, **kwargs):
        entries = []
        if with_check_cookies:
            entries.append(
                self.env.statbox.entry(
                    'check_cookies',
                    ['ip', 'track_id', 'user_agent', 'yandexuid', 'uid'],
                    host='passport.yandex.ru'
                )
            )
        entries.append(self.env.statbox.entry('base', **kwargs))
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            entries,
        )


class OtpMigrateCommonTests(object):
    with_check_cookies = False

    def test_track_id_missing__error(self):
        rv = self.make_request(exclude=['track_id'])
        self.assert_error_response(rv, ['track_id.empty'])

    def test_uid_not_in_track__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = None

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'], track_id=self.track_id)
        self.assert_statbox_empty()

    def test_bad_cookies__error(self):
        self.setup_blackbox(status=BLACKBOX_SESSIONID_INVALID_STATUS)

        rv = self.make_request()
        self.assert_error_response(rv, ['sessionid.invalid'], track_id=self.track_id)
        if self.with_check_cookies:
            self.assert_statbox_check_cookies()
        else:
            self.assert_statbox_empty()

    def test_account_disabled__error(self):
        self.setup_blackbox(enabled=False)

        rv = self.make_request()
        self.assert_error_response(rv, ['account.disabled'], track_id=self.track_id)
        if self.with_check_cookies:
            self.assert_statbox_check_cookies()
        else:
            self.assert_statbox_empty()

    def test_auth_already_passed__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = 'session'

        rv = self.make_request()
        self.assert_error_response(rv, ['action.not_required'], track_id=self.track_id)
        self.assert_statbox_empty()

    def test_2fa_is_off__error(self):
        self.setup_blackbox(attributes={})

        rv = self.make_request()
        self.assert_error_response(rv, ['action.impossible'], track_id=self.track_id)
        if self.with_check_cookies:
            self.assert_statbox_check_cookies()
        else:
            self.assert_statbox_empty()

    def test_too_many_secrets__error(self):
        self.setup_blackbox(attributes={
            'account.2fa_on': '1',
            'account.totp.secret_ids': '0:0,1:100',
        })

        rv = self.make_request()
        self.assert_error_response(rv, ['action.impossible'], track_id=self.track_id)
        if self.with_check_cookies:
            self.assert_statbox_check_cookies()
        else:
            self.assert_statbox_empty()

    def test_password_not_entered__error(self):
        self.setup_blackbox(age=3600)

        rv = self.make_request()
        self.assert_error_response(rv, ['password.required'], track_id=self.track_id)
        if self.with_check_cookies:
            self.assert_statbox_check_cookies()
        else:
            self.assert_statbox_empty()
