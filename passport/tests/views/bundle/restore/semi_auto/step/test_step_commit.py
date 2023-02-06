# -*- coding: utf-8 -*-

import time

import mock
from passport.backend.api.settings.constants.restore import RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_base import CheckAccountByLoginTests
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_step_base import (
    BaseTestMultiStepWithCommitUtils,
    eq_,
    ProcessStepFormErrorsTests,
)
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import events_info_cache
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
    TEST_ADM_FORM_DATA_URL,
    TEST_DEFAULT_BIRTHDAY,
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_LASTNAME,
    TEST_DEFAULT_PASSWORD,
    TEST_DEFAULT_REGISTRATION_COUNTRY,
    TEST_DEFAULT_UID,
    TEST_EMAILS_WITH_PHONE_ALIASES,
    TEST_HOST_TR,
    TEST_IP,
    TEST_IP_AS_SUBNET,
    TEST_MAIL_DB_ID,
    TEST_MAIL_SUID,
    TEST_PDD_CYRILLIC_DOMAIN,
    TEST_PDD_DOMAIN,
    TEST_REGISTRATION_CITY,
    TEST_REGISTRATION_CITY_2,
    TEST_REGISTRATION_CITY_ID,
    TEST_REGISTRATION_CITY_ID_2,
    TEST_REGISTRATION_COUNTRY_ID,
    TEST_REQUEST_SOURCE,
    TEST_RESTORE_ID,
    TEST_SOCIAL_LINK,
    TEST_TENSORNET_NEGATIVE_THRESHOLD,
    TEST_TENSORNET_POSITIVE_THRESHOLD,
    TEST_TENSORNET_THRESHOLDS,
)
from passport.backend.api.views.bundle.restore.base import (
    RESTORE_METHOD_SEMI_AUTO_FORM,
    RESTORE_STATE_METHOD_PASSED,
)
from passport.backend.api.views.bundle.restore.semi_auto.base import (
    DECISION_SOURCE_BASIC_FORMULA,
    DECISION_SOURCE_TENSORNET,
    DECISION_SOURCE_UNCONDITIONAL,
    RESTORE_MESSAGE_REQUEST_SOURCE_FOR_LEARNING,
    RESTORE_MESSAGE_REQUEST_SOURCE_FOR_POSITIVE_DECISION_RETRY,
    STEP_1_PERSONAL_DATA,
    STEP_2_RECOVERY_TOOLS,
    STEP_3_REGISTRATION_DATA,
    STEP_4_USED_SERVICES,
    STEP_5_SERVICES_DATA,
    STEP_6_FINAL_INFO,
    STEP_FINISHED,
)
from passport.backend.core.builders.historydb_api.exceptions import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
    events_passwords_response,
    events_response,
)
from passport.backend.core.builders.mail_apis import (
    CollieTemporaryError,
    FuritaTemporaryError,
    RPOPTemporaryError,
    WMITemporaryError,
)
from passport.backend.core.builders.social_api.faker.social_api import task_data_response
from passport.backend.core.builders.tensornet.faker.tensornet import FakeLocalTensorNet
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_NOT_SET,
    STRING_FACTOR_MATCH,
    STRING_FACTOR_NO_MATCH,
)
from passport.backend.core.compare.test.compare import compared_user_agent
from passport.backend.core.counters import restore_semi_auto_compare_counter
from passport.backend.core.historydb.events import (
    ACTION_RESTORE_SEMI_AUTO_REQUEST,
    EVENT_ACTION,
    RESTORE_STATUS_PASSED,
    RESTORE_STATUS_REJECTED,
)
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.services import Service
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from six import StringIO
from tensornet import TensorNetError


class BaseRestoreSemiAutoMultiStepCommitViewTestCase(
    BaseTestMultiStepWithCommitUtils,
):
    def setUp(self):
        super(BaseRestoreSemiAutoMultiStepCommitViewTestCase, self).setUp()
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
        super(BaseRestoreSemiAutoMultiStepCommitViewTestCase, self).tearDown()

    def make_request(self, data=None, headers=None, url=None):
        data = data or {'json_data': '{}'}
        return super(BaseRestoreSemiAutoMultiStepCommitViewTestCase, self).make_request(data, headers=headers, url=url)

    def query_params(self, **kwargs):
        # для совместимости с CheckAccountByLoginTests
        return self.request_params_step_1()


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
    RESTORE_SEMI_AUTO_POSITIVE_DECISION_ENABLED=False,
    RESTORE_SEMI_AUTO_NEGATIVE_DECISION_ENABLED=True,
    **mock_counters()
)
class RestoreSemiAutoMultiStepCommitViewTestCase(
    BaseRestoreSemiAutoMultiStepCommitViewTestCase,
    CheckAccountByLoginTests,
    ProcessStepFormErrorsTests,
):
    def test_jsonschema_validation_step_1_empty_params_error(self):
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)

        resp = self.make_request({'json_data': '{}'}, self.get_headers())

        self.assert_error_response(
            resp,
            [
                u'birthday.empty',
                u'contact_email.empty',
                u'eula_accepted.empty',
                u'firstnames.empty',
                u'lastnames.empty',
                u'password_auth_date.empty',
                u'passwords.empty',
                u'eula_accepted.not_accepted',
            ],
        )

    def test_inconsistent_process_restart_required(self):
        self.set_track_values(semi_auto_step=STEP_4_USED_SERVICES, version='outdated_version')

        resp = self.make_request(self.request_params_step_4(), self.get_headers())

        self.assert_ok_response(resp, state='process_restart_required')
        self.assert_track_unchanged()
        self.assert_state_or_error_recorded_to_statbox(
            state='process_restart_required',
            version='outdated_version',
            step=STEP_4_USED_SERVICES,
            _exclude=['uid'],
        )

    def test_invalid_step_error(self):
        self.set_track_values(semi_auto_step='invalid_step')

        resp = self.make_request(self.request_params_step_1(), self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'])

    def test_last_step_action_not_required_error(self):
        self.set_track_values(semi_auto_step=STEP_FINISHED)

        resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_error_response(resp, ['action.not_required'])

    def test_ip_limit_exceeded_fails_not_a_last_step(self):
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA, uid=TEST_DEFAULT_UID)

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit
        for i in range(counter.limit):
            counter.incr(TEST_IP)
        eq_(counter.get(TEST_IP), counter.limit)

        resp = self.make_request(self.request_params_step_1(), self.get_headers())
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()

        eq_(counter.get(TEST_IP), counter.limit)  # счетчик увеличивается только при выполнении последнего шага
        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.assert_state_or_error_recorded_to_statbox(
            state='rate_limit_exceeded',
        )

    def test_uid_limit_exceeded_fails(self):
        self.set_track_values(uid=TEST_DEFAULT_UID)

        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        # установим счетчик вызовов на uid в limit + 1
        for i in range(counter.limit):
            counter.incr(TEST_DEFAULT_UID)
        eq_(counter.get(TEST_DEFAULT_UID), counter.limit)

        resp = self.make_request(self.request_params_step_6(), self.get_headers())
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()

        eq_(counter.get(TEST_DEFAULT_UID), counter.limit)  # счетчик не должен увеличиться
        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.assert_state_or_error_recorded_to_statbox(
            state='rate_limit_exceeded',
        )

    def test_with_unconditional_pass_with_disabled_account_ok(self):
        """Флаг пропуска проверок позволяет пройти проверку предусловий заблокированному пользователю"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA, is_unconditional_pass=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )
        self.set_historydb_responses(events_passwords_response=events_passwords_response())

        resp = self.make_request(self.request_params_step_1(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_1_factors(is_unconditional_pass=True),
            semi_auto_step=STEP_2_RECOVERY_TOOLS,  # перешли на следующий шаг
            is_unconditional_pass=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_1_statbox_factors(),
            is_unconditional_pass=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_with_disabled_on_deletion_account_ok(self):
        """Аккаунт заблокирован при удалении не слишком давно"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        userinfo = self.default_userinfo_response(
            attributes={
                'account.deletion_operation_started_at': deletion_started_at,
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)
        self.set_historydb_responses(events_passwords_response=events_passwords_response())

        resp = self.make_request(self.request_params_step_1(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_1_factors(),
            semi_auto_step=STEP_2_RECOVERY_TOOLS,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_1_statbox_factors(),
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_1_passed(self):
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(events_passwords_response=events_passwords_response())

        resp = self.make_request(self.request_params_step_1(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_1_factors(),
            semi_auto_step=STEP_2_RECOVERY_TOOLS,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_1_statbox_factors(),
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_1_passed_with_registration_event(self):
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            events_passwords_response=events_passwords_response(),
            extra_events=[event_item(name='userinfo_ft', user_ip=TEST_IP, timestamp=1)],
        )

        resp = self.make_request(self.request_params_step_1(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_1_factors(),
            semi_auto_step=STEP_2_RECOVERY_TOOLS,  # перешли на следующий шаг
            events_info_cache=events_info_cache(  # обновили кеш информации о событиях
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1),
            ),
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_1_statbox_factors(),
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_1_contact_email_from_account_validation_failed(self):
        """Указан контактный email из аккаунта"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        resp = self.make_request(
            self.request_params_step_1(contact_email='login@yandex.ru'),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['contact_email.from_same_account'])
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_1_contact_email_for_portal_account_validation_failed(self):
        """Контактный email сопадает с одним из возможных портальных адресов"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA, emails=None)
        resp = self.make_request(
            self.request_params_step_1(contact_email='login@ya.ru'),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['contact_email.from_same_account'])
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_1_contact_email_is_phonenumber_alias_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        """Указан контактный email из аккаунта, являющийся цифровым алиасом - в ручке commit не пропускаем"""
        for email in ('79123456789@ya.ru', '+79123456789@ya.ru', '89123456789@ya.ru', '9123456789@ya.ru'):
            self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA, emails=' '.join(TEST_EMAILS_WITH_PHONE_ALIASES))
            resp = self.make_request(
                self.request_params_step_1(contact_email=email),
                headers=self.get_headers(),
            )

            self.assert_error_response(resp, ['contact_email.from_same_account'])
            self.assert_track_unchanged()
            self.assert_events_are_empty(self.env.handle_mock)
            self.check_restore_log_empty()
            self.assert_mail_not_sent()

    def test_step_1_change_hint_form_with_contact_email_from_account_passed(self):
        """На анкетах для смены КВ/КО не проверяем принадлежность контактного email-адреса к аккаунту"""
        self.set_track_values(
            semi_auto_step=STEP_1_PERSONAL_DATA,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(events_passwords_response=events_passwords_response())

        resp = self.make_request(
            self.request_params_step_1(contact_email='login@yandex.ru'),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_1_factors(
                request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
                contact_email='login@yandex.ru',
            ),
            semi_auto_step=STEP_2_RECOVERY_TOOLS,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_1_statbox_factors(),
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_1_eula_not_accepted_fails(self):
        """ПС не принято"""
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        resp = self.make_request(
            self.request_params_step_1(eula_accepted=False),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['eula_accepted.not_accepted'])
        self.assert_track_unchanged()
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_1_historydb_events_failed(self):
        """ Сбой HistoryDB при поиске событий в истории """
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            events_side_effect=HistoryDBApiTemporaryError,
            events_passwords_response=events_passwords_response(),
        )

        resp = self.make_request(
            self.request_params_step_1(),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['backend.historydb_api_failed'])
        self.assert_track_updated(
            factors=self.make_step_1_factors(
                historydb_api_events_status=False,
                birthday_account=[
                    {
                        u'interval': {u'start': {u'timestamp': None}, u'end': None},
                        u'value': TEST_DEFAULT_BIRTHDAY,
                    },
                ],
                birthday_registration_index=None,
                birthday_registration_factor=FACTOR_NOT_SET,
                names_account=[
                    {
                        u'firstname': TEST_DEFAULT_FIRSTNAME,
                        u'lastname': TEST_DEFAULT_LASTNAME,
                        u'interval': {u'start': {u'timestamp': None}, u'end': None},
                    },
                ],
                names_registration_index=None,
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
            ),
            semi_auto_step=STEP_1_PERSONAL_DATA,  # остались на том же шаге из-за ошибки
        )

        self.assert_compare_recorded_to_statbox(
            error='backend.historydb_api_failed',
            factors=self.make_step_1_statbox_factors(
                historydb_api_events_status=False,
                birthday_registration_factor=FACTOR_NOT_SET,
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
            ),
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_1_historydb_events_passwords_failed(self):
        """ Сбой HistoryDB при поиске пароля в истории """
        self.set_track_values(semi_auto_step=STEP_1_PERSONAL_DATA)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            events_passwords_side_effect=[
                HistoryDBApiTemporaryError(),
                events_passwords_response(password_found=False),
            ],
        )

        resp = self.make_request(
            self.request_params_step_1(passwords=[TEST_DEFAULT_PASSWORD, 'qwerty2']),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['backend.historydb_api_failed'])
        self.assert_track_updated(
            factors=self.make_step_1_factors(
                passwords_api_statuses=[False, True],
                passwords_factor_entered_count=2,
                passwords_factor_auth_found=[FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                passwords_factor_equals_current=[FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                passwords_indices=[None, None],
                passwords_intervals=[[], []],
            ),
            semi_auto_step=STEP_1_PERSONAL_DATA,  # остались на том же шаге из-за ошибки
        )

        self.assert_compare_recorded_to_statbox(
            error='backend.historydb_api_failed',
            factors=self.make_step_1_statbox_factors(
                passwords_api_status=False,
                passwords_factor_entered_count=2,
                passwords_factor_auth_found=[FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                passwords_factor_equals_current=[FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
            ),
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_2_passed(self):
        initial_factors = self.make_step_1_factors()
        self.set_track_values(semi_auto_step=STEP_2_RECOVERY_TOOLS, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            names_present=False,
            birthday_present=False,
        )

        resp = self.make_request(self.request_params_step_2(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_2_factors(initial_factors),
            semi_auto_step=STEP_3_REGISTRATION_DATA,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_2_statbox_factors(),
            step=STEP_2_RECOVERY_TOOLS,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_2_passed_events_info_cache_persists(self):
        """На шаге 2 кеш не используется. Проверим, что кеш сохранился в треке"""
        initial_factors = self.make_step_1_factors()
        self.set_track_values(
            semi_auto_step=STEP_2_RECOVERY_TOOLS,
            factors=initial_factors,
            events_info_cache=events_info_cache(
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1, yandexuid=None),
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            names_present=False,
            birthday_present=False,
        )

        resp = self.make_request(self.request_params_step_2(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_2_factors(initial_factors),
            semi_auto_step=STEP_3_REGISTRATION_DATA,  # перешли на следующий шаг
            events_info_cache=events_info_cache(
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1, yandexuid=None),
            ),
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_2_statbox_factors(),
            step=STEP_2_RECOVERY_TOOLS,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_3_passed(self):
        initial_factors = self.make_step_2_factors(self.make_step_1_factors())
        self.set_track_values(semi_auto_step=STEP_3_REGISTRATION_DATA, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            names_present=False,
            birthday_present=False,
            events_side_effect=[events_response(events=[event_item(name='userinfo_ft', user_ip=TEST_IP, timestamp=1)])],
            auths_aggregated_runtime_present=True,
        )
        region_mock = mock.Mock(
            country=dict(id=TEST_REGISTRATION_COUNTRY_ID, ename=u'Russia', short_en_name=u'RU'),
            city=dict(id=TEST_REGISTRATION_CITY_ID, ename=u'Moscow', short_en_name=u''),
        )
        region_mock.country['name'] = TEST_DEFAULT_REGISTRATION_COUNTRY.encode('utf-8')
        region_mock.city['name'] = TEST_REGISTRATION_CITY.encode('utf-8')

        with mock.patch('passport.backend.core.geobase.Region', lambda ip=None, geobase=None: region_mock):
            resp = self.make_request(
                self.request_params_step_3(
                    registration_city=TEST_REGISTRATION_CITY,
                    registration_city_id=TEST_REGISTRATION_CITY_ID,
                    registration_country_id=TEST_REGISTRATION_COUNTRY_ID,
                ),
                self.get_headers(),
            )

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_3_factors(
                initial_factors,
                registration_city_entered=TEST_REGISTRATION_CITY,
                registration_city_entered_id=TEST_REGISTRATION_CITY_ID,
                registration_city_factor_id=FACTOR_BOOL_MATCH,
                registration_city_history=TEST_REGISTRATION_CITY,
                registration_city_history_id=TEST_REGISTRATION_CITY_ID,
                registration_country_entered_id=TEST_REGISTRATION_COUNTRY_ID,
                registration_country_factor_id=FACTOR_BOOL_MATCH,
                registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
                registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
                registration_ip=TEST_IP,
                factor_ip_eq_reg=FACTOR_BOOL_MATCH,
                factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
                reg_ip=TEST_IP,
                reg_subnet=TEST_IP_AS_SUBNET,
                reg_user_agent=compared_user_agent(os=None, yandexuid='123', browser=None),
            ),
            semi_auto_step=STEP_4_USED_SERVICES,  # перешли на следующий шаг
            events_info_cache=events_info_cache(  # обновили кеш информации о событиях
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1),
            ),
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_3_statbox_factors(
                registration_city_factor_id=FACTOR_BOOL_MATCH,
                registration_country_factor_id=FACTOR_BOOL_MATCH,
                factor_ip_eq_reg=FACTOR_BOOL_MATCH,
                factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
            ),
            step=STEP_3_REGISTRATION_DATA,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_3_aggregated_auths_failed(self):
        """Отвечаем пользователю ошибкой, если не удалось получить историю авторизаций"""
        initial_factors = self.make_step_2_factors(
            self.make_step_1_factors(request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT),
        )
        self.set_track_values(
            semi_auto_step=STEP_3_REGISTRATION_DATA,
            factors=initial_factors,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
            events_info_cache=events_info_cache(
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1, yandexuid=None),
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            names_present=False,
            birthday_present=False,
            auths_aggregated_runtime_present=False,
        )
        self.env.historydb_api.set_response_side_effect(
            'auths_aggregated_runtime',
            HistoryDBApiTemporaryError,
        )

        resp = self.make_request(self.request_params_step_3(), self.get_headers())

        self.assert_error_response(resp, ['backend.historydb_api_failed'])
        final_factors = self.make_step_3_factors(
            initial_factors,
            registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
            registration_city_factor=FACTOR_BOOL_NO_MATCH,
            registration_city_history=TEST_REGISTRATION_CITY_2,
            registration_city_history_id=TEST_REGISTRATION_CITY_ID_2,
            registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
            registration_country_factor=STRING_FACTOR_MATCH,
            registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
            registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
            registration_ip=TEST_IP,
            auths_aggregated_runtime_api_status=False,
            gathered_auths_count=0,
            ip_first_auth=None,
            ip_last_auth=None,
            subnet_first_auth=None,
            subnet_last_auth=None,
            factor_ip_first_auth_depth=FACTOR_NOT_SET,
            factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            factor_ip_auth_interval=FACTOR_NOT_SET,
            factor_subnet_auth_interval=FACTOR_NOT_SET,
            factor_ip_eq_reg=FACTOR_BOOL_MATCH,
            factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
            reg_ip=TEST_IP,
            reg_subnet=TEST_IP_AS_SUBNET,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_3_REGISTRATION_DATA,  # не перешли на следующий шаг
            events_info_cache=events_info_cache(
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1, yandexuid=None),
            ),
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_3_statbox_factors(
                registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                registration_city_factor=FACTOR_BOOL_NO_MATCH,
                registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                registration_country_factor=STRING_FACTOR_MATCH,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_ip_eq_reg=FACTOR_BOOL_MATCH,
                factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
                historydb_api_events_status=None,
                whole_check_passed=False,
                auths_aggregated_runtime_api_status=False,
            ),
            step=STEP_3_REGISTRATION_DATA,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
            error='backend.historydb_api_failed',
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_3_aggregated_auths_failed_retry_successfull(self):
        """Не удалось получить историю авторизаций, повторный вызов ручки commit успешен"""
        initial_factors = self.make_step_2_factors(
            self.make_step_1_factors(request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT),
        )
        self.set_track_values(
            semi_auto_step=STEP_3_REGISTRATION_DATA,
            factors=initial_factors,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
            events_info_cache=events_info_cache(
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1, yandexuid=None),
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            names_present=False,
            birthday_present=False,
            auths_aggregated_runtime_present=False,
        )
        self.env.historydb_api.set_response_side_effect(
            'auths_aggregated_runtime',
            HistoryDBApiTemporaryError,
        )

        resp = self.make_request(self.request_params_step_3(), self.get_headers())

        self.assert_error_response(resp, ['backend.historydb_api_failed'])

        self.set_historydb_responses(auths_aggregated_runtime_present=True)
        self.env.handle_mock.reset_mock()
        self.restore_handle_mock.reset_mock()

        resp = self.make_request(self.request_params_step_3(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_3_factors(
            initial_factors,
            registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
            registration_city_factor=FACTOR_BOOL_NO_MATCH,
            registration_city_history=TEST_REGISTRATION_CITY_2,
            registration_city_history_id=TEST_REGISTRATION_CITY_ID_2,
            registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
            registration_country_factor=STRING_FACTOR_MATCH,
            registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
            registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
            registration_ip=TEST_IP,
            factor_ip_eq_reg=FACTOR_BOOL_MATCH,
            factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
            reg_ip=TEST_IP,
            reg_subnet=TEST_IP_AS_SUBNET,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_4_USED_SERVICES,  # перешли на следующий шаг
            events_info_cache=events_info_cache(
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1, yandexuid=None),
            ),
        )
        entries = self.statbox_step_entries(
            factors=self.make_step_3_statbox_factors(
                registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                registration_city_factor=FACTOR_BOOL_NO_MATCH,
                registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                registration_country_factor=STRING_FACTOR_MATCH,
                factor_ip_eq_reg=FACTOR_BOOL_MATCH,
                factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
                historydb_api_events_status=None,  # При втором вызове информация о регистрации возьмется из кеша
            ),
            step=STEP_3_REGISTRATION_DATA,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
            uid_in_submitted_record=True,
        )
        self.env.statbox.assert_equals(entries, offset=3)
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_3_passed_with_events_info_cache(self):
        """Проверим, что при наличии используется кеш информации о событиях"""
        initial_factors = self.make_step_2_factors(
            self.make_step_1_factors(request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT),
        )
        self.set_track_values(
            semi_auto_step=STEP_3_REGISTRATION_DATA,
            factors=initial_factors,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
            events_info_cache=events_info_cache(
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1, yandexuid=None),
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(
            auths_aggregated_runtime_present=True,
            # если будет выполнен вызов /events, мы должны упасть с ошибкой
            events_side_effect=HistoryDBApiTemporaryError,
        )

        resp = self.make_request(self.request_params_step_3(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_3_factors(
            initial_factors,
            registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
            registration_city_factor=FACTOR_BOOL_NO_MATCH,
            registration_city_history=TEST_REGISTRATION_CITY_2,
            registration_city_history_id=TEST_REGISTRATION_CITY_ID_2,
            registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
            registration_country_factor=STRING_FACTOR_MATCH,
            registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
            registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
            registration_ip=TEST_IP,
            factor_ip_eq_reg=FACTOR_BOOL_MATCH,
            factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
            reg_ip=TEST_IP,
            reg_subnet=TEST_IP_AS_SUBNET,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_4_USED_SERVICES,  # перешли на следующий шаг
            events_info_cache=events_info_cache(
                registration_env=events_info_interval_point(user_ip=TEST_IP, timestamp=1, yandexuid=None),
            ),
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_3_statbox_factors(
                registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                registration_city_factor=FACTOR_BOOL_NO_MATCH,
                registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                registration_country_factor=STRING_FACTOR_MATCH,
                factor_ip_eq_reg=FACTOR_BOOL_MATCH,
                factor_subnet_eq_reg=FACTOR_BOOL_MATCH,
                historydb_api_events_status=None,  # статус не должны записать, т.к. не было вызова
            ),
            step=STEP_3_REGISTRATION_DATA,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
        )

    def test_step_4_passed(self):
        initial_factors = self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors()))
        self.set_track_values(semi_auto_step=STEP_4_USED_SERVICES, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))

        resp = self.make_request(self.request_params_step_4(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_4_factors(initial_factors),
            semi_auto_step=STEP_5_SERVICES_DATA,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_4_statbox_factors(),
            step=STEP_4_USED_SERVICES,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_4_passed_with_services_match(self):
        """Пользователь выбрал сервисы, которыми он пользовался, сервисы совпали с аккаунтом"""
        initial_factors = self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors()))
        self.set_track_values(semi_auto_step=STEP_4_USED_SERVICES, factors=initial_factors)
        subscribed_services = [u'mail', u'metrika', u'cloud', u'rabota']
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(subscribed_to=[Service.by_slug(slug).sid for slug in subscribed_services]),
        )
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))

        entered_service_names = [u'mail', u'yandsearch', u'disk', u'market', u'music', u'metrika']
        resp = self.make_request(
            self.request_params_step_4(services=entered_service_names),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_4_factors(
                initial_factors,
                services_entered=entered_service_names,
                services_account=[u'mail', u'disk', u'metrika'],
                services_matches=[u'mail', u'disk', u'metrika'],
                services_factor_entered_count=6,
                services_factor_account_count=3,
                services_factor_matches_count=3,
            ),
            semi_auto_step=STEP_5_SERVICES_DATA,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_4_statbox_factors(
                services_factor_entered_count=6,
                services_factor_account_count=3,
                services_factor_matches_count=3,
            ),
            step=STEP_4_USED_SERVICES,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_5_passed__pending_status(self):
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
        )
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_5_factors(initial_factors),
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(),
            step=STEP_5_SERVICES_DATA,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_5_mail_api_not_called_if_no_mail_sid(self):
        """Не дергаем почтовое API если нет почтового сида"""
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
        )
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_5_factors(initial_factors),
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(),
            step=STEP_5_SERVICES_DATA,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_5_mail_api_failed(self):
        """Сбой API почты"""
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
        )
        self.set_track_values(
            semi_auto_step=STEP_5_SERVICES_DATA,
            factors=initial_factors,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid]),
        )
        self.env.collie.set_response_side_effect('search_contacts', CollieTemporaryError)
        self.env.furita.set_response_side_effect('blackwhite', FuritaTemporaryError)
        self.env.rpop.set_response_side_effect('list', RPOPTemporaryError)
        self.env.wmi.set_response_side_effect('folders', WMITemporaryError)
        self.set_historydb_responses(names_present=False, birthday_present=False)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_5_factors(
                initial_factors,
                email_folders_api_status=False,
                email_blacklist_api_status=False,
                email_whitelist_api_status=False,
                email_collectors_api_status=False,
                outbound_emails_api_status=False,
            ),
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                email_folders_api_status=False,
                email_blacklist_api_status=False,
                email_whitelist_api_status=False,
                email_collectors_api_status=False,
                outbound_emails_api_status=False,
            ),
            step=STEP_5_SERVICES_DATA,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

        requests = self.env.wmi.get_requests_by_method('folders')
        eq_(len(requests), 2)
        requests[0].assert_query_equals({
            u'uid': str(TEST_DEFAULT_UID),
            u'mdb': TEST_MAIL_DB_ID,
            u'suid': str(TEST_MAIL_SUID),
        })
        requests = self.env.rpop.get_requests_by_method('list')
        eq_(len(requests), 2)
        requests[0].assert_query_contains({
            u'mdb': TEST_MAIL_DB_ID,
            u'suid': str(TEST_MAIL_SUID),
        })
        requests = self.env.furita.get_requests_by_method('blackwhite')
        eq_(len(requests), 2)
        requests[0].assert_query_equals({
            u'uid': str(TEST_DEFAULT_UID),
        })
        requests = self.env.collie.get_requests_by_method('search_contacts')
        eq_(len(requests), 2)

    def test_step_5_mail_api_not_called_without_mail_sid(self):
        """API почты не вызывается при отсутствии почтового сида"""
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
        )
        self.set_track_values(
            semi_auto_step=STEP_5_SERVICES_DATA,
            factors=initial_factors,
        )
        self.set_mail_api_responses()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        self.assert_track_updated(
            factors=self.make_step_5_factors(initial_factors),
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(),
            step=STEP_5_SERVICES_DATA,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()
        eq_(self.env.collie._mock.request.call_count, 0)
        eq_(self.env.furita._mock.request.call_count, 0)
        eq_(self.env.rpop._mock.request.call_count, 0)
        eq_(self.env.wmi._mock.request.call_count, 0)

    def test_step_5_no_checks_passed__rejected_status(self):
        step_1_factors = self.make_step_1_factors(
            names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_NO_MATCH],
            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
        )
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(
                self.make_step_2_factors(step_1_factors),
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=1,
            ),
        )
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_error_response(resp, ['compare.not_matched'])
        final_factors = self.make_step_5_factors(
            initial_factors,
            restore_status=RESTORE_STATUS_REJECTED,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на финальный шаг, не на 6-й
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                any_check_passed=False,
                whole_check_passed=False,
                restore_status=RESTORE_STATUS_REJECTED,
            ),
            step=STEP_5_SERVICES_DATA,
        )
        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_REJECTED)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_step_5_only_names_birthday_passed__pending_status(self):
        step_1_factors = self.make_step_1_factors()
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(
                self.make_step_2_factors(step_1_factors),
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=1,
            ),
        )
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_5_factors(
            initial_factors,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                any_check_passed=True,
                whole_check_passed=False,
            ),
            step=STEP_5_SERVICES_DATA,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на шаге принятия решения
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)

    def test_step_5_only_ip_subnet_passed__pending_status(self):
        step_1_factors = self.make_step_1_factors(
            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
        )
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(self.make_step_2_factors(step_1_factors)),
        )
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_5_factors(initial_factors)
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                any_check_passed=True,
                whole_check_passed=False,
            ),
            step=STEP_5_SERVICES_DATA,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на шаге принятия решения
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)

    def test_step_5_passed_with_unconditional_pass__pending_status(self):
        """Выставлен флаг пропуска в саппорт без учета проверок ФИО/ДР/IP, которые не пройдены"""
        initial_factors = self.make_step_1_factors(
            # ни одна из проверок ФИО/ДР/IP не пройдена, совпадение имени роли не играет
            names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_NO_MATCH],
            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
            is_unconditional_pass=True,
        )
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(
                self.make_step_2_factors(initial_factors),
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=1,
            ),
        )
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_unconditional_pass=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_5_factors(  # статус восстановления - pending
            initial_factors,
            decision_source=DECISION_SOURCE_UNCONDITIONAL,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
            is_unconditional_pass=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                # ни одна проверка не пройдена
                any_check_passed=False,
                whole_check_passed=False,
                decision_source=DECISION_SOURCE_UNCONDITIONAL,
            ),
            step=STEP_5_SERVICES_DATA,
            is_unconditional_pass=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_step_5_passed_to_support_with_learning_and_positive_decision_disabled__pending_status(self):
        """Выставлен флаг анкеты для обучения - используем tensornet, пропускаем анкету в саппорт"""
        initial_factors = self.make_step_1_factors(
            is_for_learning=True,
        )
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)
        # Выставляем значение, достаточно для автоматического ДА, проверяем тем самым, что флаг
        # выключенности автоматического решения отрабатывает корректно.
        self.fake_tensornet.set_predict_return_value(TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        # Проверяем, что tensornet был вызван
        eq_(self.fake_tensornet.predict_call_count, 1)
        final_factors = self.make_step_5_factors(  # статус восстановления - pending
            initial_factors,
            decision_source=DECISION_SOURCE_TENSORNET,
            tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                decision_source=DECISION_SOURCE_TENSORNET,
                tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_step_5_passed_to_support_with_learning_and_positive_decision_enabled__pending_status(self):
        """Выставлен флаг анкеты для обучения - используем tensornet, можем говорить автоматически Да,
        попадаем в саппорт"""
        initial_factors = self.make_step_1_factors(
            is_for_learning=True,
        )
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)
        # Выставляем значение, недостаточное для автоматического ДА
        self.fake_tensornet.set_predict_return_value(TEST_TENSORNET_POSITIVE_THRESHOLD - 0.1)

        with settings_context(
            RESTORE_OTRS_ADDRESSES={
                'ru': 'otrs-test@passport.yandex.ru',
                'com': 'otrs-test@passport.yandex.com',
                'com.tr': 'otrs-test@passport.yandex.com.tr',
            },
            RESTORE_NOT_PASSED_ADDRESS='no_pass@passport.yandex.ru',
            DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
            RESTORE_ADM_FORM_DATA_URL=TEST_ADM_FORM_DATA_URL,
            RESTORE_SEMI_AUTO_DECISION_THRESHOLDS=TEST_TENSORNET_THRESHOLDS,
            RESTORE_SEMI_AUTO_POSITIVE_DECISION_ENABLED=True,
            **mock_counters()
        ):
            resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        # Проверяем, что tensornet был вызван
        eq_(self.fake_tensornet.predict_call_count, 1)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_TENSORNET,
            tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD - 0.1,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                decision_source=DECISION_SOURCE_TENSORNET,
                tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD - 0.1,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_step_5_passed_to_support_with_learning_and_negative_decision_disabled__pending_status(self):
        """Выставлен флаг анкеты для обучения - используем tensornet, не можем отказывать, отправляем в саппорт"""
        initial_factors = self.make_step_1_factors(
            is_for_learning=True,
        )
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)
        # Выставляем худшее возможное значение
        self.fake_tensornet.set_predict_return_value(0.0)

        with settings_context(
            RESTORE_OTRS_ADDRESSES={
                'ru': 'otrs-test@passport.yandex.ru',
                'com': 'otrs-test@passport.yandex.com',
                'com.tr': 'otrs-test@passport.yandex.com.tr',
            },
            RESTORE_NOT_PASSED_ADDRESS='no_pass@passport.yandex.ru',
            DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
            RESTORE_ADM_FORM_DATA_URL=TEST_ADM_FORM_DATA_URL,
            RESTORE_SEMI_AUTO_DECISION_THRESHOLDS=TEST_TENSORNET_THRESHOLDS,
            RESTORE_SEMI_AUTO_NEGATIVE_DECISION_ENABLED=False,
            **mock_counters()
        ):
            resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        # Проверяем, что tensornet был вызван
        eq_(self.fake_tensornet.predict_call_count, 1)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_TENSORNET,
            tensornet_estimate=0.0,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                decision_source=DECISION_SOURCE_TENSORNET,
                tensornet_estimate=0.0,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_step_5_passed_to_new_password_with_learning_and_positive_decision_enabled__passed_status(self):
        """Выставлен флаг анкеты для обучения - используем tensornet, автоматически пропускаем на смену пароля"""
        initial_factors = self.make_step_1_factors(
            is_for_learning=True,
        )
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)
        # Выставляем значение, достаточное для автоматического ДА
        self.fake_tensornet.set_predict_return_value(TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1)

        with settings_context(
            RESTORE_OTRS_ADDRESSES={
                'ru': 'otrs-test@passport.yandex.ru',
                'com': 'otrs-test@passport.yandex.com',
                'com.tr': 'otrs-test@passport.yandex.com.tr',
            },
            RESTORE_NOT_PASSED_ADDRESS='no_pass@passport.yandex.ru',
            DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
            RESTORE_ADM_FORM_DATA_URL=TEST_ADM_FORM_DATA_URL,
            RESTORE_SEMI_AUTO_DECISION_THRESHOLDS=TEST_TENSORNET_THRESHOLDS,
            RESTORE_SEMI_AUTO_POSITIVE_DECISION_ENABLED=True,
            **mock_counters()
        ):
            resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp, state='restoration_passed')
        # Проверяем, что tensornet был вызван
        eq_(self.fake_tensornet.predict_call_count, 1)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_TENSORNET,
            tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1,
            restore_status=RESTORE_STATUS_PASSED,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на финальный шаг
            is_for_learning=True,
            # Флаги для ввода новых данных в рамках автоматического восстановления
            restore_state=RESTORE_STATE_METHOD_PASSED,
            current_restore_method=RESTORE_METHOD_SEMI_AUTO_FORM,
            is_strong_password_policy_required='0',
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                decision_source=DECISION_SOURCE_TENSORNET,
                tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1,
                restore_status=RESTORE_STATUS_PASSED,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_restore_info_in_event_log(
            restore_status=RESTORE_STATUS_PASSED,
        )
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_not_sent()  # письмо не отправляется в ОТРС, т.к. восстановление пройдено

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_step_5_2fa_passed_to_support_with_learning_and_positive_decision_enabled__pending_status(self):
        """Выставлен флаг анкеты для обучения - используем tensornet, можем принимать положительное решение,
        но для 2ФА-пользователя не делаем этого"""
        initial_factors = self.make_step_1_factors(
            is_for_learning=True,
        )
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)
        # Выставляем значение, достаточно для автоматического ДА
        self.fake_tensornet.set_predict_return_value(TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1)

        with settings_context(
            RESTORE_OTRS_ADDRESSES={
                'ru': 'otrs-test@passport.yandex.ru',
                'com': 'otrs-test@passport.yandex.com',
                'com.tr': 'otrs-test@passport.yandex.com.tr',
            },
            RESTORE_NOT_PASSED_ADDRESS='no_pass@passport.yandex.ru',
            DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
            RESTORE_ADM_FORM_DATA_URL=TEST_ADM_FORM_DATA_URL,
            RESTORE_SEMI_AUTO_DECISION_THRESHOLDS=TEST_TENSORNET_THRESHOLDS,
            RESTORE_SEMI_AUTO_POSITIVE_DECISION_ENABLED=True,
            **mock_counters()
        ):
            resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        # Проверяем, что tensornet был вызван
        eq_(self.fake_tensornet.predict_call_count, 1)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_TENSORNET,
            tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                decision_source=DECISION_SOURCE_TENSORNET,
                tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_5_passed_to_support_with_learning_and_positive_decision_enabled_and_positive_retry__pending_status(self):
        """Выставлен флаг анкеты для обучения - используем tensornet, можем принимать положительное решение,
        но из-за наличия в истории автоматического положительного решения не делаем этого"""
        initial_factors = self.make_step_1_factors(
            is_for_learning=True,
        )
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value('userinfo', self.default_userinfo_response())
        attempt_ts = time.time() - 60 * 60 + 1
        self.set_historydb_responses(
            names_present=False,
            birthday_present=False,
            extra_events=[
                event_item(
                    name=EVENT_ACTION,
                    timestamp=attempt_ts,
                    value='restore_passed_by_semi_auto',
                ),
            ],
        )
        # Выставляем значение, достаточно для автоматического ДА
        self.fake_tensornet.set_predict_return_value(TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1)

        with settings_context(
                RESTORE_OTRS_ADDRESSES={
                    'ru': 'otrs-test@passport.yandex.ru',
                    'com': 'otrs-test@passport.yandex.com',
                    'com.tr': 'otrs-test@passport.yandex.com.tr',
                },
                RESTORE_NOT_PASSED_ADDRESS='no_pass@passport.yandex.ru',
                DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
                RESTORE_ADM_FORM_DATA_URL=TEST_ADM_FORM_DATA_URL,
                RESTORE_SEMI_AUTO_DECISION_THRESHOLDS=TEST_TENSORNET_THRESHOLDS,
                RESTORE_SEMI_AUTO_POSITIVE_DECISION_ENABLED=True,
                RESTORE_SEMI_AUTO_POSITIVE_DECISION_RETRY_IMPOSSIBLE_INTERVAL=60 * 60,
                **mock_counters()
        ):
            resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        # Проверяем, что tensornet был вызван
        eq_(self.fake_tensornet.predict_call_count, 1)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_TENSORNET,
            tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1,
            restore_attempts=[
                dict(
                    timestamp=attempt_ts,
                    method=RESTORE_METHOD_SEMI_AUTO_FORM,
                ),
            ],
            has_recent_positive_decision=True,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                decision_source=DECISION_SOURCE_TENSORNET,
                tensornet_estimate=TEST_TENSORNET_POSITIVE_THRESHOLD + 0.1,
                has_recent_positive_decision=True,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_5_rejected_with_learning__rejected_status(self):
        """Выставлен флаг анкеты для обучения - используем tensornet, не пропускаем анкету"""
        initial_factors = self.make_step_1_factors(is_for_learning=True)
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)
        self.fake_tensornet.set_predict_return_value(TEST_TENSORNET_NEGATIVE_THRESHOLD)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_error_response(resp, ['compare.not_matched'])
        # Проверяем, что tensornet был вызван
        eq_(self.fake_tensornet.predict_call_count, 1)
        final_factors = self.make_step_5_factors(
            initial_factors,
            restore_status=RESTORE_STATUS_REJECTED,
            decision_source=DECISION_SOURCE_TENSORNET,
            tensornet_estimate=TEST_TENSORNET_NEGATIVE_THRESHOLD,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                restore_status=RESTORE_STATUS_REJECTED,
                decision_source=DECISION_SOURCE_TENSORNET,
                tensornet_estimate=TEST_TENSORNET_NEGATIVE_THRESHOLD,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_REJECTED)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_not_sent()  # письмо не отправляется

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_step_5_rejected_with_learning_tensornet_failed__rejected_status(self):
        """Выставлен флаг анкеты для обучения - случился сбой tensornet, обычная формула не пропустила анкету"""
        initial_factors = self.make_step_1_factors(
            # ни одна из проверок ФИО/ДР/IP не пройдена
            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
            user_ip_factor=FACTOR_BOOL_NO_MATCH,
            user_env_factor=FACTOR_BOOL_NO_MATCH,
            subnet_factor=FACTOR_BOOL_NO_MATCH,
            is_for_learning=True,
        )
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(
                self.make_step_2_factors(initial_factors),
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=1,
            ),
        )
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)
        self.fake_tensornet.set_predict_side_effect(TensorNetError)

        resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_error_response(resp, ['compare.not_matched'])
        # Проверяем, что tensornet был вызван
        eq_(self.fake_tensornet.predict_call_count, 1)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_BASIC_FORMULA,
            tensornet_estimate=None,
            tensornet_status=False,
            restore_status=RESTORE_STATUS_REJECTED,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                # ни одна проверка не пройдена
                any_check_passed=False,
                whole_check_passed=False,
                decision_source=DECISION_SOURCE_BASIC_FORMULA,
                tensornet_estimate=None,
                tensornet_status=False,
                restore_status=RESTORE_STATUS_REJECTED,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_REJECTED)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 0)

    def test_step_5_rejected_with_learning_tensornet_disabled_by_indicator_file__rejcted_status(self):
        """Выставлен флаг анкеты для обучения; tensornet отключен файлом-индикатором, обычная формула не пропустила анкету"""
        initial_factors = self.make_step_1_factors(
            # ни одна из проверок ФИО/ДР/IP не пройдена
            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            birthday_current_factor=FACTOR_BOOL_NO_MATCH,
            birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
            user_ip_factor=FACTOR_BOOL_NO_MATCH,
            user_env_factor=FACTOR_BOOL_NO_MATCH,
            subnet_factor=FACTOR_BOOL_NO_MATCH,
            is_for_learning=True,
        )
        initial_factors = self.make_step_4_factors(
            self.make_step_3_factors(
                self.make_step_2_factors(initial_factors),
                ip_first_auth=None,
                ip_last_auth=None,
                subnet_first_auth=None,
                subnet_last_auth=None,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                gathered_auths_count=1,
            ),
        )
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)
        self.fake_tensornet.set_predict_return_value(0.0)
        os_mock = mock.Mock()
        os_mock.path.exists.return_value = True

        with mock.patch('passport.backend.api.views.bundle.restore.semi_auto.step_controllers.os', os_mock):
            resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_error_response(resp, ['compare.not_matched'])
        # Проверяем, что tensornet не был вызван
        eq_(self.fake_tensornet.predict_call_count, 0)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_BASIC_FORMULA,
            tensornet_estimate=None,
            tensornet_status=None,
            restore_status=RESTORE_STATUS_REJECTED,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                # ни одна проверка не пройдена
                any_check_passed=False,
                whole_check_passed=False,
                decision_source=DECISION_SOURCE_BASIC_FORMULA,
                tensornet_estimate=None,
                tensornet_status=None,
                restore_status=RESTORE_STATUS_REJECTED,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_restore_info_in_event_log(restore_status=RESTORE_STATUS_REJECTED)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_not_sent()

        # проверим, что счетчик по IP увеличился на последнем шаге
        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # счетчик увеличивается при выполнении последнего шага

    def test_step_5_with_learning_empty_features_file__pending_status(self):
        """Выставлен флаг анкеты для обучения; файл с факторами пустой, используем ручную формулу"""
        initial_factors = self.make_step_1_factors(is_for_learning=True)
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        with mock.patch('passport.backend.utils.file.read_file', return_value=''):
            resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        # Проверяем, что tensornet не был вызван
        eq_(self.fake_tensornet.predict_call_count, 0)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_BASIC_FORMULA,
            tensornet_estimate=None,
            tensornet_status=False,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                decision_source=DECISION_SOURCE_BASIC_FORMULA,
                tensornet_estimate=None,
                tensornet_status=False,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_5_with_learning_unknown_feature_in_features_file__pending_status(self):
        """Выставлен флаг анкеты для обучения; файл с факторами содержит неизвестное имя, используем ручную формулу"""
        initial_factors = self.make_step_1_factors(is_for_learning=True)
        initial_factors = self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors)))
        self.set_track_values(semi_auto_step=STEP_5_SERVICES_DATA, factors=initial_factors, is_for_learning=True)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses(names_present=False, birthday_present=False)

        with mock.patch('passport.backend.utils.file.read_file', return_value='unknown_factor_0\nunknown_factor_1'):
            resp = self.make_request(self.request_params_step_5(), self.get_headers())

        self.assert_ok_response(resp)
        # Проверяем, что tensornet не был вызван
        eq_(self.fake_tensornet.predict_call_count, 0)
        final_factors = self.make_step_5_factors(
            initial_factors,
            decision_source=DECISION_SOURCE_BASIC_FORMULA,
            tensornet_estimate=None,
            tensornet_status=False,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_6_FINAL_INFO,  # перешли на ввод доп. инфы
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_5_statbox_factors(
                decision_source=DECISION_SOURCE_BASIC_FORMULA,
                tensornet_estimate=None,
                tensornet_status=False,
            ),
            step=STEP_5_SERVICES_DATA,
            is_for_learning=True,
        )
        self.assert_events_are_empty(self.env.handle_mock)
        self.check_restore_log_empty()
        self.assert_mail_not_sent()

    def test_step_6_passed(self):
        initial_factors = self.make_step_5_factors(
            self.make_step_4_factors(
                self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
            ),
        )
        self.set_track_values(semi_auto_step=STEP_6_FINAL_INFO, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_6_factors(initial_factors)
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_6_statbox_factors(),
            step=STEP_6_FINAL_INFO,
        )
        self.assert_restore_info_in_event_log()
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent()

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 0)  # счетчик по IP не увеличивается при выполнении шага 6
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)

    def test_step_6_failed_sendmail(self):
        initial_factors = self.make_step_5_factors(
            self.make_step_4_factors(
                self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
            ),
        )
        self.set_track_values(semi_auto_step=STEP_6_FINAL_INFO, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.env.mailer.set_side_effect([Exception])

        resp = self.make_request(self.request_params_step_6(), self.get_headers())
        self.assert_error_response(resp, ['exception.unhandled'])

    def test_step_6_passed_on_different_host(self):
        """Пользователь пришел на турецкий Паспорт и прошел все шаги"""
        initial_factors = self.make_step_5_factors(
            self.make_step_4_factors(
                self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
            ),
        )
        self.set_track_values(semi_auto_step=STEP_6_FINAL_INFO, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(self.request_params_step_6(), self.get_headers(host=TEST_HOST_TR))

        self.assert_ok_response(resp)
        final_factors = self.make_step_6_factors(initial_factors)
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_6_statbox_factors(),
            step=STEP_6_FINAL_INFO,
            host=TEST_HOST_TR,
        )
        self.assert_restore_info_in_event_log()
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(tld='com.tr')

    def test_step_6_passed_with_user_enabled_false(self):
        initial_factors = self.make_step_5_factors(
            self.make_step_4_factors(
                self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
            ),
        )
        self.set_track_values(semi_auto_step=STEP_6_FINAL_INFO, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(self.request_params_step_6(user_enabled=False), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_6_factors(initial_factors, user_enabled=False)
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_6_statbox_factors(),
            step=STEP_6_FINAL_INFO,
        )
        self.assert_restore_info_in_event_log()
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(user_enabled=False)

    def test_step_6_passed_with_photo_file(self):
        initial_factors = self.make_step_5_factors(
            self.make_step_4_factors(
                self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
            ),
        )
        self.set_track_values(semi_auto_step=STEP_6_FINAL_INFO, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(
            self.request_params_step_6(photo_file=(StringIO('photo content'), '/etc/passwd')),
            self.get_headers(),
        )

        self.assert_ok_response(resp)
        final_factors = self.make_step_6_factors(initial_factors)
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_6_statbox_factors(),
            step=STEP_6_FINAL_INFO,
        )
        self.assert_restore_info_in_event_log()
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(
            photo_file_expected=True,
            photo_file_name_escaped='etc_passwd',
            photo_file_contents='photo content',
        )

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 0)
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)

    def test_step_6_passed_with_social_accounts(self):
        """Сохраняем данные о соц. аккаунтах в трек и передаем их в письме в ОТРС"""
        profile_task_data = task_data_response(
            firstname=TEST_DEFAULT_FIRSTNAME,
            lastname=TEST_DEFAULT_LASTNAME,
            links=[TEST_SOCIAL_LINK],
        )['profile']
        initial_factors = self.make_step_5_factors(
            self.make_step_4_factors(
                self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors())),
                social_accounts_entered_accounts=[profile_task_data],
            ),
        )
        self.set_track_values(semi_auto_step=STEP_6_FINAL_INFO, factors=initial_factors)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_6_factors(initial_factors)
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_6_statbox_factors(),
            step=STEP_6_FINAL_INFO,
        )
        self.assert_restore_info_in_event_log()
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(
            social_accounts='%s %s (%s)' % (TEST_DEFAULT_FIRSTNAME, TEST_DEFAULT_LASTNAME, TEST_SOCIAL_LINK),
        )

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 0)
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)

    def test_step_6_passed_with_changehint(self):
        """Анкета для смены КВ/КО - изменяется тема письма и добавляется причина обращения"""
        initial_factors = self.make_step_5_factors(self.make_step_4_factors(self.make_step_3_factors(
            self.make_step_2_factors(
                self.make_step_1_factors(
                    request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
                    real_reason='restore',
                ),
            ),
        )))
        self.set_track_values(
            semi_auto_step=STEP_6_FINAL_INFO,
            factors=initial_factors,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_6_factors(initial_factors)
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_6_statbox_factors(),
            step=STEP_6_FINAL_INFO,
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
        )
        self.assert_restore_info_in_event_log(request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT)
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(
            request_source=RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT,
            real_reason='restore',
        )

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 0)
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)

    def test_step_6_passed_to_support_with_learning(self):
        """Выставлен флаг анкеты для обучения, отправляем в саппорт"""
        initial_factors = self.make_step_1_factors(
            is_for_learning=True,
        )
        initial_factors = self.make_step_5_factors(
            self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors))),
        )
        self.set_track_values(
            semi_auto_step=STEP_6_FINAL_INFO,
            factors=initial_factors,
            is_for_learning=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        # Выставляем худшее возможное значение
        self.fake_tensornet.set_predict_return_value(0.0)

        with settings_context(
            RESTORE_OTRS_ADDRESSES={
                'ru': 'otrs-test@passport.yandex.ru',
                'com': 'otrs-test@passport.yandex.com',
                'com.tr': 'otrs-test@passport.yandex.com.tr',
            },
            RESTORE_NOT_PASSED_ADDRESS='no_pass@passport.yandex.ru',
            DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
            RESTORE_ADM_FORM_DATA_URL=TEST_ADM_FORM_DATA_URL,
            RESTORE_SEMI_AUTO_DECISION_THRESHOLDS=TEST_TENSORNET_THRESHOLDS,
            RESTORE_SEMI_AUTO_NEGATIVE_DECISION_ENABLED=False,
            **mock_counters()
        ):
            resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_6_factors(
            initial_factors,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_6_statbox_factors(
            ),
            step=STEP_6_FINAL_INFO,
            is_for_learning=True,
        )
        self.assert_restore_info_in_event_log()
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(
            request_source=RESTORE_MESSAGE_REQUEST_SOURCE_FOR_LEARNING,
        )

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 0)
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)

    def test_step_6_passed_to_support_with_positive_decision_retry(self):
        """Выставлен флаг анкеты для обучения, найдена успешная попытка восстановления через анкету -
        изменяем request_source"""
        initial_factors = self.make_step_1_factors(
            is_for_learning=True,
        )
        attempt_ts = time.time() - 60 * 60 - 10
        initial_factors = self.make_step_5_factors(
            self.make_step_4_factors(self.make_step_3_factors(self.make_step_2_factors(initial_factors))),
            restore_attempts=[
                dict(
                    timestamp=attempt_ts,
                    restore_id=TEST_RESTORE_ID,
                    request_source=TEST_REQUEST_SOURCE,
                    initial_status=RESTORE_STATUS_PASSED,
                    support_decisions=[],
                ),
            ],
            has_recent_positive_decision=True,
        )
        self.set_track_values(
            semi_auto_step=STEP_6_FINAL_INFO,
            factors=initial_factors,
            is_for_learning=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        # Выставляем худшее возможное значение
        self.fake_tensornet.set_predict_return_value(0.0)

        with settings_context(
                RESTORE_OTRS_ADDRESSES={
                    'ru': 'otrs-test@passport.yandex.ru',
                    'com': 'otrs-test@passport.yandex.com',
                    'com.tr': 'otrs-test@passport.yandex.com.tr',
                },
                RESTORE_NOT_PASSED_ADDRESS='no_pass@passport.yandex.ru',
                DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
                RESTORE_ADM_FORM_DATA_URL=TEST_ADM_FORM_DATA_URL,
                RESTORE_SEMI_AUTO_DECISION_THRESHOLDS=TEST_TENSORNET_THRESHOLDS,
                RESTORE_SEMI_AUTO_NEGATIVE_DECISION_ENABLED=False,
                RESTORE_SEMI_AUTO_POSITIVE_DECISION_RETRY_IMPOSSIBLE_INTERVAL=60 * 60,
                **mock_counters()
        ):
            resp = self.make_request(self.request_params_step_6(), self.get_headers())

        self.assert_ok_response(resp)
        final_factors = self.make_step_6_factors(
            initial_factors,
        )
        self.assert_track_updated(
            factors=final_factors,
            semi_auto_step=STEP_FINISHED,  # перешли на следующий шаг
            is_for_learning=True,
        )
        self.assert_compare_recorded_to_statbox(
            factors=self.make_step_6_statbox_factors(
            ),
            step=STEP_6_FINAL_INFO,
            is_for_learning=True,
        )
        self.assert_restore_info_in_event_log()
        self.check_restore_log_entry(
            action=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            uid=str(TEST_DEFAULT_UID),
            restore_id=TEST_RESTORE_ID,
            data_json=final_factors,
        )
        self.assert_mail_sent(
            request_source=RESTORE_MESSAGE_REQUEST_SOURCE_FOR_POSITIVE_DECISION_RETRY,
        )

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 0)
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        eq_(counter.get(TEST_DEFAULT_UID), 1)
