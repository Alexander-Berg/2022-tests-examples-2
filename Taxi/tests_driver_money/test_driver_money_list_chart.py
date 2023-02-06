import pytest


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by,timezone,expected',
    [
        ('day', 'Asia/Yekaterinburg', 'expected_response_day.json'),
        ('week', 'Europe/Moscow', 'expected_response_week.json'),
        ('month', 'Europe/Moscow', 'expected_response_month.json'),
    ],
)
async def test_driver_money_list_chart(
        taxi_driver_money,
        billing_reports,
        load_json,
        group_by,
        timezone,
        expected,
        billing_subventions_x,
):
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    billing_reports.set_balances(load_json('billing_balances_response.json'))
    response = await taxi_driver_money.get(
        'v1/driver/money/list/chart',
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
    assert load_json(expected) == response.json()


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='taximeter_expenses',
    consumers=['driver_money/v1_driver_money_list_chart'],
    clauses=[],
    default_value={
        'show_commission_in_expenses': False,
        'show_gas_stations': False,
        'show_workshifts_in_expenses': False,
        'show_parks_services': True,
    },
)
@pytest.mark.parametrize(
    'group_by,timezone,subventions,expected',
    [
        (
            'week',
            'Europe/Moscow',
            'billing_subventions_response_driver_fix.json',
            'expected_response_week_billing_with_fix.json',
        ),
    ],
)
async def test_driver_money_list_chart_with_driver_fix(
        taxi_driver_money,
        load_json,
        group_by,
        timezone,
        subventions,
        expected,
        billing_reports,
        billing_subventions_x,
        parks_driver_profiles,
        fleet_rent_expenses,
):
    parks_driver_profiles.make_self_signed_response()
    fleet_rent_expenses.set_split_response(
        load_json('fleet_rent_expenses_response_split_1.json'),
        load_json('fleet_rent_expenses_response_split_2.json'),
    )

    billing_reports.set_balances(
        load_json('billing_balances_response_driver_fix.json'),
    )
    billing_subventions_x.set_virtual_by_driver_response(
        load_json(subventions),
    )
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    response = await taxi_driver_money.get(
        'v1/driver/money/list/chart',
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
    assert load_json(expected) == response.json()


@pytest.mark.config(
    DRIVER_MONEY_BALANCES_REQUEST={
        'accrued_at_count_to_split': 15,
        'agreements_without_filters_not_split': [
            'taxi/yandex_ride+0',
            'taxi/park_ride+0',
            'taxi/yandex_ride+0/mode/driver_fix',
            'taxi/yandex_ride+0/antifraud_check',
        ],
        'agreements_without_filters_split': [
            'taxi/yandex_ride+0',
            'taxi/park_ride+0',
            'taxi/yandex_ride+0/mode/driver_fix',
            'taxi/yandex_ride+0/antifraud_check',
        ],
    },
)
@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'group_by, timezone, expected',
    [('week', 'Europe/Moscow', 'expected_response_week.json')],
)
async def test_driver_money_list_chart_billing_split(
        taxi_driver_money,
        load_json,
        group_by,
        timezone,
        expected,
        billing_reports,
        billing_subventions_x,
):
    billing_reports.set_balances(load_json('billing_balances_response.json'))
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': timezone,
    }
    response = await taxi_driver_money.get(
        'v1/driver/money/list/chart',
        params=params,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-Request-Application': 'taximeter',
            'X-Request-Version-Type': '',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert billing_reports.balance_calls == 2
    assert response.status_code == 200
    assert load_json(expected) == response.json()


@pytest.mark.parametrize(
    'empty_billing,group_by,expected_response',
    [
        (False, 'day', 'expected_response_new_design_by_day.json'),
        (True, 'day', 'expected_response_new_design_empty.json'),
        (False, 'week', 'expected_response_new_design_by_week.json'),
        (False, 'month', 'expected_response_new_design_by_month.json'),
    ],
)
@pytest.mark.now('2019-06-02T12:00:00+0300')
async def test_driver_money_list_chart_new_design(
        taxi_driver_money,
        load_json,
        billing_reports,
        empty_billing,
        group_by,
        expected_response,
        billing_subventions_x,
):
    if not empty_billing:
        billing_reports.set_balances(
            load_json('billing_balances_response.json'),
        )
    params = {
        'db': 'park_id_0',
        'session': 'test_session',
        'group_by': group_by,
        'tz': 'Europe/Moscow',
    }
    response = await taxi_driver_money.get(
        '/driver/v1/driver-money/v2/list/chart',
        params=params,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-Request-Application': 'taximeter',
            'X-Request-Version-Type': '',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200

    response_json = response.json()
    assert load_json(expected_response) == response_json
