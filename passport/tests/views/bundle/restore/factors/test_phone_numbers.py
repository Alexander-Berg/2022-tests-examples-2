# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    phone_numbers_factors,
    phone_numbers_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_IP,
    TEST_IP_3,
    TEST_USER_AGENT_2,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
    events_response,
)
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_MATCH,
    FACTOR_NOT_SET,
)
from passport.backend.core.compare.test.compare import compare_uas_factor
from passport.backend.core.historydb.events import (
    EVENT_OLD_YASMS_PHONE_ACTION,
    EVENT_OLD_YASMS_PHONE_NUMBER,
    EVENT_OLD_YASMS_PHONE_STATUS,
    EVENT_USER_AGENT,
    EVENT_USERINFO_FT,
)
from passport.backend.core.models.phones.faker import (
    build_phone_being_bound,
    build_phone_bound,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts
class PhoneNumbersHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def get_default_account_kwargs(self, phones=None, *args, **kwargs):
        account_kwargs = super(PhoneNumbersHandlerTestCase, self).get_default_account_kwargs(*args, **kwargs)
        if phones:
            account_kwargs = deep_merge(
                account_kwargs,
                *phones
            )
        return account_kwargs

    def form_values(self, phone_numbers=None):
        return {
            'phone_numbers': phone_numbers,
        }

    def test_phone_numbers_absence_not_match(self):
        """Пользователь считает, что не вводил подтвержденных номеров телефонов, а они есть"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('phone_numbers')

            expected_factors = phone_numbers_factors(
                phone_numbers_factor_history_count=2,
                phone_numbers_factor_change_count=1,
                phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                phone_numbers_history=[
                    {
                        'value': '79111234567',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None},
                        ],
                    },
                    {
                        'value': '79117654321',
                        'intervals': [
                            {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                                'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                            },
                        ],
                    },
                ],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(
                    phone_numbers_factor_history_count=2,
                    phone_numbers_factor_change_count=1,
                    phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )

    def test_phone_numbers_absence_match(self):
        """Пользователь считает, что не вводил подтвержденных номеров телефонов, и это так"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('phone_numbers')

            eq_(factors, phone_numbers_factors())
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(),
                view.statbox,
            )

    def test_phone_numbers_full_match(self):
        """Пользователь вспомнил все номера телефонов"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values(phone_numbers=['89117654321', '79111234567'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('phone_numbers')

            expected_factors = phone_numbers_factors(
                phone_numbers_entered=['89117654321', '79111234567'],
                phone_numbers_history=[
                    {
                        'value': '79111234567',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None},
                        ],
                    },
                    {
                        'value': '79117654321',
                        'intervals': [
                            {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                                'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                            },
                        ],
                    },
                ],
                phone_numbers_matches=['79117654321', '79111234567'],
                phone_numbers_match_indices=[(0, 1), (1, 0)],
                phone_numbers_factor_entered_count=2,
                phone_numbers_factor_history_count=2,
                phone_numbers_factor_matches_count=2,
                phone_numbers_factor_change_count=1,
                phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_match_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(
                    phone_numbers_factor_entered_count=2,
                    phone_numbers_factor_history_count=2,
                    phone_numbers_factor_matches_count=2,
                    phone_numbers_factor_change_count=1,
                    phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_match_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                    phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )

    def test_phone_numbers_half_match(self):
        """Пользователь вспомнил один телефон из двух"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values(phone_numbers=['89117654332', '79111234567'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('phone_numbers')

            expected_factors = phone_numbers_factors(
                phone_numbers_entered=['89117654332', '79111234567'],
                phone_numbers_history=[
                    {
                        'value': '79117654321',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None},
                        ],
                    },
                    {
                        'value': '79111234567',
                        'intervals': [
                            {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                                'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                            },
                        ],
                    },
                ],
                phone_numbers_matches=['79111234567'],
                phone_numbers_match_indices=[(1, 1)],
                phone_numbers_factor_entered_count=2,
                phone_numbers_factor_history_count=2,
                phone_numbers_factor_matches_count=1,
                phone_numbers_factor_change_count=1,
                phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_match_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(
                    phone_numbers_factor_entered_count=2,
                    phone_numbers_factor_history_count=2,
                    phone_numbers_factor_matches_count=1,
                    phone_numbers_factor_change_count=1,
                    phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_match_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_phone_numbers_similar_ignored(self):
        """Пользователь ввел один и тот же номер с разными ошибками"""
        userinfo_response = self.default_userinfo_response(registration_datetime=datetime_to_string(unixtime_to_datetime(1)))
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete', user_ip=TEST_IP),
                event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
                event_item(timestamp=4, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
                event_item(timestamp=4, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values(phone_numbers=['89111234567', '79111234567', '79111234568'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('phone_numbers')

            expected_factors = phone_numbers_factors(
                phone_numbers_entered=['89111234567', '79111234567', '79111234568'],
                phone_numbers_history=[
                    {
                        'value': '79117654321',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None},
                        ],
                    },
                    {
                        'value': '79111234567',
                        'intervals': [
                            {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                                'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                            },
                            {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                                'end': None,
                            },
                        ],
                    },
                ],
                phone_numbers_matches=['79111234567'],
                phone_numbers_match_indices=[(0, 1)],
                phone_numbers_factor_entered_count=3,
                phone_numbers_factor_history_count=2,
                phone_numbers_factor_matches_count=1,
                phone_numbers_factor_change_count=2,
                phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                # совпадение телефонов одно, но телефон задавался дважды, поэтому два значения фактора
                phone_numbers_factor_match_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(
                    phone_numbers_factor_entered_count=3,
                    phone_numbers_factor_history_count=2,
                    phone_numbers_factor_matches_count=1,
                    phone_numbers_factor_change_count=2,
                    phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                    phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_match_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                    phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )

    def test_phone_numbers_non_digit_characters_ignored(self):
        """Пользователь ввел номер с вспомогательными символами - проверяем, что они отфильтровываются"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values(phone_numbers=['8-(911)-123-45-67', '+7  911  123  99  99'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('phone_numbers')

            expected_factors = phone_numbers_factors(
                phone_numbers_entered=['8-(911)-123-45-67', '+7  911  123  99  99'],
                phone_numbers_history=[
                    {
                        'value': '79117654321',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None},
                        ],
                    },
                    {
                        'value': '79111234567',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2), 'end': None},
                        ],
                    },
                ],
                phone_numbers_matches=['79111234567'],
                phone_numbers_match_indices=[(0, 1)],
                phone_numbers_factor_entered_count=2,
                phone_numbers_factor_history_count=2,
                phone_numbers_factor_matches_count=1,
                phone_numbers_factor_change_count=1,
                phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(
                    phone_numbers_factor_entered_count=2,
                    phone_numbers_factor_history_count=2,
                    phone_numbers_factor_matches_count=1,
                    phone_numbers_factor_change_count=1,
                    phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_phone_numbers_change_env_not_eq_user(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(user_ip=TEST_IP_3, firstname=u'вася', name=EVENT_USERINFO_FT, timestamp=1),
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP_3),
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP_3),
                event_item(timestamp=10, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP_3),
                event_item(timestamp=10, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP_3),
                event_item(timestamp=10, name=EVENT_USER_AGENT, value=TEST_USER_AGENT_2),
            ]),
        )
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values()
        headers = self.get_headers(user_agent=TEST_USER_AGENT_2)
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('phone_numbers')
            expected_factors = phone_numbers_factors(
                phone_numbers_history=[
                    {
                        'value': '79117654321',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP_3, timestamp=1), 'end': None},
                        ],
                    },
                    {
                        'value': '79111234567',
                        'intervals': [
                            {
                                'start': events_info_interval_point(user_ip=TEST_IP_3, timestamp=10, user_agent=TEST_USER_AGENT_2),
                                'end': None,
                            },
                        ],
                    },
                ],
                phone_numbers_factor_history_count=2,
                phone_numbers_factor_change_count=1,
                phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, compare_uas_factor('os.name', 'browser.name')],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(
                    phone_numbers_factor_history_count=2,
                    phone_numbers_factor_change_count=1,
                    phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, compare_uas_factor('os.name', 'browser.name')],
                ),
                view.statbox,
            )

    def test_phone_numbers_history_matches_with_phones(self):
        """Номера в истории соответствуют номерам в YaSMS"""
        userinfo_response = self.default_userinfo_response(
            phones=[
                build_phone_bound(1, '+79117654321'),
                build_phone_bound(2, '+79111234567'),
                build_phone_being_bound(3, '+79123214567', 1000),
            ],
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
                event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
                event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values(phone_numbers=['8-(911)-123-45-67', '+7  911  123  99  99'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('phone_numbers')

            expected_factors = phone_numbers_factors(
                phone_numbers_entered=['8-(911)-123-45-67', '+7  911  123  99  99'],
                phone_numbers_history=[
                    {
                        'value': '79117654321',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None},
                        ],
                    },
                    {
                        'value': '79111234567',
                        'intervals': [
                            {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2), 'end': None},
                        ],
                    },
                ],
                phone_numbers_matches=['79111234567'],
                phone_numbers_match_indices=[(0, 1)],
                phone_numbers_factor_entered_count=2,
                phone_numbers_factor_history_count=2,
                phone_numbers_factor_matches_count=1,
                phone_numbers_factor_change_count=1,
                phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(
                    phone_numbers_factor_entered_count=2,
                    phone_numbers_factor_history_count=2,
                    phone_numbers_factor_matches_count=1,
                    phone_numbers_factor_change_count=1,
                    phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                ),
                view.statbox,
            )
            # Я.смс не должен вызываться
            eq_(len(self.env.yasms.requests), 0)

    def test_phone_numbers_history_not_matches_with_phones(self):
        """Номера в YaSMS не соответствуют истории"""
        dt1 = unixtime_to_datetime(1)
        dt2 = unixtime_to_datetime(2)
        userinfo_response = self.default_userinfo_response(
            phones=[
                build_phone_bound(
                    1,
                    '+79117654321',
                    phone_created=dt1,
                    phone_bound=dt1,
                    phone_confirmed=dt1,
                ),
                build_phone_bound(
                    2,
                    '+79111234567',
                    phone_created=dt2,
                    phone_bound=dt2,
                    phone_confirmed=dt2,
                ),
                build_phone_being_bound(3, '+79123214567', 1000),
            ],
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )

        form_values = self.form_values(phone_numbers=['8-(911)-123-45-67', '+7  911  123  99  99'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('phone_numbers')

            expected_factors = phone_numbers_factors(
                phone_numbers_entered=['8-(911)-123-45-67', '+7  911  123  99  99'],
                phone_numbers_history=[
                    {
                        'value': '79117654321',
                        'intervals': [
                            {
                                'start': events_info_interval_point(user_ip=None, timestamp=1, yandexuid=None),
                                'end': None,
                            },
                        ],
                    },
                    {
                        'value': '79111234567',
                        'intervals': [
                            {
                                'start': events_info_interval_point(user_ip=None, timestamp=2, yandexuid=None),
                                'end': None,
                            },
                        ],
                    },
                ],
                phone_numbers_matches=['79111234567'],
                phone_numbers_match_indices=[(0, 1)],
                phone_numbers_factor_entered_count=2,
                phone_numbers_factor_history_count=2,
                phone_numbers_factor_matches_count=1,
                phone_numbers_factor_change_count=1,
                phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                phone_numbers_statbox_entry(
                    phone_numbers_factor_entered_count=2,
                    phone_numbers_factor_history_count=2,
                    phone_numbers_factor_matches_count=1,
                    phone_numbers_factor_change_count=1,
                    phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                    phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET],
                ),
                view.statbox,
            )
            # Я.смс не должен вызываться
            eq_(len(self.env.yasms.requests), 0)
