# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_DEFAULT_AUTH_INFO,
    TEST_DEFAULT_BIRTHDAY,
    TEST_DEFAULT_COMPARE_REASONS,
    TEST_DEFAULT_ENTERED_REGISTRATION_DATE_WITH_TZ,
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_HINT_ANSWER,
    TEST_DEFAULT_HINT_QUESTION,
    TEST_DEFAULT_LASTNAME,
    TEST_DEFAULT_REGISTRATION_COUNTRY,
    TEST_DEFAULT_REGISTRATION_DATETIME,
    TEST_DEFAULT_REGISTRATION_TIMESTAMP,
    TEST_DEFAULT_STATBOX_ACCOUNT_FACTOR,
    TEST_DEFAULT_STATBOX_HISTORY_FACTOR,
    TEST_DEFAULT_UA,
    TEST_EMPTY_UA,
    TEST_IP,
    TEST_IP_AS_SUBNET,
    TEST_PASSWORD_AUTH_DATE_FACTOR,
    TEST_PASSWORD_AUTH_DATE_WITH_TZ,
    TEST_PASSWORD_AUTH_FOUND_FACTOR,
    TEST_PASSWORD_EQUALS_CURRENT_FACTOR,
    TEST_USER_AGENT_2_PARSED,
)
from passport.backend.api.views.bundle.restore.factors import (
    MAX_PASSWORD_FIELDS,
    PASSWORD_AND_PERSONAL_MAX_ANALYZED_CHANGES,
    PASSWORD_AND_RECOVERY_MAX_ANALYZED_CHANGES,
    PASSWORD_MATCH_DEPTH,
    PASSWORDS_ENTITY_NAME,
    PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES,
    PERSONAL_DATA_CHANGE_INDICES,
    RESTORE_METHODS_CHANGE_INDICES,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import events_info_interval_point
from passport.backend.core.compare import (
    BIRTHDAYS_FACTOR_FULL_MATCH,
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_MATCH,
    FACTOR_FLOAT_NO_MATCH,
    FACTOR_NOT_SET,
    STRING_FACTOR_MATCH,
)
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool


def names_factors(
    firstnames_entered=None,
    lastnames_entered=None,
    names_account=None,
    names_current_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
    names_intermediate_factor=[FACTOR_NOT_SET, FACTOR_NOT_SET],
    names_registration_factor=[STRING_FACTOR_MATCH, STRING_FACTOR_MATCH],
    names_factor_intermediate_depth=FACTOR_NOT_SET,
    names_factor_change_count=0,
    names_factor_change_depth=None,
    names_factor_change_ip_eq_user=None,
    names_factor_change_subnet_eq_user=None,
    names_factor_change_ua_eq_user=None,
    names_factor_change_ip_eq_reg=None,
    names_factor_change_subnet_eq_reg=None,
    names_factor_change_ua_eq_reg=None,
    names_current_index=[[0, 0], 0],
    names_registration_index=[[0, 0], 0],
    names_intermediate_indices=None,
    historydb_api_events_status=True,
    **kwargs
):
    not_set_values = [FACTOR_NOT_SET] * len(PERSONAL_DATA_CHANGE_INDICES)
    return {
        'names': {
            'entered': {
                'firstnames': firstnames_entered or [TEST_DEFAULT_FIRSTNAME],
                'lastnames': lastnames_entered or [TEST_DEFAULT_LASTNAME],
            },
            'account': names_account if names_account is not None else [
                {
                    'firstname': TEST_DEFAULT_FIRSTNAME,
                    'lastname': TEST_DEFAULT_LASTNAME,
                    'interval': {
                        'start': events_info_interval_point(
                            user_ip=TEST_IP,
                            timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP,
                        ),
                        'end': None,
                    },
                },
            ],
            'factor': {
                'current': names_current_factor,
                'intermediate': names_intermediate_factor,
                'intermediate_depth': names_factor_intermediate_depth,
                'registration': names_registration_factor,
                'change_count': names_factor_change_count,
                'change_depth': names_factor_change_depth or not_set_values,
                'change_ip_eq_user': names_factor_change_ip_eq_user or not_set_values,
                'change_subnet_eq_user': names_factor_change_subnet_eq_user or not_set_values,
                'change_ua_eq_user': names_factor_change_ua_eq_user or not_set_values,
                'change_ip_eq_reg': names_factor_change_ip_eq_reg or not_set_values,
                'change_subnet_eq_reg': names_factor_change_subnet_eq_reg or not_set_values,
                'change_ua_eq_reg': names_factor_change_ua_eq_reg or not_set_values,
            },
            'indices': {
                'current': names_current_index,
                'intermediate': names_intermediate_indices,
                'registration': names_registration_index,
            },
        },
        'historydb_api_events_status': historydb_api_events_status,
    }


def names_statbox_entry(
    names_current_factor=(STRING_FACTOR_MATCH, STRING_FACTOR_MATCH),
    names_intermediate_factor=(FACTOR_NOT_SET, FACTOR_NOT_SET),
    names_registration_factor=(STRING_FACTOR_MATCH, STRING_FACTOR_MATCH),
    names_factor_intermediate_depth=FACTOR_NOT_SET,
    names_factor_change_count=0,
    names_factor_change_depth=None,
    names_factor_change_ip_eq_user=None,
    names_factor_change_subnet_eq_user=None,
    names_factor_change_ua_eq_user=None,
    names_factor_change_ip_eq_reg=None,
    names_factor_change_subnet_eq_reg=None,
    names_factor_change_ua_eq_reg=None,
    historydb_api_events_status=True,
    **kwargs
):
    entry = {
        'historydb_status': tskv_bool(historydb_api_events_status),
        'names_factor_change_count': str(names_factor_change_count),
        'names_factor_intermediate_depth': str(names_factor_intermediate_depth),
    }
    for name, factor in zip(
            (
                'change_depth',
                'change_ip_eq_user',
                'change_subnet_eq_user',
                'change_ua_eq_user',
                'change_ip_eq_reg',
                'change_subnet_eq_reg',
                'change_ua_eq_reg',
            ),
            (
                names_factor_change_depth,
                names_factor_change_ip_eq_user,
                names_factor_change_subnet_eq_user,
                names_factor_change_ua_eq_user,
                names_factor_change_ip_eq_reg,
                names_factor_change_subnet_eq_reg,
                names_factor_change_ua_eq_reg,
            )
    ):
        factor = factor or [FACTOR_NOT_SET] * len(PERSONAL_DATA_CHANGE_INDICES)
        for index, value in enumerate(factor):
            entry['names_factor_%s_%s' % (name, index)] = str(value)
    for name, factor in zip(
            (
                'names_factor_current',
                'names_factor_intermediate',
                'names_factor_registration',
            ),
            (
                names_current_factor,
                names_intermediate_factor,
                names_registration_factor,
            ),
    ):
        factor = factor or [FACTOR_NOT_SET] * 2
        for index, value in enumerate(factor):
            entry['%s_%s' % (name, index)] = str(value)
    return entry


def simple_names_statbox_entry(
    names_history_status=True,
    names_account_status=True,
    names_history_found=True,
    names_history_factor=TEST_DEFAULT_STATBOX_HISTORY_FACTOR,
    names_history_reason=TEST_DEFAULT_COMPARE_REASONS,
    names_account_reason=TEST_DEFAULT_COMPARE_REASONS,
    names_account_factor=TEST_DEFAULT_STATBOX_ACCOUNT_FACTOR,
    historydb_api_events_status=True,
    **kwargs
):
    entry = {
        'names_account_status': tskv_bool(names_account_status),
        'names_account_reason': names_account_reason,
        'names_history_found': tskv_bool(names_history_found),
        'historydb_status': tskv_bool(historydb_api_events_status),
    }
    entry.update(names_account_factor)
    if historydb_api_events_status and names_history_found:
        entry.update(
            {
                'names_history_status': tskv_bool(names_history_status),
                'names_history_reason': names_history_reason,
            },
            **names_history_factor
        )
    return entry


def simple_birthday_statbox_entry(
    birthday_account_factor=FACTOR_BOOL_MATCH,
    birthday_history_factor=FACTOR_BOOL_MATCH,
    historydb_api_events_status=True,
    **kwargs
):
    entry = {
        'birthday_account_factor': str(birthday_account_factor),
        'birthday_history_factor': str(birthday_history_factor),
        'historydb_status': tskv_bool(historydb_api_events_status),
    }
    return entry


def birthday_factors(
    birthday_entered=TEST_DEFAULT_BIRTHDAY,
    birthday_account=None,
    birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
    birthday_intermediate_factor=FACTOR_NOT_SET,
    birthday_registration_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
    birthday_factor_intermediate_depth=FACTOR_NOT_SET,
    birthday_factor_change_count=0,
    birthday_factor_change_depth=None,
    birthday_factor_change_ip_eq_user=None,
    birthday_factor_change_subnet_eq_user=None,
    birthday_factor_change_ua_eq_user=None,
    birthday_factor_change_ip_eq_reg=None,
    birthday_factor_change_subnet_eq_reg=None,
    birthday_factor_change_ua_eq_reg=None,
    birthday_intermediate_index=None,
    birthday_current_index=0,
    birthday_registration_index=0,
    historydb_api_events_status=True,
    **kwargs
):
    not_set_values = [FACTOR_NOT_SET] * len(PERSONAL_DATA_CHANGE_INDICES)
    return {
        'birthday': {
            'entered': birthday_entered,
            'account': birthday_account if birthday_account is not None else [
                {
                    'value': TEST_DEFAULT_BIRTHDAY,
                    'interval': {
                        'start': events_info_interval_point(
                            user_ip=TEST_IP,
                            timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP,
                        ),
                        'end': None,
                    },
                },
            ],
            'factor': {
                'current': birthday_current_factor,
                'intermediate': birthday_intermediate_factor,
                'registration': birthday_registration_factor,
                'intermediate_depth': birthday_factor_intermediate_depth,
                'change_count': birthday_factor_change_count,
                'change_depth': birthday_factor_change_depth or not_set_values,
                'change_ip_eq_user': birthday_factor_change_ip_eq_user or not_set_values,
                'change_subnet_eq_user': birthday_factor_change_subnet_eq_user or not_set_values,
                'change_ua_eq_user': birthday_factor_change_ua_eq_user or not_set_values,
                'change_ip_eq_reg': birthday_factor_change_ip_eq_reg or not_set_values,
                'change_subnet_eq_reg': birthday_factor_change_subnet_eq_reg or not_set_values,
                'change_ua_eq_reg': birthday_factor_change_ua_eq_reg or not_set_values,
            },
            'indices': {
                'current': birthday_current_index,
                'intermediate': birthday_intermediate_index,
                'registration': birthday_registration_index,
            },
        },
        'historydb_api_events_status': historydb_api_events_status,
    }


def birthday_statbox_entry(
    birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
    birthday_intermediate_factor=FACTOR_NOT_SET,
    birthday_registration_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
    birthday_factor_intermediate_depth=FACTOR_NOT_SET,
    historydb_api_events_status=True,
    birthday_factor_change_count=0,
    birthday_factor_change_depth=None,
    birthday_factor_change_ip_eq_user=None,
    birthday_factor_change_subnet_eq_user=None,
    birthday_factor_change_ua_eq_user=None,
    birthday_factor_change_ip_eq_reg=None,
    birthday_factor_change_subnet_eq_reg=None,
    birthday_factor_change_ua_eq_reg=None,
    **kwargs
):
    entry = {
        'historydb_status': tskv_bool(historydb_api_events_status),
        'birthday_factor_current': str(birthday_current_factor),
        'birthday_factor_intermediate': str(birthday_intermediate_factor),
        'birthday_factor_registration': str(birthday_registration_factor),
        'birthday_factor_change_count': str(birthday_factor_change_count),
        'birthday_factor_intermediate_depth': str(birthday_factor_intermediate_depth),
    }
    for name, factor in zip(
            (
                'change_depth',
                'change_ip_eq_user',
                'change_subnet_eq_user',
                'change_ua_eq_user',
                'change_ip_eq_reg',
                'change_subnet_eq_reg',
                'change_ua_eq_reg',
            ),
            (
                birthday_factor_change_depth,
                birthday_factor_change_ip_eq_user,
                birthday_factor_change_subnet_eq_user,
                birthday_factor_change_ua_eq_user,
                birthday_factor_change_ip_eq_reg,
                birthday_factor_change_subnet_eq_reg,
                birthday_factor_change_ua_eq_reg,
            )
    ):
        factor = factor or [FACTOR_NOT_SET] * len(PERSONAL_DATA_CHANGE_INDICES)
        for index, value in enumerate(factor):
            entry['birthday_factor_%s_%s' % (name, index)] = str(value)
    return entry


def user_env_auths_factors(
    user_ip=TEST_IP,
    user_subnet=TEST_IP_AS_SUBNET,
    user_agent=TEST_DEFAULT_UA,
    ip_first_auth=TEST_DEFAULT_AUTH_INFO,
    subnet_first_auth=TEST_DEFAULT_AUTH_INFO,
    ua_first_auth=None,
    ip_last_auth=TEST_DEFAULT_AUTH_INFO,
    subnet_last_auth=TEST_DEFAULT_AUTH_INFO,
    ua_last_auth=None,
    reg_ip=None,
    reg_subnet=None,
    reg_user_agent=TEST_EMPTY_UA,
    factor_ip_first_auth_depth=FACTOR_FLOAT_MATCH,
    factor_subnet_first_auth_depth=FACTOR_FLOAT_MATCH,
    factor_ua_first_auth_depth=FACTOR_NOT_SET,
    factor_ip_auth_interval=FACTOR_FLOAT_NO_MATCH,
    factor_subnet_auth_interval=FACTOR_FLOAT_NO_MATCH,
    factor_ua_auth_interval=FACTOR_NOT_SET,
    factor_ip_eq_reg=FACTOR_NOT_SET,
    factor_subnet_eq_reg=FACTOR_NOT_SET,
    factor_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
    factor_auths_limit_reached=FACTOR_BOOL_NO_MATCH,
    gathered_auths_count=11,
    auths_aggregated_runtime_api_status=True,
    historydb_api_events_status=True,
    **kwargs
):
    return {
        'user_env_auths': {
            'actual': {
                'ip': user_ip,
                'subnet': user_subnet,
                'ua': user_agent,
                'ip_first_auth': ip_first_auth,
                'subnet_first_auth': subnet_first_auth,
                'ua_first_auth': ua_first_auth,
                'ip_last_auth': ip_last_auth,
                'subnet_last_auth': subnet_last_auth,
                'ua_last_auth': ua_last_auth,
                'gathered_auths_count': gathered_auths_count,
            },
            'registration': {
                'ip': reg_ip,
                'subnet': reg_subnet,
                'ua': reg_user_agent,
            },
            'factor': {
                'ip_first_auth_depth': factor_ip_first_auth_depth,
                'subnet_first_auth_depth': factor_subnet_first_auth_depth,
                'ua_first_auth_depth': factor_ua_first_auth_depth,
                'ip_auth_interval': factor_ip_auth_interval,
                'subnet_auth_interval': factor_subnet_auth_interval,
                'ua_auth_interval': factor_ua_auth_interval,
                'ip_eq_reg': factor_ip_eq_reg,
                'subnet_eq_reg': factor_subnet_eq_reg,
                'ua_eq_reg': factor_ua_eq_reg,
                'auths_limit_reached': factor_auths_limit_reached,
            },
        },
        'auths_aggregated_runtime_api_status': auths_aggregated_runtime_api_status,
        'historydb_api_events_status': historydb_api_events_status,
    }


def user_env_auths_statbox_entry(
    historydb_api_events_status=True,
    auths_aggregated_runtime_api_status=True,
    factor_ip_first_auth_depth=FACTOR_FLOAT_MATCH,
    factor_subnet_first_auth_depth=FACTOR_FLOAT_MATCH,
    factor_ua_first_auth_depth=FACTOR_NOT_SET,
    factor_ip_auth_interval=FACTOR_FLOAT_NO_MATCH,
    factor_subnet_auth_interval=FACTOR_FLOAT_NO_MATCH,
    factor_ua_auth_interval=FACTOR_NOT_SET,
    factor_ip_eq_reg=FACTOR_NOT_SET,
    factor_subnet_eq_reg=FACTOR_NOT_SET,
    factor_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
    factor_auths_limit_reached=FACTOR_BOOL_NO_MATCH,
    **kwargs
):
    entry = {
        'auths_aggregated_runtime_api_status': tskv_bool(auths_aggregated_runtime_api_status),
        'user_env_auths_factor_ip_first_auth_depth': str(factor_ip_first_auth_depth),
        'user_env_auths_factor_subnet_first_auth_depth': str(factor_subnet_first_auth_depth),
        'user_env_auths_factor_ua_first_auth_depth': str(factor_ua_first_auth_depth),
        'user_env_auths_factor_ip_auth_interval': str(factor_ip_auth_interval),
        'user_env_auths_factor_subnet_auth_interval': str(factor_subnet_auth_interval),
        'user_env_auths_factor_ua_auth_interval': str(factor_ua_auth_interval),
        'user_env_auths_factor_ip_eq_reg': str(factor_ip_eq_reg),
        'user_env_auths_factor_subnet_eq_reg': str(factor_subnet_eq_reg),
        'user_env_auths_factor_ua_eq_reg': str(factor_ua_eq_reg),
        'user_env_auths_factor_auths_limit_reached': str(factor_auths_limit_reached),
    }
    if historydb_api_events_status is not None:
        entry['historydb_status'] = tskv_bool(historydb_api_events_status)
    return entry


def phone_numbers_factors(
    historydb_api_events_status=True,
    phone_numbers_entered=None,
    phone_numbers_history=None,
    phone_numbers_matches=None,
    phone_numbers_match_indices=None,
    phone_numbers_factor_history_count=0,
    phone_numbers_factor_entered_count=0,
    phone_numbers_factor_matches_count=0,
    phone_numbers_factor_change_count=0,
    phone_numbers_factor_change_depth=None,
    phone_numbers_factor_change_ip_eq_user=None,
    phone_numbers_factor_change_ua_eq_user=None,
    phone_numbers_factor_change_subnet_eq_user=None,
    phone_numbers_factor_match_depth=None,
    phone_numbers_factor_match_ip_eq_user=None,
    phone_numbers_factor_match_ua_eq_user=None,
    phone_numbers_factor_match_subnet_eq_user=None,
    phone_numbers_factor_match_ip_eq_reg=None,
    phone_numbers_factor_match_ua_eq_reg=None,
    phone_numbers_factor_match_subnet_eq_reg=None,
    **kwargs
):
    not_set_values = [FACTOR_NOT_SET] * len(RESTORE_METHODS_CHANGE_INDICES)
    match_not_set_values = [FACTOR_NOT_SET] * 2
    return {
        'historydb_api_events_status': historydb_api_events_status,
        'phone_numbers': {
            'entered': phone_numbers_entered or [],
            'history': phone_numbers_history or [],
            'matches': phone_numbers_matches or [],
            'match_indices': phone_numbers_match_indices or [],
            'factor': {
                'entered_count': phone_numbers_factor_entered_count,
                'history_count': phone_numbers_factor_history_count,
                'matches_count': phone_numbers_factor_matches_count,
                'change_count': phone_numbers_factor_change_count,
                'change_depth': phone_numbers_factor_change_depth or not_set_values,
                'change_ip_eq_user': phone_numbers_factor_change_ip_eq_user or not_set_values,
                'change_subnet_eq_user': phone_numbers_factor_change_subnet_eq_user or not_set_values,
                'change_ua_eq_user': phone_numbers_factor_change_ua_eq_user or not_set_values,
                'match_depth': phone_numbers_factor_match_depth or match_not_set_values,
                'match_ip_eq_user': phone_numbers_factor_match_ip_eq_user or match_not_set_values,
                'match_subnet_eq_user': phone_numbers_factor_match_subnet_eq_user or match_not_set_values,
                'match_ua_eq_user': phone_numbers_factor_match_ua_eq_user or match_not_set_values,
                'match_ip_eq_reg': phone_numbers_factor_match_ip_eq_reg or match_not_set_values,
                'match_subnet_eq_reg': phone_numbers_factor_match_subnet_eq_reg or match_not_set_values,
                'match_ua_eq_reg': phone_numbers_factor_match_ua_eq_reg or match_not_set_values,
            },
        },
    }


def phone_numbers_factors_aggregated_update(
    original_factors,
    phone_numbers_factor_match_ip_first_auth_depth=None,
    phone_numbers_factor_match_subnet_first_auth_depth=None,
    phone_numbers_factor_match_ua_first_auth_depth=None,
    phone_numbers_match_ip_first_auth=None,
    phone_numbers_match_subnet_first_auth=None,
    phone_numbers_match_ua_first_auth=None,
    **kwargs
):
    none_values = [None] * 2
    match_not_set_values = [FACTOR_NOT_SET] * 2
    updated_fields = {
        'actual': {
            'match_ip_first_auth': phone_numbers_match_ip_first_auth or none_values,
            'match_subnet_first_auth': phone_numbers_match_subnet_first_auth or none_values,
            'match_ua_first_auth': phone_numbers_match_ua_first_auth or none_values,
        },
        'factor': {
            'match_ip_first_auth_depth': phone_numbers_factor_match_ip_first_auth_depth or match_not_set_values,
            'match_subnet_first_auth_depth': phone_numbers_factor_match_subnet_first_auth_depth or match_not_set_values,
            'match_ua_first_auth_depth': phone_numbers_factor_match_ua_first_auth_depth or match_not_set_values,
        },
    }
    for field in updated_fields:
        original_factors['phone_numbers'].setdefault(field, {}).update(updated_fields[field])
    return original_factors


def phone_numbers_statbox_entry(
    historydb_api_events_status=True,
    phone_numbers_factor_history_count=0,
    phone_numbers_factor_entered_count=0,
    phone_numbers_factor_matches_count=0,
    phone_numbers_factor_change_count=0,
    **kwargs
):
    entry = {
        'historydb_status': tskv_bool(historydb_api_events_status),
        'phone_numbers_factor_history_count': str(phone_numbers_factor_history_count),
        'phone_numbers_factor_entered_count': str(phone_numbers_factor_entered_count),
        'phone_numbers_factor_matches_count': str(phone_numbers_factor_matches_count),
        'phone_numbers_factor_change_count': str(phone_numbers_factor_change_count),
    }
    for factor_name in (
            'phone_numbers_factor_change_depth',
            'phone_numbers_factor_change_ip_eq_user',
            'phone_numbers_factor_change_ua_eq_user',
            'phone_numbers_factor_change_subnet_eq_user',
    ):
        factor = kwargs.get(factor_name, [FACTOR_NOT_SET] * len(RESTORE_METHODS_CHANGE_INDICES))
        for index, value in enumerate(factor):
            entry['%s_%s' % (factor_name, index)] = str(value)
    for factor_name in (
            'phone_numbers_factor_match_depth',
            'phone_numbers_factor_match_ip_eq_user',
            'phone_numbers_factor_match_ua_eq_user',
            'phone_numbers_factor_match_subnet_eq_user',
            'phone_numbers_factor_match_ip_eq_reg',
            'phone_numbers_factor_match_ua_eq_reg',
            'phone_numbers_factor_match_subnet_eq_reg',
    ):
        factor = kwargs.get(factor_name, [FACTOR_NOT_SET] * 2)
        for index, value in enumerate(factor):
            entry['%s_%s' % (factor_name, index)] = str(value)
    return entry


def phone_numbers_statbox_entry_aggregated_update(**kwargs):
    entry = {}
    for factor_name in (
            'phone_numbers_factor_match_ip_first_auth_depth',
            'phone_numbers_factor_match_subnet_first_auth_depth',
            'phone_numbers_factor_match_ua_first_auth_depth',
    ):
        factor = kwargs.get(factor_name, [FACTOR_NOT_SET] * 2)
        for index, value in enumerate(factor):
            entry['%s_%s' % (factor_name, index)] = str(value)
    return entry


def passwords_factors(
    historydb_api_events_status=True,
    password_auth_date_entered=TEST_PASSWORD_AUTH_DATE_WITH_TZ,
    passwords_intervals=None,
    passwords_indices=None,
    passwords_api_statuses=None,
    passwords_last_change_request=None,
    passwords_last_change=None,
    passwords_factor_entered_count=1,
    passwords_factor_auth_found=None,
    passwords_factor_auth_date=None,
    passwords_factor_first_auth_depth=None,
    passwords_factor_equals_current=None,
    passwords_factor_forced_change_pending=FACTOR_BOOL_NO_MATCH,
    passwords_factor_change_depth=None,
    passwords_factor_change_ip_eq_user=None,
    passwords_factor_change_subnet_eq_user=None,
    passwords_factor_change_ua_eq_user=None,
    passwords_factor_last_change_is_forced_change=FACTOR_NOT_SET,
    passwords_factor_change_count=0,
    **kwargs
):
    return {
        'historydb_api_events_status': historydb_api_events_status,
        'passwords': {
            'actual': {
                'last_change_request': passwords_last_change_request,
                'last_change': passwords_last_change,
            },
            'auth_date_entered': password_auth_date_entered,
            'intervals': passwords_intervals or [[]],
            'api_statuses': passwords_api_statuses or [True],
            'indices': passwords_indices or [None],
            'factor': {
                'entered_count': passwords_factor_entered_count,
                'auth_found': passwords_factor_auth_found or TEST_PASSWORD_AUTH_FOUND_FACTOR,
                'auth_date': passwords_factor_auth_date or TEST_PASSWORD_AUTH_DATE_FACTOR,
                'first_auth_depth': passwords_factor_first_auth_depth or [FACTOR_NOT_SET] * MAX_PASSWORD_FIELDS,
                'equals_current': passwords_factor_equals_current or TEST_PASSWORD_EQUALS_CURRENT_FACTOR,
                'forced_change_pending': passwords_factor_forced_change_pending,
                'change_depth': passwords_factor_change_depth or [FACTOR_NOT_SET],
                'change_ip_eq_user': passwords_factor_change_ip_eq_user or [FACTOR_NOT_SET],
                'change_subnet_eq_user': passwords_factor_change_subnet_eq_user or [FACTOR_NOT_SET],
                'change_ua_eq_user': passwords_factor_change_ua_eq_user or [FACTOR_NOT_SET],
                'last_change_is_forced_change': passwords_factor_last_change_is_forced_change,
                'change_count': passwords_factor_change_count,
            },
        },
    }


def passwords_factors_aggregated_update(
    original_factors,
    passwords_factor_change_ip_first_auth_depth=None,
    passwords_factor_change_subnet_first_auth_depth=None,
    passwords_factor_change_ua_first_auth_depth=None,
    passwords_change_ip_first_auth=None,
    passwords_change_subnet_first_auth=None,
    passwords_change_ua_first_auth=None,
    **kwargs
):
    updated_fields = {
        'actual': {
            'change_ip_first_auth': passwords_change_ip_first_auth or [None],
            'change_subnet_first_auth': passwords_change_subnet_first_auth or [None],
            'change_ua_first_auth': passwords_change_ua_first_auth or [None],
        },
        'factor': {
            'change_ip_first_auth_depth': passwords_factor_change_ip_first_auth_depth or [FACTOR_NOT_SET],
            'change_subnet_first_auth_depth': passwords_factor_change_subnet_first_auth_depth or [FACTOR_NOT_SET],
            'change_ua_first_auth_depth': passwords_factor_change_ua_first_auth_depth or [FACTOR_NOT_SET],
        },
    }
    for field in updated_fields:
        original_factors['passwords'][field].update(updated_fields[field])
    return original_factors


def passwords_statbox_entry(
    historydb_api_events_status=True,
    passwords_factor_entered_count=1,
    passwords_factor_forced_change_pending=FACTOR_BOOL_NO_MATCH,
    passwords_factor_last_change_is_forced_change=FACTOR_NOT_SET,
    passwords_factor_change_count=0,
    passwords_api_status=True,
    **kwargs
):
    entry = {
        'historydb_status': tskv_bool(historydb_api_events_status),
        'passwords_factor_entered_count': str(passwords_factor_entered_count),
        'passwords_api_status': tskv_bool(passwords_api_status),
        'passwords_factor_forced_change_pending': str(passwords_factor_forced_change_pending),
        'passwords_factor_last_change_is_forced_change': str(passwords_factor_last_change_is_forced_change),
        'passwords_factor_change_count': str(passwords_factor_change_count),
    }
    for factor_name, length in zip(
            (
                'passwords_factor_auth_found',
                'passwords_factor_auth_date',
                'passwords_factor_first_auth_depth',
                'passwords_factor_equals_current',
                'passwords_factor_change_depth',
                'passwords_factor_change_ip_eq_user',
                'passwords_factor_change_subnet_eq_user',
                'passwords_factor_change_ua_eq_user',
            ),
            (
                MAX_PASSWORD_FIELDS,
                MAX_PASSWORD_FIELDS,
                MAX_PASSWORD_FIELDS,
                MAX_PASSWORD_FIELDS,
                1,
                1,
                1,
                1,
            ),
    ):
        factor = kwargs.get(factor_name, [FACTOR_NOT_SET] * length)
        if factor_name in ('passwords_factor_auth_found', 'passwords_factor_equals_current'):
            factor = kwargs.get(factor_name, [FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_NOT_SET])
        for index, value in enumerate(factor):
            entry['%s_%s' % (factor_name, index)] = str(value)
    return entry


def passwords_statbox_entry_aggregated_update(**kwargs):
    entry = {}
    for factor_name in (
            'passwords_factor_change_ip_first_auth_depth',
            'passwords_factor_change_subnet_first_auth_depth',
            'passwords_factor_change_ua_first_auth_depth',
    ):
        factor = kwargs.get(factor_name, [FACTOR_NOT_SET])
        for index, value in enumerate(factor):
            entry['%s_%s' % (factor_name, index)] = str(value)
    return entry


def password_matches_factors(
    historydb_api_events_status=True,
    password_matches_factor=None,
    **kwargs
):
    return {
        'historydb_api_events_status': historydb_api_events_status,
        'password_matches': {
            'factor': password_matches_factor or [FACTOR_NOT_SET] * PASSWORD_MATCH_DEPTH,
        },
    }


def password_matches_statbox_entry(
    historydb_api_events_status=True,
    password_matches_factor=None,
    **kwargs
):
    entry = {
        'historydb_status': tskv_bool(historydb_api_events_status),
    }
    factor = password_matches_factor or [FACTOR_NOT_SET] * PASSWORD_MATCH_DEPTH
    for index, value in enumerate(factor):
        entry['password_matches_factor_%s' % index] = str(value)
    return entry


def answer_factors(
    answer_entered=TEST_DEFAULT_HINT_ANSWER,
    answer_history=None,
    answer_index_best=None,
    answer_factor_best=FACTOR_NOT_SET,
    answer_factor_current=FACTOR_NOT_SET,
    answer_factor_change_count=0,
    answer_factor_change_depth=None,
    answer_factor_change_ip_eq_user=None,
    answer_factor_change_subnet_eq_user=None,
    answer_factor_change_ua_eq_user=None,
    answer_question=TEST_DEFAULT_HINT_QUESTION,
    answer_factor_match_depth=None,
    answer_factor_match_ip_eq_user=None,
    answer_factor_match_ua_eq_user=None,
    answer_factor_match_subnet_eq_user=None,
    answer_factor_match_ip_eq_reg=None,
    answer_factor_match_ua_eq_reg=None,
    answer_factor_match_subnet_eq_reg=None,
    historydb_api_events_status=True,
    **kwargs
):
    not_set_values = [FACTOR_NOT_SET] * len(RESTORE_METHODS_CHANGE_INDICES)
    match_not_set_values = [FACTOR_NOT_SET] * 2
    return {
        'answer': {
            'entered': {
                'question': answer_question,
                'answer': answer_entered,
            },
            'history': answer_history or [],
            'indices': {
                'best': answer_index_best,
            },
            'factor': {
                'best': answer_factor_best,
                'current': answer_factor_current,
                'change_count': answer_factor_change_count,
                'change_depth': answer_factor_change_depth or not_set_values,
                'change_ip_eq_user': answer_factor_change_ip_eq_user or not_set_values,
                'change_subnet_eq_user': answer_factor_change_subnet_eq_user or not_set_values,
                'change_ua_eq_user': answer_factor_change_ua_eq_user or not_set_values,
                'match_depth': answer_factor_match_depth or match_not_set_values,
                'match_ip_eq_user': answer_factor_match_ip_eq_user or match_not_set_values,
                'match_subnet_eq_user': answer_factor_match_subnet_eq_user or match_not_set_values,
                'match_ua_eq_user': answer_factor_match_ua_eq_user or match_not_set_values,
                'match_ip_eq_reg': answer_factor_match_ip_eq_reg or match_not_set_values,
                'match_subnet_eq_reg': answer_factor_match_subnet_eq_reg or match_not_set_values,
                'match_ua_eq_reg': answer_factor_match_ua_eq_reg or match_not_set_values,
            },
        },
        'historydb_api_events_status': historydb_api_events_status,
    }


def answer_factors_aggregated_update(
    original_factors,
    answer_factor_match_ip_first_auth_depth=None,
    answer_factor_match_subnet_first_auth_depth=None,
    answer_factor_match_ua_first_auth_depth=None,
    answer_match_ip_first_auth=None,
    answer_match_subnet_first_auth=None,
    answer_match_ua_first_auth=None,
    **kwargs
):
    match_not_set_values = [FACTOR_NOT_SET] * 2
    none_values = [None] * 2
    updated_fields = {
        'actual': {
            'match_ip_first_auth': answer_match_ip_first_auth or none_values,
            'match_subnet_first_auth': answer_match_subnet_first_auth or none_values,
            'match_ua_first_auth': answer_match_ua_first_auth or none_values,
        },
        'factor': {
            'match_ip_first_auth_depth': answer_factor_match_ip_first_auth_depth or match_not_set_values,
            'match_subnet_first_auth_depth': answer_factor_match_subnet_first_auth_depth or match_not_set_values,
            'match_ua_first_auth_depth': answer_factor_match_ua_first_auth_depth or match_not_set_values,
        },
    }
    for field in updated_fields:
        original_factors['answer'].setdefault(field, {}).update(updated_fields[field])
    return original_factors


def answer_statbox_entry(
    historydb_api_events_status=True,
    answer_factor_best=FACTOR_NOT_SET,
    answer_factor_current=FACTOR_NOT_SET,
    answer_factor_change_count=0,
    **kwargs
):
    entry = {
        'historydb_status': tskv_bool(historydb_api_events_status),
        'answer_factor_best': str(answer_factor_best),
        'answer_factor_current': str(answer_factor_current),
        'answer_factor_change_count': str(answer_factor_change_count),
    }
    for factor_name in (
            'answer_factor_change_depth',
            'answer_factor_change_ip_eq_user',
            'answer_factor_change_ua_eq_user',
            'answer_factor_change_subnet_eq_user',
    ):
        factor = kwargs.get(factor_name, [FACTOR_NOT_SET] * len(RESTORE_METHODS_CHANGE_INDICES))
        for index, value in enumerate(factor):
            entry['%s_%s' % (factor_name, index)] = str(value)
    for factor_name in (
            'answer_factor_match_depth',
            'answer_factor_match_ip_eq_user',
            'answer_factor_match_ua_eq_user',
            'answer_factor_match_subnet_eq_user',
            'answer_factor_match_ip_eq_reg',
            'answer_factor_match_ua_eq_reg',
            'answer_factor_match_subnet_eq_reg',
    ):
        factor = kwargs.get(factor_name, [FACTOR_NOT_SET] * 2)
        for index, value in enumerate(factor):
            entry['%s_%s' % (factor_name, index)] = str(value)
    return entry


def answer_statbox_entry_aggregated_update(**kwargs):
    entry = {}
    for factor_name in (
            'answer_factor_match_ip_first_auth_depth',
            'answer_factor_match_subnet_first_auth_depth',
            'answer_factor_match_ua_first_auth_depth',
    ):
        factor = kwargs.get(factor_name, [FACTOR_NOT_SET] * 2)
        for index, value in enumerate(factor):
            entry['%s_%s' % (factor_name, index)] = str(value)
    return entry


def delivery_addresses_factors(
    delivery_addresses_entered=None,
    delivery_addresses_account=None,
    delivery_addresses_matches=None,
    delivery_addresses_factor_entered_count=0,
    delivery_addresses_factor_account_count=0,
    delivery_addresses_factor_matches_count=0,
    delivery_addresses_factor_absence=0,
    **kwargs
):
    return {
        'delivery_addresses': {
            'entered': delivery_addresses_entered,
            'account': delivery_addresses_account or [],
            'matches': delivery_addresses_matches or [],
            'factor': {
                'entered_count': delivery_addresses_factor_entered_count,
                'account_count': delivery_addresses_factor_account_count,
                'matches_count': delivery_addresses_factor_matches_count,
            },
        },
    }


def delivery_addresses_statbox_entry(
    delivery_addresses_factor_entered_count=0,
    delivery_addresses_factor_account_count=0,
    delivery_addresses_factor_matches_count=0,
    **kwargs
):
    return {
        'delivery_addresses_factor_entered_count': str(delivery_addresses_factor_entered_count),
        'delivery_addresses_factor_account_count': str(delivery_addresses_factor_account_count),
        'delivery_addresses_factor_matches_count': str(delivery_addresses_factor_matches_count),
    }


def confirmed_emails_factors(
    historydb_api_events_status=True,
    emails_entered=None,
    emails_history=None,
    emails_matches=None,
    emails_match_indices=None,
    emails_factor_entered_count=0,
    emails_factor_history_count=0,
    emails_factor_matches_count=0,
    **kwargs
):
    return {
        'historydb_api_events_status': historydb_api_events_status,
        'emails': {
            'entered': emails_entered or [],
            'history': emails_history or [],
            'matches': emails_matches or [],
            'match_indices': emails_match_indices or [],
            'factor': {
                'entered_count': emails_factor_entered_count,
                'history_count': emails_factor_history_count,
                'matches_count': emails_factor_matches_count,
            },
        },
    }


def confirmed_emails_statbox_entry(
    historydb_api_events_status=True,
    emails_factor_entered_count=0,
    emails_factor_history_count=0,
    emails_factor_matches_count=0,
    **kwargs
):
    return {
        'historydb_status': tskv_bool(historydb_api_events_status),
        'emails_factor_entered_count': str(emails_factor_entered_count),
        'emails_factor_history_count': str(emails_factor_history_count),
        'emails_factor_matches_count': str(emails_factor_matches_count),
    }


def email_folders_factors(
    email_folders_entered=None,
    email_folders_actual=None,
    email_folders_matches=None,
    email_folders_api_status=True,
    email_folders_factor_entered_count=0,
    email_folders_factor_actual_count=0,
    email_folders_factor_matches_count=0,
    **kwargs
):
    return {
        'email_folders': {
            'entered': email_folders_entered,
            'actual': email_folders_actual or [],
            'matches': email_folders_matches or [],
            'api_status': email_folders_api_status,
            'factor': {
                'entered_count': email_folders_factor_entered_count,
                'actual_count': email_folders_factor_actual_count,
                'matches_count': email_folders_factor_matches_count,
            },
        },
    }


def email_folders_statbox_entry(
    email_folders_api_status=1,
    email_folders_factor_entered_count=0,
    email_folders_factor_actual_count=0,
    email_folders_factor_matches_count=0,
    **kwargs
):
    return {
        'email_folders_api_status': tskv_bool(email_folders_api_status),
        'email_folders_factor_entered_count': str(email_folders_factor_entered_count),
        'email_folders_factor_actual_count': str(email_folders_factor_actual_count),
        'email_folders_factor_matches_count': str(email_folders_factor_matches_count),
    }


def email_blackwhite_factors(
    email_blacklist_entered=None,
    email_blacklist_actual=None,
    email_blacklist_matches=None,
    email_blacklist_api_status=1,
    email_blacklist_factor_entered_count=0,
    email_blacklist_factor_actual_count=0,
    email_blacklist_factor_matches_count=0,
    email_whitelist_entered=None,
    email_whitelist_actual=None,
    email_whitelist_matches=None,
    email_whitelist_api_status=1,
    email_whitelist_factor_entered_count=0,
    email_whitelist_factor_actual_count=0,
    email_whitelist_factor_matches_count=0,
    **kwargs
):
    return {
        'email_blacklist': {
            'entered': email_blacklist_entered,
            'actual': email_blacklist_actual or [],
            'matches': email_blacklist_matches or [],
            'api_status': email_blacklist_api_status,
            'factor': {
                'entered_count': email_blacklist_factor_entered_count,
                'actual_count': email_blacklist_factor_actual_count,
                'matches_count': email_blacklist_factor_matches_count,
            },
        },
        'email_whitelist': {
            'entered': email_whitelist_entered,
            'actual': email_whitelist_actual or [],
            'matches': email_whitelist_matches or [],
            'api_status': email_whitelist_api_status,
            'factor': {
                'entered_count': email_whitelist_factor_entered_count,
                'actual_count': email_whitelist_factor_actual_count,
                'matches_count': email_whitelist_factor_matches_count,
            },
        },
    }


def email_blackwhite_statbox_entry(
    email_blacklist_api_status=1,
    email_blacklist_factor_entered_count=0,
    email_blacklist_factor_actual_count=0,
    email_blacklist_factor_matches_count=0,
    email_whitelist_api_status=1,
    email_whitelist_factor_entered_count=0,
    email_whitelist_factor_actual_count=0,
    email_whitelist_factor_matches_count=0,
    **kwargs
):
    return {
        'email_blacklist_api_status': tskv_bool(email_blacklist_api_status),
        'email_blacklist_factor_entered_count': str(email_blacklist_factor_entered_count),
        'email_blacklist_factor_actual_count': str(email_blacklist_factor_actual_count),
        'email_blacklist_factor_matches_count': str(email_blacklist_factor_matches_count),
        'email_whitelist_api_status': tskv_bool(email_whitelist_api_status),
        'email_whitelist_factor_entered_count': str(email_whitelist_factor_entered_count),
        'email_whitelist_factor_actual_count': str(email_whitelist_factor_actual_count),
        'email_whitelist_factor_matches_count': str(email_whitelist_factor_matches_count),
    }


def email_collectors_factors(
    email_collectors_entered=None,
    email_collectors_actual=None,
    email_collectors_matches=None,
    email_collectors_api_status=1,
    email_collectors_factor_entered_count=0,
    email_collectors_factor_actual_count=0,
    email_collectors_factor_matches_count=0,
    **kwargs
):
    return {
        'email_collectors': {
            'entered': email_collectors_entered,
            'actual': email_collectors_actual or [],
            'matches': email_collectors_matches or [],
            'api_status': email_collectors_api_status,
            'factor': {
                'entered_count': email_collectors_factor_entered_count,
                'actual_count': email_collectors_factor_actual_count,
                'matches_count': email_collectors_factor_matches_count,
            },
        },
    }


def email_collectors_statbox_entry(
    email_collectors_api_status=1,
    email_collectors_factor_entered_count=0,
    email_collectors_factor_actual_count=0,
    email_collectors_factor_matches_count=0,
    **kwargs
):
    return {
        'email_collectors_api_status': tskv_bool(email_collectors_api_status),
        'email_collectors_factor_entered_count': str(email_collectors_factor_entered_count),
        'email_collectors_factor_actual_count': str(email_collectors_factor_actual_count),
        'email_collectors_factor_matches_count': str(email_collectors_factor_matches_count),
    }


def outbound_emails_factors(
    outbound_emails_entered=None,
    outbound_emails_actual=None,
    outbound_emails_matches=None,
    outbound_emails_api_status=1,
    outbound_emails_factor_entered_count=0,
    outbound_emails_factor_actual_count=0,
    outbound_emails_factor_matches_count=0,
    **kwargs
):
    return {
        'outbound_emails': {
            'entered': outbound_emails_entered,
            'actual': outbound_emails_actual or [],
            'matches': outbound_emails_matches or [],
            'api_status': outbound_emails_api_status,
            'factor': {
                'entered_count': outbound_emails_factor_entered_count,
                'actual_count': outbound_emails_factor_actual_count,
                'matches_count': outbound_emails_factor_matches_count,
            },
        },
    }


def outbound_emails_statbox_entry(
    outbound_emails_api_status=1,
    outbound_emails_factor_entered_count=0,
    outbound_emails_factor_actual_count=0,
    outbound_emails_factor_matches_count=0,
    **kwargs
):
    return {
        'outbound_emails_api_status': tskv_bool(outbound_emails_api_status),
        'outbound_emails_factor_entered_count': str(outbound_emails_factor_entered_count),
        'outbound_emails_factor_actual_count': str(outbound_emails_factor_actual_count),
        'outbound_emails_factor_matches_count': str(outbound_emails_factor_matches_count),
    }


def restore_attempts_factors(
    restore_attempts=None,
    has_recent_positive_decision=False,
    historydb_api_events_status=True,
    **kwargs
):
    return {
        'restore_attempts': {
            'attempts': restore_attempts or [],
            'factor': {
                'has_recent_positive_decision': has_recent_positive_decision,
            },
        },
        'historydb_api_events_status': historydb_api_events_status,
    }


def restore_attempts_statbox_entry(
    has_recent_positive_decision=False,
    historydb_api_events_status=True,
    **kwargs
):
    entry = {
        'restore_attempts_has_recent_positive_decision': tskv_bool(has_recent_positive_decision),
    }
    if historydb_api_events_status is not None:
        entry['historydb_status'] = tskv_bool(historydb_api_events_status)
    return entry


def services_factors(
    services_entered=None,
    services_account=None,
    services_matches=None,
    services_factor_entered_count=0,
    services_factor_account_count=0,
    services_factor_matches_count=0,
    **kwargs
):
    return {
        'services': {
            'entered': services_entered or [],
            'account': services_account or [],
            'matches': services_matches or [],
            'factor': {
                'entered_count': services_factor_entered_count,
                'account_count': services_factor_account_count,
                'matches_count': services_factor_matches_count,
            },
        },
    }


def services_statbox_entry(
    services_factor_entered_count=0,
    services_factor_account_count=0,
    services_factor_matches_count=0,
    **kwargs
):
    return {
        'services_factor_entered_count': str(services_factor_entered_count),
        'services_factor_account_count': str(services_factor_account_count),
        'services_factor_matches_count': str(services_factor_matches_count),
    }


def registration_date_factors(
    registration_date_entered=TEST_DEFAULT_ENTERED_REGISTRATION_DATE_WITH_TZ,
    registration_date_account=TEST_DEFAULT_REGISTRATION_DATETIME,
    registration_date_factor=FACTOR_FLOAT_MATCH,
    **kwargs
):
    return {
        'registration_date': {
            'entered': registration_date_entered,
            'account': registration_date_account,
            'factor': registration_date_factor,
        },
    }


def registration_date_factors_statbox_entry(
    registration_date_factor=FACTOR_FLOAT_MATCH,
    **kwargs
):
    return {
        'registration_date_factor': str(registration_date_factor),
    }


def reg_country_city_factors(
    historydb_api_events_status=True,
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
    **kwargs
):
    return {
        'historydb_api_events_status': historydb_api_events_status,
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


def reg_country_city_statbox_entry(
    historydb_api_events_status=True,
    registration_country_factor=FACTOR_NOT_SET,
    registration_country_factor_id=FACTOR_NOT_SET,
    registration_city_factor=FACTOR_NOT_SET,
    registration_city_factor_id=FACTOR_NOT_SET,
    **kwargs
):
    entry = {
        'registration_country_factor_text': str(registration_country_factor),
        'registration_country_factor_id': str(registration_country_factor_id),
        'registration_city_factor_text': str(registration_city_factor),
        'registration_city_factor_id': str(registration_city_factor_id),
    }
    if historydb_api_events_status is not None:
        entry['historydb_status'] = tskv_bool(historydb_api_events_status)
    return entry


def social_factors(
    social_accounts_entered_accounts=None,
    social_accounts_entered_profiles=None,
    social_accounts_account_profiles=None,
    social_accounts_factor_matches_count=0,
    social_accounts_factor_entered_accounts_count=0,
    social_accounts_factor_entered_profiles_count=0,
    social_accounts_factor_account_profiles_count=0,
    social_accounts_api_status=True,
    **kwargs
):
    return {
        'social_accounts': {
            'entered_accounts': social_accounts_entered_accounts or [],
            'entered_profiles': social_accounts_entered_profiles or [],
            'account_profiles': social_accounts_account_profiles or [],
            'factor': {
                'matches_count': social_accounts_factor_matches_count,
                'entered_accounts_count': social_accounts_factor_entered_accounts_count,
                'entered_profiles_count': social_accounts_factor_entered_profiles_count,
                'account_profiles_count': social_accounts_factor_account_profiles_count,
            },
            'api_status': social_accounts_api_status,
        },
    }


def social_statbox_entry(
    social_accounts_factor_matches_count=0,
    social_accounts_factor_entered_accounts_count=0,
    social_accounts_factor_entered_profiles_count=0,
    social_accounts_factor_account_profiles_count=0,
    social_accounts_api_status=True,
    **kwargs
):
    return {
        'social_accounts_factor_matches_count': str(social_accounts_factor_matches_count),
        'social_accounts_factor_entered_accounts_count': str(social_accounts_factor_entered_accounts_count),
        'social_accounts_factor_entered_profiles_count': str(social_accounts_factor_entered_profiles_count),
        'social_accounts_factor_account_profiles_count': str(social_accounts_factor_account_profiles_count),
        'social_accounts_api_status': tskv_bool(social_accounts_api_status),
    }


def one_day_match_env(
    entity=PASSWORDS_ENTITY_NAME,
    timestamp=1000,
    ip=TEST_IP,
    subnet=TEST_IP_AS_SUBNET,
    ua=TEST_USER_AGENT_2_PARSED,
    ip_first_auth_info=None,
    subnet_first_auth_info=None,
    ua_first_auth_info=None,
):
    return locals()


def aggregated_factors(
    original_factors,
    auths_aggregated_runtime_api_status=True,
    personal_and_recovery_ip_match=FACTOR_BOOL_NO_MATCH,
    personal_and_recovery_subnet_match=FACTOR_BOOL_NO_MATCH,
    personal_and_recovery_ua_match=FACTOR_BOOL_NO_MATCH,
    personal_and_recovery_ip_eq_user=FACTOR_NOT_SET,
    personal_and_recovery_subnet_eq_user=FACTOR_NOT_SET,
    personal_and_recovery_ua_eq_user=FACTOR_NOT_SET,
    personal_and_recovery_ip_eq_reg=FACTOR_NOT_SET,
    personal_and_recovery_subnet_eq_reg=FACTOR_NOT_SET,
    personal_and_recovery_ua_eq_reg=FACTOR_NOT_SET,
    personal_and_recovery_ip_first_auth_depth=None,
    personal_and_recovery_subnet_first_auth_depth=None,
    personal_and_recovery_ua_first_auth_depth=None,
    personal_and_recovery_matches=None,
    password_and_personal_ip_match=FACTOR_BOOL_NO_MATCH,
    password_and_personal_subnet_match=FACTOR_BOOL_NO_MATCH,
    password_and_personal_ua_match=FACTOR_BOOL_NO_MATCH,
    password_and_personal_ip_eq_user=FACTOR_NOT_SET,
    password_and_personal_subnet_eq_user=FACTOR_NOT_SET,
    password_and_personal_ua_eq_user=FACTOR_NOT_SET,
    password_and_personal_ip_eq_reg=FACTOR_NOT_SET,
    password_and_personal_subnet_eq_reg=FACTOR_NOT_SET,
    password_and_personal_ua_eq_reg=FACTOR_NOT_SET,
    password_and_personal_ip_first_auth_depth=None,
    password_and_personal_subnet_first_auth_depth=None,
    password_and_personal_ua_first_auth_depth=None,
    password_and_personal_matches=None,
    password_and_recovery_ip_match=FACTOR_BOOL_NO_MATCH,
    password_and_recovery_subnet_match=FACTOR_BOOL_NO_MATCH,
    password_and_recovery_ua_match=FACTOR_BOOL_NO_MATCH,
    password_and_recovery_ip_eq_user=FACTOR_NOT_SET,
    password_and_recovery_subnet_eq_user=FACTOR_NOT_SET,
    password_and_recovery_ua_eq_user=FACTOR_NOT_SET,
    password_and_recovery_ip_eq_reg=FACTOR_NOT_SET,
    password_and_recovery_subnet_eq_reg=FACTOR_NOT_SET,
    password_and_recovery_ua_eq_reg=FACTOR_NOT_SET,
    password_and_recovery_ip_first_auth_depth=None,
    password_and_recovery_subnet_first_auth_depth=None,
    password_and_recovery_ua_first_auth_depth=None,
    password_and_recovery_matches=None,
    **kwargs
):
    personal_and_recovery_not_set = [FACTOR_NOT_SET] * PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES
    values_not_set = [FACTOR_NOT_SET] * PASSWORD_AND_PERSONAL_MAX_ANALYZED_CHANGES
    original_factors.update({
        'auths_aggregated_runtime_api_status': auths_aggregated_runtime_api_status,
        'aggregated': {
            'matches': {
                'password_and_personal_change_one_day': password_and_personal_matches or [],
                'password_and_recovery_change_one_day': password_and_recovery_matches or [],
                'personal_and_recovery_change_one_day': personal_and_recovery_matches or [],
            },
            'factor': {
                'personal_and_recovery_change_one_day': {
                    'ip_match': personal_and_recovery_ip_match,
                    'subnet_match': personal_and_recovery_subnet_match,
                    'ua_match': personal_and_recovery_ua_match,
                    'ip_eq_user': personal_and_recovery_ip_eq_user,
                    'ip_eq_reg': personal_and_recovery_ip_eq_reg,
                    'subnet_eq_user': personal_and_recovery_subnet_eq_user,
                    'subnet_eq_reg': personal_and_recovery_subnet_eq_reg,
                    'ua_eq_user': personal_and_recovery_ua_eq_user,
                    'ua_eq_reg': personal_and_recovery_ua_eq_reg,
                    'ip_first_auth_depth': personal_and_recovery_ip_first_auth_depth or personal_and_recovery_not_set,
                    'subnet_first_auth_depth': personal_and_recovery_subnet_first_auth_depth or personal_and_recovery_not_set,
                    'ua_first_auth_depth': personal_and_recovery_ua_first_auth_depth or personal_and_recovery_not_set,
                },
                'password_and_personal_change_one_day': {
                    'ip_match': password_and_personal_ip_match,
                    'subnet_match': password_and_personal_subnet_match,
                    'ua_match': password_and_personal_ua_match,
                    'ip_eq_user': password_and_personal_ip_eq_user,
                    'ip_eq_reg': password_and_personal_ip_eq_reg,
                    'subnet_eq_user': password_and_personal_subnet_eq_user,
                    'subnet_eq_reg': password_and_personal_subnet_eq_reg,
                    'ua_eq_user': password_and_personal_ua_eq_user,
                    'ua_eq_reg': password_and_personal_ua_eq_reg,
                    'ip_first_auth_depth': password_and_personal_ip_first_auth_depth or values_not_set,
                    'subnet_first_auth_depth': password_and_personal_subnet_first_auth_depth or values_not_set,
                    'ua_first_auth_depth': password_and_personal_ua_first_auth_depth or values_not_set,
                },
                'password_and_recovery_change_one_day': {
                    'ip_match': password_and_recovery_ip_match,
                    'subnet_match': password_and_recovery_subnet_match,
                    'ua_match': password_and_recovery_ua_match,
                    'ip_eq_user': password_and_recovery_ip_eq_user,
                    'ip_eq_reg': password_and_recovery_ip_eq_reg,
                    'subnet_eq_user': password_and_recovery_subnet_eq_user,
                    'subnet_eq_reg': password_and_recovery_subnet_eq_reg,
                    'ua_eq_user': password_and_recovery_ua_eq_user,
                    'ua_eq_reg': password_and_recovery_ua_eq_reg,
                    'ip_first_auth_depth': password_and_recovery_ip_first_auth_depth or values_not_set,
                    'subnet_first_auth_depth': password_and_recovery_subnet_first_auth_depth or values_not_set,
                    'ua_first_auth_depth': password_and_recovery_ua_first_auth_depth or values_not_set,
                },
            },
        },
    })
    for entity_update_func in (
            passwords_factors_aggregated_update,
            phone_numbers_factors_aggregated_update,
            answer_factors_aggregated_update,
    ):
        original_factors = entity_update_func(original_factors, **kwargs)
    return original_factors


def aggregated_statbox_entry(
    auths_aggregated_runtime_api_status=True,
    historydb_api_events_status=True,
    personal_and_recovery_ip_match=FACTOR_BOOL_NO_MATCH,
    personal_and_recovery_subnet_match=FACTOR_BOOL_NO_MATCH,
    personal_and_recovery_ua_match=FACTOR_BOOL_NO_MATCH,
    personal_and_recovery_ip_eq_user=FACTOR_NOT_SET,
    personal_and_recovery_subnet_eq_user=FACTOR_NOT_SET,
    personal_and_recovery_ua_eq_user=FACTOR_NOT_SET,
    personal_and_recovery_ip_eq_reg=FACTOR_NOT_SET,
    personal_and_recovery_subnet_eq_reg=FACTOR_NOT_SET,
    personal_and_recovery_ua_eq_reg=FACTOR_NOT_SET,
    personal_and_recovery_ip_first_auth_depth=None,
    personal_and_recovery_subnet_first_auth_depth=None,
    personal_and_recovery_ua_first_auth_depth=None,
    password_and_personal_ip_match=FACTOR_BOOL_NO_MATCH,
    password_and_personal_subnet_match=FACTOR_BOOL_NO_MATCH,
    password_and_personal_ua_match=FACTOR_BOOL_NO_MATCH,
    password_and_personal_ip_eq_user=FACTOR_NOT_SET,
    password_and_personal_subnet_eq_user=FACTOR_NOT_SET,
    password_and_personal_ua_eq_user=FACTOR_NOT_SET,
    password_and_personal_ip_eq_reg=FACTOR_NOT_SET,
    password_and_personal_subnet_eq_reg=FACTOR_NOT_SET,
    password_and_personal_ua_eq_reg=FACTOR_NOT_SET,
    password_and_personal_ip_first_auth_depth=None,
    password_and_personal_subnet_first_auth_depth=None,
    password_and_personal_ua_first_auth_depth=None,
    password_and_recovery_ip_match=FACTOR_BOOL_NO_MATCH,
    password_and_recovery_subnet_match=FACTOR_BOOL_NO_MATCH,
    password_and_recovery_ua_match=FACTOR_BOOL_NO_MATCH,
    password_and_recovery_ip_eq_user=FACTOR_NOT_SET,
    password_and_recovery_subnet_eq_user=FACTOR_NOT_SET,
    password_and_recovery_ua_eq_user=FACTOR_NOT_SET,
    password_and_recovery_ip_eq_reg=FACTOR_NOT_SET,
    password_and_recovery_subnet_eq_reg=FACTOR_NOT_SET,
    password_and_recovery_ua_eq_reg=FACTOR_NOT_SET,
    password_and_recovery_ip_first_auth_depth=None,
    password_and_recovery_subnet_first_auth_depth=None,
    password_and_recovery_ua_first_auth_depth=None,
    **kwargs
):
    entry = {
        'auths_aggregated_runtime_api_status': tskv_bool(auths_aggregated_runtime_api_status),
    }
    if historydb_api_events_status is not None:
        entry['historydb_status'] = tskv_bool(historydb_api_events_status)
    for pair_name, change_count in zip(
            ('personal_and_recovery', 'password_and_personal', 'password_and_recovery'),
            (
                PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES,
                PASSWORD_AND_PERSONAL_MAX_ANALYZED_CHANGES,
                PASSWORD_AND_RECOVERY_MAX_ANALYZED_CHANGES,
            ),
    ):
        for factor_name in (
                'ip_match',
                'subnet_match',
                'ua_match',
                'ip_eq_user',
                'ip_eq_reg',
                'subnet_eq_user',
                'subnet_eq_reg',
                'ua_eq_user',
                'ua_eq_reg',
                'ip_first_auth_depth',
                'subnet_first_auth_depth',
                'ua_first_auth_depth',
        ):
            param_name = '%s_%s' % (pair_name, factor_name)
            param_value = locals()[param_name]
            if factor_name in ('ip_first_auth_depth', 'subnet_first_auth_depth', 'ua_first_auth_depth'):
                param_value = param_value or [FACTOR_NOT_SET] * change_count
                for index, sub_value in enumerate(param_value):
                    key = 'aggregated_factor_%s_change_one_day_%s_%d' % (pair_name, factor_name, index)
                    entry[key] = str(sub_value)
            else:
                key = 'aggregated_factor_%s_change_one_day_%s' % (pair_name, factor_name)
                entry[key] = str(param_value)
    entry.update(passwords_statbox_entry_aggregated_update(**kwargs))
    entry.update(phone_numbers_statbox_entry_aggregated_update(**kwargs))
    entry.update(answer_statbox_entry_aggregated_update(**kwargs))
    return entry


def events_info_cache(registration_env=None):
    return {
        'registration_env': registration_env or {},
    }


def device_id_factors(device_id_factor=FACTOR_NOT_SET, device_id_actual=None, device_id_history=None,
                      historydb_api_events_status=True, **kwargs):
    return {
        'device_id': {
            'actual': device_id_actual,
            'history': device_id_history or [],
            'factor': device_id_factor,
        },
        'historydb_api_events_status': historydb_api_events_status,
    }


def device_id_statbox_entry(device_id_factor=FACTOR_NOT_SET, historydb_api_events_status=True, **kwargs):
    entry = {
        'device_id_factor': str(device_id_factor),
    }
    if historydb_api_events_status is not None:
        entry['historydb_status'] = tskv_bool(historydb_api_events_status)
    return entry
