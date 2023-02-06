# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import time

import mock
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    device_id_factors,
    device_id_statbox_entry,
    registration_date_factors,
    registration_date_factors_statbox_entry,
    restore_attempts_factors,
    restore_attempts_statbox_entry,
    services_factors,
    services_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    DEFAULT_DATE_FORMAT,
    TEST_DEFAULT_ENTERED_REGISTRATION_DATE,
    TEST_DEVICE_ID_1,
    TEST_DEVICE_ID_2,
)
from passport.backend.api.views.bundle.restore.base import (
    RESTORE_METHOD_HINT,
    RESTORE_METHOD_LINK,
    RESTORE_METHOD_PHONE,
    RESTORE_METHOD_SEMI_AUTO_FORM,
)
from passport.backend.core.builders.historydb_api.exceptions import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    app_key_info,
    event_item,
    events_response,
)
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_NO_MATCH,
    FACTOR_NOT_SET,
)
from passport.backend.core.historydb.events import *
from passport.backend.core.historydb.events import EVENT_APP_KEY_INFO
from passport.backend.core.services import Service
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.time import (
    datetime_to_string,
    parse_datetime,
)
import pytz

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts()
class ServicesHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, services=None):
        return {
            'services': services or [],
        }

    def test_services_no_match(self):
        """Введенный сервис не использовался"""
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values(services=[u'mail'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('services')

            expected_factors = services_factors(
                services_entered=[u'mail'],
                services_factor_entered_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                services_statbox_entry(
                    services_factor_entered_count=1,
                ),
                view.statbox,
            )

    def test_services_match(self):
        """Введенные сервисы использовались"""
        service_names = [u'mail', u'metrika', u'disk', u'yandsearch']
        subscribed_services = [u'mail', u'metrika', u'cloud', u'rabota']
        # пользователь подписан на известные анкете сервисы, а также на другой сервис.
        userinfo_response = self.default_userinfo_response(
            subscribed_to=[Service.by_slug(slug) for slug in subscribed_services],
        )
        form_values = self.form_values(services=service_names)
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('services')

            expected_factors = services_factors(
                services_entered=service_names,
                services_account=[u'mail', u'disk', u'metrika'],  # изменился порядок
                services_matches=[u'mail', u'metrika', u'disk'],
                services_factor_entered_count=4,
                services_factor_account_count=3,
                services_factor_matches_count=3,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                services_statbox_entry(
                    services_factor_entered_count=4,
                    services_factor_account_count=3,
                    services_factor_matches_count=3,
                ),
                view.statbox,
            )


@with_settings_hosts()
class RegistrationDateHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, registration_date=TEST_DEFAULT_ENTERED_REGISTRATION_DATE):
        return {
            'registration_date': parse_datetime(registration_date, DEFAULT_DATE_FORMAT),
        }

    def test_registration_date_match(self):
        """Точное совпадение"""
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('registration_date')

            expected_factors = registration_date_factors()
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                registration_date_factors_statbox_entry(),
                view.statbox,
            )

    def test_registration_date_no_tz_detected(self):
        """Не удалось определить часовой пояс по IP"""
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            with mock.patch(
                'passport.backend.api.views.bundle.restore.factors.safe_detect_timezone',
                lambda user_ip: None
            ):
                factors = view.calculate_factors('registration_date')

            expected_factors = registration_date_factors()
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                registration_date_factors_statbox_entry(),
                view.statbox,
            )

    def test_registration_date_tz_offset_ok(self):
        """Успешная проверка, учет часового пояса пользователя при сравнении даты регистрации"""
        # пользователь приходит с часовым поясом Владивостока, говорит, что регистрировался сегодня
        # в базе дата регистрации - вчера в 11 вечера, по Владивостоку это сегодня
        user_tz = pytz.timezone('Asia/Vladivostok')
        today = datetime.today()
        reg_datetime = datetime(today.year, today.month, today.day, 23) + timedelta(days=-1)
        reg_datetime = datetime_to_string(reg_datetime)

        userinfo_response = self.default_userinfo_response(registration_datetime=reg_datetime)
        form_values = self.form_values(registration_date=today.strftime(DEFAULT_DATE_FORMAT))
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            with mock.patch(
                'passport.backend.api.views.bundle.restore.factors.safe_detect_timezone',
                lambda user_ip: user_tz,
            ), mock.patch(
                    'passport.backend.core.compare.dates.datetime',
                    mock.Mock(now=lambda: datetime(today.year, today.month, today.day, 16)),
            ):
                factors = view.calculate_factors('registration_date')

            expected_factors = registration_date_factors(
                registration_date_entered=today.strftime('%Y-%m-%d +10+1000'),
                registration_date_account=reg_datetime,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                registration_date_factors_statbox_entry(),
                view.statbox,
            )

    def test_registration_date_tz_offset_fail(self):
        """Неуспешная проверка, учет часового пояса пользователя при сравнении даты регистрации"""
        # пользователь приходит с часовым поясом Владивостока, говорит, что регистрировался сегодня
        # в базе дата регистрации - вчера в 4 дня, по Владивостоку это вчера
        user_tz = pytz.timezone('Asia/Vladivostok')
        today = datetime.today()
        reg_datetime = datetime(today.year, today.month, today.day, 16) + timedelta(days=-1)
        reg_datetime = datetime_to_string(reg_datetime)

        userinfo_response = self.default_userinfo_response(registration_datetime=reg_datetime)
        form_values = self.form_values(registration_date=today.strftime(DEFAULT_DATE_FORMAT))
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            with mock.patch(
                'passport.backend.api.views.bundle.restore.factors.safe_detect_timezone',
                lambda user_ip: user_tz,
            ), mock.patch(
                    'passport.backend.core.compare.dates.datetime',
                    mock.Mock(now=lambda: datetime(today.year, today.month, today.day, 16)),
            ):
                factors = view.calculate_factors('registration_date')

            expected_factors = registration_date_factors(
                registration_date_entered=today.strftime('%Y-%m-%d +10+1000'),
                registration_date_account=reg_datetime,
                registration_date_factor=FACTOR_FLOAT_NO_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                registration_date_factors_statbox_entry(registration_date_factor=FACTOR_FLOAT_NO_MATCH),
                view.statbox,
            )

    def test_registration_date_not_set_on_account(self):
        """Дата регистрации не установлена на аккаунте"""
        userinfo_response = self.default_userinfo_response(registration_datetime=None)
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('registration_date')

            expected_factors = registration_date_factors(
                registration_date_account=None,
                registration_date_factor=FACTOR_NOT_SET,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                registration_date_factors_statbox_entry(registration_date_factor=FACTOR_NOT_SET),
                view.statbox,
            )


@with_settings_hosts()
class DeviceIdHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def setUp(self):
        super(DeviceIdHandlerTestCase, self).setUp()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('restore')

    def tearDown(self):
        del self.track_manager
        super(DeviceIdHandlerTestCase, self).tearDown()

    def set_track_values(self, **params):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for attr_name, value in params.items():
                setattr(track, attr_name, value)

    def form_values(self):
        return {
            'track_id': self.track_id,
        }

    def test_with_no_data(self):
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('device_id')

            expected_factors = device_id_factors()
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(device_id_statbox_entry(), view.statbox)

    def test_with_no_data_in_history(self):
        self.set_track_values(device_ifv=TEST_DEVICE_ID_2)
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('device_id')

            expected_factors = device_id_factors(
                device_id_actual=TEST_DEVICE_ID_2,
                device_id_factor=FACTOR_BOOL_NO_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                device_id_statbox_entry(
                    device_id_factor=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )

    def test_with_no_user_data(self):
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_APP_KEY_INFO, value=app_key_info(device_hardware_id=TEST_DEVICE_ID_1)),
                event_item(name=EVENT_APP_KEY_INFO, value=app_key_info(device_ifv=TEST_DEVICE_ID_2, is_ios=True)),
            ]),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('device_id')

            expected_factors = device_id_factors(
                device_id_history=[TEST_DEVICE_ID_1.lower(), TEST_DEVICE_ID_2.lower()],
                device_id_factor=FACTOR_NOT_SET,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                device_id_statbox_entry(device_id_factor=FACTOR_NOT_SET),
                view.statbox,
            )

    def test_no_match(self):
        self.set_track_values(device_ifv=TEST_DEVICE_ID_2)
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_APP_KEY_INFO, value=app_key_info(device_hardware_id=TEST_DEVICE_ID_1)),
            ]),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('device_id')

            expected_factors = device_id_factors(
                device_id_actual=TEST_DEVICE_ID_2,
                device_id_history=[TEST_DEVICE_ID_1.lower()],
                device_id_factor=FACTOR_BOOL_NO_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                device_id_statbox_entry(
                    device_id_factor=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )

    def test_match(self):
        self.set_track_values(device_ifv=TEST_DEVICE_ID_2)
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_APP_KEY_INFO, value=app_key_info(device_hardware_id=TEST_DEVICE_ID_1)),
                event_item(name=EVENT_APP_KEY_INFO, value=app_key_info(device_ifv=TEST_DEVICE_ID_2, is_ios=True)),
            ]),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('device_id')

            expected_factors = device_id_factors(
                device_id_actual=TEST_DEVICE_ID_2,
                device_id_history=[TEST_DEVICE_ID_1.lower(), TEST_DEVICE_ID_2.lower()],
                device_id_factor=FACTOR_BOOL_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                device_id_statbox_entry(device_id_factor=FACTOR_BOOL_MATCH),
                view.statbox,
            )

    def test_with_historydb_fail(self):
        self.set_track_values(device_ifv=TEST_DEVICE_ID_2)
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_side_effect(
            'events',
            HistoryDBApiTemporaryError,
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('device_id')

            expected_factors = device_id_factors(
                device_id_actual=TEST_DEVICE_ID_2,
                historydb_api_events_status=False,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                device_id_statbox_entry(historydb_api_events_status=False),
                view.statbox,
            )


@with_settings_hosts(
    HISTORYDB_API_URL='http://localhost',
    RESTORE_SEMI_AUTO_POSITIVE_DECISION_RETRY_IMPOSSIBLE_INTERVAL=60 * 60,
    RESTORE_REQUEST_SOURCE_FOR_CHANGE_HINT='changehint',
)
class RestoreAttemptsHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def test_with_no_data(self):
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('restore_attempts')

            expected_factors = restore_attempts_factors()
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(restore_attempts_statbox_entry(), view.statbox)

    def test_with_recent_filtered_positive_attempts(self):
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_ACTION,
                    timestamp=1,
                    value='restore_passed_by_hint',
                ),
                event_item(
                    name=EVENT_ACTION,
                    timestamp=2,
                    value='restore_passed_by_phone',
                ),
            ]),
        )
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('restore_attempts')

            expected_factors = restore_attempts_factors(restore_attempts=[
                dict(
                    timestamp=1,
                    method=RESTORE_METHOD_HINT,
                ),
                dict(
                    timestamp=2,
                    method=RESTORE_METHOD_PHONE,
                ),
            ])
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(restore_attempts_statbox_entry(), view.statbox)

    def test_with_outdated_positive_attempt(self):
        userinfo_response = self.default_userinfo_response()
        attempt_ts = time.time() - 60 * 60 - 1
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_ACTION,
                    timestamp=attempt_ts,
                    value='restore_passed_by_link',
                ),
                event_item(
                    name=EVENT_INFO_SUPPORT_LINK_TYPE,
                    timestamp=attempt_ts,
                    value='1',
                ),
            ]),
        )
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('restore_attempts')

            expected_factors = restore_attempts_factors(restore_attempts=[
                dict(
                    timestamp=attempt_ts,
                    method=RESTORE_METHOD_LINK,
                    link_type='1',
                ),
            ])
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(restore_attempts_statbox_entry(), view.statbox)

    def test_with_matching_positive_attempt(self):
        userinfo_response = self.default_userinfo_response()
        attempt_ts = time.time() - 60 * 60 + 5
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_ACTION,
                    timestamp=attempt_ts,
                    value='restore_passed_by_semi_auto',
                ),
            ]),
        )
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('restore_attempts')

            expected_factors = restore_attempts_factors(
                restore_attempts=[
                    dict(
                        timestamp=attempt_ts,
                        method=RESTORE_METHOD_SEMI_AUTO_FORM,
                    ),
                ],
                has_recent_positive_decision=True,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                restore_attempts_statbox_entry(has_recent_positive_decision=True),
                view.statbox,
            )

    def test_with_historydb_fail(self):
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_side_effect(
            'events',
            HistoryDBApiTemporaryError,
        )
        with self.create_base_bundle_view(userinfo_response) as view:
            factors = view.calculate_factors('restore_attempts')

            expected_factors = restore_attempts_factors(historydb_api_events_status=False)
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                restore_attempts_statbox_entry(historydb_api_events_status=False),
                view.statbox,
            )
