# pylint: disable=protected-access
# pylint: disable=too-many-lines

import datetime
import typing

import pytest

from mia.crontasks import filters
from mia.crontasks import period
from mia.crontasks import user_phone_wrapper
from mia.crontasks.request_parser import common
from mia.crontasks.request_parser import request_parser_taxi
from mia.generated.service.swagger.models import api
from test_mia.cron import user_phone_dummy


_PRIMITIVE_FILTERS = {
    filters.ExactMatchFilter,
    filters.NotEqualFilter,
    filters.NormalizedFilter,
    filters.RegexFilter,
    filters.PeriodFilter,
    filters.CountryFilter,
    filters.EqualFilter,
}

_NESTED_FILTERS = {
    filters.PerformerFilter,
    filters.LastOfArrayFilter,
    filters.AnyOfArrayFilter,
}

_PERIOD_1 = api.Period(
    datetime.datetime(2019, 1, 2, 3, 4, 5, 1235),
    datetime.datetime(2019, 2, 3, 1, 1, 59, 65),
)

_PERIOD_2 = api.Period(
    datetime.datetime(2018, 10, 9, 8, 10, 1, 871),
    datetime.datetime(2018, 10, 9, 8, 10, 2, 401),
)

USER_PHONE_WRAPPER_DUMMY = user_phone_dummy.UserPhoneWrapperDummy(
    {
        'test_phone_0': [],
        'test_phone_1': ['id_1_1'],
        'test_phone_2': ['id_2_1', 'id_2_2'],
        'test_phone_3': ['id_3_1', 'id_3_2', 'id_3_3'],
    },
)


PARSER_CONFIG = request_parser_taxi.request_parser.RequestParserConfig(
    countries_filter_enabled=False, countries_dict={},
)
YT_ORDERS_MONTHS_KEPT = 6
MONTH_DURATION = 30

TAXI_PARSER = request_parser_taxi.RequestParserTaxi(
    typing.cast(user_phone_wrapper.UserPhoneWrapper, USER_PHONE_WRAPPER_DUMMY),
    YT_ORDERS_MONTHS_KEPT,
    PARSER_CONFIG,
)


@pytest.mark.parametrize(
    'query_body, expected',
    [
        (
            api.QueryBodyTaxi(
                check_all_candidates=False,
                exact=api.TextExactFieldsTaxi(
                    user_phone='test_phone_2',
                    order_id='test_order_id',
                    order_source='yandex',
                    source_address='test source adress',
                    license_plates='test_license_plates',
                    driver_license='test_driver_license',
                    driver_phone='test_driver_phone',
                    any_destination_address='test_any_destinations_adress',
                ),
                regex=api.TextRegexFieldsTaxi(
                    source_address='test_source_adress',
                    final_destination_address='test_final_destination_adress',
                    driver_name='test_driver_name',
                ),
                period=api.PeriodFieldsTaxi(
                    created=_PERIOD_1,
                    request_due=_PERIOD_2,
                    finished=_PERIOD_2,
                ),
            ),
            filters.AllOfFilter(
                [
                    filters.EqualFilter('order_source', None),
                    filters.PeriodFilter(
                        'created',
                        api.Period(
                            datetime.datetime(2020, 4, 22, 12)
                            - datetime.timedelta(
                                MONTH_DURATION * YT_ORDERS_MONTHS_KEPT,
                            ),
                            datetime.datetime(2020, 4, 22, 12),
                        ),
                    ),
                    filters.AnyOfFilter(
                        [
                            filters.ExactMatchFilter(
                                'user_phone_id', 'id_2_1',
                            ),
                            filters.ExactMatchFilter(
                                'user_phone_id', 'id_2_2',
                            ),
                            filters.ExactMatchFilter(
                                'request_source.contact_phone_id', 'id_2_1',
                            ),
                            filters.ExactMatchFilter(
                                'request_source.contact_phone_id', 'id_2_2',
                            ),
                            filters.ExactMatchFilter(
                                'extra_user_phone_id', 'id_2_1',
                            ),
                            filters.ExactMatchFilter(
                                'extra_user_phone_id', 'id_2_2',
                            ),
                            filters.AnyOfArrayFilter(
                                'request_destinations',
                                filters.ExactMatchFilter(
                                    'contact_phone_id', 'id_2_1',
                                ),
                            ),
                            filters.AnyOfArrayFilter(
                                'request_destinations',
                                filters.ExactMatchFilter(
                                    'contact_phone_id', 'id_2_2',
                                ),
                            ),
                        ],
                    ),
                    filters.ExactMatchFilter('order_id', 'test_order_id'),
                    filters.ExactMatchFilter(
                        'request_source.fullname', 'test source adress',
                    ),
                    filters.RegexFilter(
                        'request_source.fullname', 'test_source_adress',
                    ),
                    filters.AnyOfArrayFilter(
                        'request_destinations',
                        filters.ExactMatchFilter(
                            'fullname', 'test_any_destinations_adress',
                        ),
                    ),
                    filters.LastOfArrayFilter(
                        'request_destinations',
                        filters.RegexFilter(
                            'fullname', 'test_final_destination_adress',
                        ),
                    ),
                    filters.PerformerFilter(
                        filters.ExactMatchFilter(
                            'driver_phone', 'test_driver_phone',
                        ),
                    ),
                    filters.PerformerFilter(
                        filters.NormalizedFilter(
                            'driver_license', 'test_driver_license',
                        ),
                    ),
                    filters.PerformerFilter(
                        filters.NormalizedFilter(
                            'car_number', 'test_license_plates',
                        ),
                    ),
                    filters.PerformerFilter(
                        filters.RegexFilter('driver_name', 'test_driver_name'),
                    ),
                    filters.PeriodFilter('created', _PERIOD_1),
                    filters.PeriodFilter('request_due', _PERIOD_2),
                    filters.PeriodFilter('complete_time', _PERIOD_2),
                ],
            ),
        ),
        (
            api.QueryBodyTaxi(
                True,
                exact=api.TextExactFieldsTaxi(
                    user_phone='test_phone_2',
                    order_id='test_order_id',
                    order_source='uber',
                    source_address='test source adress',
                    license_plates='test_license_plates',
                    driver_license='test_driver_license',
                    driver_phone='test_driver_phone',
                    any_destination_address='test_any_destinations_adress',
                ),
                regex=api.TextRegexFieldsTaxi(
                    source_address='test_source_adress',
                    final_destination_address='test_final_destination_adress',
                    driver_name='test_driver_name',
                ),
                period=api.PeriodFieldsTaxi(
                    created=api.Period(
                        datetime.datetime(2019, 1, 2, 3, 4, 5, 1235),
                        datetime.datetime(2019, 2, 3, 1, 1, 59, 65),
                    ),
                    request_due=api.Period(
                        datetime.datetime(2018, 10, 9, 8, 10, 1, 871),
                        datetime.datetime(2018, 10, 9, 8, 10, 2, 401),
                    ),
                ),
            ),
            filters.AllOfFilter(
                [
                    filters.EqualFilter('order_source', 'yauber'),
                    filters.PeriodFilter(
                        'created',
                        api.Period(
                            datetime.datetime(2020, 4, 22, 12)
                            - datetime.timedelta(
                                MONTH_DURATION * YT_ORDERS_MONTHS_KEPT,
                            ),
                            datetime.datetime(2020, 4, 22, 12),
                        ),
                    ),
                    filters.AnyOfFilter(
                        [
                            filters.ExactMatchFilter(
                                'user_phone_id', 'id_2_1',
                            ),
                            filters.ExactMatchFilter(
                                'user_phone_id', 'id_2_2',
                            ),
                            filters.ExactMatchFilter(
                                'request_source.contact_phone_id', 'id_2_1',
                            ),
                            filters.ExactMatchFilter(
                                'request_source.contact_phone_id', 'id_2_2',
                            ),
                            filters.ExactMatchFilter(
                                'extra_user_phone_id', 'id_2_1',
                            ),
                            filters.ExactMatchFilter(
                                'extra_user_phone_id', 'id_2_2',
                            ),
                            filters.AnyOfArrayFilter(
                                'request_destinations',
                                filters.ExactMatchFilter(
                                    'contact_phone_id', 'id_2_1',
                                ),
                            ),
                            filters.AnyOfArrayFilter(
                                'request_destinations',
                                filters.ExactMatchFilter(
                                    'contact_phone_id', 'id_2_2',
                                ),
                            ),
                        ],
                    ),
                    filters.ExactMatchFilter('order_id', 'test_order_id'),
                    filters.ExactMatchFilter(
                        'request_source.fullname', 'test source adress',
                    ),
                    filters.RegexFilter(
                        'request_source.fullname', 'test_source_adress',
                    ),
                    filters.AnyOfArrayFilter(
                        'request_destinations',
                        filters.ExactMatchFilter(
                            'fullname', 'test_any_destinations_adress',
                        ),
                    ),
                    filters.LastOfArrayFilter(
                        'request_destinations',
                        filters.RegexFilter(
                            'fullname', 'test_final_destination_adress',
                        ),
                    ),
                    filters.AnyOfArrayFilter(
                        'candidates',
                        filters.ExactMatchFilter(
                            'driver_phone', 'test_driver_phone',
                        ),
                    ),
                    filters.AnyOfArrayFilter(
                        'candidates',
                        filters.NormalizedFilter(
                            'driver_license', 'test_driver_license',
                        ),
                    ),
                    filters.AnyOfArrayFilter(
                        'candidates',
                        filters.NormalizedFilter(
                            'car_number', 'test_license_plates',
                        ),
                    ),
                    filters.AnyOfArrayFilter(
                        'candidates',
                        filters.RegexFilter('driver_name', 'test_driver_name'),
                    ),
                    filters.PeriodFilter('created', _PERIOD_1),
                    filters.PeriodFilter('request_due', _PERIOD_2),
                ],
            ),
        ),
    ],
)
@pytest.mark.now('2020-04-22T12:00:00.0')
async def test_parse_taxi(query_body, expected):
    result = await TAXI_PARSER._parse(query_body)
    _assert_filters_equality(result, expected)


@pytest.mark.parametrize(
    'query_body, expected',
    [
        (
            api.QueryBodyTaxi(False, country='RU'),
            [
                filters.AnyOfFilter(
                    [
                        filters.CountryFilter(
                            'request_source.country',
                            {
                                'Роccия': 'RU',
                                'Russia': 'RU',
                                'Беларусь': 'BL',
                                'Belarus': 'BL',
                            },
                            'RU',
                        ),
                        filters.AnyOfArrayFilter(
                            'request_destinations',
                            filters.CountryFilter(
                                'country',
                                {
                                    'Роccия': 'RU',
                                    'Russia': 'RU',
                                    'Беларусь': 'BL',
                                    'Belarus': 'BL',
                                },
                                'RU',
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)
async def test_parse_country(query_body, expected):
    config_with_countries = (
        request_parser_taxi.request_parser.RequestParserConfig(
            countries_filter_enabled=True,
            countries_dict={
                'BU': ['Россия', 'Russia'],
                'BL': ['Беларусь', 'Belarus'],
            },
        )
    )

    request_parser_taxi.RequestParserTaxi(
        USER_PHONE_WRAPPER_DUMMY, YT_ORDERS_MONTHS_KEPT, config_with_countries,
    )

    result = TAXI_PARSER._get_country_filter(query_body)

    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'query_body, expected',
    [
        (api.QueryBodyTaxi(False), []),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(user_phone='test_phone_1'),
            ),
            [
                filters.AnyOfFilter(
                    [
                        filters.ExactMatchFilter('user_phone_id', 'id_1_1'),
                        filters.ExactMatchFilter(
                            'request_source.contact_phone_id', 'id_1_1',
                        ),
                        filters.ExactMatchFilter(
                            'extra_user_phone_id', 'id_1_1',
                        ),
                        filters.AnyOfArrayFilter(
                            'request_destinations',
                            filters.ExactMatchFilter(
                                'contact_phone_id', 'id_1_1',
                            ),
                        ),
                    ],
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(user_phone='test_phone_2'),
            ),
            [
                filters.AnyOfFilter(
                    [
                        filters.ExactMatchFilter('user_phone_id', 'id_2_1'),
                        filters.ExactMatchFilter('user_phone_id', 'id_2_2'),
                        filters.ExactMatchFilter(
                            'request_source.contact_phone_id', 'id_2_1',
                        ),
                        filters.ExactMatchFilter(
                            'request_source.contact_phone_id', 'id_2_2',
                        ),
                        filters.ExactMatchFilter(
                            'extra_user_phone_id', 'id_2_1',
                        ),
                        filters.ExactMatchFilter(
                            'extra_user_phone_id', 'id_2_2',
                        ),
                        filters.AnyOfArrayFilter(
                            'request_destinations',
                            filters.ExactMatchFilter(
                                'contact_phone_id', 'id_2_1',
                            ),
                        ),
                        filters.AnyOfArrayFilter(
                            'request_destinations',
                            filters.ExactMatchFilter(
                                'contact_phone_id', 'id_2_2',
                            ),
                        ),
                    ],
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(user_phone='test_phone_3'),
            ),
            [
                filters.AnyOfFilter(
                    [
                        filters.ExactMatchFilter('user_phone_id', 'id_3_1'),
                        filters.ExactMatchFilter('user_phone_id', 'id_3_2'),
                        filters.ExactMatchFilter('user_phone_id', 'id_3_3'),
                        filters.ExactMatchFilter(
                            'request_source.contact_phone_id', 'id_3_1',
                        ),
                        filters.ExactMatchFilter(
                            'request_source.contact_phone_id', 'id_3_2',
                        ),
                        filters.ExactMatchFilter(
                            'request_source.contact_phone_id', 'id_3_3',
                        ),
                        filters.ExactMatchFilter(
                            'extra_user_phone_id', 'id_3_1',
                        ),
                        filters.ExactMatchFilter(
                            'extra_user_phone_id', 'id_3_2',
                        ),
                        filters.ExactMatchFilter(
                            'extra_user_phone_id', 'id_3_3',
                        ),
                        filters.AnyOfArrayFilter(
                            'request_destinations',
                            filters.ExactMatchFilter(
                                'contact_phone_id', 'id_3_1',
                            ),
                        ),
                        filters.AnyOfArrayFilter(
                            'request_destinations',
                            filters.ExactMatchFilter(
                                'contact_phone_id', 'id_3_2',
                            ),
                        ),
                        filters.AnyOfArrayFilter(
                            'request_destinations',
                            filters.ExactMatchFilter(
                                'contact_phone_id', 'id_3_3',
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)
async def test_parse_phones_taxi(query_body, expected):
    result = await TAXI_PARSER._parse_phones(query_body)
    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'query_body',
    [
        api.QueryBodyTaxi(
            False, exact=api.TextExactFieldsTaxi(user_phone='test_phone_0'),
        ),
        api.QueryBodyTaxi(
            False, exact=api.TextExactFieldsTaxi(user_phone='test_phone_4'),
        ),
    ],
)
async def test_parse_phones_taxi_exception(query_body):
    try:
        await TAXI_PARSER._parse_phones(query_body)
    except common.UnknownPhone:
        return
    assert False


@pytest.mark.parametrize(
    'query_body, expected',
    [
        (api.QueryBodyTaxi(check_all_candidates=False), []),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(
                    source_address='test_source_adress',
                ),
            ),
            [
                filters.ExactMatchFilter(
                    'request_source.fullname', 'test_source_adress',
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False, exact=api.TextExactFieldsTaxi(order_id='test_order_id'),
            ),
            [filters.ExactMatchFilter('order_id', 'test_order_id')],
        ),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(
                    order_id='test_order_id',
                    source_address='test source adress',
                ),
            ),
            [
                filters.ExactMatchFilter('order_id', 'test_order_id'),
                filters.ExactMatchFilter(
                    'request_source.fullname', 'test source adress',
                ),
            ],
        ),
    ],
)
async def test_parse_exact_taxi(query_body, expected):
    result = TAXI_PARSER._parse_exact(query_body)
    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'test',
    [
        {
            'corp_orders': 'corp_excluded',
            'expected': [filters.NotEqualFilter('payment_tech_type', 'corp')],
        },
        {
            'corp_orders': 'corp_only',
            'expected': [
                filters.ExactMatchFilter('payment_tech_type', 'corp'),
            ],
        },
    ],
)
async def test_parse_corp(test):
    result = TAXI_PARSER._parse_corp(test['corp_orders'])
    _assert_lists_of_filters_equality(result, test['expected'])


@pytest.mark.parametrize(
    'query_body, expected',
    [
        (api.QueryBodyTaxi(check_all_candidates=False), []),
        (
            api.QueryBodyTaxi(
                False,
                regex=api.TextRegexFieldsTaxi(
                    source_address='test_source_adress',
                ),
            ),
            [
                filters.RegexFilter(
                    'request_source.fullname', 'test_source_adress',
                ),
            ],
        ),
    ],
)
async def test_parse_regex_taxi(query_body, expected):
    result = TAXI_PARSER._parse_regex(query_body)
    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'query_body, expected',
    [
        (api.QueryBodyTaxi(check_all_candidates=False), []),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(
                    any_destination_address='test_any_destinations_adress',
                ),
            ),
            [
                filters.AnyOfArrayFilter(
                    'request_destinations',
                    filters.ExactMatchFilter(
                        'fullname', 'test_any_destinations_adress',
                    ),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False,
                regex=api.TextRegexFieldsTaxi(
                    final_destination_address='test_final_destination_adress',
                ),
            ),
            [
                filters.LastOfArrayFilter(
                    'request_destinations',
                    filters.RegexFilter(
                        'fullname', 'test_final_destination_adress',
                    ),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False,
                regex=api.TextRegexFieldsTaxi(
                    final_destination_address='test_final_destination_adress',
                ),
                exact=api.TextExactFieldsTaxi(
                    any_destination_address='test_any_destinations_adress',
                ),
            ),
            [
                filters.AnyOfArrayFilter(
                    'request_destinations',
                    filters.ExactMatchFilter(
                        'fullname', 'test_any_destinations_adress',
                    ),
                ),
                filters.LastOfArrayFilter(
                    'request_destinations',
                    filters.RegexFilter(
                        'fullname', 'test_final_destination_adress',
                    ),
                ),
            ],
        ),
    ],
)
async def test_parse_in_array_taxi(query_body, expected):
    result = TAXI_PARSER._parse_in_array(query_body)
    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'query_body, expected',
    [
        (api.QueryBodyTaxi(check_all_candidates=False), []),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(
                    driver_phone='test_driver_phone',
                ),
            ),
            [
                filters.PerformerFilter(
                    filters.ExactMatchFilter(
                        'driver_phone', 'test_driver_phone',
                    ),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(
                    driver_license='test_driver_license',
                ),
            ),
            [
                filters.PerformerFilter(
                    filters.NormalizedFilter(
                        'driver_license', 'test_driver_license',
                    ),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(
                    license_plates='test_license_plates',
                ),
            ),
            [
                filters.PerformerFilter(
                    filters.NormalizedFilter(
                        'car_number', 'test_license_plates',
                    ),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False,
                regex=api.TextRegexFieldsTaxi(driver_name='test_driver_name'),
            ),
            [
                filters.PerformerFilter(
                    filters.RegexFilter('driver_name', 'test_driver_name'),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                True,
                exact=api.TextExactFieldsTaxi(
                    driver_phone='test_driver_phone',
                ),
            ),
            [
                filters.AnyOfArrayFilter(
                    'candidates',
                    filters.ExactMatchFilter(
                        'driver_phone', 'test_driver_phone',
                    ),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                True,
                exact=api.TextExactFieldsTaxi(
                    driver_license='test_driver_license',
                ),
            ),
            [
                filters.AnyOfArrayFilter(
                    'candidates',
                    filters.NormalizedFilter(
                        'driver_license', 'test_driver_license',
                    ),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                True,
                exact=api.TextExactFieldsTaxi(
                    license_plates='test_license_plates',
                ),
            ),
            [
                filters.AnyOfArrayFilter(
                    'candidates',
                    filters.NormalizedFilter(
                        'car_number', 'test_license_plates',
                    ),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                True,
                regex=api.TextRegexFieldsTaxi(driver_name='test_driver_name'),
            ),
            [
                filters.AnyOfArrayFilter(
                    'candidates',
                    filters.RegexFilter('driver_name', 'test_driver_name'),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                True,
                exact=api.TextExactFieldsTaxi(
                    license_plates='test_license_plates',
                    driver_license='test_driver_license',
                    driver_phone='test_driver_phone',
                ),
                regex=api.TextRegexFieldsTaxi(driver_name='test_driver_name'),
            ),
            [
                filters.AnyOfArrayFilter(
                    'candidates',
                    filters.ExactMatchFilter(
                        'driver_phone', 'test_driver_phone',
                    ),
                ),
                filters.AnyOfArrayFilter(
                    'candidates',
                    filters.NormalizedFilter(
                        'driver_license', 'test_driver_license',
                    ),
                ),
                filters.AnyOfArrayFilter(
                    'candidates',
                    filters.NormalizedFilter(
                        'car_number', 'test_license_plates',
                    ),
                ),
                filters.AnyOfArrayFilter(
                    'candidates',
                    filters.RegexFilter('driver_name', 'test_driver_name'),
                ),
            ],
        ),
        (
            api.QueryBodyTaxi(
                False,
                exact=api.TextExactFieldsTaxi(
                    license_plates='test_license_plates',
                    driver_license='test_driver_license',
                    driver_phone='test_driver_phone',
                ),
                regex=api.TextRegexFieldsTaxi(driver_name='test_driver_name'),
            ),
            [
                filters.PerformerFilter(
                    filters.ExactMatchFilter(
                        'driver_phone', 'test_driver_phone',
                    ),
                ),
                filters.PerformerFilter(
                    filters.NormalizedFilter(
                        'driver_license', 'test_driver_license',
                    ),
                ),
                filters.PerformerFilter(
                    filters.NormalizedFilter(
                        'car_number', 'test_license_plates',
                    ),
                ),
                filters.PerformerFilter(
                    filters.RegexFilter('driver_name', 'test_driver_name'),
                ),
            ],
        ),
    ],
)
async def test_parse_candidates_taxi(query_body, expected):
    result = TAXI_PARSER._parse_candidates(query_body)
    _assert_lists_of_filters_equality(result, expected)


@pytest.mark.parametrize(
    'queries, expected',
    [
        (
            [api.QueryBodyTaxi(False)],
            period.Period(
                datetime.datetime(2019, 4, 1, 0, 0),
                datetime.datetime(2019, 10, 17, 12, 0),
            ),
        ),
        (
            [
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        created=api.Period(
                            datetime.datetime(2019, 6, 2, 10, 52),
                            datetime.datetime(2019, 7, 12, 23, 48),
                        ),
                    ),
                ),
            ],
            period.Period(
                datetime.datetime(2019, 6, 2, 10, 52),
                datetime.datetime(2019, 7, 12, 23, 48),
            ),
        ),
        (
            [
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        created=None,
                        request_due=api.Period(
                            datetime.datetime(2019, 6, 2, 10, 52),
                            datetime.datetime(2019, 7, 12, 23, 48),
                        ),
                    ),
                ),
            ],
            period.Period(
                datetime.datetime(2019, 5, 31, 10, 52),
                datetime.datetime(2019, 7, 14, 23, 48),
            ),
        ),
        (
            [
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        created=api.Period(
                            datetime.datetime(2019, 5, 5, 10, 52),
                            datetime.datetime(2019, 9, 29, 23, 48),
                        ),
                        request_due=api.Period(
                            datetime.datetime(2019, 5, 5, 10, 52),
                            datetime.datetime(2019, 9, 24, 23, 48),
                        ),
                    ),
                ),
            ],
            period.Period(
                datetime.datetime(2019, 5, 3, 10, 52),
                datetime.datetime(2019, 9, 29, 23, 48),
            ),
        ),
        (
            [
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        request_due=api.Period(
                            datetime.datetime(2019, 6, 25, 11, 52, 38),
                            datetime.datetime(2019, 9, 26, 7, 54, 17),
                        ),
                    ),
                ),
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        created=api.Period(
                            datetime.datetime(2019, 8, 10, 23, 59, 36),
                            datetime.datetime(2019, 10, 9, 3, 9, 33),
                        ),
                        request_due=api.Period(
                            datetime.datetime(2019, 8, 3, 8, 31, 35),
                            datetime.datetime(2019, 8, 27, 6, 43, 11),
                        ),
                    ),
                ),
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        request_due=api.Period(
                            datetime.datetime(2019, 8, 23, 23, 26, 10),
                            datetime.datetime(2019, 8, 24, 13, 16, 29),
                        ),
                    ),
                ),
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        created=api.Period(
                            datetime.datetime(2019, 6, 17, 20, 48, 12),
                            datetime.datetime(2019, 8, 12, 23, 16, 39),
                        ),
                    ),
                ),
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        created=api.Period(
                            datetime.datetime(2019, 7, 1, 2, 24, 57),
                            datetime.datetime(2019, 7, 30, 15, 17, 36),
                        ),
                        request_due=api.Period(
                            datetime.datetime(2019, 7, 10, 16, 2, 16),
                            datetime.datetime(2019, 7, 12, 0, 14, 4),
                        ),
                    ),
                ),
                api.QueryBodyTaxi(
                    False,
                    period=api.PeriodFieldsTaxi(
                        created=api.Period(
                            datetime.datetime(2019, 6, 14, 12, 44, 16),
                            datetime.datetime(2019, 9, 12, 5, 42, 0),
                        ),
                        request_due=api.Period(
                            datetime.datetime(2019, 6, 28, 13, 27, 56),
                            datetime.datetime(2019, 7, 10, 3, 10, 12),
                        ),
                    ),
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
async def test_calculate_interval_taxi(queries, expected):
    assert TAXI_PARSER._calculate_interval(queries) == expected


@pytest.mark.parametrize(
    'queries',
    [
        [
            api.QueryBodyTaxi(
                False,
                period=api.PeriodFieldsTaxi(
                    created=api.Period(
                        datetime.datetime(2019, 3, 17, 12, 0),
                        datetime.datetime(2019, 7, 12, 23, 48),
                    ),
                ),
            ),
        ],
        [
            api.QueryBodyTaxi(
                False,
                period=api.PeriodFieldsTaxi(
                    created=None,
                    request_due=api.Period(
                        datetime.datetime(2019, 4, 2, 23, 59),
                        datetime.datetime(2019, 4, 4, 0, 1),
                    ),
                ),
            ),
        ],
        [
            api.QueryBodyTaxi(
                False,
                period=api.PeriodFieldsTaxi(
                    created=api.Period(
                        datetime.datetime(2018, 4, 5, 10, 52),
                        datetime.datetime(2019, 9, 29, 23, 48),
                    ),
                    request_due=api.Period(
                        datetime.datetime(2019, 5, 5, 10, 52),
                        datetime.datetime(2019, 5, 24, 23, 48),
                    ),
                ),
            ),
        ],
    ],
)
@pytest.mark.now('2019-10-17T12:00:00Z')
async def test_calculate_interval_taxi_exception(queries):
    try:
        TAXI_PARSER._calculate_interval(queries)
    except common.DatesTooOldError:
        return
    assert False


@pytest.mark.parametrize(
    'period_fields, expected',
    [
        (api.PeriodFieldsTaxi(), []),
        (
            api.PeriodFieldsTaxi(created=_PERIOD_1),
            [filters.PeriodFilter('created', _PERIOD_1)],
        ),
        (
            api.PeriodFieldsTaxi(request_due=_PERIOD_1),
            [filters.PeriodFilter('request_due', _PERIOD_1)],
        ),
        (
            api.PeriodFieldsTaxi(created=_PERIOD_1, request_due=_PERIOD_2),
            [
                filters.PeriodFilter('created', _PERIOD_1),
                filters.PeriodFilter('request_due', _PERIOD_2),
            ],
        ),
    ],
)
async def test_taxi_parse_period_fields(period_fields, expected):
    query_body = api.QueryBodyTaxi(False, period=period_fields)
    result = TAXI_PARSER._parse_period_fields(query_body)
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
