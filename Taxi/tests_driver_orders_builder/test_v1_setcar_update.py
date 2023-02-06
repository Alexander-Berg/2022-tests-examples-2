import json

import pytest


HANDLER = '/v1/setcar/update'
DRIVER = 'driver1'
PARK = 'park1'

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


@pytest.mark.parametrize(
    'setcar_file,changes',
    [
        ('setcar.json', []),
        ('setcar.json', [{'change_type': 'pool'}]),
        (
            'setcar_hide_address.json',
            [{'change_type': 'pool'}, {'change_type': 'user_ready'}],
        ),
    ],
)
async def test_setcar_update_without_change(
        taxi_driver_orders_builder, load_json, setcar_file, changes,
):
    setcar_json = load_json(setcar_file)
    response = await taxi_driver_orders_builder.post(
        HANDLER,
        params={'driver_profile_id': DRIVER, 'park_id': PARK},
        json={'setcar': setcar_json, 'changes': changes},
    )
    assert response.status_code == 200, response.text
    response = response.json()
    del setcar_json['waiting_mode']
    if setcar_file == 'setcar_hide_address.json':
        del setcar_json['route_points']
        del setcar_json['address_to']
    assert response == setcar_json


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_setcar_update_patching': True},
)
@pytest.mark.parametrize(
    'setcar_fixed_price',
    [FIXED_PRICE_SETCAR_VALUE, FIXED_PRICE_SETCAR_HIDDEN_VALUE, None],
    ids=['simple-fixed-price', 'hidden-fixed-price', 'no-fixed-price'],
)
async def test_setcar_hide_base_price(
        taxi_driver_orders_builder, setcar_fixed_price, redis_store, load_json,
):
    setcar_json = load_json('setcar.json')

    setcar_json['base_price'] = {
        'user': BASE_PRICE_EXPECTED,
        'driver': BASE_PRICE_EXPECTED,
    }
    if setcar_fixed_price:
        setcar_json['fixed_price'] = setcar_fixed_price
        setcar_json['driver_fixed_price'] = setcar_fixed_price
    else:
        setcar_json.pop('fixed_price')
        setcar_json.pop('driver_fixed_price')

    response = await taxi_driver_orders_builder.post(
        HANDLER,
        params={'driver_profile_id': DRIVER, 'park_id': PARK},
        json={
            'setcar': setcar_json,
            'changes': [{'change_type': 'destinations'}],
        },
    )
    assert response.status_code == 200, response.text
    response = response.json()
    if setcar_fixed_price and setcar_fixed_price['show']:
        assert response['base_price'] == {
            'user': BASE_PRICE_EXPECTED,
            'driver': BASE_PRICE_EXPECTED,
        }
    else:
        assert 'base_price' not in response

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    if setcar_fixed_price:
        assert redis_dict['base_price']['user'] == BASE_PRICE_EXPECTED
        assert redis_dict['base_price']['driver'] == BASE_PRICE_EXPECTED
    else:
        assert 'base_price' not in redis_dict
