# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_base import BaseTestRestoreSemiAutoView
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    reg_country_city_statbox_entry,
    registration_date_factors_statbox_entry,
    simple_birthday_statbox_entry,
    simple_names_statbox_entry,
    user_env_auths_factors,
    user_env_auths_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_COMPARE_REASONS_NO_MATCH,
    TEST_DEFAULT_BIRTHDAY,
    TEST_DEFAULT_COMPARE_REASONS,
    TEST_DEFAULT_ENTERED_REGISTRATION_DATE,
    TEST_DEFAULT_ENTERED_REGISTRATION_DATE_WITH_TZ,
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_LASTNAME,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_NAMES,
    TEST_DEFAULT_NAMES_FACTOR,
    TEST_DEFAULT_NAMES_FACTOR_MATCH,
    TEST_DEFAULT_NAMES_FACTOR_NO_MATCH,
    TEST_DEFAULT_REGISTRATION_COUNTRY,
    TEST_DEFAULT_REGISTRATION_DATE_FACTOR,
    TEST_DEFAULT_REGISTRATION_DATETIME,
    TEST_DEFAULT_STATBOX_ACCOUNT_FACTOR_NO_MATCH,
    TEST_DEFAULT_UID,
    TEST_IP,
    TEST_PHONE,
    TEST_REQUEST_SOURCE,
)
from passport.backend.api.views.bundle.exceptions import AccountDisabledError
from passport.backend.api.views.bundle.states import PasswordChangeForbidden
from passport.backend.core.builders.historydb_api import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_response,
)
from passport.backend.core.compare.compare import FACTOR_NOT_SET
from passport.backend.core.counters import restore_semi_auto_compare_counter
from passport.backend.core.historydb.events import (
    RESTORE_STATUS_PASSED,
    RESTORE_STATUS_REJECTED,
)
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator


eq_ = iterdiff(eq_)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_RETRIES=1,
)
class TestRestoreSemiAutoShortFormView(BaseTestRestoreSemiAutoView):
    statbox_action = 'submitted_short_form'

    def setUp(self):
        super(TestRestoreSemiAutoShortFormView, self).setUp()
        self.default_url = '/1/bundle/restore/semi_auto/short_form/?consumer=dev'
        self.setup_statbox_templates()
        self.set_historydb_responses(
            auths_aggregated_runtime_present=True,
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(),
        )

    def tearDown(self):
        super(TestRestoreSemiAutoShortFormView, self).tearDown()

    def setup_trackid_generator(self):
        # Да, в этой ручке используется auth-трек
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

    def setup_statbox_templates(self):
        super(TestRestoreSemiAutoShortFormView, self).setup_statbox_templates(
            mode='restore_short_form',
        )
        self.env.statbox.bind_entry(
            'submitted',
            action='submitted_short_form',
            _exclude=['uid'],
        )

    def statbox_compared_action(self, check_passed=True, **kwargs):
        default_compared_entry = {}
        for entry_getter in (
            simple_birthday_statbox_entry,
            simple_names_statbox_entry,
            user_env_auths_statbox_entry,
            reg_country_city_statbox_entry,
            registration_date_factors_statbox_entry,
        ):
            default_compared_entry.update(**entry_getter(**kwargs))
        return self.env.statbox.entry(
            'compared',
            check_passed=tskv_bool(check_passed),
            **default_compared_entry
        )

    def get_expected_factors(self,
                             request_source=TEST_REQUEST_SOURCE,
                             restore_status=RESTORE_STATUS_PASSED,
                             historydb_api_events_status=True,
                             names_entered=TEST_DEFAULT_NAMES,
                             names_account=TEST_DEFAULT_NAMES,
                             names_account_status=True,
                             names_account_reason=TEST_DEFAULT_COMPARE_REASONS,
                             names_account_factor=TEST_DEFAULT_NAMES_FACTOR_MATCH,
                             names_history=TEST_DEFAULT_NAMES,
                             names_history_status=True,
                             names_history_factor=TEST_DEFAULT_NAMES_FACTOR_MATCH,
                             names_history_reason=TEST_DEFAULT_COMPARE_REASONS,
                             birthday_entered=TEST_DEFAULT_BIRTHDAY,
                             birthday_account=TEST_DEFAULT_BIRTHDAY,
                             birthday_account_factor=1,
                             birthday_history=TEST_DEFAULT_BIRTHDAY,
                             birthday_history_factor=1,
                             registration_date_entered=TEST_DEFAULT_ENTERED_REGISTRATION_DATE_WITH_TZ,
                             registration_date_account=TEST_DEFAULT_REGISTRATION_DATETIME,
                             registration_date_factor=TEST_DEFAULT_REGISTRATION_DATE_FACTOR,
                             registration_ip=None,
                             registration_country_entered=TEST_DEFAULT_REGISTRATION_COUNTRY,
                             registration_country_entered_id=None,
                             registration_country_history=None,
                             registration_country_history_id=None,
                             registration_country_factor=FACTOR_NOT_SET,
                             registration_country_factor_id=FACTOR_NOT_SET,
                             registration_city_entered=None,
                             registration_city_entered_id=None,
                             registration_city_history=None,
                             registration_city_history_id=None,
                             registration_city_factor=FACTOR_NOT_SET,
                             registration_city_factor_id=FACTOR_NOT_SET,
                             **params):
        factors = {
            'request_source': request_source,
            'restore_status': restore_status,
            'historydb_api_events_status': historydb_api_events_status,
            'names': {
                'entered': names_entered.split(', '),
                'account': names_account.split(', '),
                'account_factor': names_account_factor,
                'account_status': names_account_status,
                'history': names_history.split(', ') if names_history else names_history,
                'history_factor': names_history_factor if names_history else TEST_DEFAULT_NAMES_FACTOR,
                'history_status': names_history_status if names_history else False,
            },
            'birthday': {
                'entered': birthday_entered,
                'account': birthday_account,
                'account_factor': birthday_account_factor,
                'history': birthday_history,
                'history_factor': birthday_history_factor if birthday_history else FACTOR_NOT_SET,
            },
            'registration_date': {
                'entered': registration_date_entered,
                'account': registration_date_account,
                'factor': registration_date_factor,
            },
            'registration_ip': registration_ip,
            'registration_country': {
                'entered': registration_country_entered,
                'entered_id': registration_country_entered_id,
                'history': registration_country_history,
                'history_id': registration_country_history_id,
                'factor': {
                    'text': registration_country_factor,
                    'id': registration_country_factor_id,
                },
            },
            'registration_city': {
                'entered': registration_city_entered,
                'entered_id': registration_city_entered_id,
                'history': registration_city_history,
                'history_id': registration_city_history_id,
                'factor': {
                    'text': registration_city_factor,
                    'id': registration_city_factor_id,
                },
            },
        }
        factors.update(user_env_auths_factors(**params))
        return factors

    def assert_track_updated(self,
                             factors=None,
                             uid=TEST_DEFAULT_UID,
                             login=TEST_DEFAULT_LOGIN,
                             compare_info_present=True,
                             **params):
        factors = factors or self.get_expected_factors()
        params.update(
            uid=str(uid),
            login=login,
            country='ru',
        )
        expected_track_data = dict(self.orig_track._data)
        expected_track_data.update(params)
        track = self.track_manager.read(self.track_id)
        new_track_data = dict(track._data)
        if compare_info_present:
            # Отдельно проверяем факторы в JSON'е
            new_factors = json.loads(new_track_data['factors'])
            del new_track_data['factors']
            eq_(factors, new_factors)

        eq_(new_track_data, expected_track_data)

    def query_params(self,
                     firstname=TEST_DEFAULT_FIRSTNAME,
                     eula_accepted=True,
                     lastname=TEST_DEFAULT_LASTNAME,
                     birthday=TEST_DEFAULT_BIRTHDAY,
                     registration_date=TEST_DEFAULT_ENTERED_REGISTRATION_DATE,
                     registration_country=TEST_DEFAULT_REGISTRATION_COUNTRY,
                     registration_country_id=None,
                     registration_city=None,
                     registration_city_id=None):
        params = {
            'track_id': self.track_id,
            'firstname': firstname,
            'lastname': lastname,
            'birthday': birthday,
            'registration_date': registration_date,
            'registration_country': registration_country,
            'eula_accepted': eula_accepted,
        }
        return params

    def set_track_values(self, **kwargs):
        params = {
            'user_entered_login': TEST_DEFAULT_LOGIN,
            'request_source': 'restore',
        }
        params.update(kwargs)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for attr_name, value in params.items():
                setattr(track, attr_name, value)
            self.orig_track = track.snapshot()

    def test_eula_not_accepted_fails(self):
        """ПС не принято"""
        self.set_track_values()
        resp = self.make_request(
            self.query_params(eula_accepted=False),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['eula_accepted.not_accepted'])
        self.assert_submit_state_or_error_recorded_to_statbox()
        self.assert_track_unchanged()

    def test_short_auths_runtime_temporary_unavailable_ok(self):
        """Данные об авторизациях не удалось получить, в остальном все ок"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(emails=None),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(),
        )
        self.env.historydb_api.set_response_side_effect(
            'auths_aggregated_runtime',
            HistoryDBApiTemporaryError,
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['backend.historydb_api_failed'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.statbox_compared_action(
                check_passed=False,
                auths_aggregated_runtime_api_status=False,
                names_history_found=False,
                birthday_history_factor=FACTOR_NOT_SET,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            ),
            self.env.statbox.entry(
                'finished_with_error',
                error='backend.historydb_api_failed',
            ),
        ])
        self.assert_track_updated(
            factors=self.get_expected_factors(
                auths_aggregated_runtime_api_status=False,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ip_first_auth=None,
                subnet_first_auth=None,
                ip_last_auth=None,
                subnet_last_auth=None,
                gathered_auths_count=0,
                birthday_history_factor=FACTOR_NOT_SET,
                birthday_history=None,
                names_history=None,
                restore_status=RESTORE_STATUS_REJECTED,
            ),
            emails='',
        )

    def test_short_no_auths_in_history_no_match_fails(self):
        """Данные об авторизациях не найдены в истории, при этом данные ФИО/ДР неверные"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(emails=None),
        )
        self.set_historydb_responses(
            auths_aggregated_runtime_present=True,
            auths_aggregated_runtime_items=[],
            names_present=False,
            birthday_present=False,
        )
        self.set_track_values()
        resp = self.make_request(
            self.query_params(firstname=u'A', lastname=u'B', birthday='1990-10-10'),
            self.get_headers(),
        )

        self.assert_error_response(resp, ['compare.not_matched'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.statbox_compared_action(
                check_passed=False,
                names_account_status=False,
                names_account_reason=TEST_COMPARE_REASONS_NO_MATCH,
                names_account_factor=TEST_DEFAULT_STATBOX_ACCOUNT_FACTOR_NO_MATCH,
                birthday_account_factor=0,
                birthday_history_factor=FACTOR_NOT_SET,
                names_history_found=False,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            ),
        ])
        self.assert_track_updated(
            factors=self.get_expected_factors(
                names_entered=u'A, B',
                names_account_status=False,
                names_account_reason=TEST_COMPARE_REASONS_NO_MATCH,
                names_account_factor=TEST_DEFAULT_NAMES_FACTOR_NO_MATCH,
                birthday_entered='1990-10-10',
                birthday_account_factor=0,
                birthday_history=None,
                names_history=None,
                restore_status=RESTORE_STATUS_REJECTED,
                factor_ip_auth_interval=FACTOR_NOT_SET,
                factor_ip_first_auth_depth=FACTOR_NOT_SET,
                factor_subnet_auth_interval=FACTOR_NOT_SET,
                factor_subnet_first_auth_depth=FACTOR_NOT_SET,
                ip_first_auth=None,
                subnet_first_auth=None,
                ip_last_auth=None,
                subnet_last_auth=None,
                gathered_auths_count=0,
            ),
            emails='',
        )

    def test_short_ip_limit_exceeded(self):
        """Слишком много попыток для данного IP"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses()
        self.set_track_values()

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit
        for i in range(counter.limit):
            counter.incr(TEST_IP)

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.assert_submit_state_or_error_recorded_to_statbox(
            state='rate_limit_exceeded',
            _exclude=['uid'],
        )
        self.assert_track_unchanged()

    def test_short_uid_limit_exceeded(self):
        """Слишком много попыток для данного UID"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_historydb_responses()
        self.set_track_values()

        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        # установим счетчик вызовов на uid в limit + 1
        for i in range(counter.limit + 1):
            counter.incr(TEST_DEFAULT_UID)

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.assert_submit_state_or_error_recorded_to_statbox(
            state='rate_limit_exceeded',
        )
        self.assert_track_unchanged()

    def test_short_uid_limit_updated_on_match(self):
        """При совпадении, счетчик по UID увеличивается"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(emails=None),
        )
        self.set_historydb_responses()
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp)
        counter = restore_semi_auto_compare_counter.get_per_uid_buckets().get(TEST_DEFAULT_UID)
        eq_(counter, 1)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.statbox_compared_action(),
        ])
        self.assert_track_updated(
            emails='',
            is_short_form_factors_checked='1',
        )

    def test_short_full_match_ok(self):
        """Все данные совпадают с аккаунтом"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(emails=None),
        )
        self.set_historydb_responses()
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.statbox_compared_action(),
        ])
        self.assert_track_updated(
            emails='',
            is_short_form_factors_checked='1',
        )

    def test_short_match_birthday_empty_ok(self):
        """Все данные совпадают с аккаунтом, кроме ДР, который не задан"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(birthday='', emails=None),
        )
        self.set_historydb_responses()
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.statbox_compared_action(birthday_account_factor=FACTOR_NOT_SET),
        ])
        self.assert_track_updated(
            factors=self.get_expected_factors(
                birthday_account=None,
                birthday_account_factor=FACTOR_NOT_SET,
            ),
            emails='',
            is_short_form_factors_checked='1',
        )

    def test_short_match_historydb_no_birthday_value_ok(self):
        """Все данные совпадают с аккаунтом, historydb вернула запись
        info.birthday без значения"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(emails=None),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(
                events=[event_item(name='info.birthday', value=None)],
            ),
        )
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.statbox_compared_action(
                names_history_found=False,
                birthday_history_factor=FACTOR_NOT_SET,
            ),
        ])
        self.assert_track_updated(
            factors=self.get_expected_factors(
                birthday_history=None,
                names_history=None,
            ),
            emails='',
            is_short_form_factors_checked='1',
        )

    def test_short_account_processing_finished(self):
        """Валидация аккаунта выдает, что обработка завершена."""

        def validation_failed_effect(self, *args, **kwargs):
            return True

        self.set_track_values()
        validate_account_patch = mock.patch(
            'passport.backend.api.views.bundle.restore.base.GetAccountForRestoreMixin.get_and_validate_account',
            side_effect=validation_failed_effect,
            autospec=True,
        )
        with validate_account_patch:
            resp = self.make_request(
                self.query_params(),
                self.get_headers(),
            )

        self.assert_ok_response(resp)
        self.assert_track_unchanged()

    def test_short_account_processing_failed(self):
        """Валидация аккаунта не проходит."""

        def validation_failed_effect(self, *args, **kwargs):
            self.state = PasswordChangeForbidden()
            raise AccountDisabledError

        self.set_track_values()
        validate_account_patch = mock.patch(
            'passport.backend.api.views.bundle.restore.base.GetAccountForRestoreMixin.get_and_validate_account',
            side_effect=validation_failed_effect,
            autospec=True,
        )
        with validate_account_patch:
            resp = self.make_request(
                self.query_params(),
                self.get_headers(),
            )

        self.assert_error_response(resp, ['account.disabled'])
        self.assert_track_unchanged()

    def test_short_with_secure_phone_error(self):
        """Все данные совпадают с аккаунтом, но есть номер телефона подтвержденный, эту анкету использовать нельзя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
                emails=None,
            ),
        )
        self.set_historydb_responses()
        self.set_track_values()
        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_track_unchanged()
