# -*- coding: utf-8 -*-
import re

from nose.tools import (
    istest,
    nottest,
)
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.views.bundle.auth.social.base import (
    OUTPUT_MODE_AUTHORIZATION_CODE,
    OUTPUT_MODE_SESSIONID,
    OUTPUT_MODE_XTOKEN,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_loginoccupation_response
from passport.backend.core.builders.social_api.faker.social_api import (
    APP_PARTY_3RD_PARTY,
    APP_PARTY_YANDEX,
    task_data_response,
)
from passport.backend.core.builders.social_broker.faker.social_broker import social_broker_error_response
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_DEFAULT_AVATAR1,
    TEST_DISPLAY_LOGIN1,
    TEST_EMAIL1,
    TEST_LOGIN1,
    TEST_PROCESS_UUID1,
    TEST_RETPATH1,
    TEST_SOCIAL_LOGIN1,
    TEST_SOCIAL_LOGIN2,
    TEST_SOCIAL_TASK_ID1,
    TEST_TRACK_ID1,
    TEST_TRACK_ID2,
    TEST_UID1,
    TEST_UID2,
    TEST_YANDEX_AUTHORIZATION_CODE1,
    TEST_YANDEX_EMAIL1,
    TEST_YANDEX_TOKEN1,
    TEST_YANDEX_TOKEN_EXPIRES_IN1,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.email.email import domain_from_email

from .base import BaseTestCase


@nottest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class CallbackTestPlan(BaseTestCase):
    """
    План тестирования Callback и её аналогов в нативном окружении.
    """
    def examine_native_start(self, builder):
        raise NotImplementedError()  # pragma: no cover

    def examine_choose(self, builder):
        raise NotImplementedError()  # pragma: no cover

    def examine_callback(self, builder):
        raise NotImplementedError()  # pragma: no cover

    def request_native_start(self, builder, headers=None):
        return builder.request_native_start(headers=headers)

    def request_choose(self, builder, chosen_uid):
        return builder.request_choose(uid=chosen_uid)

    def request_callback(self, builder, headers=None):
        return builder.request_callback(headers=headers)

    def test_callback(self):
        self.examine_callback(self.get_primary_builder())

    def test_native_start(self):
        self.examine_native_start(self.get_primary_builder())

    def test_third_party_native_start(self):
        self.examine_native_start(self.get_third_party_builder())

    def test_choose(self):
        self.examine_choose(self.get_primary_builder())

    def test_third_party_choose(self):
        self.examine_choose(self.get_third_party_builder())


@istest
@with_settings_hosts()
class TestLoginToPhonish(CallbackTestPlan):
    def assert_register_response(self, rv, builder, is_native=True):
        self.assert_ok_response(rv, **builder.build_register_response(is_native=is_native))

    def assert_uid_rejected_response(self, rv, builder):
        self.assert_error_response(
            rv,
            ['uid.rejected'],
            **builder.build_error_response(
                account=None,
                profile_id=None,
            )
        )

    def examine_native_start(self, builder):
        b = builder
        b.setup_task_for_token(b.build_task())
        b.setup_social_profiles([
            b.build_social_profile(),
        ])
        b.setup_yandex_accounts(
            profile_accounts=[
                b.build_yandex_phonish_account(),
            ],
            email_account=None,
        )

        rv = self.request_native_start(b)

        self.assert_register_response(rv, b)

    def examine_choose(self, builder):
        b = builder
        b.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([
            b.build_social_profile(uid=TEST_UID1, allow_auth=True),
            b.build_social_profile(uid=TEST_UID2, allow_auth=True),
        ])
        b.setup_yandex_accounts([
            b.build_yandex_phonish_account(uid=TEST_UID1),
            b.build_yandex_social_account(uid=TEST_UID2),
        ])

        rv = self.request_choose(b, chosen_uid=TEST_UID1)
        self.assert_uid_rejected_response(rv, b)

    def examine_callback(self, builder):
        b = builder
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(b.build_task())
        b.setup_social_profiles([
            b.build_social_profile(uid=TEST_UID1),
        ])
        b.setup_yandex_accounts(
            profile_accounts=[
                b.build_yandex_phonish_account(uid=TEST_UID1),
            ],
            email_account=None,
        )

        rv = self.request_callback(b)

        self.assert_register_response(rv, b, is_native=False)


@istest
@with_settings_hosts()
class TestAccountDisabled(CallbackTestPlan):
    def assert_account_disabled_response(self,
                                         rv,
                                         builder,
                                         has_enabled_accounts=False,
                                         is_native=True):
        b = builder
        self.assert_error_response(
            rv,
            ['account.disabled'],
            **b.build_error_response(
                account=b.get_account_response(
                    login=TEST_LOGIN1,
                    display_name=b.build_full_display_name(),
                ),
                has_enabled_accounts=has_enabled_accounts,
                is_native=is_native,
                profile_id=None,
            )
        )

    def examine_native_start(self, builder):
        b = builder
        b.setup_task_for_token(b.build_task())
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([
            b.build_yandex_full_account(
                enabled=False,
                login=TEST_LOGIN1,
            ),
        ])

        rv = self.request_native_start(b)

        self.assert_account_disabled_response(rv, b)

    def examine_choose(self, builder):
        b = builder
        b.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([
            b.build_social_profile(uid=TEST_UID1),
            b.build_social_profile(uid=TEST_UID2),
        ])
        b.setup_yandex_accounts([
            b.build_yandex_full_account(uid=TEST_UID1, enabled=False),
            b.build_yandex_social_account(uid=TEST_UID2),
        ])

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_account_disabled_response(rv, b, has_enabled_accounts=True)

    def examine_callback(self, builder):
        b = builder
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(b.build_task())
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([
            b.build_yandex_full_account(enabled=False),
        ])

        rv = self.request_callback(b)

        self.assert_account_disabled_response(rv, b, is_native=False)


@istest
@with_settings_hosts()
class TestNoYandexAccount(CallbackTestPlan):
    def setup_statbox_templates(self, builder):
        builder.setup_statbox_templates()
        self.env.statbox.bind_entry(
            'callback_end',
            _exclude=['accounts', 'login'],
            state='register',
            enabled_accounts_count='0',
        )

    def assert_register_response(self, rv, builder, is_native=True):
        self.assert_ok_response(rv, **builder.build_register_response(is_native=is_native))

    def assert_uid_rejected_response(self, rv, builder):
        self.assert_error_response(
            rv,
            ['uid.rejected'],
            **builder.build_error_response(
                account=None,
                profile_id=None,
                has_enabled_accounts=False,
            )
        )

    def examine_native_start(self, builder):
        b = builder
        b.setup_task_for_token(b.build_task())
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=None)

        rv = self.request_native_start(b)

        self.assert_register_response(rv, b)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('native_start_submitted'),
            self.env.statbox.entry('callback_end'),
        ])

        self.env.event_logger.assert_events_are_logged({})

    def examine_choose(self, builder):
        b = builder
        b.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([])

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_uid_rejected_response(rv, b)

        self.env.statbox.assert_has_written([])

        self.env.event_logger.assert_events_are_logged({})

    def examine_callback(self, builder):
        b = builder
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(b.build_task())
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=None)

        rv = self.request_callback(b)

        self.assert_register_response(rv, b, is_native=False)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry('callback_end'),
        ])

        self.env.event_logger.assert_events_are_logged({})


@istest
@with_settings_hosts()
class TestSocialAuthenticationNotAllowed(TestNoYandexAccount):
    def examine_native_start(self, builder):
        b = builder
        b.setup_task_for_token(b.build_task())
        b.setup_social_profiles([b.build_social_profile(allow_auth=False)])
        b.setup_yandex_accounts(email_account=None)

        rv = self.request_native_start(b)

        self.assert_register_response(rv, b)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('native_start_submitted'),
            self.env.statbox.entry('callback_end'),
        ])

        self.env.event_logger.assert_events_are_logged({})

    def examine_choose(self, builder):
        b = builder
        b.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([b.build_social_profile(allow_auth=False)])

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_uid_rejected_response(rv, b)

        self.env.statbox.assert_has_written([])

        self.env.event_logger.assert_events_are_logged({})

    def examine_callback(self, builder):
        b = builder
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(b.build_task())
        b.setup_social_profiles([b.build_social_profile(allow_auth=False)])
        b.setup_yandex_accounts(email_account=None)

        rv = self.request_callback(b)

        self.assert_register_response(rv, b, is_native=False)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry('callback_end'),
        ])

        self.env.event_logger.assert_events_are_logged({})


@istest
@with_settings_hosts()
class TestSocialAccount(CallbackTestPlan):
    def assert_auth_with_token_response(self, rv, builder, is_native=True):
        b = builder
        self.assert_ok_response(
            rv,
            **b.build_auth_response(
                account=b.get_account_response(),
                is_native=is_native,
                token=TEST_YANDEX_TOKEN1,
                token_expires_in=TEST_YANDEX_TOKEN_EXPIRES_IN1,
            )
        )

    def assert_auth_with_session_response(self, rv, builder):
        b = builder
        self.assert_ok_response(
            rv,
            skip=['cookies'],
            **b.build_auth_response(
                account=b.get_account_response(),
                is_native=False,
                default_uid=TEST_UID1,
            )
        )
        self.assert_session_cookies_ok(rv)

    def examine_native_start(self, builder):
        b = builder
        b.setup_task_for_token(b.build_task())
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_native_start(b)

        self.assert_auth_with_token_response(rv, b)

        b.setup_statbox_templates()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('native_start_submitted'),
            self.env.statbox.entry('callback_end'),
            self.env.statbox.entry('auth'),
        ])

        self.env.event_logger.assert_events_are_logged({})

    def examine_choose(self, builder):
        b = builder
        b.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([b.build_social_profile(uid=TEST_UID1)])
        b.setup_yandex_accounts([
            b.build_yandex_social_account(uid=TEST_UID1),
        ])
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_auth_with_token_response(rv, b)

        b.setup_statbox_templates()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('auth'),
        ])

        self.env.event_logger.assert_events_are_logged({})

    def examine_callback(self, builder):
        b = builder
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(b.build_task())
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([
            b.build_yandex_social_account(),
        ])
        b.setup_profile_creation()
        b.setup_session_generation()

        rv = self.request_callback(b)

        self.assert_auth_with_session_response(rv, b)

        b.setup_statbox_templates()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry('callback_end'),
            self.env.statbox.entry('auth'),
            self.env.statbox.entry('cookie_set'),
        ])

        self.env.event_logger.assert_events_are_logged({})


@istest
@with_settings_hosts()
class TestManyAccounts(CallbackTestPlan):
    def assert_choose_response(self, rv, builder, is_native=True):
        b = builder
        self.assert_ok_response(
            rv,
            state='choose',
            **b.build_ok_response(
                is_native=is_native,
                accounts=[
                    b.get_account_response(uid=TEST_UID1, login=TEST_SOCIAL_LOGIN1),
                    b.get_account_response(uid=TEST_UID2, login=TEST_SOCIAL_LOGIN2),
                ],
                has_enabled_accounts=True,
                account=None,
                profile_id=None,
            )
        )

    def assert_auth_response(self, rv, builder):
        b = builder
        self.assert_ok_response(
            rv,
            **b.build_auth_response(
                account=b.get_account_response(login=TEST_SOCIAL_LOGIN1),
                is_native=True,
                token=TEST_YANDEX_TOKEN1,
                token_expires_in=TEST_YANDEX_TOKEN_EXPIRES_IN1,
            )
        )

    def build_social_profiles(self, builder):
        return [
            builder.build_social_profile(uid=TEST_UID1),
            builder.build_social_profile(uid=TEST_UID2),
        ]

    def build_yandex_accounts(self, builder):
        return [
            builder.build_yandex_social_account(
                uid=TEST_UID1,
                login=TEST_SOCIAL_LOGIN1,
                social_alias=TEST_SOCIAL_LOGIN1,
            ),
            builder.build_yandex_social_account(
                uid=TEST_UID2,
                login=TEST_SOCIAL_LOGIN2,
                social_alias=TEST_SOCIAL_LOGIN2,
            ),
        ]

    def setup_statbox_templates(self, builder):
        builder.setup_statbox_templates()
        self.env.statbox.bind_entry(
            'callback_end',
            state='choose',
            accounts=str(TEST_UID1) + ',' + str(TEST_UID2),
            enabled_accounts_count='2',
        )

    def examine_native_start(self, builder):
        b = builder
        b.setup_task_for_token(b.build_task())
        b.setup_social_profiles(self.build_social_profiles(b))
        b.setup_yandex_accounts(self.build_yandex_accounts(b))

        rv = self.request_native_start(b)

        self.assert_choose_response(rv, b)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('native_start_submitted'),
            self.env.statbox.entry('callback_end'),
        ])

        self.env.event_logger.assert_events_are_logged({})

    def examine_choose(self, builder):
        b = builder
        b.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles(self.build_social_profiles(b))
        b.setup_yandex_accounts(self.build_yandex_accounts(b))
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_auth_response(rv, b)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('auth'),
        ])

        self.env.event_logger.assert_events_are_logged({})

    def examine_callback(self, builder):
        b = builder
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(b.build_task())
        b.setup_social_profiles(self.build_social_profiles(b))
        b.setup_yandex_accounts(self.build_yandex_accounts(b))

        rv = self.request_callback(b)

        self.assert_choose_response(rv, b, is_native=False)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry('callback_end'),
        ])

        self.env.event_logger.assert_events_are_logged({})


@istest
@with_settings_hosts()
class TestThirdPartyApp(CallbackTestPlan):
    def build_task(self, builder):
        return builder.build_task(app_party=APP_PARTY_3RD_PARTY)

    def setup_token_mode_track(self, builder):
        builder.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )

    def assert_application_invalid_response(self, rv, builder, is_native=True):
        self.assert_error_response(
            rv,
            ['application.invalid'],
            **builder.build_error_response(
                profile_id=None,
                has_enabled_accounts=None,
                account=None,
                is_native=is_native,
            )
        )

    def assert_auth_response(self, rv, builder, uid=TEST_UID1):
        b = builder
        self.assert_ok_response(
            rv,
            **b.build_auth_response(
                account=b.get_account_response(uid=uid),
                is_native=True,
                token=TEST_YANDEX_TOKEN1,
                token_expires_in=TEST_YANDEX_TOKEN_EXPIRES_IN1,
            )
        )

    def request_register(self, builder, headers=None):
        return builder.request_register(headers=headers)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))

        rv = self.request_native_start(b)

        self.assert_application_invalid_response(rv, b)

    def test_third_party_native_start(self):
        b = self.get_third_party_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_native_start(b)

        self.assert_auth_response(rv, b)

    def test_choose(self):
        b = self.get_primary_builder()
        self.setup_token_mode_track(b)
        b.setup_task_for_track(self.build_task(b))

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_application_invalid_response(rv, b)

    def test_third_party_choose(self):
        b = self.get_third_party_builder()
        self.setup_token_mode_track(b)
        b.setup_task_for_track(self.build_task(b))
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_auth_response(rv, b)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))

        rv = self.request_callback(b)

        self.assert_application_invalid_response(rv, b, is_native=False)

    def test_register(self):
        b = self.get_primary_builder()
        b.setup_track(
            social_output_mode=OUTPUT_MODE_SESSIONID,
        )
        b.setup_task_for_track(self.build_task(b))

        rv = self.request_register(b, headers=b.build_web_headers())

        self.assert_application_invalid_response(rv, b, is_native=False)

    def test_third_party_register(self):
        b = self.get_third_party_builder()
        self.setup_token_mode_track(b)
        b.setup_task_for_track(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_login_available_for_registration()
        b.setup_frodo_check()
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_register(b)

        self.assert_auth_response(rv, b, uid=1)
        b.assert_social_account_exists()
        b.assert_avatars_log_written()


@istest
@with_settings_hosts()
class TestYandexApp(CallbackTestPlan):
    def build_task(self, builder):
        return builder.build_task(app_party=APP_PARTY_YANDEX)

    def build_task_without_related_yandex_client(self, builder):
        return builder.build_task(
            app_party=APP_PARTY_YANDEX,
            related_yandex_client_id=None,
            related_yandex_client_secret=None,
        )

    def setup_token_mode_track(self, builder):
        builder.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )

    def assert_application_invalid_response(self, rv, builder, is_native=True):
        self.assert_error_response(
            rv,
            ['application.invalid'],
            **builder.build_error_response(
                profile_id=None,
                has_enabled_accounts=None,
                account=None,
                is_native=is_native,
            )
        )

    def assert_auth_with_token_response(self, rv, builder, uid=TEST_UID1):
        b = builder
        self.assert_ok_response(
            rv,
            **b.build_auth_response(
                account=b.get_account_response(uid=uid),
                is_native=True,
                token=TEST_YANDEX_TOKEN1,
                token_expires_in=TEST_YANDEX_TOKEN_EXPIRES_IN1,
            )
        )

    def assert_auth_with_session_response(self, rv, builder, uid=TEST_UID1):
        b = builder
        self.assert_ok_response(
            rv,
            skip=['cookies'],
            **b.build_auth_response(
                account=b.get_account_response(uid=uid),
                is_native=False,
                default_uid=uid,
            )
        )
        self.assert_session_cookies_ok(rv)

    def request_register(self, builder, headers=None):
        return builder.request_register(headers=headers)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_native_start(b)

        self.assert_auth_with_token_response(rv, b)

    def test_third_party_native_start(self):
        b = self.get_third_party_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_native_start(b)

        self.assert_auth_with_token_response(rv, b)

    def test_third_party_native_start__no_related_yandex_client(self):
        b = self.get_third_party_builder()
        b.setup_task_for_token(self.build_task_without_related_yandex_client(b))

        rv = self.request_native_start(b)

        self.assert_application_invalid_response(rv, b)

    def test_choose(self):
        b = self.get_primary_builder()
        self.setup_token_mode_track(b)
        b.setup_task_for_track(self.build_task(b))
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_auth_with_token_response(rv, b)

    def test_third_party_choose(self):
        b = self.get_third_party_builder()
        self.setup_token_mode_track(b)
        b.setup_task_for_track(self.build_task(b))
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_auth_with_token_response(rv, b)

    def test_third_party_choose__no_related_yandex_client(self):
        b = self.get_third_party_builder()
        self.setup_token_mode_track(b)
        b.setup_task_for_track(self.build_task_without_related_yandex_client(b))

        rv = self.request_choose(b, chosen_uid=TEST_UID1)

        self.assert_application_invalid_response(rv, b)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_session_generation()

        rv = self.request_callback(b)

        self.assert_auth_with_session_response(rv, b)

    def test_register(self):
        b = self.get_primary_builder()
        b.setup_track(
            social_output_mode=OUTPUT_MODE_SESSIONID,
        )
        b.setup_task_for_track(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_login_available_for_registration()
        b.setup_frodo_check()
        b.setup_profile_creation()
        b.setup_session_generation()

        rv = self.request_register(b, headers=b.build_web_headers())

        self.assert_auth_with_session_response(rv, b, uid=1)
        b.assert_social_account_exists()
        b.assert_avatars_log_written()

    def test_third_party_register(self):
        b = self.get_third_party_builder()
        self.setup_token_mode_track(b)
        b.setup_task_for_track(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_login_available_for_registration()
        b.setup_frodo_check()
        b.setup_profile_creation()
        b.setup_yandex_token_generation(TEST_YANDEX_TOKEN1)

        rv = self.request_register(b)

        self.assert_auth_with_token_response(rv, b, uid=1)
        b.assert_social_account_exists()
        b.assert_avatars_log_written()

    def test_third_party_register__no_related_yandex_client(self):
        b = self.get_third_party_builder()
        self.setup_token_mode_track(b)
        b.setup_task_for_track(self.build_task_without_related_yandex_client(b))

        rv = self.request_register(b)

        self.assert_application_invalid_response(rv, b)


@with_settings_hosts()
class TestInvalidToken(BaseTestCase):
    def setup_token_is_invalid(self, builder):
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            social_broker_error_response('OAuthTokenInvalidError'),
        )

    def request_native_start(self, builder):
        return builder.request_native_start()

    def assert_provider_token_invalid_response(self, rv, builder):
        self.assert_error_response(
            rv,
            ['provider_token.invalid'],
            **builder.build_error_response(
                account=None,
                profile_id=None,
                profile=None,
                has_enabled_accounts=None,
                provider=None,
            )
        )

    def examine_native_start(self, builder):
        b = builder
        self.setup_token_is_invalid(b)

        rv = self.request_native_start(b)

        self.assert_provider_token_invalid_response(rv, b)

    def test_native_start(self):
        self.examine_native_start(self.get_primary_builder())

    def test_third_party_native_start(self):
        self.examine_native_start(self.get_third_party_builder())


@istest
@with_settings_hosts()
class TestLoginToMailish(CallbackTestPlan):
    def assert_register_response(self, rv, builder, is_native=True):
        self.assert_ok_response(rv, **builder.build_register_response(is_native=is_native))

    def assert_uid_rejected_response(self, rv, builder):
        self.assert_error_response(
            rv,
            ['uid.rejected'],
            **builder.build_error_response(
                account=None,
                profile_id=None,
            )
        )

    def examine_native_start(self, builder):
        b = builder
        b.setup_task_for_token(b.build_task())
        b.setup_social_profiles([
            b.build_social_profile(),
        ])
        b.setup_yandex_accounts(
            profile_accounts=[
                b.build_yandex_mailish_account(),
            ],
            email_account=None,
        )

        rv = self.request_native_start(b)

        self.assert_register_response(rv, b)

    def examine_choose(self, builder):
        b = builder
        b.setup_track(
            social_output_mode=OUTPUT_MODE_XTOKEN,
        )
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([
            b.build_social_profile(uid=TEST_UID1, allow_auth=True),
            b.build_social_profile(uid=TEST_UID2, allow_auth=True),
        ])
        b.setup_yandex_accounts([
            b.build_yandex_mailish_account(uid=TEST_UID1),
            b.build_yandex_social_account(uid=TEST_UID2),
        ])

        rv = self.request_choose(b, chosen_uid=TEST_UID1)
        self.assert_uid_rejected_response(rv, b)

    def examine_callback(self, builder):
        b = builder
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(b.build_task())
        b.setup_social_profiles([
            b.build_social_profile(uid=TEST_UID1),
        ])
        b.setup_yandex_accounts(
            profile_accounts=[
                b.build_yandex_mailish_account(uid=TEST_UID1),
            ],
            email_account=None,
        )

        rv = self.request_callback(b)

        self.assert_register_response(rv, b, is_native=False)


@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestSessionMode(BaseTestCase):
    def setup_track(self, builder):
        builder.setup_track(
            social_output_mode=OUTPUT_MODE_SESSIONID,
        )

    def assert_auth_response(self, rv, builder, uid=TEST_UID1):
        b = builder
        self.assert_ok_response(
            rv,
            skip=['cookies'],
            **b.build_auth_response(
                is_native=False,
                account=b.get_account_response(uid=uid),
                default_uid=uid,
            )
        )
        self.assert_session_cookies_ok(rv)

    def request_choose(self, builder):
        return builder.request_choose(
            uid=TEST_UID1,
            headers=builder.build_web_headers(),
        )

    def request_register(self, builder):
        return builder.request_register(headers=builder.build_web_headers())

    def assert_track_invalid_state_response(self, rv, builder):
        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            **builder.build_error_response(
                is_native=False,
                provider=None,
                profile=None,
                profile_id=None,
                has_enabled_accounts=None,
                account=None,
            )
        )

    def test_choose(self):
        b = self.get_primary_builder()
        self.setup_track(b)
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        b.setup_session_generation()

        rv = self.request_choose(b)

        self.assert_auth_response(rv, b)

    def test_third_party_choose(self):
        b = self.get_third_party_builder()
        self.setup_track(b)

        rv = self.request_choose(b)

        self.assert_track_invalid_state_response(rv, b)

    def test_register(self):
        b = self.get_primary_builder()
        self.setup_track(b)
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([])
        b.setup_login_available_for_registration()
        b.setup_frodo_check()
        b.setup_profile_creation()
        b.setup_session_generation()

        rv = self.request_register(b)

        self.assert_auth_response(rv, b, uid=1)

    def test_third_party_register(self):
        b = self.get_third_party_builder()
        self.setup_track(b)

        rv = self.request_register(b)

        self.assert_track_invalid_state_response(rv, b)


@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestAuthorizationCodeMode(BaseTestCase):
    def setup_track(self, builder):
        builder.setup_track(
            social_output_mode=OUTPUT_MODE_AUTHORIZATION_CODE,
        )

    def assert_auth_response(self, rv, builder, uid=TEST_UID1):
        b = builder
        self.assert_ok_response(
            rv,
            **b.build_auth_response(
                is_native=False,
                account=b.get_account_response(uid=uid),
                yandex_authorization_code=TEST_YANDEX_AUTHORIZATION_CODE1,
            )
        )

    def request_choose(self, builder):
        return builder.request_choose(uid=TEST_UID1)

    def request_register(self, builder):
        return builder.request_register()

    def assert_track_invalid_state_response(self, rv, builder):
        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            **builder.build_error_response(
                is_native=False,
                provider=None,
                profile=None,
                profile_id=None,
                has_enabled_accounts=None,
                account=None,
            )
        )

    def setup_yandex_auth_code_generation(self, builder):
        builder.setup_yandex_auth_code_generation(TEST_YANDEX_AUTHORIZATION_CODE1)

    def test_choose(self):
        b = self.get_primary_builder()
        self.setup_track(b)
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([b.build_social_profile()])
        b.setup_yandex_accounts([b.build_yandex_social_account()])
        b.setup_profile_creation()
        self.setup_yandex_auth_code_generation(b)

        rv = self.request_choose(b)

        self.assert_auth_response(rv, b)

    def test_third_party_choose(self):
        b = self.get_third_party_builder()
        self.setup_track(b)

        rv = self.request_choose(b)

        self.assert_track_invalid_state_response(rv, b)

    def test_register(self):
        b = self.get_primary_builder()
        self.setup_track(b)
        b.setup_task_for_track(b.build_task())
        b.setup_social_profiles([])
        b.setup_login_available_for_registration()
        b.setup_frodo_check()
        b.setup_profile_creation()
        self.setup_yandex_auth_code_generation(b)

        rv = self.request_register(b)

        self.assert_auth_response(rv, b, uid=1)

    def test_third_party_register(self):
        b = self.get_third_party_builder()
        self.setup_track(b)

        rv = self.request_register(b)

        self.assert_track_invalid_state_response(rv, b)


@with_settings_hosts()
class TestUnknownProvider(BaseTestCase):
    def setup_provider_is_unknown(self, builder):
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            social_broker_error_response('ProviderUnknownError'),
        )

    def request_native_start(self, builder):
        return builder.request_native_start()

    def assert_provider_token_invalid_response(self, rv, builder):
        self.assert_error_response(
            rv,
            ['provider.invalid'],
            **builder.build_error_response(
                account=None,
                profile_id=None,
                profile=None,
                has_enabled_accounts=None,
                provider=None,
            )
        )

    def examine_native_start(self, builder):
        b = builder
        self.setup_provider_is_unknown(b)

        rv = self.request_native_start(b)

        self.assert_provider_token_invalid_response(rv, b)

    def test_native_start(self):
        self.examine_native_start(self.get_primary_builder())

    def test_third_party_native_start(self):
        self.examine_native_start(self.get_third_party_builder())


@with_settings_hosts()
class TestUnknownApplication(BaseTestCase):
    def setup_application_is_unknown(self, builder):
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            social_broker_error_response('ApplicationUnknownError'),
        )

    def request_native_start(self, builder):
        return builder.request_native_start()

    def assert_provider_token_invalid_response(self, rv, builder):
        self.assert_error_response(
            rv,
            ['application.invalid'],
            **builder.build_error_response(
                account=None,
                profile_id=None,
                profile=None,
                has_enabled_accounts=None,
                provider=None,
            )
        )

    def examine_native_start(self, builder):
        b = builder
        self.setup_application_is_unknown(b)

        rv = self.request_native_start(b)

        self.assert_provider_token_invalid_response(rv, b)

    def test_native_start(self):
        self.examine_native_start(self.get_primary_builder())

    def test_third_party_native_start(self):
        self.examine_native_start(self.get_third_party_builder())


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestEmaillessProfile(BaseTestCase):
    def assert_register_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.pop('email', None)
        self.assert_ok_response(
            rv,
            **builder.build_register_response(
                is_native=is_native,
                profile=profile_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=None)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])

        rv = b.request_callback()

        self.assert_register_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])

        rv = b.request_native_start()

        self.assert_register_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountIsPortal(BaseTestCase):
    def assert_suggest_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)

        suggested_accounts_response = [
            builder.get_suggested_account_response(),
        ]

        self.assert_ok_response(
            rv,
            **builder.build_suggest_response(
                auth_retpath=TEST_RETPATH1,
                auth_track_id=TEST_TRACK_ID1,
                can_register_social=True,
                is_native=is_native,
                profile=profile_response,
                register_social_track_id=TEST_TRACK_ID1,
                suggested_accounts=suggested_accounts_response,
            )
        )

    def assert_register_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)
        self.assert_ok_response(
            rv,
            **builder.build_register_response(
                is_native=is_native,
                profile=profile_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_YANDEX_EMAIL1)

    def setup_statbox_templates(self, builder):
        builder.setup_statbox_templates()
        self.env.statbox.bind_entry(
            'native_start_submitted',
            host='passport.yandex.ru',
        )
        self.env.statbox.bind_entry(
            'callback_end',
            _exclude=['accounts'],
            enabled_accounts_count='0',
            state='suggest',
        )

    def build_yandex_full_account(self, builder):
        return builder.build_yandex_full_account(
            default_avatar_key=TEST_DEFAULT_AVATAR1,
            display_login=TEST_DISPLAY_LOGIN1,
            emails=[
                self.env.email_toolkit.create_native_email(*TEST_YANDEX_EMAIL1.split('@')),
            ],
            login=TEST_LOGIN1,
            uid=TEST_UID1,
        )

    def build_headers(self, builder, **kwargs):
        defaults = dict(host='passport.yandex.ru')
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return builder.build_headers(**kwargs)

    def assert_blackbox_get_suggested_account_called(self, request):
        request.assert_post_data_contains(
            dict(
                aliases='all_with_hidden',
                email_attributes='all',
                emails='getall',
                format='json',
                get_public_name='yes',
                is_display_name_empty='yes',
                login=TEST_YANDEX_EMAIL1,
                method='userinfo',
                regname='yes',
            ),
        )
        request.assert_contains_attributes(
            {
                'account.is_disabled',
                'password.encrypted',
                'account.2fa_on',
                'account.default_email',
            },
        )
        request.assert_contains_dbfields(
            {
                'subscription.suid.67',
            },
        )

    def request_native_start(self, builder, headers=None):
        if headers is None:
            headers = self.build_headers(builder)
        return builder.request_native_start(headers=headers)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_full_account(b))

        rv = b.request_callback(headers=self.build_headers(b))

        self.assert_suggest_response(rv, b, is_native=False)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry('callback_end'),
        ])

        self.env.event_logger.assert_events_are_logged({})
        self.assert_blackbox_get_suggested_account_called(self.env.blackbox.requests[0])

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_full_account(b))

        rv = self.request_native_start(b)

        self.assert_suggest_response(rv, b)

        self.setup_statbox_templates(b)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('native_start_submitted'),
            self.env.statbox.entry('callback_end'),
        ])

        self.env.event_logger.assert_events_are_logged({})
        self.assert_blackbox_get_suggested_account_called(self.env.blackbox.requests[0])

    def test_third_party_native_start(self):
        b = self.get_third_party_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_full_account(b))

        rv = self.request_native_start(b)

        self.assert_register_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
    SOCIAL_SUGGEST_RELATED_ACCOUNT_ENABLED=False,
)
class TestSuggestRelatedAccoutDisabled(BaseTestCase):
    def assert_register_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)
        self.assert_ok_response(
            rv,
            **builder.build_register_response(
                is_native=is_native,
                profile=profile_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_YANDEX_EMAIL1)

    def examine_native_start(self, builder):
        b = builder
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=b.build_yandex_full_account())

        rv = b.request_native_start()

        self.assert_register_response(rv, b)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=b.build_yandex_full_account())

        rv = b.request_callback()

        self.assert_register_response(rv, b, is_native=False)

    def test_native_start(self):
        self.examine_native_start(self.get_primary_builder())

    def test_third_party_native_start(self):
        self.examine_native_start(self.get_third_party_builder())


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountIsLite(BaseTestCase):
    def assert_suggest_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_EMAIL1)

        suggested_accounts_response = [builder.get_suggested_lite_response()]

        self.assert_ok_response(
            rv,
            skip=['auth_retpath'],
            **builder.build_suggest_response(
                auth_track_id=TEST_TRACK_ID1,
                is_native=is_native,
                profile=profile_response,
                suggested_accounts=suggested_accounts_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_EMAIL1)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=b.build_yandex_lite_account())

        rv = b.request_callback()

        self.assert_suggest_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=b.build_yandex_lite_account())

        rv = b.request_native_start()

        self.assert_suggest_response(rv, b)


@istest
@with_settings_hosts()
class TestRelatedAccountIsDisabledPortal(BaseTestCase):
    def assert_register_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)
        self.assert_ok_response(
            rv,
            **builder.build_register_response(
                is_native=is_native,
                profile=profile_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_YANDEX_EMAIL1)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=b.build_yandex_full_account(enabled=False))

        rv = b.request_callback()

        self.assert_register_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=b.build_yandex_full_account(enabled=False))

        rv = b.request_native_start()

        self.assert_register_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountNotFoundProfileEmailNotYandex(BaseTestCase):
    def setUp(self):
        super(TestRelatedAccountNotFoundProfileEmailNotYandex, self).setUp()
        self.track_id_generator.set_side_effect(
            [
                TEST_TRACK_ID1,
                TEST_TRACK_ID2,
            ],
        )

    def assert_suggest_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_EMAIL1)

        self.assert_ok_response(
            rv,
            skip=['auth_retpath'],
            **builder.build_suggest_response(
                can_register_lite=True,
                is_native=is_native,
                process_uuid=TEST_PROCESS_UUID1,
                profile=profile_response,
                register_lite_track_id=TEST_TRACK_ID2,
                retpath=TEST_RETPATH1,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_EMAIL1)

    def check_social_auth_track_ok(self):
        track = self.track_manager.read(TEST_TRACK_ID1)
        expected = dict(
            retpath=TEST_RETPATH1,
        )
        for key in expected:
            self.assertEqual(getattr(track, key), expected[key])

    def check_register_lite_track_ok(self, social_task_data):
        track = self.track_manager.read(TEST_TRACK_ID2)

        expected = dict(
            process_name=PROCESS_WEB_REGISTRATION,
            process_uuid=TEST_PROCESS_UUID1,
            retpath=TEST_RETPATH1,
            social_task_data=task_data_response(**social_task_data)
        )
        for key in expected:
            self.assertEqual(getattr(track, key), expected[key])

    def build_headers(self, builder, **kwargs):
        defaults = dict(host='passport.yandex.ru')
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return builder.build_headers(**kwargs)

    def setup_login_available_for_registration(self):
        self.env.blackbox.set_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL1: 'free'}),
        )

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(
            retpath=TEST_RETPATH1,
            social_output_mode=OUTPUT_MODE_SESSIONID,
            process_uuid=TEST_PROCESS_UUID1,
        )

        task = self.build_task(b)
        b.setup_task_for_task_id(task)

        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=None)
        self.setup_login_available_for_registration()

        rv = b.request_callback(task_id=TEST_SOCIAL_TASK_ID1)

        self.assert_suggest_response(rv, b, is_native=False)

        self.check_social_auth_track_ok()
        self.check_register_lite_track_ok(social_task_data=task)

    def test_native_start(self):
        b = self.get_primary_builder()

        task = self.build_task(b)
        b.setup_task_for_token(task)

        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=None)
        self.setup_login_available_for_registration()

        rv = b.request_native_start(
            headers=self.build_headers(b),
            process_uuid=TEST_PROCESS_UUID1,
            retpath=TEST_RETPATH1,
        )

        self.assert_suggest_response(rv, b)

        self.check_social_auth_track_ok()
        self.check_register_lite_track_ok(social_task_data=task)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
    LITE_LOGIN_BLACKLISTED_DOMAINS=[domain_from_email(TEST_EMAIL1)],
)
class TestRelatedAccountNotFoundProfileEmailInvalidLiteLogin(BaseTestCase):
    def assert_register_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_EMAIL1)
        self.assert_ok_response(
            rv,
            **builder.build_register_response(
                is_native=is_native,
                profile=profile_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_EMAIL1)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)

        task = self.build_task(b)
        b.setup_task_for_task_id(task)

        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=None)

        rv = b.request_callback(task_id=TEST_SOCIAL_TASK_ID1)

        self.assert_register_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()

        task = self.build_task(b)
        b.setup_task_for_token(task)

        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=None)

        rv = b.request_native_start()

        self.assert_register_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountNotFoundProfileEmailNotAvailableLiteLogin(BaseTestCase):
    def assert_register_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_EMAIL1)
        self.assert_ok_response(
            rv,
            **builder.build_register_response(
                is_native=is_native,
                profile=profile_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_EMAIL1)

    def setup_login_unavailable_for_registration(self):
        self.env.blackbox.set_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL1: 'occupied'}),
        )

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)

        task = self.build_task(b)
        b.setup_task_for_task_id(task)

        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=None)
        self.setup_login_unavailable_for_registration()

        rv = b.request_callback(task_id=TEST_SOCIAL_TASK_ID1)

        self.assert_register_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()

        task = self.build_task(b)
        b.setup_task_for_token(task)

        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=None)
        self.setup_login_unavailable_for_registration()

        rv = b.request_native_start()

        self.assert_register_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountIsSocialWithLogin(BaseTestCase):
    def assert_register_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)
        self.assert_ok_response(
            rv,
            **builder.build_register_response(
                is_native=is_native,
                profile=profile_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_YANDEX_EMAIL1)

    def build_account(self, builder):
        return builder.build_yandex_social_account(
            aliases=dict(portal=TEST_LOGIN1),
        )

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_account(b))

        rv = b.request_callback()

        self.assert_register_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_account(b))

        rv = b.request_native_start()

        self.assert_register_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountIsPortalWithStrongPasswordPolicy(BaseTestCase):
    def assert_suggest_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)

        suggested_accounts_response = [
            builder.get_suggested_account_response(
                default_avatar='',
                default_email=None,
                display_login='login',
            ),
        ]

        self.assert_ok_response(
            rv,
            skip=['auth_retpath'],
            **builder.build_suggest_response(
                auth_track_id=TEST_TRACK_ID1,
                can_register_social=True,
                is_native=is_native,
                profile=profile_response,
                register_social_track_id=TEST_TRACK_ID1,
                suggested_accounts=suggested_accounts_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_YANDEX_EMAIL1)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(
            email_account=b.build_yandex_full_account(
                dbfields={
                    'subscription.suid.67': '1',
                },
            ),
        )

        rv = b.request_callback()

        self.assert_suggest_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(
            email_account=b.build_yandex_full_account(
                dbfields={
                    'subscription.suid.67': '1',
                },
            ),
        )

        rv = b.request_native_start()

        self.assert_suggest_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestProcessUuid(BaseTestCase):
    def setUp(self):
        super(TestProcessUuid, self).setUp()
        self.b = self.get_primary_builder()

    def assert_register_response(self, rv, is_native=True):
        profile_response = self.b.get_profile_response()
        profile_response.pop('email', None)
        self.assert_ok_response(
            rv,
            **self.b.build_register_response(
                is_native=is_native,
                process_uuid=TEST_PROCESS_UUID1,
                profile=profile_response,
            )
        )

    def build_task(self):
        return self.b.build_task(email=None)

    def setup_social_profiles(self):
        self.b.setup_social_profiles(list())

    def test_native_start(self):
        self.b.setup_task_for_token(self.build_task())
        self.setup_social_profiles()

        rv = self.b.request_native_start(process_uuid=TEST_PROCESS_UUID1)

        self.assert_register_response(rv)

        track = self.track_manager.read(TEST_TRACK_ID1)
        self.assertEqual(track.process_uuid, TEST_PROCESS_UUID1)

    def test_callback(self):
        self.b.setup_track(
            process_uuid=TEST_PROCESS_UUID1,
            social_output_mode=OUTPUT_MODE_SESSIONID,
        )
        self.b.setup_task_for_task_id(self.build_task())
        self.setup_social_profiles()

        rv = self.b.request_callback()

        self.assert_register_response(rv, is_native=False)

        track = self.track_manager.read(TEST_TRACK_ID1)
        self.assertEqual(track.process_uuid, TEST_PROCESS_UUID1)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountIsPortalWith2Fa(BaseTestCase):
    def assert_suggest_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)

        suggested_accounts_response = [
            builder.get_suggested_account_response(
                default_avatar='',
                default_email=None,
                display_login='login',
            ),
        ]

        self.assert_ok_response(
            rv,
            skip=['auth_retpath'],
            **builder.build_suggest_response(
                auth_track_id=TEST_TRACK_ID1,
                can_register_social=True,
                is_native=is_native,
                profile=profile_response,
                register_social_track_id=TEST_TRACK_ID1,
                suggested_accounts=suggested_accounts_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_YANDEX_EMAIL1)

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(
            email_account=b.build_yandex_full_account(
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )

        rv = b.request_callback()

        self.assert_suggest_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(
            email_account=b.build_yandex_full_account(
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )

        rv = b.request_native_start()

        self.assert_suggest_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountIsLiteWith2Fa(BaseTestCase):
    def assert_suggest_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_EMAIL1)

        suggested_accounts_response = [builder.get_suggested_lite_response()]

        self.assert_ok_response(
            rv,
            skip=['auth_retpath'],
            **builder.build_suggest_response(
                auth_track_id=TEST_TRACK_ID1,
                can_register_social=True,
                is_native=is_native,
                profile=profile_response,
                register_social_track_id=TEST_TRACK_ID1,
                suggested_accounts=suggested_accounts_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_EMAIL1)

    def build_yandex_lite_account(self, builder):
        return builder.build_yandex_lite_account(
            attributes={
                'account.2fa_on': '1',
            },
        )

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_lite_account(b))

        rv = b.request_callback()

        self.assert_suggest_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_lite_account(b))

        rv = b.request_native_start()

        self.assert_suggest_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
)
class TestRelatedAccountIsLiteWithStrongPasswordPolicy(BaseTestCase):
    def assert_suggest_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_EMAIL1)

        suggested_accounts_response = [builder.get_suggested_lite_response()]

        self.assert_ok_response(
            rv,
            skip=['auth_retpath'],
            **builder.build_suggest_response(
                auth_track_id=TEST_TRACK_ID1,
                can_register_social=True,
                is_native=is_native,
                profile=profile_response,
                register_social_track_id=TEST_TRACK_ID1,
                suggested_accounts=suggested_accounts_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_EMAIL1)

    def build_yandex_lite_account(self, builder):
        return builder.build_yandex_lite_account(
            dbfields={
                'subscription.suid.67': '1',
            },
        )

    def test_callback(self):
        b = self.get_primary_builder()
        b.setup_track(social_output_mode=OUTPUT_MODE_SESSIONID)
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_lite_account(b))

        rv = b.request_callback()

        self.assert_suggest_response(rv, b, is_native=False)

    def test_native_start(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_lite_account(b))

        rv = b.request_native_start()

        self.assert_suggest_response(rv, b)


@istest
@with_settings_hosts(
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=False,
    SOCIAL_SUGGEST_RELATED_ACCOUNT_CONSUMERS_RE_LIST=[re.compile('^%s$' % TEST_CONSUMER1)],
)
class TestSuggestRelatedAccoutOnlyToConsumer(BaseTestCase):
    def assert_suggest_response(self, rv, builder, is_native=True):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)

        suggested_accounts_response = [
            builder.get_suggested_account_response(),
        ]

        self.assert_ok_response(
            rv,
            **builder.build_suggest_response(
                auth_retpath=TEST_RETPATH1,
                auth_track_id=TEST_TRACK_ID1,
                can_register_social=True,
                is_native=is_native,
                profile=profile_response,
                register_social_track_id=TEST_TRACK_ID1,
                suggested_accounts=suggested_accounts_response,
            )
        )

    def assert_register_response(
        self,
        rv,
        builder,
        is_native=True,
        broker_consumer=TEST_CONSUMER1,
    ):
        profile_response = builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)
        self.assert_ok_response(
            rv,
            **builder.build_register_response(
                broker_consumer=broker_consumer,
                is_native=is_native,
                profile=profile_response,
            )
        )

    def build_task(self, builder):
        return builder.build_task(email=TEST_YANDEX_EMAIL1)

    def build_yandex_full_account(self, builder):
        return builder.build_yandex_full_account(
            default_avatar_key=TEST_DEFAULT_AVATAR1,
            display_login=TEST_DISPLAY_LOGIN1,
            emails=[
                self.env.email_toolkit.create_native_email(*TEST_YANDEX_EMAIL1.split('@')),
            ],
            login=TEST_LOGIN1,
            uid=TEST_UID1,
        )

    def test_callback_allowed_consumer(self):
        b = self.get_primary_builder()
        b.setup_track(
            social_broker_consumer=TEST_CONSUMER1,
            social_output_mode=OUTPUT_MODE_SESSIONID,
        )
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_full_account(b))

        rv = b.request_callback()

        self.assert_suggest_response(rv, b, is_native=False)

    def test_callback_forbidden_consumer(self):
        b = self.get_primary_builder()
        b.setup_track(
            social_broker_consumer='forbidden',
            social_output_mode=OUTPUT_MODE_SESSIONID,
        )
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_full_account(b))

        rv = b.request_callback()

        self.assert_register_response(
            rv,
            b,
            is_native=False,
            broker_consumer='forbidden',
        )

    def test_callback_broker_consumer_undefined(self):
        b = self.get_primary_builder()
        b.setup_track(
            social_broker_consumer=None,
            social_output_mode=OUTPUT_MODE_SESSIONID,
        )
        b.setup_task_for_task_id(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_full_account(b))

        rv = b.request_callback()

        self.assert_register_response(
            rv,
            b,
            is_native=False,
            broker_consumer=None,
        )

    def test_native_start_allowed_consumer(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_full_account(b))

        rv = b.request_native_start()

        self.assert_suggest_response(rv, b)

    def test_native_start_forbidden_consumer(self):
        b = self.get_primary_builder()
        b.setup_task_for_token(self.build_task(b))
        b.setup_social_profiles([])
        b.setup_yandex_accounts(email_account=self.build_yandex_full_account(b))

        rv = b.request_native_start(broker_consumer='forbidden')

        self.assert_register_response(rv, b, broker_consumer='forbidden')
