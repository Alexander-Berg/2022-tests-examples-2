# pylint: disable=protected-access
# pylint: disable=too-many-lines

import datetime
import typing

import pytest

import generated.clients.personal as personal_client

from mia.crontasks import filters
from mia.crontasks import period
from mia.crontasks import personal_wrapper
from mia.crontasks import user_phone_wrapper
from mia.crontasks.request_parser import common
from mia.crontasks.request_parser import request_parser_lavka
from mia.generated.service.swagger.models import api
from test_mia.cron import personal_dummy
from test_mia.cron import user_phone_dummy


_PRIMITIVE_FILTERS = {
    filters.ExactMatchFilter,
    filters.NormalizedFilter,
    filters.RegexFilter,
    filters.PeriodFilter,
    filters.EqualFilter,
    filters.CountryFilter,
}

_NESTED_FILTERS = {
    filters.PerformerFilter,
    filters.LastOfArrayFilter,
    filters.AnyOfArrayFilter,
}

USER_PHONE_WRAPPER_DUMMY = user_phone_dummy.UserPhoneWrapperDummy({})

PERSONAL_WRAPPER_DUMMY = personal_wrapper.PersonalWrapper(
    typing.cast(
        personal_client.PersonalClient, personal_dummy.PersonalDummy(),
    ),
)

COUNTRIES_DICT = {'RU': ['Россия', 'Russia'], 'BL': ['Беларусь', 'Belarus']}

PARSER_CONFIG = request_parser_lavka.request_parser.RequestParserConfig(
    countries_filter_enabled=True, countries_dict=COUNTRIES_DICT,
)
YT_ORDERS_MONTHS_KEPT = 6
MONTH_DURATION = 30


LAVKA_PARSER = request_parser_lavka.RequestParserLavka(
    typing.cast(user_phone_wrapper.UserPhoneWrapper, USER_PHONE_WRAPPER_DUMMY),
    YT_ORDERS_MONTHS_KEPT,
    PARSER_CONFIG,
    PERSONAL_WRAPPER_DUMMY,
)


@pytest.mark.parametrize(
    (
        'completed_only, exact_fields, regex_fields,'
        ' period_fields, countries, raw_filters'
    ),
    [
        (
            False,
            api.TextExactFieldsLavka(
                order_id='1',
                order_nr='test_order_nr',
                address_city='test_address_city',
                address_street='test_address_street',
                address_house='test_address_house',
                courier_name='test_courier_name',
                user_phone='+79999999999',
            ),
            api.TextRegexFieldsLavka(courier_name='test_courier_name'),
            api.PeriodFieldsLavka(
                created=api.Period(
                    datetime.datetime(2019, 1, 2, 3, 4, 5, 1235),
                    datetime.datetime(2019, 2, 3, 1, 1, 59, 65),
                ),
                finished=api.Period(
                    datetime.datetime(2020, 1, 2, 3, 4, 5, 1235),
                    datetime.datetime(2020, 2, 3, 1, 1, 59, 65),
                ),
            ),
            None,
            [
                filters.PeriodFilter(
                    'created_at',
                    api.Period(
                        datetime.datetime(2019, 3, 4, 12, 20)
                        - datetime.timedelta(
                            MONTH_DURATION * YT_ORDERS_MONTHS_KEPT,
                        ),
                        datetime.datetime(2019, 3, 4, 12, 20),
                    ),
                ),
                filters.ExactMatchFilter('order_id', '1'),
                filters.ExactMatchFilter('order_nr', 'test_order_nr'),
                filters.ExactMatchFilter(
                    'personal_phone_id', '+79999999999_id',
                ),
                filters.ExactMatchFilter(
                    'dispatch_courier_name', 'test_courier_name',
                ),
                filters.RegexFilter(
                    'dispatch_courier_name', 'test_courier_name',
                ),
                filters.PeriodFilter(
                    'created_at',
                    api.Period(
                        datetime.datetime(2019, 1, 2, 3, 4, 5, 1235),
                        datetime.datetime(2019, 2, 3, 1, 1, 59, 65),
                    ),
                ),
                filters.PeriodFilter(
                    'finished_at',
                    api.Period(
                        datetime.datetime(2020, 1, 2, 3, 4, 5, 1235),
                        datetime.datetime(2020, 2, 3, 1, 1, 59, 65),
                    ),
                ),
                filters.RegexFilter(
                    'address_city', '(.*)test_address_city(.*)',
                ),
                filters.RegexFilter(
                    'address_street', '(.*)test_address_street(.*)',
                ),
                filters.RegexFilter(
                    'address_house', '(.*)test_address_house(.*)',
                ),
            ],
        ),
        (
            True,
            api.TextExactFieldsLavka(
                order_id='1',
                order_nr='test_order_nr',
                address_city='test_address_city',
                address_street='test_address_street',
                address_house='test_address_house',
                courier_name='test_courier_name',
            ),
            api.TextRegexFieldsLavka(courier_name='test_courier_name'),
            api.PeriodFieldsLavka(
                created=api.Period(
                    datetime.datetime(2019, 1, 2, 3, 4, 5, 1235),
                    datetime.datetime(2019, 2, 3, 1, 1, 59, 65),
                ),
            ),
            ['RU', 'BL'],
            [
                filters.ExactMatchFilter('status', 'closed'),
                filters.PeriodFilter(
                    'created_at',
                    api.Period(
                        datetime.datetime(2019, 3, 4, 12, 20)
                        - datetime.timedelta(
                            MONTH_DURATION * YT_ORDERS_MONTHS_KEPT,
                        ),
                        datetime.datetime(2019, 3, 4, 12, 20),
                    ),
                ),
                filters.ExactMatchFilter('order_id', '1'),
                filters.ExactMatchFilter('order_nr', 'test_order_nr'),
                filters.ExactMatchFilter(
                    'dispatch_courier_name', 'test_courier_name',
                ),
                filters.RegexFilter(
                    'dispatch_courier_name', 'test_courier_name',
                ),
                filters.PeriodFilter(
                    'created_at',
                    api.Period(
                        datetime.datetime(2019, 1, 2, 3, 4, 5, 1235),
                        datetime.datetime(2019, 2, 3, 1, 1, 59, 65),
                    ),
                ),
                filters.RegexFilter(
                    'address_city', '(.*)test_address_city(.*)',
                ),
                filters.RegexFilter(
                    'address_street', '(.*)test_address_street(.*)',
                ),
                filters.RegexFilter(
                    'address_house', '(.*)test_address_house(.*)',
                ),
                filters.AnyOfFilter(
                    [
                        filters.CountryFilter(
                            'address_country',
                            {
                                'Роccия': 'RU',
                                'Russia': 'RU',
                                'Беларусь': 'BL',
                                'Belarus': 'BL',
                            },
                            'RU',
                        ),
                        filters.CountryFilter(
                            'address_country',
                            {
                                'Роccия': 'RU',
                                'Russia': 'RU',
                                'Беларусь': 'BL',
                                'Belarus': 'BL',
                            },
                            'BL',
                        ),
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2019-03-04T12:20:00.0')
async def test_parse_lavka(
        completed_only,
        exact_fields,
        regex_fields,
        period_fields,
        countries,
        raw_filters,
):
    query_body = api.QueryBodyLavka(
        completed_only=completed_only,
        exact=exact_fields,
        regex=regex_fields,
        period=period_fields,
        countries=countries,
    )
    result = await LAVKA_PARSER._parse(query_body)
    expected = filters.AllOfFilter(raw_filters)
    _assert_filters_equality(result, expected)


@pytest.mark.now('2019-03-04T12:20:00.0')
async def test_parse_completed_only_lavka():
    query_body = api.QueryBodyLavka(
        completed_only=True, exact=api.TextExactFieldsLavka(),
    )
    result = await LAVKA_PARSER._parse(query_body)
    expected = filters.AllOfFilter(
        [
            filters.ExactMatchFilter('status', 'closed'),
            filters.PeriodFilter(
                'created_at',
                api.Period(
                    datetime.datetime(2019, 3, 4, 12, 20)
                    - datetime.timedelta(
                        MONTH_DURATION * YT_ORDERS_MONTHS_KEPT,
                    ),
                    datetime.datetime(2019, 3, 4, 12, 20),
                ),
            ),
        ],
    )
    _assert_filters_equality(result, expected)


@pytest.mark.parametrize(
    'exact_fields, expected',
    [
        (None, []),
        (
            api.TextExactFieldsLavka(order_id='1'),
            [filters.ExactMatchFilter('order_id', '1')],
        ),
        (
            api.TextExactFieldsLavka(order_nr='test_order_nr'),
            [filters.ExactMatchFilter('order_nr', 'test_order_nr')],
        ),
        (
            api.TextExactFieldsLavka(courier_name='test_courier_name'),
            [
                filters.ExactMatchFilter(
                    'dispatch_courier_name', 'test_courier_name',
                ),
            ],
        ),
        (
            api.TextExactFieldsLavka(
                order_id='1',
                order_nr='test_order_nr',
                address_city='test_address_city',
                address_street='test_address_street',
                address_house='test_address_house',
                courier_name='test_courier_name',
            ),
            [
                filters.ExactMatchFilter('order_id', '1'),
                filters.ExactMatchFilter('order_nr', 'test_order_nr'),
                filters.ExactMatchFilter(
                    'dispatch_courier_name', 'test_courier_name',
                ),
            ],
        ),
    ],
)
async def test_parse_exact_lavka(exact_fields, expected):
    query_body = api.QueryBodyLavka(False, exact=exact_fields)
    result = LAVKA_PARSER._parse_exact(query_body)
    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'regex_fields, expected',
    [
        (None, []),
        (
            api.TextRegexFieldsLavka(courier_name='test_courier_name'),
            [
                filters.RegexFilter(
                    'dispatch_courier_name', 'test_courier_name',
                ),
            ],
        ),
    ],
)
async def test_parse_regex_lavka(regex_fields, expected):
    query_body = api.QueryBodyLavka(False, regex=regex_fields)
    result = LAVKA_PARSER._parse_regex(query_body)
    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'exact_fields, expected',
    [
        (
            api.TextExactFieldsLavka(address_city='test_address_city'),
            [filters.RegexFilter('address_city', '(.*)test_address_city(.*)')],
        ),
        (
            api.TextExactFieldsLavka(address_street='test_address_street'),
            [
                filters.RegexFilter(
                    'address_street', '(.*)test_address_street(.*)',
                ),
            ],
        ),
        (
            api.TextExactFieldsLavka(address_house='test_address_house'),
            [
                filters.RegexFilter(
                    'address_house', '(.*)test_address_house(.*)',
                ),
            ],
        ),
    ],
)
async def test_parse_substring(exact_fields, expected):
    query_body = api.QueryBodyLavka(False, exact=exact_fields)
    result = LAVKA_PARSER._parse_substring_fields(query_body)
    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'created_periods_list, expected',
    [
        (
            [],
            period.Period(
                datetime.datetime(2019, 4, 1, 0, 0),
                datetime.datetime(2019, 10, 17, 12, 0),
            ),
        ),
        (
            [
                api.Period(
                    datetime.datetime(2019, 6, 2, 10, 52),
                    datetime.datetime(2019, 7, 12, 23, 48),
                ),
            ],
            period.Period(
                datetime.datetime(2019, 6, 2, 10, 52),
                datetime.datetime(2019, 7, 12, 23, 48),
            ),
        ),
        (
            [
                api.Period(
                    datetime.datetime(2019, 5, 5, 10, 52),
                    datetime.datetime(2019, 9, 29, 23, 48),
                ),
                api.Period(
                    datetime.datetime(2019, 5, 5, 10, 52),
                    datetime.datetime(2019, 9, 24, 23, 48),
                ),
            ],
            period.Period(
                datetime.datetime(2019, 5, 5, 10, 52),
                datetime.datetime(2019, 9, 29, 23, 48),
            ),
        ),
        (
            [
                api.Period(
                    datetime.datetime(2019, 6, 25, 11, 52, 38),
                    datetime.datetime(2019, 9, 26, 7, 54, 17),
                ),
                api.Period(
                    datetime.datetime(2019, 8, 10, 23, 59, 36),
                    datetime.datetime(2019, 10, 9, 3, 9, 33),
                ),
                api.Period(
                    datetime.datetime(2019, 8, 3, 8, 31, 35),
                    datetime.datetime(2019, 8, 27, 6, 43, 11),
                ),
                api.Period(
                    datetime.datetime(2019, 8, 23, 23, 26, 10),
                    datetime.datetime(2019, 8, 24, 13, 16, 29),
                ),
                api.Period(
                    datetime.datetime(2019, 6, 17, 20, 48, 12),
                    datetime.datetime(2019, 8, 12, 23, 16, 39),
                ),
                api.Period(
                    datetime.datetime(2019, 7, 1, 2, 24, 57),
                    datetime.datetime(2019, 7, 30, 15, 17, 36),
                ),
                api.Period(
                    datetime.datetime(2019, 7, 10, 16, 2, 16),
                    datetime.datetime(2019, 7, 12, 0, 14, 4),
                ),
                api.Period(
                    datetime.datetime(2019, 6, 14, 12, 44, 16),
                    datetime.datetime(2019, 9, 12, 5, 42, 0),
                ),
                api.Period(
                    datetime.datetime(2019, 6, 28, 13, 27, 56),
                    datetime.datetime(2019, 7, 10, 3, 10, 12),
                ),
            ],
            period.Period(
                datetime.datetime(2019, 6, 14, 12, 44, 16),
                datetime.datetime(2019, 10, 9, 3, 9, 33),
            ),
        ),
    ],
)
@pytest.mark.now('2019-10-17T12:00:00Z')
async def test_calculate_interval_lavka(created_periods_list, expected):
    queries = []
    for created_period in created_periods_list:
        queries.append(
            api.QueryBodyLavka(
                False, period=api.PeriodFieldsLavka(created=created_period),
            ),
        )
    assert LAVKA_PARSER._calculate_interval(queries) == expected


@pytest.mark.parametrize(
    'created_periods_list',
    [
        [
            api.Period(
                datetime.datetime(2019, 3, 17, 12, 0),
                datetime.datetime(2019, 7, 12, 23, 48),
            ),
        ],
        [
            api.Period(
                datetime.datetime(2018, 4, 5, 10, 52),
                datetime.datetime(2019, 9, 29, 23, 48),
            ),
            api.Period(
                datetime.datetime(2019, 5, 5, 10, 52),
                datetime.datetime(2019, 5, 24, 23, 48),
            ),
        ],
    ],
)
@pytest.mark.now('2019-10-17T12:00:00Z')
async def test_calculate_interval_lavka_exception(created_periods_list):
    queries = []
    for created_period in created_periods_list:
        queries.append(
            api.QueryBodyLavka(
                False, period=api.PeriodFieldsLavka(created=created_period),
            ),
        )
    try:
        LAVKA_PARSER._calculate_interval(queries)
    except common.DatesTooOldError:
        return
    assert False


@pytest.mark.parametrize(
    'created_period, finished_period, expected',
    [
        (None, None, []),
        (
            api.Period(
                datetime.datetime(2019, 1, 2, 3, 4, 5, 1235),
                datetime.datetime(2019, 2, 3, 1, 1, 59, 65),
            ),
            api.Period(
                datetime.datetime(2020, 1, 2, 3, 4, 5, 1235),
                datetime.datetime(2020, 2, 3, 1, 1, 59, 65),
            ),
            [
                filters.PeriodFilter(
                    'created_at',
                    api.Period(
                        datetime.datetime(2019, 1, 2, 3, 4, 5, 1235),
                        datetime.datetime(2019, 2, 3, 1, 1, 59, 65),
                    ),
                ),
                filters.PeriodFilter(
                    'finished_at',
                    api.Period(
                        datetime.datetime(2020, 1, 2, 3, 4, 5, 1235),
                        datetime.datetime(2020, 2, 3, 1, 1, 59, 65),
                    ),
                ),
            ],
        ),
    ],
)
async def test_lavka_parse_period_fields(
        created_period, finished_period, expected,
):
    query_body = api.QueryBodyLavka(
        False,
        period=api.PeriodFieldsLavka(
            created=created_period, finished=finished_period,
        ),
    )
    result = LAVKA_PARSER._parse_period_fields(query_body)
    _assert_lists_of_filters_equality(result, expected)


def _assert_lists_of_filters_equality(result_list, expected_list):
    assert len(result_list) == len(expected_list)
    for result_filter, expected_filter in zip(result_list, expected_list):
        _assert_filters_equality(result_filter, expected_filter)


def _assert_filters_equality(filter_a, filter_b):
    assert filter_a.__class__ == filter_b.__class__
    assert filter_a.row_field_name == filter_b.row_field_name
    if filter_b.__class__ in _PRIMITIVE_FILTERS:
        assert filter_a.reference_value == filter_b.reference_value
        return
    if filter_b.__class__ in _NESTED_FILTERS:
        _assert_filters_equality(
            filter_a.reference_value, filter_b.reference_value,
        )
        return
    assert len(filter_a.reference_value) == len(filter_b.reference_value)
    for f_a, f_b in zip(filter_a.reference_value, filter_b.reference_value):
        _assert_filters_equality(f_a, f_b)
    return
