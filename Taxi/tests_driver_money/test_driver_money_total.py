import pytest


@pytest.mark.now('2019-06-02T12:00:00+0300')
async def test_driver_money_total_empty(
        taxi_driver_money, billing_reports, load_json, billing_subventions_x,
):
    billing_reports.set_balances(
        load_json('billing_balances_response_empty.json'),
    )
    response = await taxi_driver_money.get(
        'v1/driver/money/total',
        params={
            'db': 'park_id_0',
            'session': 'test_session',
            'tz': 'Europe/Moscow',
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert {
        'complete_order_count_formatted': '0 заказов',
        'total_income_formatted': '0,00 ₽',
    } == response.json()


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='taximeter_expenses',
    consumers=['driver_money/v1_driver_money_total'],
    clauses=[],
    default_value={
        'show_commission_in_expenses': False,
        'show_gas_stations': False,
        'show_workshifts_in_expenses': False,
        'show_parks_services': True,
    },
)
async def test_driver_money_total_with_driver_fix(
        taxi_driver_money,
        billing_reports,
        billing_subventions_x,
        load_json,
        parks_driver_profiles,
        fleet_rent_expenses,
):
    parks_driver_profiles.make_self_signed_response()
    billing_reports.set_balances(
        load_json('billing_balances_response_driver_fix.json'),
    )
    billing_subventions_x.set_virtual_by_driver_response(
        load_json('billing_subventions_response_driver_fix.json'),
    )
    response = await taxi_driver_money.get(
        'v1/driver/money/total',
        params={
            'db': 'park_id_0',
            'session': 'test_session',
            'tz': 'Europe/Moscow',
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert {
        'complete_order_count_formatted': '2 заказа',
        'total_income_formatted': '737,75 ₽',
    } == response.json()


@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_driver_money_total_no_driver_fix(
        taxi_driver_money, billing_reports, load_json, billing_subventions_x,
):
    billing_reports.set_balances(load_json('billing_balances_response.json'))
    response = await taxi_driver_money.get(
        'v1/driver/money/total',
        params={
            'db': 'park_id_0',
            'session': 'test_session',
            'tz': 'Europe/Moscow',
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert {
        'complete_order_count_formatted': '4 заказа',
        'total_income_formatted': '580,00 ₽',
    } == response.json()


@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_selfreg_total(taxi_driver_money, load_json, mockserver):
    response = await taxi_driver_money.get(
        'v1/driver/money/total',
        params={
            'db': 'park_id_0',
            'session': 'sdddd',
            'tz': 'Europe/Moscow',
            'selfreg_token': 'some_token',
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'X-Request-Application-Version': '8.90',
        },
    )
    assert response.status_code == 200
    assert {
        'complete_order_count_formatted': '0 заказов',
        'total_income_formatted': '0,00 ₽',
    } == response.json()
