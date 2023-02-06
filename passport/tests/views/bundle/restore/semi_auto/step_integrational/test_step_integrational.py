# -*- coding: utf-8 -*-

import json
import time

import mock
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_step_base import (
    BaseTestMultiStepWithCommitUtils,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
    TEST_ADM_FORM_DATA_URL,
    TEST_APP_ID,
    TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
    TEST_DEFAULT_UID,
    TEST_IP,
    TEST_PDD_CYRILLIC_DOMAIN,
    TEST_PDD_DOMAIN,
    TEST_RESTORE_ID,
    TEST_TENSORNET_NEGATIVE_THRESHOLD,
    TEST_TENSORNET_THRESHOLDS,
)
from passport.backend.api.views.bundle.restore.factors import RESTORE_METHODS_CHANGE_INDICES
from passport.backend.api.views.bundle.restore.semi_auto.base import (
    DECISION_SOURCE_TENSORNET,
    DECISION_SOURCE_UNCONDITIONAL,
    RESTORE_MESSAGE_REQUEST_SOURCE_FOR_LEARNING,
    STEP_1_PERSONAL_DATA,
    STEP_2_RECOVERY_TOOLS,
    STEP_3_REGISTRATION_DATA,
    STEP_4_USED_SERVICES,
    STEP_5_SERVICES_DATA,
    STEP_6_FINAL_INFO,
    STEP_FINISHED,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_successful_aggregated_browser_info,
    auth_successful_aggregated_runtime_auth_item,
    auth_successful_aggregated_runtime_auths_item,
    events_passwords_response,
)
from passport.backend.core.builders.tensornet.faker.tensornet import FakeLocalTensorNet
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_NO_MATCH,
    FACTOR_NOT_SET,
    STRING_FACTOR_NO_MATCH,
)
from passport.backend.core.counters import restore_semi_auto_compare_counter
from passport.backend.core.historydb.events import (
    ACTION_RESTORE_SEMI_AUTO_REQUEST,
    RESTORE_STATUS_PENDING,
    RESTORE_STATUS_REJECTED,
)
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)


eq_ = iterdiff(eq_)


class BaseRestoreSemiAutoMultiStepIntegrationalTestCase(
    BaseTestMultiStepWithCommitUtils,
):
    def setUp(self):
        super(BaseRestoreSemiAutoMultiStepIntegrationalTestCase, self).setUp()
        self.default_url = '/4/bundle/restore/semi_auto/commit/'

        self.restore_handle_mock = mock.Mock()
        self._restore_logger = mock.Mock()
        self._restore_logger.debug = self.restore_handle_mock
        self.restore_log_patch = mock.patch(
            'passport.backend.api.views.bundle.restore.semi_auto.controllers.restore_log',
            self._restore_logger,
        )
        self.restore_log_patch.start()
        self.restore_id_patch = mock.patch(
            'passport.backend.api.views.bundle.restore.semi_auto.controllers.RestoreSemiAutoViewBase.restore_id',
            TEST_RESTORE_ID,
        )
        self.restore_id_patch.start()
        self.fake_tensornet = FakeLocalTensorNet('passport.backend.api.views.bundle.restore.semi_auto.step_controllers.TensorNet')
        self.fake_tensornet.start()
        self.fake_tensornet.set_predict_return_value(0.0)

    def tearDown(self):
        self.fake_tensornet.stop()
        self.restore_id_patch.stop()
        self.restore_log_patch.stop()
        del self.restore_handle_mock
        del self._restore_logger
        del self.restore_log_patch
        del self.restore_id_patch
        del self.fake_tensornet
        super(BaseRestoreSemiAutoMultiStepIntegrationalTestCase, self).tearDown()

    def make_request(self, data=None, headers=None, url=None):
        data = data or {'json_data': '{}'}
        return super(BaseRestoreSemiAutoMultiStepIntegrationalTestCase, self).make_request(data, headers=headers, url=url)

    def get_state_request(self):
        return self.make_request(headers=self.get_headers(), url='/3/bundle/restore/semi_auto/get_state/')


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_RETRIES=1,
    RESTORE_OTRS_ADDRESSES={
        'ru': 'otrs-test@passport.yandex.ru',
        'com': 'otrs-test@passport.yandex.com',
        'com.tr': 'otrs-test@passport.yandex.com.tr',
    },
    RESTORE_NOT_PASSED_ADDRESS='no_pass@passport.yandex.ru',
    COLLIE_API_RETRIES=2,
    FURITA_API_RETRIES=2,
    RPOP_API_RETRIES=2,
    WMI_API_RETRIES=2,
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    RESTORE_ADM_FORM_DATA_URL=TEST_ADM_FORM_DATA_URL,
    RESTORE_SEMI_AUTO_DECISION_THRESHOLDS=TEST_TENSORNET_THRESHOLDS,
    **mock_counters()
)
class RestoreSemiAutoMultiStepIntegrationalTestCase(
    BaseRestoreSemiAutoMultiStepIntegrationalTestCase,
):
    def test_integrational_not_passed(self):
        """Ни одна из проверок не пройдена, не пишем в рассылки"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            events_passwords_response=events_passwords_response(),
            auths_aggregated_runtime_present=True,
            auths_aggregated_runtime_items=[
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                        ),
                    ],
                    timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
                ),
            ],
        )
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))

        resp = self.make_request(
            self.request_params_step_1(firstname='A', lastname='B', birthday='2011-11-11'),
            self.get_headers(),
        )

        self.assert_ok_response(resp)

        for params_method in (
                self.request_params_step_2,
                self.request_params_step_3,
                self.request_params_step_4,
        ):
            resp = self.make_request(params_method(), self.get_headers())

            self.assert_ok_response(resp)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_error_response(resp, ['compare.not_matched'])

        final_factors = self.make_step_5_factors(
            self.make_step_4_factors(self.make_step_3_factors(
                self.make_step_2_factors(
                    self.make_step_1_factors(
                        firstnames_entered=['A'],
                        lastnames_entered=['B'],
                        birthday_entered='2011-11-11',
                        names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                        names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                        birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                        birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                        user_ip_factor=0,
                    ),
                ),
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=1,
            )),
            restore_status=RESTORE_STATUS_REJECTED,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
        )

        statbox_factors = self.make_step_1_statbox_factors(
            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
            user_ip_factor=0,
        )
        statbox_entries = self.statbox_step_entries(statbox_factors)
        for step, factors_method in zip(
                (
                    STEP_2_RECOVERY_TOOLS,
                    STEP_3_REGISTRATION_DATA,
                    STEP_4_USED_SERVICES,
                    STEP_5_SERVICES_DATA,
                ),
                (
                    self.make_step_2_statbox_factors,
                    self.make_step_3_statbox_factors,
                    self.make_step_4_statbox_factors,
                ),
        ):
            statbox_factors = factors_method(
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            )
            statbox_entries.extend(self.statbox_step_entries(statbox_factors, step=step, uid_in_submitted_record=True))
        statbox_entries.extend(self.statbox_step_entries(
            self.make_step_5_statbox_factors(
                restore_status=RESTORE_STATUS_REJECTED,
                any_check_passed=False,
                whole_check_passed=False,
            ),
            step=STEP_5_SERVICES_DATA,
            uid_in_submitted_record=True,
        ))
        self.check_statbox_log_entries(self.env.statbox_handle_mock, statbox_entries)

        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_REJECTED)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился ровно один раз
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага
        # проверим, что счетчик по UID НЕ увеличился
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 0)

    def test_integrational_passed_with_unconditional_pass(self):
        """Установлен флаг пропуска проверок; аккаунт заблокирован и ни одна из проверок не пройдена"""
        self.set_track_values(
            semi_auto_step=STEP_1_PERSONAL_DATA,
            is_unconditional_pass=True,
            device_application=TEST_APP_ID,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )
        self.set_historydb_responses(
            events_passwords_response=events_passwords_response(),
            auths_aggregated_runtime_present=True,
            auths_aggregated_runtime_items=[
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                        ),
                    ],
                    timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
                ),
            ],
        )
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))

        resp = self.make_request(
            self.request_params_step_1(firstname='A', lastname='B', birthday='2011-11-11'),
            self.get_headers(),
        )

        self.assert_ok_response(resp)

        for params_method in (
                self.request_params_step_2,
                self.request_params_step_3,
                self.request_params_step_4,
                self.request_params_step_5,
        ):
            resp = self.make_request(params_method(), self.get_headers())

            self.assert_ok_response(resp)

        resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_ok_response(resp)

        final_factors = self.make_step_6_factors(
            self.make_step_5_factors(
                self.make_step_4_factors(self.make_step_3_factors(
                    self.make_step_2_factors(
                        self.make_step_1_factors(
                            firstnames_entered=['A'],
                            lastnames_entered=['B'],
                            birthday_entered='2011-11-11',
                            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                            user_ip_factor=0,
                            is_unconditional_pass=True,
                        ),
                    ),
                    ip_first_auth=None,
                    ip_last_auth=None,
                    subnet_first_auth=None,
                    subnet_last_auth=None,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                    gathered_auths_count=1,
                )),
                restore_status=RESTORE_STATUS_PENDING,
                decision_source=DECISION_SOURCE_UNCONDITIONAL,
            ),
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            is_unconditional_pass=True,
        )

        statbox_factors = self.make_step_1_statbox_factors(
            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
            user_ip_factor=0,
        )
        statbox_entries = self.statbox_step_entries(statbox_factors, is_unconditional_pass=True)
        for step, factors_method in zip(
                (
                    STEP_2_RECOVERY_TOOLS,
                    STEP_3_REGISTRATION_DATA,
                    STEP_4_USED_SERVICES,
                    STEP_5_SERVICES_DATA,
                ),
                (
                    self.make_step_2_statbox_factors,
                    self.make_step_3_statbox_factors,
                    self.make_step_4_statbox_factors,
                    self.make_step_5_statbox_factors,
                ),
        ):
            statbox_factors = factors_method(
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                restore_status=RESTORE_STATUS_PENDING,
                any_check_passed=False,
                whole_check_passed=False,
                decision_source=DECISION_SOURCE_UNCONDITIONAL,
            )
            statbox_entries.extend(
                self.statbox_step_entries(
                    statbox_factors,
                    step=step,
                    uid_in_submitted_record=True,
                    is_unconditional_pass=True,
                )
            )
        statbox_entries.extend(self.statbox_step_entries(
            self.make_step_6_statbox_factors(),
            step=STEP_6_FINAL_INFO,
            uid_in_submitted_record=True,
            is_unconditional_pass=True,
        ))
        self.check_statbox_log_entries(self.env.statbox_handle_mock, statbox_entries)

        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_PENDING)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(
            names='A, B',
            birthday='2011-11-11',
            app_id=TEST_APP_ID,
        )

        # проверим, что счетчик по IP увеличился ровно один раз
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага
        # проверим, что счетчик по UID увеличился
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)

    def test_integrational_passed_with_disabled_on_deletion(self):
        """Аккаунт заблокирован при удалении не слишком давно"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        userinfo = self.default_userinfo_response(
            attributes={
                'account.deletion_operation_started_at': deletion_started_at,
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
            },
            hintq=None,
            hinta=None,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.set_historydb_responses(
            events_passwords_response=events_passwords_response(),
            auths_aggregated_runtime_present=True,
        )
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))

        resp = self.get_state_request()
        self.assert_get_state_response_ok(resp, track_state=STEP_1_PERSONAL_DATA)
        resp = self.make_request(
            self.request_params_step_1(),
            self.get_headers(),
        )
        self.assert_ok_response(resp)

        for step, params_method in zip(
                (
                    STEP_2_RECOVERY_TOOLS,
                    STEP_3_REGISTRATION_DATA,
                    STEP_4_USED_SERVICES,
                    STEP_5_SERVICES_DATA,
                ),
                (
                    self.request_params_step_2,
                    self.request_params_step_3,
                    self.request_params_step_4,
                    self.request_params_step_5,
                ),
        ):
            resp = self.get_state_request()
            expected_data = dict(track_state=step)
            if step == STEP_2_RECOVERY_TOOLS:
                expected_data['questions'] = []
            self.assert_get_state_response_ok(resp, **expected_data)

            resp = self.make_request(params_method(), self.get_headers())
            self.assert_ok_response(resp)

        resp = self.get_state_request()
        self.assert_get_state_response_ok(resp, track_state=STEP_6_FINAL_INFO)
        resp = self.make_request(self.request_params_step_6(), self.get_headers())
        self.assert_ok_response(resp)

        final_factors = self.make_step_6_factors(
            self.make_step_5_factors(
                self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(
                    self.make_step_1_factors(),
                ))),
            ),
            restore_status=RESTORE_STATUS_PENDING,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            questions='[]',
        )

        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_PENDING)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent()

    def test_integrational_passed_with_learning(self):
        """Установлен флаг анкеты для обучения; ни одна из проверок не пройдена"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            events_passwords_response=events_passwords_response(),
            auths_aggregated_runtime_present=True,
            auths_aggregated_runtime_items=[
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                        ),
                    ],
                    timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
                ),
            ],
        )
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))
        self.fake_tensornet.set_predict_return_value(TEST_TENSORNET_NEGATIVE_THRESHOLD + 0.1)

        resp = self.make_request(
            self.request_params_step_1(firstname='A', lastname='B', birthday='2011-11-11'),
            self.get_headers(),
        )

        self.assert_ok_response(resp)

        for params_method in (
                self.request_params_step_2,
                self.request_params_step_3,
                self.request_params_step_4,
                self.request_params_step_5,
        ):
            resp = self.make_request(params_method(), self.get_headers())

            self.assert_ok_response(resp)

        resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_ok_response(resp)

        final_factors = self.make_step_6_factors(
            self.make_step_5_factors(
                self.make_step_4_factors(self.make_step_3_factors(
                    self.make_step_2_factors(
                        self.make_step_1_factors(
                            firstnames_entered=['A'],
                            lastnames_entered=['B'],
                            birthday_entered='2011-11-11',
                            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                            user_ip_factor=0,
                            is_for_learning=True,
                        ),
                    ),
                    ip_first_auth=None,
                    ip_last_auth=None,
                    subnet_first_auth=None,
                    subnet_last_auth=None,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                    gathered_auths_count=1,
                )),
                restore_status=RESTORE_STATUS_PENDING,
                tensornet_estimate=TEST_TENSORNET_NEGATIVE_THRESHOLD + 0.1,
                decision_source=DECISION_SOURCE_TENSORNET,
            ),
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            is_for_learning=True,
        )

        statbox_factors = self.make_step_1_statbox_factors(
            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
            user_ip_factor=0,
        )
        statbox_entries = self.statbox_step_entries(statbox_factors, is_for_learning=True)
        for step, factors_method in zip(
                (
                    STEP_2_RECOVERY_TOOLS,
                    STEP_3_REGISTRATION_DATA,
                    STEP_4_USED_SERVICES,
                    STEP_5_SERVICES_DATA,
                ),
                (
                    self.make_step_2_statbox_factors,
                    self.make_step_3_statbox_factors,
                    self.make_step_4_statbox_factors,
                    self.make_step_5_statbox_factors,
                ),
        ):
            statbox_factors = factors_method(
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                restore_status=RESTORE_STATUS_PENDING,
                any_check_passed=False,
                whole_check_passed=False,
                tensornet_estimate=TEST_TENSORNET_NEGATIVE_THRESHOLD + 0.1,
                decision_source=DECISION_SOURCE_TENSORNET,
            )
            statbox_entries.extend(
                self.statbox_step_entries(
                    statbox_factors,
                    step=step,
                    uid_in_submitted_record=True,
                    is_for_learning=True,
                )
            )
        statbox_entries.extend(self.statbox_step_entries(
            self.make_step_6_statbox_factors(
            ),
            step=STEP_6_FINAL_INFO,
            uid_in_submitted_record=True,
            is_for_learning=True,
        ))
        self.check_statbox_log_entries(self.env.statbox_handle_mock, statbox_entries)

        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_PENDING)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(
            names='A, B',
            birthday='2011-11-11',
            request_source=RESTORE_MESSAGE_REQUEST_SOURCE_FOR_LEARNING,
        )

        # проверим, что счетчик по IP увеличился ровно один раз
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага
        # проверим, что счетчик по UID увеличился
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)

    def test_integrational_fio_check_passed_counter_almost_overflows(self):
        """Пройдена проверка по ФИО/ДР, шлем в промежуточную рассылку"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            events_passwords_response=events_passwords_response(),
            auths_aggregated_runtime_present=True,
            auths_aggregated_runtime_items=[
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                        ),
                    ],
                    timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY,
                ),
            ],
        )
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit - 1
        # на шаге 5 счетчик обновится (и станет переполненным), но на шаге 6 проверяться не будет
        for i in range(counter.limit - 1):
            counter.incr(TEST_IP)
        eq_(counter.get(TEST_IP), counter.limit - 1)

        resp = self.make_request(
            self.request_params_step_1(),
            self.get_headers(),
        )

        self.assert_ok_response(resp)

        for params_method in (
                self.request_params_step_2,
                self.request_params_step_3,
                self.request_params_step_4,
                self.request_params_step_5,
        ):
            resp = self.make_request(params_method(), self.get_headers())

            self.assert_ok_response(resp)

        resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_error_response(resp, ['compare.not_matched'])

        final_factors = self.make_step_6_factors(
            self.make_step_5_factors(
                self.make_step_4_factors(self.make_step_3_factors(
                    self.make_step_2_factors(
                        self.make_step_1_factors(
                            user_ip_factor=0,
                        ),
                    ),
                    ip_first_auth=None,
                    ip_last_auth=None,
                    subnet_first_auth=None,
                    subnet_last_auth=None,
                    factor_ip_auth_interval=FACTOR_NOT_SET,
                    factor_ip_first_auth_depth=FACTOR_NOT_SET,
                    factor_subnet_auth_interval=FACTOR_NOT_SET,
                    factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                    gathered_auths_count=1,
                )),
                restore_status=RESTORE_STATUS_PENDING,
            ),
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
        )

        statbox_factors = self.make_step_1_statbox_factors(
            user_ip_factor=0,
        )
        statbox_entries = self.statbox_step_entries(statbox_factors)
        for step, factors_method in zip(
                (
                    STEP_2_RECOVERY_TOOLS,
                    STEP_3_REGISTRATION_DATA,
                    STEP_4_USED_SERVICES,
                    STEP_5_SERVICES_DATA,
                ),
                (
                    self.make_step_2_statbox_factors,
                    self.make_step_3_statbox_factors,
                    self.make_step_4_statbox_factors,
                    self.make_step_5_statbox_factors,
                ),
        ):
            statbox_factors = factors_method(
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                restore_status=RESTORE_STATUS_PENDING,
                any_check_passed=True,
                whole_check_passed=False,
            )
            statbox_entries.extend(self.statbox_step_entries(statbox_factors, step=step, uid_in_submitted_record=True))
        statbox_entries.extend(self.statbox_step_entries(
            self.make_step_6_statbox_factors(),
            step=STEP_6_FINAL_INFO,
            uid_in_submitted_record=True,
        ))
        self.check_statbox_log_entries(self.env.statbox_handle_mock, statbox_entries)

        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_PENDING)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(check_passed=False)

        # проверим, что счетчик по IP увеличился ровно один раз
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), counter.limit)  # счетчик увеличивается при выполнении последнего шага
        # проверим увеличение счетчика по UID
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_integrational_all_checks_passed_with_get_state(self):
        """Пройдены проверки по ФИО/ДР и по IP, шлем в основную рассылку; тестируем с вызовами ручки get_state"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                hinta=None,
                hintq=None,
            ),
        )
        self.set_historydb_responses(
            events_passwords_response=events_passwords_response(),
            auths_aggregated_runtime_present=True,
        )
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit - 1
        # на шаге 5 счетчик обновится (и станет переполненным), но на шаге 6 проверяться не будет
        for i in range(counter.limit - 1):
            counter.incr(TEST_IP)
        eq_(counter.get(TEST_IP), counter.limit - 1)

        resp = self.get_state_request()
        self.assert_get_state_response_ok(resp, track_state=STEP_1_PERSONAL_DATA)
        resp = self.make_request(
            self.request_params_step_1(),
            self.get_headers(),
        )
        self.assert_ok_response(resp)

        for step, params_method in zip(
                (
                    STEP_2_RECOVERY_TOOLS,
                    STEP_3_REGISTRATION_DATA,
                    STEP_4_USED_SERVICES,
                    STEP_5_SERVICES_DATA,
                ),
                (
                    self.request_params_step_2,
                    self.request_params_step_3,
                    self.request_params_step_4,
                    self.request_params_step_5,
                ),
        ):
            resp = self.get_state_request()
            expected_data = dict(track_state=step)
            if step == STEP_2_RECOVERY_TOOLS:
                expected_data['questions'] = []
            self.assert_get_state_response_ok(resp, **expected_data)

            resp = self.make_request(params_method(), self.get_headers())
            self.assert_ok_response(resp)

        resp = self.get_state_request()
        self.assert_get_state_response_ok(resp, track_state=STEP_6_FINAL_INFO)
        resp = self.make_request(self.request_params_step_6(), self.get_headers())
        self.assert_ok_response(resp)

        final_factors = self.make_step_6_factors(
            self.make_step_5_factors(
                self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(
                    self.make_step_1_factors(),
                ))),
            ),
            restore_status=RESTORE_STATUS_PENDING,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            questions='[]',
        )

        statbox_factors = self.make_step_1_statbox_factors()
        statbox_entries = self.statbox_step_entries(
            statbox_factors,
            uid_in_submitted_record=True,
            with_got_state_entry=True,
        )
        for step, factors_method in zip(
                (
                    STEP_2_RECOVERY_TOOLS,
                    STEP_3_REGISTRATION_DATA,
                    STEP_4_USED_SERVICES,
                    STEP_5_SERVICES_DATA,
                ),
                (
                    self.make_step_2_statbox_factors,
                    self.make_step_3_statbox_factors,
                    self.make_step_4_statbox_factors,
                    self.make_step_5_statbox_factors,
                ),
        ):
            statbox_factors = factors_method()
            statbox_entries.extend(self.statbox_step_entries(
                statbox_factors,
                step=step,
                uid_in_submitted_record=True,
                with_got_state_entry=True,
            ))
        statbox_entries.extend(self.statbox_step_entries(
            self.make_step_6_statbox_factors(
                restore_status=RESTORE_STATUS_PENDING,
                any_check_passed=True,
                whole_check_passed=True,
            ),
            step=STEP_6_FINAL_INFO,
            uid_in_submitted_record=True,
            with_got_state_entry=True,
        ))
        self.check_statbox_log_entries(self.env.statbox_handle_mock, statbox_entries)

        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_PENDING)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent()

        # проверим, что счетчик по IP увеличился ровно один раз
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), counter.limit)  # счетчик увеличивается при выполнении последнего шага
        # проверим увеличение счетчика по UID
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)  # счетчик увеличивается при выполнении последнего шага

        # попытка перезагрузить страницу
        resp = self.get_state_request()
        self.assert_get_state_response_ok(resp, track_state=STEP_FINISHED)

    def test_integrational_known_question_id_patch_works(self):
        """Проверим, что ID вопроса корректно преобразуется при отдаче фронтенду и при получении от фронтенда"""
        initial_factors = self.make_step_1_factors()
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            names_present=False,
            birthday_present=False,
            auths_aggregated_runtime_present=True,
        )

        resp = self.get_state_request()

        self.assert_get_state_response_ok(
            resp,
            track_state=STEP_2_RECOVERY_TOOLS,
            questions=[
                {u'id': 0, u'text': u'question'},
            ],
        )
        questions_in_track = [
            {u'id': 99, u'text': u'question'},
        ]
        self.assert_track_updated(
            factors=initial_factors,
            questions=json.dumps(questions_in_track),
        )

        resp = self.make_request(
            self.request_params_step_2(
                question=u'что-то не то от фронтенда',  # при наличии правильного ID, не смотрим на текст
                question_id=1,
                answer=u'answer',
            ),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        change_factors_count = len(RESTORE_METHODS_CHANGE_INDICES)
        self.assert_track_updated(
            factors=self.make_step_2_factors(
                initial_factors,
                answer_question=u'99:что-то не то от фронтенда',
                answer_entered=u'answer',
                answer_index_best=None,  # в списке ответов на КВ (с номером 1), лучшее совпадение имеет индекс 1
                answer_factor_best=FACTOR_NOT_SET,
                answer_factor_current=FACTOR_NOT_SET,
                answer_factor_change_count=0,
                answer_factor_change_ip_eq_user=[FACTOR_NOT_SET] * change_factors_count,
                answer_factor_change_subnet_eq_user=[FACTOR_NOT_SET] * change_factors_count,
                answer_factor_change_ua_eq_user=[FACTOR_NOT_SET] * change_factors_count,
                answer_factor_match_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                answer_factor_match_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                answer_factor_match_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                answer_factor_match_ua_eq_reg=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                answer_history=[],
            ),
            semi_auto_step=STEP_3_REGISTRATION_DATA,  # перешли на следующий шаг
            questions=json.dumps(questions_in_track),
        )

    def test_integrational_unknown_question_id_patch_works(self):
        """Проверим, что неизвестный ID вопроса корректно преобразуется в пользовательский при получении от фронтенда"""
        initial_factors = self.make_step_1_factors()
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            names_present=False,
            birthday_present=False,
            auths_aggregated_runtime_present=True,
        )

        resp = self.get_state_request()

        self.assert_get_state_response_ok(
            resp,
            track_state=STEP_2_RECOVERY_TOOLS,
            questions=[
                {u'id': 0, u'text': u'question'},
            ],
        )
        questions_in_track = json.dumps([
            {u'id': 99, u'text': u'question'},
        ])
        self.assert_track_updated(
            factors=initial_factors,
            questions=questions_in_track,
        )

        resp = self.make_request(
            self.request_params_step_2(
                question=u'пользовательский вопрос',  # при получении неизвестного ID, берем текст и подставляем ID 99
                question_id=-1,
                answer='answer',
            ),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_2_factors(initial_factors, answer_question=u'99:пользовательский вопрос'),
            semi_auto_step=STEP_3_REGISTRATION_DATA,  # перешли на следующий шаг
            questions=questions_in_track,
        )
