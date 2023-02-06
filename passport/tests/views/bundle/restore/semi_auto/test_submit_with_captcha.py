# -*- coding: utf-8 -*-
import time

from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.api.settings.constants.restore import (
    RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE,
    RESTORE_REQUEST_SOURCE_FOR_DIRECT_URL,
)
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_base import BaseTestRestoreSemiAutoView
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_UID,
    TEST_LITE_LOGIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_REQUEST_SOURCE,
)
from passport.backend.api.views.bundle.restore.semi_auto.base import MULTISTEP_FORM_VERSION
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_ERROR_INVALID_CHARACTERS_IN_LOGIN,
    BLACKBOX_ERROR_LOGIN_EMPTY_DOMAIN_PART,
)
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    settings_context,
    with_settings_hosts,
)
from six import string_types


eq_ = iterdiff(eq_)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    RESTORE_SEMI_AUTO_LEARNING_DENOMINATORS={RESTORE_REQUEST_SOURCE_FOR_DIRECT_URL: 1},
)
class TestRestoreSemiAutoSubmitView(BaseTestRestoreSemiAutoView):
    def setUp(self):
        super(TestRestoreSemiAutoSubmitView, self).setUp()

        self.default_url = '/1/bundle/restore/semi_auto/submit_with_captcha/?consumer=dev'

    def setup_statbox_templates(self):
        super(TestRestoreSemiAutoSubmitView, self).setup_statbox_templates(
            step='submit_with_captcha',
            request_source=TEST_REQUEST_SOURCE,
            is_unconditional_pass='0',
        )
        self.env.statbox.bind_entry(
            'submit_with_captcha_passed',
            action='submit_with_captcha_passed',
            version=MULTISTEP_FORM_VERSION,
        )

    def set_track_values(self, is_captcha_checked=True, is_captcha_recognized=True):
        params = {
            'is_captcha_checked': is_captcha_checked,
            'is_captcha_recognized': is_captcha_recognized,
        }
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for attr_name, value in params.items():
                setattr(track, attr_name, value)
            self.orig_track = track.snapshot()

    def query_params(self, login=TEST_DEFAULT_LOGIN, is_unconditional_pass=None, request_source=None):
        params = dict(
            login=login,
            track_id=self.track_id,
            is_unconditional_pass=is_unconditional_pass,
            request_source=request_source,
        )
        return params

    def assert_track_ok(self, **params):
        """Трек заполнен полностью и корректно"""
        track = self.track_manager.read(self.track_id)
        for attr_name, value in params.items():
            actual_value = getattr(track, attr_name)
            expected_value = str(value) if not isinstance(value, (string_types, bool)) else value
            eq_(actual_value, expected_value, [attr_name, actual_value, expected_value])

    def assert_submit_recorded_to_statbox(self, uid=TEST_DEFAULT_UID, login=TEST_DEFAULT_LOGIN,
                                          is_unconditional_pass=False, request_source=TEST_REQUEST_SOURCE,
                                          is_for_learning=False):
        entry = self.env.statbox.entry(
            'submit_with_captcha_passed',
            login=login,
            uid=str(uid),
            is_for_learning=tskv_bool(is_for_learning),
            is_unconditional_pass=tskv_bool(is_unconditional_pass),
            request_source=request_source,
        )
        self.env.statbox.assert_has_written([entry])

    def test_captcha_not_checked_fails(self):
        self.set_track_values(is_captcha_checked=False, is_captcha_recognized=False)
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, error_codes=['user.not_verified'])

        self.assert_track_unchanged()
        self.assert_state_or_error_recorded_to_statbox(error='user.not_verified', _exclude=['uid'])

    def test_captcha_checked_but_not_recognized_fails(self):
        self.set_track_values(is_captcha_checked=True, is_captcha_recognized=False)
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, error_codes=['user.not_verified'])

        self.assert_track_unchanged()
        self.assert_state_or_error_recorded_to_statbox(error='user.not_verified', _exclude=['uid'])

    def test_login_not_found_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, error_codes=['account.not_found'])

        self.assert_track_unchanged()
        self.assert_state_or_error_recorded_to_statbox(error='account.not_found', _exclude=['uid'])

    def test_incomplete_pdd_state_redirect(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_LOGIN,
                uid=TEST_PDD_UID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(login=TEST_PDD_LOGIN), self.get_headers())

        self.assert_ok_response(resp, state='complete_pdd')

        self.assert_track_unchanged()
        self.assert_state_or_error_recorded_to_statbox(
            state='complete_pdd',
            login=TEST_PDD_LOGIN,
            uid=str(TEST_PDD_UID),
        )

    def test_submit_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(country='tr'),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            country='tr',
        )
        self.assert_submit_recorded_to_statbox()

    @parameterized.expand([
        (BLACKBOX_ERROR_LOGIN_EMPTY_DOMAIN_PART,),
        (BLACKBOX_ERROR_INVALID_CHARACTERS_IN_LOGIN,),
    ])
    def test_submit__userinfo_fails_with_invalid_params__error(self, blackbox_error_prefix):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            blackbox.BlackboxInvalidParamsError(blackbox_error_prefix + '. request_id=123'),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['account.not_found'])
        self.assert_state_or_error_recorded_to_statbox(error='account.not_found', _exclude=['uid'])

    def test_submit_with_no_country_on_account_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(country=None),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            country='ru',
        )
        self.assert_submit_recorded_to_statbox()

    def test_submit_with_2fa_account_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(password='', attributes={'account.2fa_on': '1'}),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
        )
        self.assert_submit_recorded_to_statbox()

    def test_submit_with_unconditional_pass_ok(self):
        """Флаг пропуска проверок сохраняется в трек"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(is_unconditional_pass=True), self.get_headers())

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            is_unconditional_pass=True,
        )
        self.assert_submit_recorded_to_statbox(is_unconditional_pass=True)

    def test_submit_with_unconditional_pass_with_disabled_account_ok(self):
        """Флаг пропуска проверок позволяет пройти проверку заблокированному пользователю"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(is_unconditional_pass=True), self.get_headers())

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            is_unconditional_pass=True,
        )
        self.assert_submit_recorded_to_statbox(is_unconditional_pass=True)

    def test_submit_with_disabled_on_deletion_account_ok(self):
        """Аккаунт заблокирован при удалении не слишком давно"""
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        userinfo = self.default_userinfo_response(
            attributes={
                'account.deletion_operation_started_at': deletion_started_at,
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
        )
        self.assert_submit_recorded_to_statbox()

    def test_submit_with_unconditional_pass_with_disabled_lite_account_ok(self):
        """Флаг пропуска проверок позволяет пройти проверку заблокированному lite-пользователю"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                self.default_userinfo_response(uid=None),
                self.default_userinfo_response(
                    enabled=False,
                    aliases={
                        'lite': TEST_LITE_LOGIN,
                    },
                ),
            ],
        )
        self.set_track_values()
        resp = self.make_request(
            self.query_params(is_unconditional_pass=True, login=TEST_LITE_LOGIN),
            self.get_headers(),
        )

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_LITE_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            is_unconditional_pass=True,
        )
        self.assert_submit_recorded_to_statbox(is_unconditional_pass=True, login=TEST_LITE_LOGIN)

    def test_submit_with_unconditional_pass_with_incomplete_pdd_ok(self):
        """Флаг пропуска проверок позволяет пройти проверку недорегистрированному ПДД-пользователю"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_LOGIN,
                uid=TEST_PDD_UID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )
        self.set_track_values()
        resp = self.make_request(
            self.query_params(is_unconditional_pass=True, login=TEST_PDD_LOGIN),
            self.get_headers(),
        )

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_PDD_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            is_unconditional_pass=True,
        )
        self.assert_submit_recorded_to_statbox(is_unconditional_pass=True, login=TEST_PDD_LOGIN, uid=TEST_PDD_UID)

    def test_submit_with_unconditional_pass_with_account_without_password_ok(self):
        """Флаг пропуска проверок позволяет пройти проверку пользователю без пароля"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(password=''),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(is_unconditional_pass=True), self.get_headers())

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            is_unconditional_pass=True,
        )
        self.assert_submit_recorded_to_statbox(is_unconditional_pass=True)

    def test_submit_suitable_for_learning_ok(self):
        """Анкета подходит по условиям для обучения"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        with settings_context(
            RESTORE_SEMI_AUTO_LEARNING_DENOMINATORS={RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE: 1},
        ):
            resp = self.make_request(
                self.query_params(request_source=RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE),
                self.get_headers(),
            )

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            version=MULTISTEP_FORM_VERSION,
            request_source=RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE,
            is_for_learning=True,
        )
        self.assert_submit_recorded_to_statbox(
            request_source=RESTORE_REQUEST_SOURCE_FOR_AUTO_RESTORE,
            is_for_learning=True,
        )

    def test_submit_not_suitable_for_learning_not_in_share_ok(self):
        """Анкета не подходит по условиям для обучения, пользователь не попал в долю"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        with settings_context(
            RESTORE_SEMI_AUTO_LEARNING_DENOMINATORS={RESTORE_REQUEST_SOURCE_FOR_DIRECT_URL: 0},
        ):
            resp = self.make_request(
                self.query_params(request_source=RESTORE_REQUEST_SOURCE_FOR_DIRECT_URL),
                self.get_headers(),
            )

        self.assert_ok_response(resp)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            version=MULTISTEP_FORM_VERSION,
            request_source=RESTORE_REQUEST_SOURCE_FOR_DIRECT_URL,
            is_for_learning=False,
        )
        self.assert_submit_recorded_to_statbox(
            request_source=RESTORE_REQUEST_SOURCE_FOR_DIRECT_URL,
        )
