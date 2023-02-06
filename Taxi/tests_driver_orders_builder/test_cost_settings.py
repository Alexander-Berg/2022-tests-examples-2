import pytest

SETCAR_CREATE_URL = '/v2/setcar'
CREATE_PARAMS = {
    'driver': {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '4d605a2849d747079b5d8c7012830419',
    },
    'order_id': 'test_order_id',
}

SETCAR_UPDATE_URL = '/v1/setcar/update'
UPDATE_PARAMS = {'park_id': 'park1', 'driver_profile_id': 'driver1'}

SHOW_BOTH = {'show_driver_cost': True, 'show_passenger_cost': True}
SHOW_DRIVER = {'show_driver_cost': True, 'show_passenger_cost': False}
SHOW_PASSENGER = {'show_driver_cost': False, 'show_passenger_cost': True}
SHOW_NONE = {'show_driver_cost': False, 'show_passenger_cost': False}
FIXED_PRICE_SETCAR_VALUE = {
    'max_distance': 501.0,
    'price': 353.0,
    'show': True,
}
FIXED_PRICE_SETCAR_HIDDEN_VALUE = {
    'max_distance': 501.0,
    'price': 353.0,
    'show': False,
}
BASE_PRICE_EXPECTED = {
    'boarding': 49,
    'destination_waiting': 0,
    'distance': 2514.358041402936,
    'requirements': 0,
    'time': 89.63333333333333,
    'transit_waiting': 0,
    'waiting': 0,
}

PRICING_DATA_PROJECTION = {
    'order.pricing_data.geoarea_ids',
    'order.pricing_data.currency',
    'order.pricing_data.is_fallback',
    'order.pricing_data.driver.base_price',
    'order.pricing_data.driver.meta',
    'order.pricing_data.driver.data.country_code2',
    'order.pricing_data.driver.category_prices_id',
    'order.pricing_data.user.base_price',
    'order.pricing_data.user.meta',
    'order.pricing_data.user.data.country_code2',
    'order.pricing_data.user.category_prices_id',
    'order.pricing_data.driver.trip_information.distance',
}


@pytest.mark.parametrize(
    [
        'setcar_fixed_price',
        'fixed_price_in_order_proc',
        'expected_base_price',
        'expected_redis_base_price',
    ],
    [
        (None, False, None, None),
        (None, True, None, BASE_PRICE_EXPECTED),
        (FIXED_PRICE_SETCAR_VALUE, False, None, None),
        (
            FIXED_PRICE_SETCAR_VALUE,
            True,
            BASE_PRICE_EXPECTED,
            BASE_PRICE_EXPECTED,
        ),
        (FIXED_PRICE_SETCAR_HIDDEN_VALUE, True, None, BASE_PRICE_EXPECTED),
    ],
    ids=[
        'no_base_price_no_fixed_price',
        'only_orderproc_base_price',
        'fixed_price_without_order_proc_base_price',
        'fixed_price_with_base_price',
        'hidden_prices',
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_driver_mode_request': True,
        'enable_setcar_update_patching': True,
    },
)
@pytest.mark.parametrize(
    'driver_mode,country_id,payment_type,expected_json',
    [
        ('orders', 'rus', 'card', SHOW_DRIVER),
        ('orders', 'isr', 'card', SHOW_BOTH),
        ('driver_fix', 'rus', 'cash', SHOW_PASSENGER),
        ('driver_fix', 'rus', 'card', SHOW_NONE),
    ],
)
async def test_cost_settings_base_price(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        parks,
        driver_ui_profile,
        redis_store,
        setcar_fixed_price,
        fixed_price_in_order_proc,
        expected_base_price,
        expected_redis_base_price,
        driver_mode,
        country_id,
        payment_type,
        expected_json,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    if fixed_price_in_order_proc:
        order_proc.order_proc['fields']['order']['pricing_data'][
            'user'
        ].update({'base_price': BASE_PRICE_EXPECTED})
        order_proc.order_proc['fields']['order']['pricing_data'][
            'driver'
        ].update({'base_price': BASE_PRICE_EXPECTED})
    order_proc.order_proc['fields']['payment_tech']['type'] = payment_type

    def order_proc_assert(request_fields):
        assert all(
            field in request_fields for field in PRICING_DATA_PROJECTION
        )

    order_proc.set_fields_request_assert = order_proc_assert

    parks.set_response(country_id)
    driver_ui_profile.set_response(driver_mode)

    setcar_json = load_json('setcar.json')
    if setcar_fixed_price is None:
        setcar_json.pop('fixed_price')
        setcar_json.pop('driver_fixed_price')
    else:
        setcar_json['fixed_price'] = setcar_fixed_price
        setcar_json['driver_fixed_price'] = setcar_fixed_price

    request = CREATE_PARAMS
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )

    assert response.status_code == 200
    response_json = response.json()['setcar_push']
    if expected_base_price is not None:
        assert response_json['base_price'] == {
            'user': expected_base_price,
            'driver': expected_base_price,
        }
    else:
        assert 'base_price' not in response_json

    setcar_json['base_price'] = {
        'user': BASE_PRICE_EXPECTED,
        'driver': BASE_PRICE_EXPECTED,
    }
    response = await taxi_driver_orders_builder.post(
        SETCAR_UPDATE_URL,
        params=UPDATE_PARAMS,
        json={
            'setcar': setcar_json,
            'changes': [{'change_type': 'destination'}],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    patched_expected_json = expected_json.copy()
    if setcar_fixed_price and setcar_fixed_price['show']:
        assert response_json['base_price'] == {
            'user': BASE_PRICE_EXPECTED,
            'driver': BASE_PRICE_EXPECTED,
        }
    elif not setcar_fixed_price:
        assert 'base_price' not in response_json
    else:
        patched_expected_json['show_driver_cost'] = False
        patched_expected_json['show_passenger_cost'] = False
        assert 'base_price' not in response_json
