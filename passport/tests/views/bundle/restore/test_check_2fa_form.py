# -*- coding: utf-8 -*-

import base64

from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    device_id_statbox_entry,
    names_statbox_entry,
    password_matches_statbox_entry,
    user_env_auths_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_HINT_ANSWER,
    TEST_DEFAULT_LASTNAME,
    TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
    TEST_INVALID_HINT_ANSWER,
    TEST_IP,
    TEST_OPERATION_TTL,
    TEST_PASSWORD,
    TEST_PDD_CYRILLIC_DOMAIN,
    TEST_PDD_DOMAIN,
    TEST_PHONE,
    TEST_PHONE2,
    USUAL_2FA_RESTORE_METHODS,
)
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonMethodTestsMixin,
    CommonTestsMixin,
    eq_,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import (
    RESTORE_METHOD_PHONE,
    RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
    RESTORE_METHOD_SEMI_AUTO_FORM,
    RESTORE_STATE_METHOD_PASSED,
    RESTORE_STATE_METHOD_SELECTED,
    RESTORE_STEP_CHECK_2FA_FORM,
)
from passport.backend.api.views.bundle.restore.factors import PASSWORD_MATCH_DEPTH
from passport.backend.core import authtypes
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_test_pwd_hashes_response
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    app_key_info,
    auth_successful_aggregated_browser_info,
    auth_successful_aggregated_runtime_auth_item,
    auth_successful_aggregated_runtime_auths_item,
    auth_successful_aggregated_runtime_ip_info,
    auths_successful_aggregated_runtime_response,
    event_item,
    events_response,
)
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_NOT_SET,
)
from passport.backend.core.counters import restore_counter
from passport.backend.core.historydb.events import (
    EVENT_APP_KEY_INFO,
    EVENT_INFO_PASSWORD,
)
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    RESTORE_2FA_FORM_CHECK_ERRORS_CAPTCHA_THRESHOLD=3,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class RestoreCheck2FAFormTestCase(RestoreBaseTestCase, CommonTestsMixin,
                                  AccountValidityTestsMixin, CommonMethodTestsMixin):

    restore_step = RESTORE_STEP_CHECK_2FA_FORM

    default_url = '/1/bundle/restore/2fa_form/check/'

    account_validity_tests_extra_statbox_params = {
        'is_captcha_required': '0',
    }

    def setUp(self):
        super(RestoreCheck2FAFormTestCase, self).setUp()

        self.env.statbox.bind_entry(
            '2fa_form_passed',
            _inherit_from='passed',
            user_env_check_passed='1',
            password_check_passed='1',
            names_check_passed='1',
            answer_check_passed='1',
            suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
            current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
            is_captcha_required='0',
        )
        self.env.statbox.bind_entry(
            '2fa_form_compare_not_matched',
            _inherit_from='2fa_form_passed',
            action='finished_with_error',
            error='compare.not_matched',
            user_env_check_passed='0',
            password_check_passed='0',
            names_check_passed='0',
            answer_check_passed='0',
            **{'2fa_form_checks_count': '1'}
        )

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_SELECTED,
                         current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                         phone_confirmation_is_confirmed=True,
                         secure_phone_number=TEST_PHONE,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
            phone_confirmation_is_confirmed=phone_confirmation_is_confirmed,
            secure_phone_number=secure_phone_number,
        )
        super(RestoreCheck2FAFormTestCase, self).set_track_values(**params)

    def query_params(self, answer=TEST_DEFAULT_HINT_ANSWER, password=TEST_PASSWORD,
                     firstname=TEST_DEFAULT_FIRSTNAME, lastname=TEST_DEFAULT_LASTNAME, **kwargs):
        return dict(
            answer=answer,
            password=password,
            firstname=firstname,
            lastname=lastname,
        )

    def set_historydb_api_responses(self, auths_items=None, events=None):
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=auths_items),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=events),
        )

    def make_expected_statbox_factors(self, **kwargs):
        entry = {}
        getters = names_statbox_entry, user_env_auths_statbox_entry, password_matches_statbox_entry, device_id_statbox_entry
        for entry_getter in getters:
            entry.update(entry_getter(**kwargs))
        return entry

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.global_counter_overflow_case(RESTORE_METHOD_PHONE_AND_2FA_FACTOR)

    def test_phone_not_confirmed_fails(self):
        """Телефон еще не подтвержден, ручка недоступна"""
        self.track_invalid_state_case(phone_confirmation_is_confirmed=False)

    def test_captcha_required_and_not_passed_fails(self):
        """Требуется ввод капчи, капча не пройдена"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            restore_2fa_form_checks_count=4,
            is_captcha_recognized=False,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['user.not_verified'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='user.not_verified',
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                is_captcha_required='1',
                **{'2fa_form_checks_count': '4'}
            ),
        ])

    def test_restore_method_no_more_available_fails(self):
        """Восстановление по анкете для 2ФА стало недоступно"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                is_captcha_required='0',
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_phone_suitable_for_restore_changed_fails(self):
        """Изменился телефон на аккаунте - нельзя продолжить"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE2,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['phone.changed'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone.changed',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                is_captcha_required='0',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_compare_not_matched_with_only_names_passed_with_captcha_invalidation(self):
        """Введены неверные данные (совпадение только по ФИО), выставлено требование капчи"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
                hintq=None,
                hinta=None,
            ),
        )
        self.set_track_values(
            restore_2fa_form_checks_count=2,
        )
        self.set_historydb_api_responses(events=[])

        resp = self.make_request(
            self.query_params(answer=TEST_INVALID_HINT_ANSWER),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['compare.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            restore_2fa_form_checks_count=3,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM,
        )
        entry = self.env.statbox.entry(
            '2fa_form_compare_not_matched',
            names_check_passed='1',
            **self.make_expected_statbox_factors(
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            )
        )
        entry['2fa_form_checks_count'] = '3'
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_compare_not_matched_with_only_answer_passed(self):
        """Введены неверные данные (совпадение только по КО)"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()
        self.set_historydb_api_responses(events=[])

        resp = self.make_request(
            self.query_params(
                answer=TEST_DEFAULT_HINT_ANSWER,
                firstname='bad firstname',
                lastname='bad lastname',
            ),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['compare.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            restore_2fa_form_checks_count=1,
            last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM,
        )
        entry = self.env.statbox.entry(
            '2fa_form_compare_not_matched',
            answer_check_passed='1',
            **self.make_expected_statbox_factors(
                names_current_factor=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            )
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_compare_not_matched_with_only_password_passed(self):
        """Введены неверные данные (совпадение только по последнему паролю)"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()
        self.set_historydb_api_responses(events=[
            event_item(name=EVENT_INFO_PASSWORD, value='1:hash1'),
        ])
        encoded_hash = base64.b64encode('1:hash1')
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response({encoded_hash: True}),
        )

        resp = self.make_request(
            self.query_params(
                answer=TEST_INVALID_HINT_ANSWER,
                firstname='bad firstname',
                lastname='bad lastname',
            ),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['compare.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            restore_2fa_form_checks_count=1,
            last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM,
        )
        entry = self.env.statbox.entry(
            '2fa_form_compare_not_matched',
            password_check_passed='1',
            **self.make_expected_statbox_factors(
                password_matches_factor=[FACTOR_BOOL_MATCH] + [FACTOR_NOT_SET] * (PASSWORD_MATCH_DEPTH - 1),
                names_current_factor=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            )
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_compare_not_matched_with_only_device_id_passed(self):
        """Введены неверные данные (совпадение только по device id)"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(device_hardware_id='test_id')
        self.set_historydb_api_responses(events=[
            event_item(name=EVENT_APP_KEY_INFO, value=app_key_info(device_hardware_id='test_id')),
        ])

        resp = self.make_request(
            self.query_params(
                answer=TEST_INVALID_HINT_ANSWER,
                firstname='bad firstname',
                lastname='bad lastname',
            ),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['compare.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            restore_2fa_form_checks_count=1,
            last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM,
        )
        entry = self.env.statbox.entry(
            '2fa_form_compare_not_matched',
            user_env_check_passed='1',
            **self.make_expected_statbox_factors(
                device_id_factor=FACTOR_BOOL_MATCH,
                names_current_factor=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            )
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def test_compare_not_matched_with_only_ip_passed(self):
        """Введены неверные данные (совпадение только по ip/subnet/ua)"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()
        self.set_historydb_api_responses(
            events=[
                event_item(name=EVENT_INFO_PASSWORD, value='1:hash1'),
                event_item(name=EVENT_INFO_PASSWORD, value='2:hash2'),
            ],
            auths_items=[
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            authtype=authtypes.AUTH_TYPE_IMAP,
                            status='successful',
                            ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP),
                        ),
                        auth_successful_aggregated_runtime_auth_item(
                            browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                            count=10,
                        ),
                    ],
                    timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
                ),
            ],
        )
        encoded_hash1 = base64.b64encode('1:hash1')
        encoded_hash2 = base64.b64encode('2:hash2')
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            # Последний пароль не совпал
            blackbox_test_pwd_hashes_response({encoded_hash1: True, encoded_hash2: False}),
        )

        resp = self.make_request(
            self.query_params(
                answer=TEST_INVALID_HINT_ANSWER,
                firstname='bad firstname',
                lastname='bad lastname',
            ),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['compare.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            restore_2fa_form_checks_count=1,
            last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM,
        )
        entry = self.env.statbox.entry(
            '2fa_form_compare_not_matched',
            user_env_check_passed='1',
            **self.make_expected_statbox_factors(
                password_matches_factor=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH] + [FACTOR_NOT_SET] * (PASSWORD_MATCH_DEPTH - 2),
                names_current_factor=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
            )
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

    def base_compare_result_test(self, names_check_passed=False, answer_check_passed=False,
                                 password_check_passed=False, user_env_check_passed=False,
                                 whole_check_passed=False):
        """Общий код тестов, проверяющий условия пропуска пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()
        auth_items = []
        events = []
        if password_check_passed:
            events = [event_item(name=EVENT_INFO_PASSWORD, value='1:hash1')]
        if user_env_check_passed:
            auth_items = [
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            authtype=authtypes.AUTH_TYPE_IMAP,
                            status='successful',
                            ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP),
                        ),
                        auth_successful_aggregated_runtime_auth_item(
                            browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                            count=10,
                        ),
                    ],
                    timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
                ),
            ]
        self.set_historydb_api_responses(
            events=events,
            auths_items=auth_items,
        )
        if password_check_passed:
            encoded_hash = base64.b64encode('1:hash1')
            self.env.blackbox.set_response_value(
                'test_pwd_hashes',
                blackbox_test_pwd_hashes_response({encoded_hash: True}),
            )

        query_params = dict(
            answer=TEST_INVALID_HINT_ANSWER,
            firstname='bad firstname',
            lastname='bad lastname',
        )
        if answer_check_passed:
            query_params.pop('answer')
        if names_check_passed:
            query_params.pop('firstname')
            query_params.pop('lastname')

        resp = self.make_request(
            self.query_params(**query_params),
            headers=self.get_headers(),
        )

        if whole_check_passed:
            self.assert_ok_response(resp, **self.base_expected_response())
            track_kwargs = dict(
                is_strong_password_policy_required=False,
                restore_state=RESTORE_STATE_METHOD_PASSED,
            )
        else:
            self.assert_error_response(resp, ['compare.not_matched'], **self.base_expected_response())
            track_kwargs = dict(restore_2fa_form_checks_count=1)
        self.assert_track_updated(last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM, **track_kwargs)

        factors_kwargs = dict(names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET])
        if not names_check_passed:
            factors_kwargs.update(names_current_factor=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH])
        if not user_env_check_passed:
            factors_kwargs.update(
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            )
        if password_check_passed:
            factors_kwargs.update(
                password_matches_factor=[FACTOR_BOOL_MATCH] + [FACTOR_NOT_SET] * (PASSWORD_MATCH_DEPTH - 1),
            )

        entry = self.env.statbox.entry(
            '2fa_form_passed' if whole_check_passed else '2fa_form_compare_not_matched',
            user_env_check_passed=tskv_bool(user_env_check_passed),
            answer_check_passed=tskv_bool(answer_check_passed),
            names_check_passed=tskv_bool(names_check_passed),
            password_check_passed=tskv_bool(password_check_passed),
            **self.make_expected_statbox_factors(**factors_kwargs)
        )
        self.env.statbox.assert_has_written([entry])
        self.assert_blackbox_userinfo_called()

        counter = restore_counter.get_per_ip_buckets()
        if not whole_check_passed:
            eq_(counter.get(TEST_IP), 1)
        else:
            eq_(counter.get(TEST_IP), 0)

    def test_names_and_answer_compare_not_matched(self):
        self.base_compare_result_test(names_check_passed=True, answer_check_passed=True)

    def test_names_and_user_env_compare_not_matched(self):
        self.base_compare_result_test(names_check_passed=True, user_env_check_passed=True)

    def test_names_and_password_compare_not_matched(self):
        self.base_compare_result_test(names_check_passed=True, password_check_passed=True)

    def test_answer_and_user_env_compare_not_matched(self):
        self.base_compare_result_test(answer_check_passed=True, user_env_check_passed=True)

    def test_answer_and_password_compare_not_matched(self):
        self.base_compare_result_test(answer_check_passed=True, password_check_passed=True)

    def test_user_env_and_password_passed(self):
        self.base_compare_result_test(user_env_check_passed=True, password_check_passed=True, whole_check_passed=True)

    def test_names_and_answer_and_password_compare_not_matched(self):
        self.base_compare_result_test(names_check_passed=True, answer_check_passed=True, password_check_passed=True)

    def test_names_and_answer_and_user_env_passed(self):
        self.base_compare_result_test(
            names_check_passed=True,
            answer_check_passed=True,
            user_env_check_passed=True,
            whole_check_passed=True,
        )

    def test_names_and_password_and_user_env_passed(self):
        self.base_compare_result_test(
            names_check_passed=True,
            password_check_passed=True,
            user_env_check_passed=True,
            whole_check_passed=True,
        )

    def test_answer_and_password_and_user_env_passed(self):
        self.base_compare_result_test(
            answer_check_passed=True,
            password_check_passed=True,
            user_env_check_passed=True,
            whole_check_passed=True,
        )

    def test_names_and_answer_and_password_and_user_env_passed(self):
        self.base_compare_result_test(
            names_check_passed=True,
            answer_check_passed=True,
            password_check_passed=True,
            user_env_check_passed=True,
            whole_check_passed=True,
        )
