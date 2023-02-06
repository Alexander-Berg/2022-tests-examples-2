# -*- coding: utf-8 -*-
import base64

import mock
from nose.tools import (
    assert_raises,
    ok_,
)
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    password_matches_factors,
    password_matches_statbox_entry,
    passwords_factors,
    passwords_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.views.bundle.restore.factors import PASSWORD_MATCH_DEPTH
from passport.backend.core.builders.blackbox.exceptions import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_test_pwd_hashes_response
from passport.backend.core.builders.historydb_api.exceptions import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
    events_passwords_response,
    events_response,
)
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_MATCH,
    FACTOR_FLOAT_NO_MATCH,
    FACTOR_NOT_SET,
    UA_FACTOR_FULL_MATCH,
)
from passport.backend.core.compare.test.compare import compare_uas_factor
from passport.backend.core.historydb.events import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.validators import LooseDateValidator
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)
import pytz

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts()
class PasswordsHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, password_auth_date=TEST_PASSWORD_AUTH_DATE, passwords=None):
        return {
            'password_auth_date': LooseDateValidator.to_python(password_auth_date),
            'passwords': passwords or [TEST_PASSWORD],
        }

    def test_password_not_found(self):
        """Введенный пароль не найден в истории"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        form_values = self.form_values(passwords=['qwerty'], password_auth_date='2010-10-10')
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                password_auth_date_entered='2010-10-10 MSD+0400',
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(passwords_statbox_entry(), view.statbox)

    def test_password_historydb_find_password_fail(self):
        """Сбой HistoryDB при запросе истории пароля"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_side_effect(
            'events_passwords',
            HistoryDBApiTemporaryError,
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        form_values = self.form_values(passwords=['qwerty'], password_auth_date='2010-10-10')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                password_auth_date_entered='2010-10-10 MSD+0400',
                passwords_factor_auth_found=[FACTOR_NOT_SET] * 3,
                passwords_factor_equals_current=[FACTOR_NOT_SET] * 3,
                passwords_api_statuses=[False],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_api_status=False,
                    passwords_factor_auth_found=[FACTOR_NOT_SET] * 3,
                    passwords_factor_equals_current=[FACTOR_NOT_SET] * 3,
                ),
                view.statbox,
            )

    def test_password_found_in_range(self):
        """Введенный пароль найден в истории, дата попадает в период использования"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(
                password_found=True,
                active_ranges=[[1000000000, None], [90000, 100000000]],
            ),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        form_values = self.form_values(passwords=['qwerty'], password_auth_date='2002-00-00')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                password_auth_date_entered='2002-01-01 MSK+0300',
                passwords_factor_auth_found=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                passwords_factor_equals_current=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                passwords_factor_auth_date=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                passwords_indices=[1],
                passwords_intervals=[
                    [
                        {
                            'start': {'timestamp': 90000},
                            'end': {'timestamp': 100000000},
                        },
                        {
                            'start': {'timestamp': 1000000000},
                            'end': None,
                        },
                    ],
                ],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_factor_auth_found=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    passwords_factor_equals_current=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    passwords_factor_auth_date=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_password_found_out_of_range_tz_offset(self):
        """Введенный пароль найден в истории, дата не попадает в период использования,
        пользователь в другом часовом поясе"""
        userinfo_response = self.default_userinfo_response()
        password_valid_from_ts = int(time.time() - timedelta(days=4 * 365).total_seconds())
        password_valid_to_ts = int(time.time() - timedelta(days=3 * 365).total_seconds())
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(
                password_found=True,
                active_ranges=[[password_valid_from_ts, password_valid_to_ts]],
            ),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        form_values = self.form_values(passwords=['qwerty'], password_auth_date='2005-00-00')

        with mock.patch(
                'passport.backend.api.views.bundle.restore.factors.safe_detect_timezone',
                lambda user_ip: pytz.timezone('Asia/Vladivostok'),
        ):
            with self.create_base_bundle_view(userinfo_response, form_values) as view:
                factors = view.calculate_factors('passwords')

                expected_factors = passwords_factors(
                    password_auth_date_entered='2005-01-01 +10+1000',
                    passwords_indices=[0],
                    passwords_factor_auth_found=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    passwords_factor_auth_date=[FACTOR_FLOAT_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    passwords_factor_first_auth_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    passwords_intervals=[
                        [
                            {
                                'start': {'timestamp': password_valid_from_ts},
                                'end': {'timestamp': password_valid_to_ts},
                            },
                        ],
                    ],
                )
                eq_(factors, expected_factors)
                self.assert_entry_in_statbox(
                    passwords_statbox_entry(
                        passwords_factor_auth_found=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                        passwords_factor_auth_date=[FACTOR_FLOAT_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                        passwords_factor_first_auth_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    ),
                    view.statbox,
                )

    def test_password_found_inexact_match(self):
        """Введенный пароль найден в истории, дата не попадает в период
        использования, ошибка небольшая"""
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        range_start = today + timedelta(days=-5)
        range_end = today + timedelta(days=-3)
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(today + timedelta(days=-5)))
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(
                password_found=True,
                active_ranges=[
                    [datetime_to_unixtime(range_start), datetime_to_unixtime(range_end)],
                ],
            ),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        datetime_entered = range_start + timedelta(days=-1)
        form_values = self.form_values(
            passwords=['qwerty'],
            password_auth_date=datetime_entered.strftime(DEFAULT_DATE_FORMAT),
        )

        with self.create_base_bundle_view(userinfo_response, form_values) as view, self.time_now_mock(datetime_to_unixtime(today)):
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                password_auth_date_entered=datetime_entered.strftime('%Y-%m-%d MSK+0300'),
                passwords_factor_auth_found=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                passwords_factor_auth_date=[0.7, FACTOR_NOT_SET, FACTOR_NOT_SET],
                passwords_factor_first_auth_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                passwords_indices=[0],
                passwords_intervals=[
                    [
                        {
                            'start': {'timestamp': datetime_to_unixtime(range_start)},
                            'end': {'timestamp': datetime_to_unixtime(range_end)},
                        },
                    ],
                ],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_factor_auth_found=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    passwords_factor_auth_date=[0.7, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    passwords_factor_first_auth_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_multiple_passwords(self):
        """Несколько вариантов пароля"""
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        range_start = today + timedelta(days=-5)
        range_end = today + timedelta(days=-3)
        range_end_2 = range_end + timedelta(days=1)
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(range_start))
        self.env.historydb_api.set_response_side_effect(
            'events_passwords',
            [
                events_passwords_response(
                    password_found=True,
                    active_ranges=[
                        [datetime_to_unixtime(range_end_2), None],
                        [datetime_to_unixtime(range_end), datetime_to_unixtime(range_end_2)],
                    ],
                ),
                events_passwords_response(
                    password_found=False,
                ),
                events_passwords_response(
                    password_found=True,
                    active_ranges=[[datetime_to_unixtime(range_start), datetime_to_unixtime(range_end)]],
                ),
            ],
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        datetime_entered = range_end + timedelta(days=1)
        form_values = self.form_values(
            passwords=['qwerty', u'пороль', 'passward'],
            password_auth_date=datetime_entered.strftime(DEFAULT_DATE_FORMAT),
        )

        with self.create_base_bundle_view(userinfo_response, form_values) as view, self.time_now_mock(datetime_to_unixtime(today)):
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                password_auth_date_entered=datetime_entered.strftime('%Y-%m-%d MSK+0300'),
                passwords_factor_entered_count=3,
                passwords_factor_auth_found=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                passwords_factor_equals_current=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                passwords_factor_auth_date=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, 7.0 / 12],
                passwords_factor_first_auth_depth=[0.7, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                passwords_indices=[0, None, 0],
                passwords_intervals=[
                    [
                        {
                            'start': {'timestamp': datetime_to_unixtime(range_end)},
                            'end': {'timestamp': datetime_to_unixtime(range_end_2)},
                        },
                        {
                            'start': {'timestamp': datetime_to_unixtime(range_end_2)},
                            'end': None,
                        },
                    ],
                    [],
                    [
                        {
                            'start': {'timestamp': datetime_to_unixtime(range_start)},
                            'end': {'timestamp': datetime_to_unixtime(range_end)},
                        },
                    ],
                ],
                passwords_api_statuses=[True] * 3,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_factor_entered_count=3,
                    passwords_factor_auth_found=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                    passwords_factor_equals_current=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                    passwords_factor_auth_date=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, 7.0 / 12],
                    passwords_factor_first_auth_depth=[0.7, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                ),
                view.statbox,
            )

    def test_password_change_voluntary_eq_user(self):
        """Окружение последней смены пароля (добровольной) совпадает с пользовательским"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(
                password_found=False,
            ),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_USER_AGENT, value=TEST_USER_AGENT_2),
                event_item(
                    timestamp=1,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_CHANGE_PASSWORD,
                    user_ip=TEST_IP,
                    yandexuid=TEST_YANDEXUID_COOKIE,
                ),
                event_item(timestamp=1, name=EVENT_INFO_PASSWORD, value='hash'),
            ]),
        )
        headers = self.get_headers(user_agent=TEST_USER_AGENT_2)
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                passwords_last_change={
                    'origin_info': events_info_interval_point(
                        user_ip=TEST_IP,
                        timestamp=1,
                        user_agent=TEST_USER_AGENT_2,
                        yandexuid=TEST_YANDEXUID_COOKIE,
                    ),
                    'change_type': PASSWORD_CHANGE_TYPE_VOLUNTARY,
                },
                passwords_factor_change_count=1,
                passwords_factor_change_depth=[FACTOR_FLOAT_MATCH],
                passwords_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH],
                passwords_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH],
                passwords_factor_change_ua_eq_user=[UA_FACTOR_FULL_MATCH],
                passwords_factor_last_change_is_forced_change=FACTOR_BOOL_NO_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_factor_change_count=1,
                    passwords_factor_change_depth=[FACTOR_FLOAT_MATCH],
                    passwords_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH],
                    passwords_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH],
                    passwords_factor_change_ua_eq_user=[UA_FACTOR_FULL_MATCH],
                    passwords_factor_last_change_is_forced_change=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )

    def test_password_change_forced_env_not_eq_user(self):
        """Последняя смена пароля принудительная, выполнена пользователем, окружение не совпадает"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(
                password_found=False,
            ),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    timestamp=1,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_PASSWORD,
                    admin='alexco',
                    comment='broken',
                    user_ip=TEST_IP,
                ),
                event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|5'),
                event_item(
                    timestamp=2,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_CHANGE_PASSWORD,
                    user_ip=TEST_IP,
                    yandexuid=TEST_YANDEXUID_COOKIE,
                ),
                event_item(timestamp=2, name=EVENT_SID_LOGIN_RULE, value='8|1'),
            ]),
        )
        headers = self.get_headers(ip=TEST_IP_3)
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                passwords_last_change={
                    'origin_info': events_info_interval_point(
                        user_ip=TEST_IP,
                        timestamp=2,
                        yandexuid=TEST_YANDEXUID_COOKIE,
                    ),
                    'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                },
                passwords_last_change_request={
                    'comment': u'broken',
                    'admin': u'alexco',
                    'origin_info': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                    'change_required': True,
                },
                passwords_factor_change_count=1,
                passwords_factor_change_depth=[FACTOR_FLOAT_MATCH],
                passwords_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH],
                passwords_factor_change_ua_eq_user=[compare_uas_factor('yandexuid')],
                passwords_factor_last_change_is_forced_change=FACTOR_BOOL_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_factor_change_count=1,
                    passwords_factor_change_depth=[FACTOR_FLOAT_MATCH],
                    passwords_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH],
                    passwords_factor_change_ua_eq_user=[compare_uas_factor('yandexuid')],
                    passwords_factor_last_change_is_forced_change=FACTOR_BOOL_MATCH,
                ),
                view.statbox,
            )

    def test_password_change_forced_and_pending_env_not_eq_user(self):
        """Последняя смена пароля принудительная, не выполнена пользователем (но выполнялась ранее), окружение не совпадает"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(
                password_found=False,
            ),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    timestamp=1,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_PASSWORD,
                    admin='alexco',
                    comment='broken',
                    user_ip=TEST_IP,
                ),
                event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|5'),
                event_item(
                    timestamp=2,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_CHANGE_PASSWORD,
                    user_ip=TEST_IP,
                    yandexuid=TEST_YANDEXUID_COOKIE,
                ),
                event_item(timestamp=2, name=EVENT_SID_LOGIN_RULE, value='8|1'),
                event_item(
                    timestamp=3,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_PASSWORD,
                    admin='alexco',
                    comment='still broken!',
                    user_ip=TEST_IP,
                ),
                event_item(timestamp=3, name=EVENT_SID_LOGIN_RULE, value='8|5'),
            ]),
        )
        headers = self.get_headers(ip=TEST_IP_3)
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                passwords_last_change={
                    'origin_info': events_info_interval_point(
                        user_ip=TEST_IP,
                        timestamp=2,
                        yandexuid=TEST_YANDEXUID_COOKIE,
                    ),
                    'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                },
                passwords_last_change_request={
                    'comment': u'still broken!',
                    'admin': u'alexco',
                    'origin_info': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                    'change_required': True,
                },
                passwords_factor_change_count=1,
                passwords_factor_change_depth=[FACTOR_FLOAT_MATCH],
                passwords_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH],
                passwords_factor_change_ua_eq_user=[compare_uas_factor('yandexuid')],
                passwords_factor_last_change_is_forced_change=FACTOR_BOOL_MATCH,
                passwords_factor_forced_change_pending=FACTOR_BOOL_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_factor_change_count=1,
                    passwords_factor_change_depth=[FACTOR_FLOAT_MATCH],
                    passwords_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH],
                    passwords_factor_change_ua_eq_user=[compare_uas_factor('yandexuid')],
                    passwords_factor_last_change_is_forced_change=FACTOR_BOOL_MATCH,
                    passwords_factor_forced_change_pending=FACTOR_BOOL_MATCH,
                ),
                view.statbox,
            )

    def test_password_change_forced_and_pending_and_no_password_changes_present_env_not_eq_user(self):
        """Требуется принудительная смена пароля ,не выполнена пользователем (и не выполнялась ранее), окружение не совпадает"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(
                password_found=False,
            ),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    timestamp=1,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_PASSWORD,
                    admin='alexco',
                    comment='broken',
                    user_ip=TEST_IP,
                ),
                event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|5'),
            ]),
        )
        headers = self.get_headers(ip=TEST_IP_3)
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                passwords_last_change_request={
                    'comment': u'broken',
                    'admin': u'alexco',
                    'origin_info': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                    'change_required': True,
                },
                passwords_factor_forced_change_pending=FACTOR_BOOL_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_factor_forced_change_pending=FACTOR_BOOL_MATCH,
                ),
                view.statbox,
            )

    def test_password_change_forced_and_unset_env_not_eq_user(self):
        """Требование смены пароля снято, окружение не совпадает"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events_passwords',
            events_passwords_response(
                password_found=False,
            ),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    timestamp=1,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_PASSWORD,
                    admin='alexco',
                    comment='broken',
                    user_ip=TEST_IP,
                ),
                event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|5'),
                event_item(
                    timestamp=2,
                    name=EVENT_ACTION,
                    value=ACTION_ACCOUNT_PASSWORD,
                    admin='alexco',
                    comment='not broken, oops',
                    user_ip=TEST_IP,
                ),
                event_item(timestamp=2, name=EVENT_SID_LOGIN_RULE, value='8|1'),
            ]),
        )
        headers = self.get_headers(ip=TEST_IP_3)
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('passwords')

            expected_factors = passwords_factors(
                passwords_last_change_request={
                    'comment': u'not broken, oops',
                    'admin': u'alexco',
                    'origin_info': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                    'change_required': False,
                },
                passwords_factor_forced_change_pending=FACTOR_BOOL_NO_MATCH,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                passwords_statbox_entry(
                    passwords_factor_forced_change_pending=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )


@with_settings_hosts(BLACKBOX_RETRIES=4)
class PasswordMatchesHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, password=TEST_PASSWORD):
        return {
            'password': password,
        }

    def test_no_passwords_in_history(self):
        """Пароли в истории не найдены"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('password_matches')

        expected_factors = password_matches_factors()
        eq_(factors, expected_factors)
        self.assert_entry_in_statbox(password_matches_statbox_entry(), view.statbox)

        # Проверяем, что ЧЯ не вызывался
        eq_(len(self.env.blackbox.requests), 0)

    def test_history_passwords_processing(self):
        """Правильно подготавливаем хеши паролей для вызова ЧЯ"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_INFO_PASSWORD, value='*'),
                event_item(timestamp=2, name=EVENT_INFO_PASSWORD, value='hash1'),
                event_item(timestamp=3, name=EVENT_INFO_PASSWORD, value='2:hash2'),
                event_item(timestamp=4, name=EVENT_INFO_PASSWORD, value='hash1'),  # Дубликат
                event_item(timestamp=5, name=EVENT_INFO_PASSWORD, value=''),
            ]),
        )
        encoded_hash1 = base64.b64encode('1:hash1')
        encoded_hash2 = base64.b64encode('2:hash2')
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response({encoded_hash1: True, encoded_hash2: False}),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('password_matches')

        matches_factor = [FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET]
        expected_factors = password_matches_factors(
            password_matches_factor=matches_factor,
        )
        eq_(factors, expected_factors)
        self.assert_entry_in_statbox(
            password_matches_statbox_entry(
                password_matches_factor=matches_factor,
            ),
            view.statbox,
        )

        eq_(len(self.env.blackbox.requests), 1)
        request = self.env.blackbox.requests[0]
        request.assert_post_data_contains(
            {
                'method': 'test_pwd_hashes',
                'password': TEST_PASSWORD,
                'hashes': ','.join([encoded_hash1, encoded_hash2]),
                'uid': TEST_DEFAULT_UID,
            },
        )

    def test_with_many_passwords_in_history(self):
        """Смотрим только на заданное число паролей"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_INFO_PASSWORD, value='1:hash1'),
                event_item(timestamp=2, name=EVENT_INFO_PASSWORD, value='2:hash2'),
                event_item(timestamp=3, name=EVENT_INFO_PASSWORD, value='3:hash3'),
                event_item(timestamp=4, name=EVENT_INFO_PASSWORD, value='4:hash4'),
                event_item(timestamp=5, name=EVENT_INFO_PASSWORD, value='5:hash5'),
                event_item(timestamp=6, name=EVENT_INFO_PASSWORD, value='6:hash6'),
            ]),
        )
        encoded_hashes = [base64.b64encode(hash) for hash in ['2:hash2', '3:hash3', '4:hash4', '5:hash5', '6:hash6']]
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                dict(
                    {encoded_hash: False for encoded_hash in encoded_hashes},
                    **{encoded_hashes[0]: True}  # Совпадение для самого "старого" из хешей
                ),
            ),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('password_matches')

        matches_factor = [FACTOR_BOOL_NO_MATCH] * PASSWORD_MATCH_DEPTH
        matches_factor[-1] = FACTOR_BOOL_MATCH  # Видим совпадение для самого "старого" хеша
        expected_factors = password_matches_factors(
            password_matches_factor=matches_factor,
        )
        eq_(factors, expected_factors)
        self.assert_entry_in_statbox(
            password_matches_statbox_entry(
                password_matches_factor=matches_factor,
            ),
            view.statbox,
        )

        eq_(len(self.env.blackbox.requests), 1)
        request = self.env.blackbox.requests[0]
        request.assert_post_data_contains(
            {
                'method': 'test_pwd_hashes',
                'password': TEST_PASSWORD,
                'uid': TEST_DEFAULT_UID,
            },
        )
        ok_('hashes' in request.post_args)
        hashes = request.post_args['hashes'].split(',')
        eq_(sorted(hashes), sorted(encoded_hashes))

    def test_with_historydb_events_error(self):
        """Сбой HistoryDBApi - записывается в лог, исключение не выкидывается"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_side_effect(
            'events',
            HistoryDBApiTemporaryError,
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('password_matches')

        expected_factors = password_matches_factors(historydb_api_events_status=False)
        eq_(factors, expected_factors)
        self.assert_entry_in_statbox(
            password_matches_statbox_entry(historydb_api_events_status=False),
            view.statbox,
        )

        # Проверяем, что ЧЯ не вызывался
        eq_(len(self.env.blackbox.requests), 0)

    def test_with_blackbox_test_pwd_hashes_error(self):
        """Сбой test_pwd_hashes"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_INFO_PASSWORD, value='*'),
                event_item(timestamp=2, name=EVENT_INFO_PASSWORD, value='hash1'),
                event_item(timestamp=3, name=EVENT_INFO_PASSWORD, value='2:hash2'),
                event_item(timestamp=4, name=EVENT_INFO_PASSWORD, value='hash1'),  # Дубликат
                event_item(timestamp=5, name=EVENT_INFO_PASSWORD, value=''),
            ]),
        )
        encoded_hash1 = base64.b64encode('1:hash1')
        encoded_hash2 = base64.b64encode('2:hash2')
        self.env.blackbox.set_response_side_effect(
            'test_pwd_hashes',
            BlackboxTemporaryError,
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            with assert_raises(BlackboxTemporaryError):
                view.calculate_factors('password_matches')

        eq_(len(self.env.blackbox.requests), 4)
        request = self.env.blackbox.requests[0]
        request.assert_post_data_contains(
            {
                'method': 'test_pwd_hashes',
                'password': TEST_PASSWORD,
                'hashes': ','.join([encoded_hash1, encoded_hash2]),
                'uid': TEST_DEFAULT_UID,
            },
        )
