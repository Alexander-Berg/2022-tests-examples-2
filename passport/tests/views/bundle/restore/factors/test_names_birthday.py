# -*- coding: utf-8 -*-
from nose.tools import ok_
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    birthday_factors,
    birthday_statbox_entry,
    names_factors,
    names_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.views.bundle.restore.factors import get_names_birthday_check_status
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
    events_response,
)
from passport.backend.core.compare import (
    BIRTHDAYS_FACTOR_FULL_MATCH,
    BIRTHDAYS_FACTOR_INEXACT_MATCH,
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_MATCH,
    FACTOR_NOT_SET,
    STRING_FACTOR_INEXACT_MATCH,
    STRING_FACTOR_MATCH,
    STRING_FACTOR_NO_MATCH,
    UA_FACTOR_FULL_MATCH,
)
from passport.backend.core.compare.test.compare import compare_uas_factor
from passport.backend.core.historydb.events import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.birthday import Birthday
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
class MultipleNamesHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, firstnames=None, lastnames=None):
        return {
            'firstnames': firstnames or [TEST_DEFAULT_FIRSTNAME],
            'lastnames': lastnames or [TEST_DEFAULT_LASTNAME],
        }

    def test_no_match_names_not_set(self):
        """ФИО не установлены на аккаунте"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        userinfo_response = self.default_userinfo_response(firstname=None, lastname=None)
        form_values = self.form_values()

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                names_account=[],
                names_current_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_current_index=None,
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_registration_index=None,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_no_match_no_registration_factor(self):
        """Нет совпадений, фактор регистрации не вычисляется т.к. ФИО установлены после регистрации"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_INFO_FIRSTNAME,
                    value=TEST_DEFAULT_FIRSTNAME,
                    user_ip=TEST_IP,
                    timestamp=2,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            lastname=None,
        )
        form_values = self.form_values(firstnames=['A'], lastnames=['B'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                firstnames_entered=['A'],
                lastnames_entered=['B'],
                names_account=[
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': None,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': None,
                        },
                    },
                ],
                names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_current_index=((0, 0), 0),
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_registration_index=None,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_no_match_no_registration_datetime_at_account(self):
        """Нет совпадений, фактор регистрации не вычисляется т.к. на аккаунте не установлена дата регистрации"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_INFO_FIRSTNAME,
                    value=TEST_DEFAULT_FIRSTNAME,
                    user_ip=TEST_IP,
                    timestamp=2,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=None,
            lastname=None,
        )
        form_values = self.form_values(firstnames=['A'], lastnames=['B'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                firstnames_entered=['A'],
                lastnames_entered=['B'],
                names_account=[
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': None,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': None,
                        },
                    },
                ],
                names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_current_index=((0, 0), 0),
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_registration_index=None,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_no_match_with_registration_factor(self):
        """Нет совпадений, фактор регистрации вычисляется т.к. ФИО установлены при регистрации"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                # ФИО заданы при регистрации, далее изменена фамилия
                event_item(
                    name=EVENT_USERINFO_FT,
                    firstname=TEST_DEFAULT_FIRSTNAME,
                    lastname=TEST_DEFAULT_LASTNAME,
                    user_ip=TEST_IP,
                    timestamp=1,
                ),
                event_item(
                    name=EVENT_INFO_LASTNAME,
                    value=TEST_DEFAULT_LASTNAME_INEXACT,
                    user_ip=TEST_IP_2,
                    timestamp=10,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            lastname=TEST_DEFAULT_LASTNAME_INEXACT,
        )
        form_values = self.form_values(firstnames=['A'], lastnames=['B', 'P'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                firstnames_entered=['A'],
                lastnames_entered=['B', 'P'],
                names_account=[
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=10),
                        },
                    },
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=10),
                            'end': None,
                        },
                    },
                ],
                names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_current_index=((0, 0), 1),
                names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_registration_index=((0, 0), 0),
                names_factor_change_count=1,
                names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), FACTOR_NOT_SET, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_factor_change_count=1,
                    names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_no_match_with_intermediate_factor(self):
        """Нет совпадений, есть промежуточные значения ФИО в истории"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                # ФИО заданы при регистрации, далее изменена фамилия
                event_item(
                    name=EVENT_USERINFO_FT,
                    firstname=TEST_DEFAULT_FIRSTNAME,
                    lastname=TEST_DEFAULT_LASTNAME,
                    user_ip=TEST_IP,
                    timestamp=1,
                ),
                event_item(
                    name=EVENT_INFO_FIRSTNAME,
                    value=TEST_DEFAULT_FIRSTNAME_INEXACT,
                    user_ip=TEST_IP_2,
                    timestamp=10,
                ),
                event_item(
                    name=EVENT_INFO_LASTNAME,
                    value=TEST_DEFAULT_LASTNAME_INEXACT,
                    user_ip=TEST_IP,
                    timestamp=100,
                    yandexuid=TEST_YANDEXUID_COOKIE,
                ),
                event_item(name=EVENT_USER_AGENT, timestamp=100, value=TEST_USER_AGENT_2)
            ]),
        )
        headers = self.get_headers(user_agent=TEST_USER_AGENT_2)
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            firstname=TEST_DEFAULT_FIRSTNAME_INEXACT,
            lastname=TEST_DEFAULT_LASTNAME_INEXACT,
        )
        form_values = self.form_values(firstnames=['A'], lastnames=['B', 'P'])
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('multiple_names')

            third_point = events_info_interval_point(
                user_ip=TEST_IP,
                timestamp=100,
                user_agent=TEST_USER_AGENT_2,
                yandexuid=TEST_YANDEXUID_COOKIE,
            )
            expected_factors = names_factors(
                firstnames_entered=['A'],
                lastnames_entered=['B', 'P'],
                names_account=[
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=10),
                        },
                    },
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME_INEXACT,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=10),
                            'end': third_point,
                        },
                    },
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME_INEXACT,
                        'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                        'interval': {
                            'start': third_point,
                            'end': None,
                        },
                    },
                ],
                names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_current_index=((0, 0), 2),
                names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_registration_index=((0, 0), 0),
                names_intermediate_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_intermediate_indices=((0, 0), 1),
                names_factor_intermediate_depth=FACTOR_NOT_SET,  # не вычисляется, т.к. нет совпадения
                names_factor_change_count=2,
                names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                names_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, UA_FACTOR_FULL_MATCH],
                names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                names_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_intermediate_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_factor_intermediate_depth=FACTOR_NOT_SET,  # не вычисляется, т.к. нет совпадения
                    names_factor_change_count=2,
                    names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    names_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, UA_FACTOR_FULL_MATCH],
                    names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    names_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )

    def test_no_match_unexpected_account_names(self):
        """Нет совпадений, ФИО на аккаунте не найдены в истории"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_INFO_FIRSTNAME,
                    value=TEST_DEFAULT_FIRSTNAME,
                    user_ip=TEST_IP,
                    timestamp=1,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
        )
        form_values = self.form_values(firstnames=['A'], lastnames=['B'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                firstnames_entered=['A'],
                lastnames_entered=['B'],
                names_account=[
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': None,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': {'timestamp': None},
                        },

                    },
                    # запись, сформированная из данных аккаунта
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': {'timestamp': None},
                            'end': None,
                        },
                    },
                ],
                names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_current_index=((0, 0), 1),
                names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_registration_index=((0, 0), 0),
                names_factor_change_count=1,
                names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_factor_change_count=1,
                    names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_match_history_not_found(self):
        """Данных в истории нет, на аккаунте получили совпадение"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        userinfo_response = self.default_userinfo_response()
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                names_account=[
                    # запись, сформированная из данных аккаунта
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': {'timestamp': None},
                            'end': None,
                        },
                    },
                ],
                names_current_index=((0, 0), 0),
                names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
                names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                names_registration_index=None,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
                    names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_match_current_and_registration_with_timestamp_offset(self):
        """При регистрации указаны ФИО, являющиеся текущими - сопавдение; правильно отрабатываем
        при сдвиге времени события относительно времени регистрации из-за округления"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_USERINFO_FT,
                    firstname=TEST_DEFAULT_FIRSTNAME,
                    lastname=TEST_DEFAULT_LASTNAME_INEXACT,
                    user_ip=TEST_IP,
                    timestamp=1.1,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            lastname=TEST_DEFAULT_LASTNAME_INEXACT,
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('multiple_names')

            eq_(
                factors,
                names_factors(
                    names_account=[
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1.1),
                                'end': None,
                            },
                        },
                    ],
                    names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_INEXACT_MATCH],
                    names_current_index=((0, 0), 0),
                    names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_INEXACT_MATCH],
                    names_registration_index=((0, 0), 0),
                ),
            )
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_INEXACT_MATCH],
                    names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_INEXACT_MATCH],
                ),
                view.statbox,
            )

    def test_match_intermediate_best_match(self):
        """Совпадение только с промежуточным значением"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                # ФИО заданы при регистрации, далее изменена фамилия
                event_item(
                    name=EVENT_USERINFO_FT,
                    firstname='bad name',
                    lastname='bad name',
                    user_ip=TEST_IP_2,
                    timestamp=1,
                ),
                event_item(
                    name=EVENT_INFO_FIRSTNAME,
                    value=TEST_DEFAULT_FIRSTNAME_INEXACT,
                    user_ip=TEST_IP_3,
                    timestamp=10,
                ),
                event_item(
                    name=EVENT_INFO_LASTNAME,
                    value=TEST_DEFAULT_LASTNAME_INEXACT,
                    user_ip=TEST_IP_3,
                    timestamp=10,
                ),
                event_item(
                    name=EVENT_INFO_FIRSTNAME,
                    value=TEST_DEFAULT_FIRSTNAME,
                    user_ip=TEST_IP_2,
                    timestamp=20,
                ),
                event_item(
                    name=EVENT_INFO_LASTNAME,
                    value=TEST_DEFAULT_LASTNAME,
                    user_ip=TEST_IP_2,
                    timestamp=20,
                ),
                event_item(
                    name=EVENT_INFO_FIRSTNAME,
                    value='bad name',
                    user_ip=TEST_IP_2,
                    timestamp=30,
                ),
                event_item(
                    name=EVENT_INFO_LASTNAME,
                    value='bad name',
                    user_ip=TEST_IP_2,
                    timestamp=30,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            firstname='bad name',
            lastname='bad name',
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                names_account=[
                    {
                        'firstname': 'bad name',
                        'lastname': 'bad name',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP_3, timestamp=10),
                        },
                    },
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME_INEXACT,
                        'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP_3, timestamp=10),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                        },
                    },
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=30),
                        },
                    },
                    {
                        'firstname': 'bad name',
                        'lastname': 'bad name',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=30),
                            'end': None,
                        },
                    },
                ],
                names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_current_index=((0, 0), 3),
                names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                names_registration_index=((0, 0), 0),
                # лучшее совпадение - точное
                names_intermediate_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
                names_intermediate_indices=((0, 0), 2),
                names_factor_intermediate_depth=FACTOR_FLOAT_MATCH,
                names_factor_change_count=3,
                names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                names_factor_change_subnet_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                names_factor_change_subnet_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), compare_uas_factor('yandexuid'), compare_uas_factor('yandexuid')],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
                    names_intermediate_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
                    names_factor_intermediate_depth=FACTOR_FLOAT_MATCH,
                    names_factor_change_count=3,
                    names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                    names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                    names_factor_change_subnet_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                    names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    names_factor_change_subnet_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), compare_uas_factor('yandexuid'), compare_uas_factor('yandexuid')],
                ),
                view.statbox,
            )

    def test_match_inverted_no_registration_names(self):
        """Совпадение, но ФИО установлены после регистрации"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_USERINFO_FT,
                    firstname=TEST_DEFAULT_FIRSTNAME,
                    lastname=TEST_DEFAULT_LASTNAME,
                    user_ip=TEST_IP,
                    timestamp=2,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
        )
        with self.create_base_bundle_view(userinfo_response, self.form_values()) as view:
            factors = view.calculate_factors('multiple_names')

            eq_(
                factors,
                names_factors(
                    names_account=[
                        {
                            'firstname': TEST_DEFAULT_FIRSTNAME,
                            'lastname': TEST_DEFAULT_LASTNAME,
                            'interval': {
                                'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                                'end': None,
                            },
                        },
                    ],
                    names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
                    names_current_index=((0, 0), 0),
                    names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                    names_registration_index=None,
                ),
            )
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
                    names_registration_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_match_multiple_correct_firstnames(self):
        """Введенные имена учитываются при сравнении"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(
                    name=EVENT_USERINFO_FT,
                    firstname=TEST_DEFAULT_FIRSTNAME,
                    lastname=TEST_DEFAULT_LASTNAME,
                    user_ip=TEST_IP,
                    timestamp=1,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
        )
        form_values = self.form_values(
            firstnames=[TEST_DEFAULT_FIRSTNAME, TEST_DEFAULT_LASTNAME],
            lastnames=['B'],
        )
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                firstnames_entered=[TEST_DEFAULT_FIRSTNAME, TEST_DEFAULT_LASTNAME],
                lastnames_entered=['B'],
                names_account=[
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': None,
                        },
                    },
                ],
                names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_NO_MATCH],
                names_current_index=((0, 0), 0),
                names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_NO_MATCH],
                names_registration_index=((0, 0), 0),
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_NO_MATCH],
                    names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_NO_MATCH],
                ),
                view.statbox,
            )

    def test_match_multiple_correct_lastnames_best_match(self):
        """Несколько правильных введенных фамилий - выбираем лучшее совпадение"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                # ФИО заданы при регистрации, далее изменена фамилия
                event_item(
                    name=EVENT_USERINFO_FT,
                    firstname=TEST_DEFAULT_FIRSTNAME,
                    lastname=TEST_DEFAULT_LASTNAME,
                    user_ip=TEST_IP,
                    timestamp=1,
                ),
                event_item(
                    name=EVENT_INFO_FIRSTNAME,
                    value=TEST_DEFAULT_FIRSTNAME_INEXACT,
                    user_ip=TEST_IP_2,
                    timestamp=10,
                ),
                event_item(
                    name=EVENT_INFO_LASTNAME,
                    value=TEST_DEFAULT_LASTNAME_INEXACT,
                    user_ip=TEST_IP_2,
                    timestamp=10,
                ),
                event_item(
                    name=EVENT_INFO_LASTNAME,
                    value=TEST_DEFAULT_LASTNAME,
                    user_ip=TEST_IP,
                    timestamp=100,
                ),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            firstname=TEST_DEFAULT_FIRSTNAME_INEXACT,
        )
        form_values = self.form_values(
            lastnames=[TEST_DEFAULT_LASTNAME_INEXACT, TEST_DEFAULT_LASTNAME],
        )
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('multiple_names')

            expected_factors = names_factors(
                lastnames_entered=[TEST_DEFAULT_LASTNAME_INEXACT, TEST_DEFAULT_LASTNAME],
                names_account=[
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=10),
                        },
                    },
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME_INEXACT,
                        'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=10),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=100),
                        },
                    },
                    {
                        'firstname': TEST_DEFAULT_FIRSTNAME_INEXACT,
                        'lastname': TEST_DEFAULT_LASTNAME,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=100),
                            'end': None,
                        },
                    },
                ],
                names_current_factor=[STRING_FACTOR_INEXACT_MATCH, STRING_FACTOR_MATCH],
                names_current_index=((0, 1), 2),
                names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
                names_registration_index=((0, 1), 0),
                names_intermediate_factor=[STRING_FACTOR_INEXACT_MATCH, STRING_FACTOR_MATCH],
                names_intermediate_indices=((0, 0), 1),
                names_factor_intermediate_depth=FACTOR_FLOAT_MATCH,
                names_factor_change_count=2,
                names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                names_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                names_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), FACTOR_NOT_SET, compare_uas_factor('yandexuid')],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                names_statbox_entry(
                    names_current_factor=[STRING_FACTOR_INEXACT_MATCH, STRING_FACTOR_MATCH],
                    names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
                    names_intermediate_factor=[STRING_FACTOR_INEXACT_MATCH, STRING_FACTOR_MATCH],
                    names_factor_intermediate_depth=FACTOR_FLOAT_MATCH,
                    names_factor_change_count=2,
                    names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    names_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    names_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), FACTOR_NOT_SET, compare_uas_factor('yandexuid')],
                ),
                view.statbox,
            )


@with_settings_hosts()
class BirthdayHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, birthday=TEST_DEFAULT_BIRTHDAY):
        return {
            'birthday': Birthday.parse(birthday),
        }

    def test_no_match_birthday_not_set(self):
        """ДР не установлен на аккаунте"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        userinfo_response = self.default_userinfo_response(birthday=None)
        form_values = self.form_values()

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_account=[],
                birthday_current_factor=FACTOR_NOT_SET,
                birthday_registration_factor=FACTOR_NOT_SET,
                birthday_current_index=None,
                birthday_registration_index=None,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=FACTOR_NOT_SET,
                    birthday_registration_factor=FACTOR_NOT_SET,
                ),
                view.statbox,
            )

    def test_no_match_empty_history(self):
        """ДР установлен на аккаунте, история пустая"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values(birthday='2012-01-01')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_entered='2012-01-01',
                birthday_account=[
                    {
                        'value': TEST_DEFAULT_BIRTHDAY,
                        'interval': {
                            'start': {'timestamp': None},
                            'end': None,
                        },
                    },
                ],
                birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                birthday_current_index=0,
                birthday_registration_factor=FACTOR_NOT_SET,
                birthday_registration_index=None,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_registration_factor=FACTOR_NOT_SET,
                ),
                view.statbox,
            )

    def test_no_match_bad_birthday_in_history(self):
        """ДР установлен на аккаунте, в истории невалидный ДР"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name=EVENT_INFO_BIRTHDAY, value='abcd')]),
        )
        userinfo_response = self.default_userinfo_response()
        form_values = self.form_values(birthday='2012-01-01')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_entered='2012-01-01',
                birthday_account=[
                    {
                        'value': TEST_DEFAULT_BIRTHDAY,
                        'interval': {
                            'start': {'timestamp': None},
                            'end': None,
                        },
                    },
                ],
                birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                birthday_current_index=0,
                birthday_registration_factor=FACTOR_NOT_SET,
                birthday_registration_index=None,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_registration_factor=FACTOR_NOT_SET,
                ),
                view.statbox,
            )

    def test_no_match_account_birthday_not_in_history(self):
        """ДР установлен на аккаунте, не найден в истории"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_INFO_BIRTHDAY, value='2011-11-11', user_ip=TEST_IP, timestamp=1),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
        )
        form_values = self.form_values(birthday='2012-01-01')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_entered='2012-01-01',
                birthday_account=[
                    {
                        'value': '2011-11-11',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
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
                birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                birthday_current_index=1,
                birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                birthday_registration_index=0,
                birthday_factor_change_count=1,
                birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_factor_change_count=1,
                    birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_no_match(self):
        """Нет ни одного совпадения"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_INFO_BIRTHDAY, value='2011-12-11', user_ip=TEST_IP, timestamp=1),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2011-12-12', user_ip=TEST_IP, timestamp=2),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2011-12-13', user_ip=TEST_IP, timestamp=3),
                event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT_2, timestamp=3),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            birthday='2011-12-13',
        )
        form_values = self.form_values()
        headers = self.get_headers(user_agent=TEST_USER_AGENT_2)
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_account=[
                    {
                        'value': '2011-12-11',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                        },
                    },
                    {
                        'value': '2011-12-12',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3, user_agent=TEST_USER_AGENT_2),
                        },
                    },
                    {
                        'value': '2011-12-13',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3, user_agent=TEST_USER_AGENT_2),
                            'end': None,
                        },
                    },
                ],
                birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                birthday_intermediate_factor=FACTOR_BOOL_NO_MATCH,
                # первое не совпадение для промежуточных данных
                birthday_intermediate_index=1,
                birthday_registration_index=0,
                birthday_current_index=2,
                birthday_factor_change_count=2,
                birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, compare_uas_factor('os.name', 'browser.name')],
                birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_intermediate_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_factor_change_count=2,
                    birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, compare_uas_factor('os.name', 'browser.name')],
                    birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )

    def test_match_same_current_and_registration_birthday(self):
        """Совпадение с единственным ДР (текущий и при регистрации)"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_INFO_BIRTHDAY, value=TEST_DEFAULT_BIRTHDAY, user_ip=TEST_IP, timestamp=1),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
        )
        form_values = self.form_values()

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_account=[
                    {
                        'value': TEST_DEFAULT_BIRTHDAY,
                        'interval': {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None},
                    },
                ],
                birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                birthday_current_index=0,
                birthday_registration_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                birthday_registration_index=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                    birthday_registration_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                ),
                view.statbox,
            )

    def test_match_registration_birthday(self):
        """Совпадение ДР при регистрации, текущий отличается"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX, timestamp=1, user_ip=TEST_IP),
                event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT_2, timestamp=1),
                event_item(name=EVENT_INFO_BIRTHDAY, value=TEST_DEFAULT_BIRTHDAY, user_ip=TEST_IP, timestamp=1),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2001-01-01', user_ip=TEST_IP, timestamp=2),
                event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT_2, timestamp=2),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            birthday='2001-01-01',
        )
        form_values = self.form_values()
        headers = self.get_headers(ip=TEST_IP_2)
        with self.create_base_bundle_view(userinfo_response, form_values, headers=headers) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_account=[
                    {
                        'value': TEST_DEFAULT_BIRTHDAY,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1, user_agent=TEST_USER_AGENT_2),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=2, user_agent=TEST_USER_AGENT_2),
                        },
                    },
                    {
                        'value': '2001-01-01',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2, user_agent=TEST_USER_AGENT_2),
                            'end': None,
                        },
                    },
                ],
                birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                birthday_current_index=1,
                birthday_registration_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                birthday_registration_index=0,
                birthday_factor_change_count=1,
                birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_ip_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_ua_eq_reg=[UA_FACTOR_FULL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_registration_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                    birthday_factor_change_count=1,
                    birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_ip_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_ua_eq_reg=[UA_FACTOR_FULL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )

    def test_match_current_birthday(self):
        """Совпадение только с текущим ДР"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_INFO_BIRTHDAY, value=TEST_DEFAULT_BIRTHDAY, user_ip=TEST_IP, timestamp=1),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2010-02-02', user_ip=TEST_IP, timestamp=2),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2001-01-01', user_ip=TEST_IP, timestamp=3),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            birthday='2001-01-01',
        )
        form_values = self.form_values(birthday='2001-01-01')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_entered='2001-01-01',
                birthday_account=[
                    {
                        'value': TEST_DEFAULT_BIRTHDAY,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                        },
                    },
                    {
                        'value': '2010-02-02',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                        },
                    },
                    {
                        'value': '2001-01-01',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                            'end': None,
                        },
                    },
                ],
                birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                birthday_current_index=2,
                birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                birthday_registration_index=0,
                birthday_intermediate_factor=FACTOR_BOOL_NO_MATCH,
                birthday_intermediate_index=1,
                birthday_factor_change_count=2,
                birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                    birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_intermediate_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_factor_change_count=2,
                    birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )

    def test_inexact_match_current_birthday(self):
        """Неточное совпадение только с текущим ДР"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_INFO_BIRTHDAY, value=TEST_DEFAULT_BIRTHDAY, user_ip=TEST_IP, timestamp=1),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2010-02-02', user_ip=TEST_IP, timestamp=2),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2001-01-01', user_ip=TEST_IP, timestamp=3),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            birthday='2001-01-01',
        )
        form_values = self.form_values(birthday='2002-01-01')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_entered='2002-01-01',
                birthday_account=[
                    {
                        'value': TEST_DEFAULT_BIRTHDAY,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                        },
                    },
                    {
                        'value': '2010-02-02',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                        },
                    },
                    {
                        'value': '2001-01-01',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                            'end': None,
                        },
                    },
                ],
                birthday_current_factor=BIRTHDAYS_FACTOR_INEXACT_MATCH,
                birthday_current_index=2,
                birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                birthday_registration_index=0,
                birthday_intermediate_factor=FACTOR_BOOL_NO_MATCH,
                birthday_intermediate_index=1,
                birthday_factor_change_count=2,
                birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=BIRTHDAYS_FACTOR_INEXACT_MATCH,
                    birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_intermediate_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_factor_change_count=2,
                    birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
                    birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
                    birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                    birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )

    def test_match_intermediate_birthday_best_match_no_registration_factor(self):
        """Лучшее совпадение с промежуточным ДР, ДР при регистрации не установлен"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_INFO_BIRTHDAY, value=TEST_DEFAULT_BIRTHDAY, user_ip=TEST_IP, timestamp=1),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2001-01-01', user_ip=TEST_IP, timestamp=2),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2010-02-02', user_ip=TEST_IP, timestamp=3),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2001-01-01', user_ip=TEST_IP, timestamp=4),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2010-02-02', user_ip=TEST_IP_2, timestamp=5),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2001-01-01', user_ip=TEST_IP, timestamp=6),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(0)),
            birthday='2001-01-01',
        )
        form_values = self.form_values(birthday='2010-02-02')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_entered='2010-02-02',
                birthday_account=[
                    {
                        'value': TEST_DEFAULT_BIRTHDAY,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                        },
                    },
                    {
                        'value': '2001-01-01',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                        },
                    },
                    {
                        'value': '2010-02-02',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                        },
                    },
                    {
                        'value': '2001-01-01',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=5),
                        },
                    },
                    {
                        'value': '2010-02-02',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=5),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                        },
                    },
                    {
                        'value': '2001-01-01',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                            'end': None,
                        },
                    },
                ],
                birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                birthday_current_index=5,
                birthday_registration_factor=FACTOR_NOT_SET,
                birthday_registration_index=None,
                birthday_intermediate_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                birthday_factor_intermediate_depth=FACTOR_FLOAT_MATCH,
                # берется индекс самого "старого" промежуточного совпадения
                birthday_intermediate_index=2,
                birthday_factor_change_count=5,
                birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_registration_factor=FACTOR_NOT_SET,
                    birthday_intermediate_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                    birthday_factor_intermediate_depth=FACTOR_FLOAT_MATCH,
                    birthday_factor_change_count=5,
                    birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
                    birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
                    birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
                    birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                    birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
                ),
                view.statbox,
            )

    def test_match_intermediate_with_current_birthday_deleted(self):
        """Совпадение с промежуточным ДР, последний ДР удален пользователем"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_INFO_BIRTHDAY, value=TEST_DEFAULT_BIRTHDAY, user_ip=TEST_IP, timestamp=1),
                event_item(name=EVENT_INFO_BIRTHDAY, value='2010-02-02', user_ip=TEST_IP, timestamp=2),
                event_item(name=EVENT_INFO_BIRTHDAY, value=None, user_ip=TEST_IP, timestamp=3),
            ]),
        )
        userinfo_response = self.default_userinfo_response(
            registration_datetime=datetime_to_string(unixtime_to_datetime(1)),
            birthday=None,
        )
        form_values = self.form_values(birthday='2010-02-02')

        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('birthday')

            expected_factors = birthday_factors(
                birthday_entered='2010-02-02',
                birthday_account=[
                    {
                        'value': TEST_DEFAULT_BIRTHDAY,
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                        },
                    },
                    {
                        'value': '2010-02-02',
                        'interval': {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                        },
                    },
                ],
                # текущего значения нет - фактор не вычислялся
                birthday_current_factor=FACTOR_NOT_SET,
                birthday_current_index=None,
                birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                birthday_registration_index=0,
                birthday_intermediate_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                birthday_intermediate_index=1,
                birthday_factor_intermediate_depth=FACTOR_FLOAT_MATCH,
                birthday_factor_change_count=1,
                birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                birthday_statbox_entry(
                    birthday_current_factor=FACTOR_NOT_SET,
                    birthday_registration_factor=FACTOR_BOOL_NO_MATCH,
                    birthday_intermediate_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                    birthday_factor_intermediate_depth=FACTOR_FLOAT_MATCH,
                    birthday_factor_change_count=1,
                    birthday_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                    birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET],
                ),
                view.statbox,
            )


@with_settings_hosts()
class NamesBirthdayCheckStatusTestCase(BaseCalculateFactorsMixinTestCase):

    def test_only_registration_names_match(self):
        factors = merge_dicts(
            names_factors(names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_INEXACT_MATCH]),
            birthday_factors(),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_only_intermediate_names_match(self):
        factors = merge_dicts(
            names_factors(names_intermediate_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_INEXACT_MATCH]),
            birthday_factors(),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_only_current_names_match(self):
        factors = merge_dicts(
            names_factors(names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_INEXACT_MATCH]),
            birthday_factors(),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_only_registration_birthday_match(self):
        factors = merge_dicts(
            names_factors(),
            birthday_factors(birthday_registration_factor=BIRTHDAYS_FACTOR_FULL_MATCH),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_only_intermediate_birthday_match(self):
        factors = merge_dicts(
            names_factors(),
            birthday_factors(birthday_intermediate_factor=BIRTHDAYS_FACTOR_FULL_MATCH),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_only_current_birthday_match(self):
        factors = merge_dicts(
            names_factors(),
            birthday_factors(birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_only_registration_birthday_inexact_match(self):
        factors = merge_dicts(
            names_factors(),
            birthday_factors(birthday_registration_factor=BIRTHDAYS_FACTOR_INEXACT_MATCH),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_only_intermediate_birthday_inexact_match(self):
        factors = merge_dicts(
            names_factors(),
            birthday_factors(birthday_intermediate_factor=BIRTHDAYS_FACTOR_INEXACT_MATCH),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_only_current_birthday_inexact_match(self):
        factors = merge_dicts(
            names_factors(),
            birthday_factors(birthday_current_factor=BIRTHDAYS_FACTOR_INEXACT_MATCH),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_all_factors_match(self):
        factors = merge_dicts(
            names_factors(
                names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_MATCH],
                names_intermediate_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_INEXACT_MATCH],
                names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_MATCH],
            ),
            birthday_factors(
                birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                birthday_intermediate_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
                birthday_registration_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
            ),
        )
        ok_(get_names_birthday_check_status(factors))

    def test_no_match_firstname_result_not_counts(self):
        """Нет совпадения; не учитываем успешное сравнение имени"""
        factors = merge_dicts(
            names_factors(
                names_current_factor=[STRING_FACTOR_MATCH, FACTOR_NOT_SET],
                names_registration_factor=[STRING_FACTOR_MATCH, FACTOR_NOT_SET],
            ),
            birthday_factors(
                birthday_current_factor=FACTOR_NOT_SET,
                birthday_registration_factor=FACTOR_NOT_SET,
            ),
        )
        ok_(not get_names_birthday_check_status(factors))
