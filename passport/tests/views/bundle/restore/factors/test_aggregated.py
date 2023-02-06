# -*- coding: utf-8 -*-

from copy import deepcopy

from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    aggregated_factors,
    aggregated_statbox_entry,
    answer_factors,
    birthday_factors,
    names_factors,
    one_day_match_env,
    passwords_factors,
    phone_numbers_factors,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.views.bundle.restore.factors import (
    ANSWERS_ENTITY_NAME,
    BIRTHDAYS_ENTITY_NAME,
    NAMES_ENTITY_NAME,
    PASSWORDS_ENTITY_NAME,
    PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES,
    PHONE_NUMBERS_ENTITY_NAME,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_successful_aggregated_browser_info,
    auth_successful_aggregated_os_info,
    auth_successful_aggregated_runtime_auth_item,
    auth_successful_aggregated_runtime_auths_item,
    auth_successful_aggregated_runtime_ip_info,
    auths_successful_aggregated_runtime_response,
    event_item,
    events_info_interval_point,
    events_response,
)
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_MATCH,
    FACTOR_FLOAT_NO_MATCH,
    FACTOR_NOT_SET,
    STRING_FACTOR_INEXACT_MATCH,
    UA_FACTOR_FULL_MATCH,
)
from passport.backend.core.compare.dates import LOOSE_DATE_THRESHOLD_FACTOR
from passport.backend.core.compare.test.compare import (
    compare_uas_factor,
    compared_user_agent,
)
from passport.backend.core.historydb.events import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts()
class AggregatedHandlerTestCase(BaseCalculateFactorsMixinTestCase):

    def setup_default_auth_history(self, now_ts, half_ts, reg_ts):
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=[
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            authtype=authtypes.AUTH_TYPE_IMAP,
                            status='successful',
                            ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP_2),
                            browser_info=auth_successful_aggregated_browser_info(
                                name='firefox',
                                yandexuid=TEST_YANDEXUID_COOKIE,
                            ),
                            os_info=auth_successful_aggregated_os_info(name='windows xp'),
                        ),
                    ],
                    timestamp=now_ts,
                ),
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            authtype=authtypes.AUTH_TYPE_IMAP,
                            status='successful',
                            ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP),
                        ),
                    ],
                    timestamp=half_ts,
                ),
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            authtype=authtypes.AUTH_TYPE_IMAP,
                            status='successful',
                            ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP_2),
                            browser_info=auth_successful_aggregated_browser_info(
                                name='firefox',
                                yandexuid=TEST_YANDEXUID_COOKIE,
                            ),
                            os_info=auth_successful_aggregated_os_info(name='windows xp'),
                        ),
                    ],
                    timestamp=reg_ts,
                ),
            ]),
        )

    def test_with_no_changes(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=[]),
        )

        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            previos_factors = merge_dicts(
                passwords_factors(),
                phone_numbers_factors(),
                answer_factors(),
                names_factors(),
                birthday_factors(),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))
            expected_factors = aggregated_factors(previos_factors)

            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(),
                view.statbox,
            )

    def test_with_changes_not_in_one_day(self):
        """Изменения пароля, КВ/КО и телефона, ФИО и ДР есть, но произошли в разные дни"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=[]),
        )
        day_1_ts = 1000
        day_2_ts = 10000000
        day_3_ts = 10000000000

        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            previos_factors = merge_dicts(
                passwords_factors(
                    passwords_last_change={
                        'origin_info': events_info_interval_point(
                            user_ip=TEST_IP,
                            timestamp=day_1_ts,
                            yandexuid=TEST_YANDEXUID_COOKIE,
                        ),
                        'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                    },
                ),
                phone_numbers_factors(
                    phone_numbers_history=[
                        {
                            'value': '79117654321',
                            'intervals': [
                                {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts), 'end': None},
                            ],
                        },
                        {
                            'value': '79111234567',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 1),
                                    'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 2),
                                },
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 3),
                                    'end': None,
                                },
                            ],
                        },
                    ],
                ),
                answer_factors(
                    answer_history=[
                        {
                            'question': u'1:qqq',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts),
                                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 1),
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'question': u'99:my question',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 1),
                                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 2),
                                        },
                                    ],
                                },
                                {
                                    'value': u'ответ',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 2),
                                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 4),
                                        },
                                    ],
                                },
                                {
                                    'value': u'answer',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 4),
                                            'end': None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                ),
                names_factors(
                    names_account=[
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_3_ts),
                                'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_3_ts + 1),
                            },
                        },
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_3_ts + 1),
                                'end': None,
                            },
                        },
                    ],
                ),
                birthday_factors(
                    birthday_account=[
                        {
                            'value': '2011-11-11',
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_3_ts),
                                # ДР более не актуальна, но подробностей мы не знаем
                                'end': {'timestamp': None},
                            },
                        },
                        {
                            'value': TEST_DEFAULT_BIRTHDAY,
                            'interval': {
                                'start': {'timestamp': None},
                                'end': None,
                            },
                        },
                    ],
                ),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            expected_factors = aggregated_factors(previos_factors)
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(),
                view.statbox,
            )

    def test_with_password_and_names_changes_in_one_day_with_env_match(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=[]),
        )
        day_1_ts = 1000
        day_2_ts = 10000000
        day_3_ts = 10000000000

        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response) as view:
            previos_factors = merge_dicts(
                passwords_factors(
                    passwords_last_change={
                        'origin_info': events_info_interval_point(
                            user_ip=TEST_IP,
                            timestamp=day_1_ts,
                            yandexuid=TEST_YANDEXUID_COOKIE,
                        ),
                        'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                    },
                ),
                phone_numbers_factors(
                    phone_numbers_history=[
                        {
                            'value': '79117654321',
                            'intervals': [
                                {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts), 'end': None},
                            ],
                        },
                        {
                            'value': '79111234567',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 1),
                                    'end': None,
                                },
                            ],
                        },
                    ],
                ),
                answer_factors(
                    answer_history=[
                        {
                            'question': u'1:qqq',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts),
                                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 1),
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'question': u'99:my question',
                            'answers': [
                                {
                                    'value': u'answer',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts + 1),
                                            'end': None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                ),
                names_factors(
                    names_account=[
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts),
                                'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_1_ts + 1),
                            },
                        },
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_1_ts + 1),
                                'end': None,
                            },
                        },
                    ],
                ),
                birthday_factors(
                    birthday_account=[
                        {
                            'value': '2011-11-11',
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_3_ts),
                                # ДР более не актуальна, но подробностей мы не знаем
                                'end': {'timestamp': None},
                            },
                        },
                        {
                            'value': TEST_DEFAULT_BIRTHDAY,
                            'interval': {
                                'start': {'timestamp': None},
                                'end': None,
                            },
                        },
                    ],
                ),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            expected_factors = aggregated_factors(
                previos_factors,
                password_and_personal_subnet_match=FACTOR_BOOL_MATCH,
                password_and_personal_ip_eq_user=FACTOR_BOOL_MATCH,
                password_and_personal_subnet_eq_user=FACTOR_BOOL_MATCH,
                password_and_personal_ua_eq_user=compare_uas_factor('yandexuid'),
                password_and_personal_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                password_and_personal_matches=[
                    {
                        'envs': [
                            one_day_match_env(
                                timestamp=1000,
                                entity=PASSWORDS_ENTITY_NAME,
                                ua=compared_user_agent(os=None, browser=None, yandexuid=TEST_YANDEXUID_COOKIE),
                            ),
                            one_day_match_env(
                                timestamp=1001,
                                entity=NAMES_ENTITY_NAME,
                                ip=TEST_IP_2,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                            ),
                        ],
                        'fields': ['subnet'],
                    },
                ],
            )

            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    password_and_personal_subnet_match=FACTOR_BOOL_MATCH,
                    password_and_personal_ip_eq_user=FACTOR_BOOL_MATCH,
                    password_and_personal_subnet_eq_user=FACTOR_BOOL_MATCH,
                    password_and_personal_ua_eq_user=compare_uas_factor('yandexuid'),
                    password_and_personal_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )

    def test_with_password_and_answer_and_phone_number_changes_in_one_day_with_env_match(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name=EVENT_USERINFO_FT, user_ip=TEST_IP, timestamp=100)]),
        )
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=[]),
        )
        day_1_ts = 1000

        headers = self.get_headers(user_agent=TEST_USER_AGENT_2)
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response, headers=headers) as view:
            previos_factors = merge_dicts(
                passwords_factors(
                    passwords_last_change={
                        'origin_info': events_info_interval_point(
                            user_ip=TEST_IP,
                            timestamp=day_1_ts + 10,
                            yandexuid=TEST_YANDEXUID_COOKIE,
                            user_agent=TEST_USER_AGENT_2,
                        ),
                        'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                    },
                ),
                phone_numbers_factors(
                    phone_numbers_history=[
                        {
                            'value': '79117654321',
                            'intervals': [
                                {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts), 'end': None},
                            ],
                        },
                        {
                            'value': '79111234567',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_1_ts + 1),
                                    'end': None,
                                },
                            ],
                        },
                    ],
                ),
                answer_factors(
                    answer_history=[
                        {
                            'question': u'1:qqq',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts + 2),
                                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts + 3),
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'question': u'99:my question',
                            'answers': [
                                {
                                    'value': u'answer',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts + 3),
                                            'end': None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                ),
                names_factors(
                    names_account=[
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts),
                                'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_1_ts + 1),
                            },
                        },
                    ],
                ),
                birthday_factors(
                    birthday_account=[],
                ),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            expected_factors = aggregated_factors(
                previos_factors,
                password_and_recovery_ip_match=FACTOR_BOOL_MATCH,
                password_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                password_and_recovery_ip_eq_user=FACTOR_BOOL_MATCH,
                password_and_recovery_subnet_eq_user=FACTOR_BOOL_MATCH,
                password_and_recovery_ua_eq_user=UA_FACTOR_FULL_MATCH,
                password_and_recovery_ip_eq_reg=FACTOR_BOOL_MATCH,
                password_and_recovery_subnet_eq_reg=FACTOR_BOOL_MATCH,
                password_and_recovery_ua_eq_reg=compare_uas_factor('yandexuid'),
                password_and_recovery_matches=[
                    {
                        'envs': [
                            one_day_match_env(
                                timestamp=1010,
                                entity=PASSWORDS_ENTITY_NAME,
                            ),
                            one_day_match_env(
                                timestamp=1003,
                                entity=ANSWERS_ENTITY_NAME,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                            ),
                        ],
                        'fields': ['ip', 'subnet'],
                    },
                    {
                        'envs': [
                            one_day_match_env(
                                timestamp=1010,
                                entity=PASSWORDS_ENTITY_NAME,
                            ),
                            one_day_match_env(
                                timestamp=1001,
                                entity=PHONE_NUMBERS_ENTITY_NAME,
                                ip=TEST_IP_2,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                            ),
                        ],
                        'fields': ['subnet'],
                    },
                ],
            )

            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    password_and_recovery_ip_match=FACTOR_BOOL_MATCH,
                    password_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                    password_and_recovery_ip_eq_user=FACTOR_BOOL_MATCH,
                    password_and_recovery_subnet_eq_user=FACTOR_BOOL_MATCH,
                    password_and_recovery_ua_eq_user=UA_FACTOR_FULL_MATCH,
                    password_and_recovery_ip_eq_reg=FACTOR_BOOL_MATCH,
                    password_and_recovery_subnet_eq_reg=FACTOR_BOOL_MATCH,
                    password_and_recovery_ua_eq_reg=compare_uas_factor('yandexuid'),
                ),
                view.statbox,
            )

    def test_with_multiple_pairs_in_one_day_with_no_env_match(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=[]),
        )
        day_1_ts = 1000
        day_2_ts = 1000000

        headers = self.get_headers(user_agent=TEST_USER_AGENT, ip=TEST_IP_3)
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response, headers=headers) as view:
            previos_factors = merge_dicts(
                passwords_factors(
                    passwords_last_change={
                        'origin_info': events_info_interval_point(
                            user_ip=TEST_IP_2,
                            timestamp=day_2_ts + 10,
                            yandexuid=TEST_YANDEXUID_COOKIE,
                            user_agent=TEST_USER_AGENT_2,
                        ),
                        'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                    },
                ),
                phone_numbers_factors(
                    phone_numbers_history=[
                        {
                            'value': '79117654321',
                            'intervals': [
                                {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts), 'end': None},
                            ],
                        },
                        {
                            'value': '79111234567',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_2_ts + 1),
                                    'end': None,
                                },
                            ],
                        },
                    ],
                ),
                answer_factors(
                    answer_history=[
                        {
                            'question': u'1:qqq',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts + 2),
                                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts + 3),
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'question': u'99:my question',
                            'answers': [
                                {
                                    'value': u'answer',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts + 3),
                                            'end': None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                ),
                names_factors(
                    names_account=[
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts),
                                'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_1_ts + 1),
                            },
                        },
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_1_ts + 1),
                                'end': None,
                            },
                        },
                    ],
                ),
                birthday_factors(
                    birthday_account=[],
                ),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            expected_factors = aggregated_factors(
                previos_factors,
                password_and_recovery_ip_match=FACTOR_BOOL_MATCH,
                password_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                password_and_recovery_ip_eq_user=FACTOR_BOOL_NO_MATCH,
                password_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
                password_and_recovery_ua_eq_user=compare_uas_factor('yandexuid'),
                password_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                password_and_recovery_matches=[
                    {
                        'envs': [
                            one_day_match_env(
                                timestamp=1000010,
                                entity=PASSWORDS_ENTITY_NAME,
                                ip=TEST_IP_2,
                            ),
                            one_day_match_env(
                                timestamp=1000001,
                                entity=PHONE_NUMBERS_ENTITY_NAME,
                                ip=TEST_IP_2,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                            ),
                        ],
                        'fields': ['ip', 'subnet'],
                    },
                ],
                personal_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                personal_and_recovery_ip_eq_user=FACTOR_BOOL_NO_MATCH,
                personal_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
                personal_and_recovery_ua_eq_user=FACTOR_BOOL_NO_MATCH,
                personal_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                personal_and_recovery_matches=[
                    {
                        'envs': [
                            one_day_match_env(
                                timestamp=1001,
                                entity=NAMES_ENTITY_NAME,
                                ip=TEST_IP_2,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                            ),
                            one_day_match_env(
                                timestamp=1003,
                                entity=ANSWERS_ENTITY_NAME,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                            ),
                        ],
                        'fields': ['subnet'],
                    },
                ],
            )

            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    password_and_recovery_ip_match=FACTOR_BOOL_MATCH,
                    password_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                    password_and_recovery_ip_eq_user=FACTOR_BOOL_NO_MATCH,
                    password_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
                    password_and_recovery_ua_eq_user=compare_uas_factor('yandexuid'),
                    password_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                    personal_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                    personal_and_recovery_ip_eq_user=FACTOR_BOOL_NO_MATCH,
                    personal_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
                    personal_and_recovery_ua_eq_user=FACTOR_BOOL_NO_MATCH,
                    personal_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )

    def test_auth_history_password_and_recovery_lookup(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        now_ts = time.time()
        reg_ts = now_ts - timedelta(days=40).total_seconds()
        half_ts = now_ts - timedelta(days=25).total_seconds()
        change_ts = now_ts - timedelta(days=10).total_seconds()
        self.setup_default_auth_history(now_ts, half_ts, reg_ts)
        day_2_ts = now_ts

        headers = self.get_headers(user_agent=TEST_USER_AGENT, ip=TEST_IP_3)
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        with self.create_base_bundle_view(userinfo_response, headers=headers) as view, self.time_now_mock(now_ts):
            previos_factors = merge_dicts(
                passwords_factors(
                    passwords_last_change={
                        'origin_info': events_info_interval_point(
                            user_ip=TEST_IP,
                            timestamp=change_ts,
                            yandexuid=TEST_YANDEXUID_COOKIE,
                            user_agent=TEST_USER_AGENT_2,
                        ),
                        'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                    },
                ),
                phone_numbers_factors(
                    phone_numbers_history=[
                        {
                            'value': '79117654321',
                            'intervals': [
                                {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=change_ts - 1), 'end': None},
                            ],
                        },
                        {
                            'value': '79111234567',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=change_ts),
                                    'end': None,
                                },
                            ],
                        },
                    ],
                ),
                answer_factors(
                    answer_history=[
                        {
                            'question': u'1:qqq',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts - 1),
                                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts),
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'question': u'99:my question',
                            'answers': [
                                {
                                    'value': u'answer',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts),
                                            'end': None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                ),
                names_factors(
                    names_account=[],
                ),
                birthday_factors(
                    birthday_account=[],
                ),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            factor_1 = LOOSE_DATE_THRESHOLD_FACTOR / 2
            factor_2 = LOOSE_DATE_THRESHOLD_FACTOR
            expected_factors = aggregated_factors(
                previos_factors,
                password_and_recovery_ip_first_auth_depth=[factor_2, factor_1, FACTOR_NOT_SET],
                password_and_recovery_subnet_first_auth_depth=[factor_2, FACTOR_NOT_SET, FACTOR_NOT_SET],
                password_and_recovery_ua_first_auth_depth=[factor_2, FACTOR_NOT_SET, FACTOR_NOT_SET],
                password_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                password_and_recovery_ip_eq_user=FACTOR_BOOL_NO_MATCH,
                password_and_recovery_ua_eq_user=compare_uas_factor('yandexuid'),
                password_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
                password_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                password_and_recovery_matches=[
                    {
                        'envs': [
                            one_day_match_env(
                                timestamp=change_ts,
                                entity=PASSWORDS_ENTITY_NAME,
                                ip_first_auth_info=build_auth_info(timestamp=half_ts),
                                subnet_first_auth_info=build_auth_info(timestamp=reg_ts),
                                ua_first_auth_info=build_auth_info(timestamp=reg_ts),
                            ),
                            one_day_match_env(
                                timestamp=change_ts,
                                entity=PHONE_NUMBERS_ENTITY_NAME,
                                ip=TEST_IP_2,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                                ip_first_auth_info=build_auth_info(timestamp=reg_ts),
                                subnet_first_auth_info=build_auth_info(timestamp=reg_ts),
                            ),
                        ],
                        'fields': ['subnet'],
                    },
                ],
                passwords_factor_change_ip_first_auth_depth=[factor_1],
                passwords_factor_change_subnet_first_auth_depth=[factor_2],
                passwords_factor_change_ua_first_auth_depth=[factor_2],
                passwords_change_ip_first_auth=[build_auth_info(timestamp=half_ts)],
                passwords_change_subnet_first_auth=[build_auth_info(timestamp=reg_ts)],
                passwords_change_ua_first_auth=[build_auth_info(timestamp=reg_ts)],
            )

            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    password_and_recovery_ip_first_auth_depth=[factor_2, factor_1, FACTOR_NOT_SET],
                    password_and_recovery_subnet_first_auth_depth=[factor_2, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    password_and_recovery_ua_first_auth_depth=[factor_2, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    password_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                    password_and_recovery_ip_eq_user=FACTOR_BOOL_NO_MATCH,
                    password_and_recovery_ua_eq_user=compare_uas_factor('yandexuid'),
                    password_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
                    password_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                    passwords_factor_change_ip_first_auth_depth=[factor_1],
                    passwords_factor_change_subnet_first_auth_depth=[factor_2],
                    passwords_factor_change_ua_first_auth_depth=[factor_2],
                ),
                view.statbox,
            )

    def test_auth_history_multiple_env_matches_lookup(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        now_ts = round(time.time())
        now_ts = now_ts - now_ts % timedelta(days=1).total_seconds()
        reg_ts = now_ts - timedelta(days=120).total_seconds()
        half_ts = now_ts - timedelta(days=75).total_seconds()
        self.setup_default_auth_history(now_ts, half_ts, reg_ts)
        day_1_ts = reg_ts
        day_2_ts = now_ts

        headers = self.get_headers(user_agent=TEST_USER_AGENT, ip=TEST_IP_3)
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        with self.create_base_bundle_view(userinfo_response, headers=headers) as view, self.time_now_mock(now_ts):
            previos_factors = merge_dicts(
                passwords_factors(
                    passwords_last_change={
                        'origin_info': events_info_interval_point(
                            user_ip=TEST_IP,
                            timestamp=day_1_ts,
                            yandexuid=TEST_YANDEXUID_COOKIE,
                            user_agent=TEST_USER_AGENT_2,
                        ),
                        'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                    },
                ),
                phone_numbers_factors(
                    phone_numbers_history=[
                        {
                            'value': '79117654321',
                            'intervals': [
                                {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts - 1), 'end': None},
                            ],
                        },
                        {
                            'value': '79111234567',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=day_2_ts),
                                    'end': None,
                                },
                            ],
                        },
                    ],
                ),
                answer_factors(
                    answer_history=[
                        {
                            'question': u'1:qqq',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts - 1),
                                            'end': events_info_interval_point(
                                                user_ip=TEST_IP_4,
                                                timestamp=day_2_ts,
                                                yandexuid=TEST_YANDEXUID_COOKIE,
                                                user_agent=TEST_USER_AGENT_2,
                                            ),
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'question': u'99:my question',
                            'answers': [
                                {
                                    'value': u'answer',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(
                                                user_ip=TEST_IP_4,
                                                timestamp=day_2_ts,
                                                yandexuid=TEST_YANDEXUID_COOKIE,
                                                user_agent=TEST_USER_AGENT_2,
                                            ),
                                            'end': None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                ),
                names_factors(
                    names_account=[
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts - 1),
                                'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts),
                            },
                        },
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts),
                                'end': None,
                            },
                        },
                    ],
                ),
                birthday_factors(
                    birthday_account=[
                        {
                            'value': '2011-11-11',
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts - 1),
                                'end': events_info_interval_point(
                                    user_ip=TEST_IP_3,
                                    timestamp=day_2_ts,
                                    yandexuid=TEST_YANDEXUID_COOKIE,
                                    user_agent=TEST_USER_AGENT_2,
                                ),
                            },
                        },
                        {
                            'value': TEST_DEFAULT_BIRTHDAY,
                            'interval': {
                                'start': events_info_interval_point(
                                    user_ip=TEST_IP_3,
                                    timestamp=day_2_ts,
                                    yandexuid=TEST_YANDEXUID_COOKIE,
                                    user_agent=TEST_USER_AGENT_2,
                                ),
                                'end': None,
                            },
                        },
                    ],
                ),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            factor_1 = (1 + LOOSE_DATE_THRESHOLD_FACTOR) / 2
            ip_depth = [FACTOR_FLOAT_MATCH, factor_1, FACTOR_NOT_SET, FACTOR_NOT_SET]
            subnet_depth = [FACTOR_FLOAT_MATCH] + [FACTOR_NOT_SET] * (PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES - 1)
            ua_depth = [FACTOR_FLOAT_MATCH] + [FACTOR_NOT_SET] * (PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES - 1)
            expected_factors = aggregated_factors(
                previos_factors,
                personal_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                personal_and_recovery_ua_match=FACTOR_BOOL_MATCH,
                personal_and_recovery_ip_eq_user=FACTOR_BOOL_MATCH,
                personal_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
                personal_and_recovery_ua_eq_user=compare_uas_factor('yandexuid'),
                personal_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                personal_and_recovery_ip_first_auth_depth=ip_depth,
                personal_and_recovery_subnet_first_auth_depth=subnet_depth,
                personal_and_recovery_ua_first_auth_depth=ua_depth,
                personal_and_recovery_matches=[
                    {
                        'envs': [
                            one_day_match_env(
                                timestamp=day_2_ts,
                                entity=NAMES_ENTITY_NAME,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                                ip_first_auth_info=build_auth_info(timestamp=half_ts),
                                subnet_first_auth_info=build_auth_info(timestamp=reg_ts),
                            ),
                            one_day_match_env(
                                timestamp=day_2_ts,
                                entity=PHONE_NUMBERS_ENTITY_NAME,
                                ip=TEST_IP_2,
                                ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                                ip_first_auth_info=build_auth_info(timestamp=reg_ts),
                                subnet_first_auth_info=build_auth_info(timestamp=reg_ts),
                            ),
                        ],
                        'fields': ['subnet'],
                    },
                    {
                        'envs': [
                            one_day_match_env(
                                timestamp=day_2_ts,
                                entity=BIRTHDAYS_ENTITY_NAME,
                                ip=TEST_IP_3,
                                subnet=None,
                                ua_first_auth_info=build_auth_info(timestamp=reg_ts),
                            ),
                            one_day_match_env(
                                timestamp=day_2_ts,
                                entity=ANSWERS_ENTITY_NAME,
                                ip=TEST_IP_4,
                                subnet=None,
                                ua_first_auth_info=build_auth_info(timestamp=reg_ts),
                            ),
                        ],
                        'fields': ['ua'],
                    },
                ],
                passwords_factor_change_ip_first_auth_depth=[FACTOR_NOT_SET],  # т.к. IP появился после того как была сделана смена
                passwords_factor_change_subnet_first_auth_depth=[FACTOR_FLOAT_NO_MATCH],
                passwords_factor_change_ua_first_auth_depth=[FACTOR_FLOAT_NO_MATCH],
                passwords_change_ip_first_auth=[build_auth_info(timestamp=half_ts)],
                passwords_change_subnet_first_auth=[build_auth_info(timestamp=reg_ts)],
                passwords_change_ua_first_auth=[build_auth_info(timestamp=reg_ts)],
            )

            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    personal_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
                    personal_and_recovery_ua_match=FACTOR_BOOL_MATCH,
                    personal_and_recovery_ip_eq_user=FACTOR_BOOL_MATCH,
                    personal_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
                    personal_and_recovery_ua_eq_user=compare_uas_factor('yandexuid'),
                    personal_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
                    personal_and_recovery_ip_first_auth_depth=ip_depth,
                    personal_and_recovery_subnet_first_auth_depth=subnet_depth,
                    personal_and_recovery_ua_first_auth_depth=ua_depth,
                    passwords_factor_change_ip_first_auth_depth=[FACTOR_NOT_SET],  # т.к. IP появился после того как была сделана смена
                    passwords_factor_change_subnet_first_auth_depth=[FACTOR_FLOAT_NO_MATCH],
                    passwords_factor_change_ua_first_auth_depth=[FACTOR_FLOAT_NO_MATCH],
                ),
                view.statbox,
            )

    def test_phone_numbers_match_factors_update(self):
        """Вычисление факторов авторизации для совпадения телефонов"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        now_ts = round(time.time())
        now_ts = now_ts - now_ts % timedelta(days=1).total_seconds()
        reg_ts = now_ts - timedelta(days=120).total_seconds()
        half_ts = now_ts - timedelta(days=75).total_seconds()
        self.setup_default_auth_history(now_ts, half_ts, reg_ts)
        day_1_ts = reg_ts
        day_2_ts = now_ts

        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        with self.create_base_bundle_view(userinfo_response) as view:
            previos_factors = merge_dicts(
                passwords_factors(),
                phone_numbers_factors(
                    phone_numbers_history=[
                        {
                            'value': '79117654321',
                            'intervals': [
                                {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts), 'end': None},
                            ],
                        },
                        {
                            'value': '79111234567',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts),
                                    'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts - 1),
                                },
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts),
                                    'end': None,
                                },
                            ],
                        },
                    ],
                    phone_numbers_match_indices=[(0, 1)],  # совпадение со вторым значением в истории
                ),
                answer_factors(),
                names_factors(),
                birthday_factors(),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            factor_1 = (1 + LOOSE_DATE_THRESHOLD_FACTOR) / 2
            expected_factors = aggregated_factors(
                previos_factors,
                # IP в истории авторизаций появился в half_ts; первое совпадение с этим IP в reg_ts < half_ts, поэтому
                # значение фактора FACTOR_NOT_SET
                phone_numbers_factor_match_ip_first_auth_depth=[FACTOR_NOT_SET, factor_1],
                # subnet в истории авторизаций появился в момент reg_ts; первое совпадение с ним в reg_ts,
                # второе - now_ts
                phone_numbers_factor_match_subnet_first_auth_depth=[FACTOR_FLOAT_NO_MATCH, FACTOR_FLOAT_MATCH],
                phone_numbers_match_ip_first_auth=[build_auth_info(timestamp=half_ts), build_auth_info(timestamp=half_ts)],
                phone_numbers_match_subnet_first_auth=[build_auth_info(timestamp=reg_ts), build_auth_info(timestamp=reg_ts)],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    phone_numbers_factor_match_ip_first_auth_depth=[FACTOR_NOT_SET, factor_1],
                    phone_numbers_factor_match_subnet_first_auth_depth=[FACTOR_FLOAT_NO_MATCH, FACTOR_FLOAT_MATCH],
                ),
                view.statbox,
            )

    def test_phone_numbers_multiple_matches_factors_update(self):
        """Вычисление факторов авторизации для нескольких совпадений телефонов"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        now_ts = round(time.time())
        now_ts = now_ts - now_ts % timedelta(days=1).total_seconds()
        reg_ts = now_ts - timedelta(days=120).total_seconds()
        half_ts = now_ts - timedelta(days=75).total_seconds()
        self.setup_default_auth_history(now_ts, half_ts, reg_ts)

        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        with self.create_base_bundle_view(userinfo_response) as view:
            previos_factors = merge_dicts(
                passwords_factors(),
                phone_numbers_factors(
                    phone_numbers_history=[
                        {
                            'value': '79117654321',
                            'intervals': [
                                {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=half_ts), 'end': None},
                            ],
                        },
                        {
                            'value': '79111234567',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=now_ts),
                                    'end': events_info_interval_point(user_ip=TEST_IP, timestamp=now_ts + 1),
                                },
                            ],
                        },
                    ],
                    phone_numbers_match_indices=[(0, 1), (1, 0)],  # совпадение с обоими значениями
                ),
                answer_factors(),
                names_factors(),
                birthday_factors(),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            factor_1 = (1 + LOOSE_DATE_THRESHOLD_FACTOR) / 2
            expected_factors = aggregated_factors(
                previos_factors,
                phone_numbers_factor_match_ip_first_auth_depth=[FACTOR_FLOAT_NO_MATCH, factor_1],
                phone_numbers_factor_match_subnet_first_auth_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                phone_numbers_match_ip_first_auth=[build_auth_info(timestamp=half_ts), build_auth_info(timestamp=half_ts)],
                phone_numbers_match_subnet_first_auth=[build_auth_info(timestamp=reg_ts), build_auth_info(timestamp=reg_ts)],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    phone_numbers_factor_match_ip_first_auth_depth=[FACTOR_FLOAT_NO_MATCH, factor_1],
                    phone_numbers_factor_match_subnet_first_auth_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                ),
                view.statbox,
            )

    def test_answer_match_factor_update(self):
        """Вычисление факторов авторизации для совпадения КО"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        now_ts = round(time.time())
        now_ts = now_ts - now_ts % timedelta(days=1).total_seconds()
        reg_ts = now_ts - timedelta(days=120).total_seconds()
        half_ts = now_ts - timedelta(days=75).total_seconds()
        self.setup_default_auth_history(now_ts, half_ts, reg_ts)
        day_2_ts = now_ts

        headers = self.get_headers(user_agent=TEST_USER_AGENT, ip=TEST_IP_3)
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        with self.create_base_bundle_view(userinfo_response, headers=headers) as view, self.time_now_mock(now_ts):
            previos_factors = merge_dicts(
                passwords_factors(),
                phone_numbers_factors(),
                answer_factors(
                    answer_index_best=(1, 0),  # второй КВ, первый КО на этот КВ
                    answer_factor_best=STRING_FACTOR_INEXACT_MATCH,  # без успешного сравнения фактор не считается
                    answer_history=[
                        {
                            'question': u'1:qqq',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts - 1),
                                            'end': events_info_interval_point(
                                                user_ip=TEST_IP_4,
                                                timestamp=day_2_ts,
                                                yandexuid=TEST_YANDEXUID_COOKIE,
                                                user_agent=TEST_USER_AGENT_2,
                                            ),
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'question': u'99:my question',
                            'answers': [
                                {
                                    'value': u'answer',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(
                                                user_ip=TEST_IP_4,
                                                timestamp=day_2_ts,
                                                yandexuid=TEST_YANDEXUID_COOKIE,
                                                user_agent=TEST_USER_AGENT_2,
                                            ),
                                            'end': None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                ),
                names_factors(),
                birthday_factors(),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            expected_factors = aggregated_factors(
                previos_factors,
                answer_factor_match_ua_first_auth_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET],
                answer_match_ua_first_auth=[build_auth_info(timestamp=reg_ts), None],
            )

            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    answer_factor_match_ua_first_auth_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_answer_match_factor_update_with_multiple_intervals(self):
        """Вычисление факторов авторизации для совпадения КО для нескольких интервалов актуальности"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        now_ts = round(time.time())
        now_ts = now_ts - now_ts % timedelta(days=1).total_seconds()
        reg_ts = now_ts - timedelta(days=120).total_seconds()
        half_ts = now_ts - timedelta(days=75).total_seconds()
        self.setup_default_auth_history(now_ts, half_ts, reg_ts)
        day_1_ts = reg_ts
        day_2_ts = now_ts

        headers = self.get_headers(user_agent=TEST_USER_AGENT, ip=TEST_IP_3)
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(reg_ts)))
        with self.create_base_bundle_view(userinfo_response, headers=headers) as view, self.time_now_mock(now_ts):
            previos_factors = merge_dicts(
                passwords_factors(),
                phone_numbers_factors(),
                answer_factors(
                    answer_index_best=(1, 0),  # второй КВ, первый КО на этот КВ
                    answer_factor_best=STRING_FACTOR_INEXACT_MATCH,  # без успешного сравнения фактор не считается
                    answer_history=[
                        {
                            'question': u'1:qqq',
                            'answers': [
                                {
                                    'value': u'КО',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts - 1),
                                            'end': events_info_interval_point(
                                                user_ip=TEST_IP_4,
                                                timestamp=day_2_ts,
                                                yandexuid=TEST_YANDEXUID_COOKIE,
                                                user_agent=TEST_USER_AGENT_2,
                                            ),
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'question': u'99:my question',
                            'answers': [
                                {
                                    'value': u'answer',
                                    'intervals': [
                                        {
                                            'start': events_info_interval_point(
                                                user_ip=TEST_IP_4,
                                                timestamp=day_1_ts,
                                                yandexuid=TEST_YANDEXUID_COOKIE,
                                                user_agent=TEST_USER_AGENT_2,
                                            ),
                                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=day_1_ts + 1),
                                        },
                                        {
                                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=day_2_ts),
                                            'end': None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                ),
                names_factors(),
                birthday_factors(),
            )
            factors = view.calculate_factors('aggregated_factors', calculated_factors=deepcopy(previos_factors))

            factor_1 = (1 + LOOSE_DATE_THRESHOLD_FACTOR) / 2
            expected_factors = aggregated_factors(
                previos_factors,
                answer_factor_match_ip_first_auth_depth=[FACTOR_NOT_SET, factor_1],
                answer_factor_match_subnet_first_auth_depth=[FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                answer_factor_match_ua_first_auth_depth=[FACTOR_FLOAT_NO_MATCH, FACTOR_NOT_SET],
                answer_match_ip_first_auth=[None, build_auth_info(timestamp=half_ts)],
                answer_match_subnet_first_auth=[None, build_auth_info(timestamp=reg_ts)],
                answer_match_ua_first_auth=[build_auth_info(timestamp=reg_ts), None],
            )

            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                aggregated_statbox_entry(
                    answer_factor_match_ip_first_auth_depth=[FACTOR_NOT_SET, factor_1],
                    answer_factor_match_subnet_first_auth_depth=[FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    answer_factor_match_ua_first_auth_depth=[FACTOR_FLOAT_NO_MATCH, FACTOR_NOT_SET],
                ),
                view.statbox,
            )
