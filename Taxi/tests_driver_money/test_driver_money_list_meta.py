# pylint: disable=too-many-lines
import copy

import pytest

from tests_driver_money import common


HEADERS_DEFAULT = {
    'User-Agent': 'Taximeter 8.90 (228)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '8.90',
    'X-YaTaxi-Park-Id': 'park_id_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver',
}

HEADERS_UBER = {
    'User-Agent': 'Taximeter-uber 8.90 (228)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '8.90',
    'X-YaTaxi-Park-Id': 'park_id_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver',
}

HEADERS_SELFREG = {
    'User-Agent': 'Taximeter 8.90 (228)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '8.90',
}

DAY_DEFAULT_PARAMS = ('day', None, 'Asia/Yekaterinburg')
MPH_DAY_DEFAULT_PARAMS = (
    *DAY_DEFAULT_PARAMS,
    'billing_balances_request_day.json',
    'billing_balances_response_day.json',
)

WEEK_DEFAULT_PARAMS = ('week', '2019-05-13T00:00:00', '+03:00')
MPH_WEEK_DEFAULT_PARAMS = (
    *WEEK_DEFAULT_PARAMS,
    'billing_balances_request_week.json',
    'billing_balances_response_week.json',
)

MONTH_DEFAULT_PARAMS = ('month', '2019-06-01T00:00:00', 'Unknown timezone')
MPH_MONTH_DEFAULT_PARAMS = (
    *MONTH_DEFAULT_PARAMS,
    'billing_balances_request_month.json',
    'billing_balances_response_month.json',
)

DRIVER_MONEY_MPH_ACCESS_BY_SCALE = {
    'DRIVER_MONEY_MPH_ACCESS_BY_SCALE': {
        'day': True,
        'week': False,
        'month': True,
        'enable': True,
    },
}

DRIVER_MONEY_MPH_ZONES_WITHOUT_HINT = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'is_config': False,
    'name': 'driver_mph_zones',
    'consumers': ['driver_money/v1_driver_money_list_meta'],
    'clauses': [],
    'default_value': {
        'park_ids': [],
        'cities': [{'Москва': 400.0}],
        'countries': [{'rus': 100.0}],
        'default_mph_hint_enabled': False,
    },
}

DRIVER_MONEY_MPH_ZONES_WITH_HINT = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'is_config': False,
    'name': 'driver_mph_zones',
    'consumers': ['driver_money/v1_driver_money_list_meta'],
    'clauses': [],
    'default_value': {
        'park_ids': [],
        'cities': [{'Москва': 400.0}],
        'countries': [{'rus': 100.0}],
        'default_mph_hint_enabled': True,
    },
}

DRIVER_MONEY_TAXIMETER_EXPENSES_ALL = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'is_config': False,
    'name': 'taximeter_expenses',
    'consumers': ['driver_money/v1_driver_money_list_meta'],
    'clauses': [],
    'default_value': {
        'show_commission_in_expenses': True,
        'show_gas_stations': True,
        'show_workshifts_in_expenses': True,
        'show_parks_services': True,
    },
}

DRIVER_MONEY_TAXIMETER_EXPENSES_PS = copy.deepcopy(
    DRIVER_MONEY_TAXIMETER_EXPENSES_ALL,
)
DRIVER_MONEY_TAXIMETER_EXPENSES_PS['default_value'] = {
    'show_commission_in_expenses': False,
    'show_gas_stations': False,
    'show_workshifts_in_expenses': False,
    'show_parks_services': True,
}

DRIVER_MONEY_TAXIMETER_EXPENSES_GAS_WS = copy.deepcopy(
    DRIVER_MONEY_TAXIMETER_EXPENSES_ALL,
)
DRIVER_MONEY_TAXIMETER_EXPENSES_GAS_WS['default_value'] = {
    'show_commission_in_expenses': False,
    'show_gas_stations': True,
    'show_workshifts_in_expenses': True,
    'show_parks_services': False,
}

DRIVER_MONEY_TAXIMETER_EXPENSES_COMMISSION_WS = copy.deepcopy(
    DRIVER_MONEY_TAXIMETER_EXPENSES_ALL,
)
DRIVER_MONEY_TAXIMETER_EXPENSES_COMMISSION_WS['default_value'] = {
    'show_commission_in_expenses': True,
    'show_gas_stations': False,
    'show_workshifts_in_expenses': True,
    'show_parks_services': False,
}

DRIVER_MONEY_TAXIMETER_EXPENSES_NOTHING = copy.deepcopy(
    DRIVER_MONEY_TAXIMETER_EXPENSES_ALL,
)
DRIVER_MONEY_TAXIMETER_EXPENSES_NOTHING['default_value'] = {
    'show_commission_in_expenses': False,
    'show_gas_stations': False,
    'show_workshifts_in_expenses': False,
    'show_parks_services': False,
}

# @pytest.mark.now('2019-06-02T12:00:00+0300')
# @pytest.mark.parametrize(
#     'params,headers,balances_response,expected',
#     [
#         (
#                 *WEEK_DEFAULT_PARAMS,
#                 'expected_response_week_uber.json',
#         ),
#     ],
# )
# async def test_v1(
#         params,
#         headers,
#         balances_response,
#         expected,
#         billing_reports,
#         load_json,
# ):
#     billing_reports.set_balances(
#         load_json('billing_balances_response_week.json'),
#     )


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by,before,timezone,expected',
    [(*WEEK_DEFAULT_PARAMS, 'expected_response_week_uber.json')],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='uberdriver_original_money_info',
    consumers=['driver_money/v1_driver_money_list_meta'],
    clauses=[],
    default_value=True,
)
async def test_uber(
        taxi_driver_money,
        billing_reports,
        load_json,
        group_by,
        before,
        timezone,
        expected,
        mockserver,
        billing_subventions_x,
):
    billing_reports.set_balances(
        load_json('billing_balances_response_week.json'),
    )

    @mockserver.json_handler('/fleet-synchronizer/v1/mapping/driver')
    def _mapping_driver_handler(request):
        return {
            'mapping': [
                {
                    'park_id': 'park_orig',
                    'driver_id': 'driver_orig',
                    'app_family': 'taximeter',
                },
                {
                    'park_id': 'park_id_0',
                    'driver_id': 'driver',
                    'app_family': 'uberdriver',
                },
            ],
        }

    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        'v1/driver/money/list/meta', params=params, headers=HEADERS_UBER,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected)


@pytest.mark.now('2019-06-03T12:00:00+0300')
async def test_az_override(
        taxi_driver_money,
        billing_reports,
        load_json,
        mockserver,
        billing_subventions_x,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        return {
            'driver_profiles': [
                {
                    'accounts': [
                        {
                            'balance': '2444216.6162',
                            'currency': 'AZN',
                            'id': 'driver',
                        },
                    ],
                    'driver_profile': {
                        'id': 'driver',
                        'created_date': '2020-05-05T21:00:00.1241Z',
                        'first_name': 'Ivan',
                        'last_name': 'Ivanov',
                        'payment_service_id': '123456',
                    },
                },
            ],
            'offset': 0,
            'parks': [
                {'id': 'park_id_0', 'city': 'Баку', 'country_id': 'aze'},
            ],
            'total': 1,
            'limit': 1,
        }

    response = await taxi_driver_money.get(
        'v1/driver/money/list/meta',
        params={
            'db': 'park_id_0',
            'session': 'test_session',
            'group_by': 'day',
            'tz': 'Europe/Moscow',
        },
        headers={
            'User-Agent': 'Taximeter-az 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_az_override.json')


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by,before,timezone,balances_request,balances,subventions,expected',
    [
        (
            *WEEK_DEFAULT_PARAMS,
            'billing_balances_request_week.json',
            'billing_balances_response_week_driver_fix.json',
            'billing_subventions_response_driver_fix.json',
            'expected_response_week_billing_with_fix.json',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            'billing_balances_request_week.json',
            'billing_balances_response_week_driver_fix.json',
            'billing_subventions_response_driver_fix.json',
            'expected_response_week_billing_with_fix_split_cash.json',
            marks=pytest.mark.experiments3(
                filename='experiments3_split_cash.json',
            ),
            id='split cash in header when driver_fix',
        ),
    ],
)
async def test_with_driver_fix(
        taxi_driver_money,
        load_json,
        group_by,
        before,
        timezone,
        balances_request,
        balances,
        subventions,
        expected,
        billing_reports,
        billing_subventions_x,
):
    billing_reports.set_balances(load_json(balances))
    billing_subventions_x.set_virtual_by_driver_response(
        load_json(subventions),
    )
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        'v1/driver/money/list/meta', params=params, headers=HEADERS_DEFAULT,
    )
    assert response.status_code == 200
    assert common.are_equal_json(
        load_json(balances_request), billing_reports.get_request(),
    )
    assert response.json() == load_json(expected)


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by, before, timezone, headers, '
    'balances_request, balances, partner_payment_source_flag, '
    'rent_other_currency_flag, hide_ya_commission, expected',
    [
        (
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            False,
            False,
            False,
            'expected_response_week_billing_no_fix.json',
        ),
        (
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week_zero_diff_vat.json',
            False,
            False,
            False,
            'expected_response_week_billing_zero_diff_vat_no_fix.json',
        ),
        (
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week_no_vat.json',
            False,
            False,
            False,
            'expected_response_week_billing_no_vat_no_fix.json',
        ),
        (
            *WEEK_DEFAULT_PARAMS,
            HEADERS_UBER,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            False,
            False,
            False,
            'expected_response_week_uber_noexp.json',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            False,
            False,
            False,
            'expected_response_week_expenses_nothing.json',
            marks=pytest.mark.experiments3(
                **DRIVER_MONEY_TAXIMETER_EXPENSES_NOTHING,
            ),
            id='expenses: exp3 - nothing',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            True,
            False,
            False,
            'expected_response_week_expenses_all.json',
            marks=pytest.mark.experiments3(
                **DRIVER_MONEY_TAXIMETER_EXPENSES_ALL,
            ),
            id='expenses: exp3 - with all',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            True,
            False,
            False,
            'expected_response_week_expenses_ps.json',
            marks=pytest.mark.experiments3(
                **DRIVER_MONEY_TAXIMETER_EXPENSES_PS,
            ),
            id='expenses: exp3 - no gas, no commission, no ws, with ps',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            True,
            True,
            False,
            'expected_response_week_expenses_az_ps.json',
            marks=pytest.mark.experiments3(
                **DRIVER_MONEY_TAXIMETER_EXPENSES_PS,
            ),
            id='expenses: exp3 - no gas, no commission, no ws, with ps, '
            'but other currency',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            False,
            False,
            False,
            'expected_response_week_expenses_nothing.json',
            marks=pytest.mark.experiments3(
                **DRIVER_MONEY_TAXIMETER_EXPENSES_PS,
            ),
            id='expenses: exp3 - no gas, no commission, no ws, with ps, '
            'but no partner source',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            False,
            False,
            False,
            'expected_response_week_expenses_com_ws.json',
            marks=pytest.mark.experiments3(
                **DRIVER_MONEY_TAXIMETER_EXPENSES_COMMISSION_WS,
            ),
            id='expenses: exp3 - no gas, with commission, with ws, no ps',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            False,
            False,
            False,
            'expected_response_week_expenses_gas_ws.json',
            marks=pytest.mark.experiments3(
                **DRIVER_MONEY_TAXIMETER_EXPENSES_GAS_WS,
            ),
            id='expenses: exp3 - with gas, no commission, with ws, no ps',
        ),
        pytest.param(
            *DAY_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_day.json',
            'billing_balances_response_day.json',
            False,
            False,
            False,
            'expected_response_day_split_cash.json',
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_split_cash.json',
                ),
            ],
        ),
        (
            *DAY_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_day.json',
            'billing_balances_response_day.json',
            False,
            False,
            True,
            'expected_response_day_no_ya_commission.json',
        ),
        pytest.param(
            *MONTH_DEFAULT_PARAMS,
            HEADERS_DEFAULT,
            'billing_balances_request_month.json',
            'billing_balances_response_month.json',
            False,
            False,
            False,
            'expected_response_month_balance_oebs.json',
            id='test oebs balance',
            marks=pytest.mark.experiments3(
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='balance_oebs',
                consumers=['driver_money/v1_driver_money_list_meta'],
                clauses=[
                    {
                        'value': {'enabled': True},
                        'is_signal': False,
                        'predicate': {
                            'init': {
                                'predicates': [
                                    {
                                        'init': {
                                            'set': ['driver'],
                                            'arg_name': 'driver_id',
                                            'set_elem_type': 'string',
                                        },
                                        'type': 'in_set',
                                    },
                                    {
                                        'init': {
                                            'value': (
                                                '2020-01-01T12:00:00.000Z'
                                            ),
                                            'arg_name': 'created_date',
                                            'arg_type': 'datetime',
                                        },
                                        'type': 'gte',
                                    },
                                ],
                            },
                            'type': 'all_of',
                        },
                        'is_paired_signal': False,
                    },
                ],
            ),
        ),
    ],
)
async def test_no_driver_fix(
        taxi_driver_money,
        load_json,
        group_by,
        before,
        timezone,
        balances_request,
        balances,
        partner_payment_source_flag,
        rent_other_currency_flag,
        expected,
        billing_reports,
        fleet_rent_expenses,
        parks_driver_profiles,
        mockserver,
        headers,
        hide_ya_commission,
        taxi_config,
        billing_subventions_x,
):
    if hide_ya_commission:
        taxi_config.set_values(
            dict(DRIVER_MONEY_COUNTRIES_TO_HIDE_COMMISSION=['rus']),
        )
    if partner_payment_source_flag:
        parks_driver_profiles.make_self_signed_response()

    if rent_other_currency_flag:
        fleet_rent_expenses.set_az_currency_response()

    billing_reports.set_balances(load_json(balances))
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        'v1/driver/money/list/meta', params=params, headers=headers,
    )
    assert response.status_code == 200
    assert common.are_equal_json(
        load_json(balances_request), billing_reports.get_request(),
    )
    assert response.json() == load_json(expected)


MPH_NO_SCALE_NO_ZONES_PARAMS = (
    pytest.param(
        *MPH_DAY_DEFAULT_PARAMS,
        'expected_response_day_billing_mph.json',
        id='no scale and no zone configs - day',
    ),
    pytest.param(
        *MPH_WEEK_DEFAULT_PARAMS,
        'expected_response_week_mph.json',
        id='no scale and no zones configs - week',
    ),
)

MPH_WITH_SCALE_NO_ZONES_PARAMS = (
    pytest.param(
        *MPH_DAY_DEFAULT_PARAMS,
        'expected_response_day_billing_mph.json',
        id='with scale and no zones configs - day',
        marks=pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
    ),
    pytest.param(
        *MPH_DAY_DEFAULT_PARAMS,
        'expected_response_day_billing_mph.json',
        id='cant override mph with split cash',
        marks=[
            pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
            pytest.mark.experiments3(filename='experiments3_split_cash.json'),
        ],
    ),
    pytest.param(
        *MPH_DAY_DEFAULT_PARAMS,
        'expected_response_day_split_cash.json',
        id='override mph with split cash',
        marks=[
            pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
            pytest.mark.experiments3(
                filename='experiments3_split_cash_override.json',
            ),
        ],
    ),
    pytest.param(
        *MPH_WEEK_DEFAULT_PARAMS,
        'expected_response_week_billing_no_fix.json',
        id='with scale and no zones configs - week',
        marks=pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
    ),
    pytest.param(
        *MPH_MONTH_DEFAULT_PARAMS,
        'expected_response_month_billing_mph.json',
        id='with scale and no zones configs - month',
        marks=pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
    ),
)

MPH_WITH_SCALE_WITH_ZONES_PARAMS = (
    pytest.param(
        *MPH_DAY_DEFAULT_PARAMS,
        'expected_response_day.json',
        id='with scale and zone configs - day',
        marks=[
            pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
            pytest.mark.experiments3(**DRIVER_MONEY_MPH_ZONES_WITHOUT_HINT),
        ],
    ),
    pytest.param(
        *MPH_WEEK_DEFAULT_PARAMS,
        'expected_response_week_billing_no_fix.json',
        id='with scale and zone configs - week',
        marks=[
            pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
            pytest.mark.experiments3(**DRIVER_MONEY_MPH_ZONES_WITHOUT_HINT),
        ],
    ),
    pytest.param(
        *MPH_MONTH_DEFAULT_PARAMS,
        'expected_response_month_billing_mph.json',
        id='with scale and zone configs - month',
        marks=[
            pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
            pytest.mark.experiments3(**DRIVER_MONEY_MPH_ZONES_WITHOUT_HINT),
        ],
    ),
)

MPH_DEFAULT_TITLE_PARAMS = (
    pytest.param(
        *MPH_DAY_DEFAULT_PARAMS,
        'expected_response_day_billing_mph_default_title.json',
        id='default title - day',
        marks=[
            pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
            pytest.mark.experiments3(**DRIVER_MONEY_MPH_ZONES_WITH_HINT),
        ],
    ),
    pytest.param(
        *MPH_WEEK_DEFAULT_PARAMS,
        'expected_response_week_billing_mph_default_title.json',
        id='default title - week',
        marks=[
            pytest.mark.config(**DRIVER_MONEY_MPH_ACCESS_BY_SCALE),
            pytest.mark.experiments3(**DRIVER_MONEY_MPH_ZONES_WITH_HINT),
        ],
    ),
)


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='driver_mph',
    consumers=['driver_money/v1_driver_money_list_meta'],
    clauses=[],
    default_value={},
)
@pytest.mark.parametrize(
    [
        'group_by',
        'before',
        'timezone',
        'balances_request',
        'balances',
        'expected',
    ],
    (
        *MPH_NO_SCALE_NO_ZONES_PARAMS,
        *MPH_WITH_SCALE_NO_ZONES_PARAMS,
        *MPH_WITH_SCALE_WITH_ZONES_PARAMS,
        *MPH_DEFAULT_TITLE_PARAMS,
    ),
)
async def test_mph(
        taxi_driver_money,
        load_json,
        group_by,
        before,
        timezone,
        balances_request,
        balances,
        expected,
        billing_reports,
        mockserver,
        billing_subventions_x,
):
    @mockserver.json_handler(
        '/driver-supply-hours/v1/parks/drivers-profiles/supply/retrieve',
    )
    def _sh_handler(request):
        return {
            'driver_profiles': [
                {
                    'driver_profile_id': '123',
                    'supply': [
                        {
                            'from': '2019-05-13T00:00:00Z',
                            'to': '2019-06-13T00:00:00Z',
                            'seconds': 7200,
                        },
                    ],
                },
            ],
        }

    billing_reports.set_balances(load_json(balances))
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        'v1/driver/money/list/meta', params=params, headers=HEADERS_DEFAULT,
    )
    assert response.status_code == 200
    assert common.are_equal_json(
        load_json(balances_request), billing_reports.get_request(),
    )
    assert response.json() == load_json(expected)


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by,before,expected',
    [
        ('day', None, 'expected_response_day_selfreg.json'),
        ('week', None, 'expected_response_week_selfreg.json'),
        ('month', None, 'expected_response_month_selfreg.json'),
        (
            'month',
            '2019-05-13T00:00:00',
            'expected_response_month_selfreg_with_before.json',
        ),
    ],
)
async def test_selfreg(
        taxi_driver_money,
        load_json,
        group_by,
        before,
        expected,
        billing_reports,
):
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': '+03:00',
        'selfreg_token': 'some_token',
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        'v1/driver/money/list/meta', params=params, headers=HEADERS_SELFREG,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected)


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by,before,timezone,balances,subventions,status_code,'
    'is_response_with_msg',
    [
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            None,
            'billing_subventions_response_driver_fix.json',
            429,
            False,
            id='429 from billing-reports',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            None,
            'billing_subventions_response_driver_fix.json',
            429,
            True,
            id='429 from billing-reports with message',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            'billing_balances_response_week.json',
            None,
            429,
            False,
            id='429 from billing-subventions',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            'billing_balances_response_week.json',
            None,
            429,
            True,
            id='429 from billing-subventions with message',
        ),
        pytest.param(
            *WEEK_DEFAULT_PARAMS,
            None,
            None,
            429,
            False,
            id='429 from billing-reports and billing-subventions',
        ),
    ],
)
async def test_billing_429(
        taxi_driver_money,
        load_json,
        group_by,
        before,
        timezone,
        balances,
        subventions,
        status_code,
        billing_reports,
        billing_subventions_x,
        is_response_with_msg,
):
    if balances is not None:
        billing_reports.set_balances(load_json(balances))
    else:
        billing_reports.set_balances_select_429(is_response_with_msg)

    if subventions is not None:
        billing_subventions_x.set_virtual_by_driver_response(
            load_json(subventions),
        )
    else:
        billing_subventions_x.set_virtual_by_driver_429(is_response_with_msg)

    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        'v1/driver/money/list/meta', params=params, headers=HEADERS_DEFAULT,
    )
    assert response.status_code == status_code


@pytest.mark.now('2019-06-02T12:00:00+0300')
async def test_without_total(
        taxi_driver_money, billing_reports, load_json, billing_subventions_x,
):
    billing_reports.set_balances(
        load_json('billing_balances_response_day.json'),
    )
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': 'day',
        'tz': 'Asia/Yekaterinburg',
    }
    response = await taxi_driver_money.get(
        'v1/driver/money/list/meta',
        params=params,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_day_without_total.json',
    )


@pytest.mark.parametrize(
    'group_by, before, timezone, '
    'balances_request, balances, partner_payment_source_flag, '
    'rent_other_currency_flag, hide_ya_commission, expected',
    [
        (
            *WEEK_DEFAULT_PARAMS,
            'billing_balances_request_week.json',
            'billing_balances_response_week.json',
            False,
            False,
            False,
            'expected_response_new_design_week.json',
        ),
        (
            *DAY_DEFAULT_PARAMS,
            'billing_balances_request_day.json',
            'billing_balances_response_day.json',
            False,
            False,
            False,
            'expected_response_new_design_day.json',
        ),
        pytest.param(
            *DAY_DEFAULT_PARAMS,
            'billing_balances_request_day.json',
            'billing_balances_response_day.json',
            False,
            False,
            True,
            'expected_response_new_design_day_ya_comission_hidden.json',
            id='hide_ya_comission',
        ),
    ],
)
@pytest.mark.now('2019-06-02T12:00:00+0300')
async def test_v2(
        taxi_driver_money,
        load_json,
        group_by,
        before,
        timezone,
        balances_request,
        balances,
        partner_payment_source_flag,
        rent_other_currency_flag,
        expected,
        billing_reports,
        fleet_rent_expenses,
        parks_driver_profiles,
        mockserver,
        hide_ya_commission,
        taxi_config,
        billing_subventions_x,
):
    if hide_ya_commission:
        taxi_config.set_values(
            dict(DRIVER_MONEY_COUNTRIES_TO_HIDE_COMMISSION=['rus']),
        )
    if partner_payment_source_flag:
        parks_driver_profiles.make_self_signed_response()

    if rent_other_currency_flag:
        fleet_rent_expenses.set_az_currency_response()

    billing_reports.set_balances(load_json(balances))
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        '/driver/v1/driver-money/v2/list/meta',
        params=params,
        headers=HEADERS_DEFAULT,
    )
    assert response.status_code == 200
    assert common.are_equal_json(
        load_json(balances_request), billing_reports.get_request(),
    )

    assert response.json() == load_json(expected)


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by,expected',
    [
        ('day', 'expected_response_new_design_day_selfreg.json'),
        ('week', 'expected_response_new_design_week_selfreg.json'),
        ('month', 'expected_response_new_design_month_selfreg.json'),
    ],
)
async def test_v2_selfreg(
        taxi_driver_money, load_json, group_by, expected, billing_reports,
):
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': '+03:00',
        'selfreg_token': 'some_token',
    }
    response = await taxi_driver_money.get(
        '/driver/v1/driver-money/v2/list/meta',
        params=params,
        headers=HEADERS_SELFREG,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected)


@pytest.mark.parametrize(
    'group_by, before, timezone, '
    'balances_request, balances, subventions, expected',
    [
        (
            *WEEK_DEFAULT_PARAMS,
            'billing_balances_request_week.json',
            'billing_balances_response_week_driver_fix.json',
            'billing_subventions_response_driver_fix.json',
            'expected_response_new_design_week_driver_fix.json',
        ),
        (
            *WEEK_DEFAULT_PARAMS,
            'billing_balances_request_week.json',
            'billing_balances_response_week_driver_fix_empty.json',
            'billing_subventions_response_driver_fix.json',
            'expected_response_new_design_week_driver_fix_emtpy.json',
        ),
    ],
)
@pytest.mark.now('2019-06-02T12:00:00+0300')
async def test_v2_with_driver_fix(
        taxi_driver_money,
        load_json,
        group_by,
        before,
        timezone,
        balances_request,
        balances,
        expected,
        billing_reports,
        subventions,
        billing_subventions_x,
):
    billing_subventions_x.set_virtual_by_driver_response(
        load_json(subventions),
    )
    billing_reports.set_balances(load_json(balances))
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    if before:
        params['before'] = before
    response = await taxi_driver_money.get(
        '/driver/v1/driver-money/v2/list/meta',
        params=params,
        headers=HEADERS_DEFAULT,
    )
    assert response.status_code == 200
    assert common.are_equal_json(
        load_json(balances_request), billing_reports.get_request(),
    )

    assert response.json() == load_json(expected)
