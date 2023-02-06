# pylint: disable=too-many-lines

import pytest

SETCAR_CREATE_URL = '/v2/setcar'
PARAMS = {
    'driver': {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '4d605a2849d747079b5d8c7012830419',
    },
    'order_id': 'test_order_id',
}

ORIGIN_MULTIPLYS = {
    'minimal_price': 1.4,
    'price_per_km': 1.4,
    'price_per_minute': 1.4,
    'surge_text': '×1.40',
}

NEW_MULTIPLYS = {
    'minimal_price': 100.4,
    'price_per_km': 100.4,
    'price_per_minute': 100.4,
    'surge_text': '×100.40',
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
async def test_multiplys_replace_modes(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        params_wo_original_setcar,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert resp['multiplys'] == NEW_MULTIPLYS


@pytest.mark.parametrize(
    'pricing_meta,expected_multiplys',
    [
        ({}, None),
        ({}, None),
        (
            {'setcar.show_surcharge': 231},
            {'surcharge': 231, 'surge_text': '+231 ₽'},
        ),
        (
            {'setcar.show_surcharge': 231},
            {'surcharge': 231, 'surge_text': '+231 ₽'},
        ),
        (
            {'setcar.show_surge': 44.21},
            {
                'minimal_price': 44.21,
                'price_per_km': 44.21,
                'price_per_minute': 44.21,
                'surge_text': '×44.21',
            },
        ),
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
        'enable_cargo_multipoints': True,
    },
)
async def test_multiplys_builder(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        pricing_meta,
        expected_multiplys,
        params_wo_original_setcar,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['order']['pricing_data']['driver'][
        'meta'
    ] = pricing_meta

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    if expected_multiplys is None:
        assert 'multiplys' not in resp
    else:
        assert resp['multiplys'] == expected_multiplys
