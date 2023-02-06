# pylint: disable=too-many-lines

import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_cargo_multipoints': True},
)
@pytest.mark.parametrize(
    ('is_picker_order', 'custom_context', 'setcar_cargo_object'),
    [
        # Test field 'is_picker_order'
        (
            True,
            None,
            {
                'is_picker_order': True,
                'is_batch_order': False,
                'corp_client_id': 'corp_client_id_1',
            },
        ),
        # Test no extra fields
        (
            False,
            None,
            {'is_batch_order': False, 'corp_client_id': 'corp_client_id_1'},
        ),
        # Test 'place_id' in custom_context
        (
            False,
            {'place_id': 1234},
            {
                'is_batch_order': False,
                'external_place_id': 1234,
                'corp_client_id': 'corp_client_id_1',
            },
        ),
    ],
)
async def test_setcar_cargo_object(
        taxi_driver_orders_builder,
        load_json,
        order_proc,
        mock_cargo_setcar_data,
        setcar_create_params,
        is_picker_order: bool,
        custom_context: dict,
        setcar_cargo_object: dict,
):
    order_proc.set_file(load_json, 'order_core_response_courier.json')
    mock_cargo_setcar_data(
        is_picker_order=is_picker_order, custom_context=custom_context,
    )

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert resp['cargo'] == setcar_cargo_object


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_cargo_multipoints': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='some_picker_exp',
    consumers=['driver-orders-builder/setcar'],
    clauses=[
        {
            'title': 'matched',
            'predicate': {
                'init': {
                    'value': 'picker_order',
                    'arg_name': 'picker_order_type',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'matched': True},
        },
    ],
)
@pytest.mark.config(
    EXPERIMENTS3_TO_TAXIMETER_SETTINGS_MAP={
        'experiments': [
            {
                'name': 'some_picker_exp',
                'taximeter_settings_property': 'picker_property',
            },
        ],
        'configs': [],
    },
)
@pytest.mark.parametrize(
    ('is_picker_order', 'should_match'),
    (pytest.param(True, True), pytest.param(False, False)),
)
async def test_picker_kwarg_for_exp3(
        taxi_driver_orders_builder,
        order_proc,
        load_json,
        mock_cargo_setcar_data,
        setcar_create_params,
        is_picker_order,
        should_match,
):
    order_proc.set_file(load_json, 'order_core_response_courier.json')
    mock_cargo_setcar_data(is_picker_order=is_picker_order)

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    if should_match:
        assert resp['taximeter_settings']['picker_property'] == {
            'matched': True,
        }
    else:
        assert 'picker_property' not in resp['taximeter_settings']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'surge': {'id': 'surge_item'},
        'cargo': {'id': 'cargo_item'},
    },
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'modifications_items': '2.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_price_activity_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.parametrize(
    'json_file, tyler_exists',
    [
        ['order_core_response_cargo.json', True],
        ['order_core_response_courier.json', False],
    ],
)
async def test_cargo_modifications_items(
        taxi_driver_orders_builder,
        load_json,
        order_proc,
        mock_cargo_setcar_data,
        json_file,
        tyler_exists,
        params_wo_original_setcar,
):
    order_proc.set_file(load_json, json_file)

    mock_cargo_setcar_data(
        taximeter_tylers=[
            {
                'name': 'cargo',
                'title': 'cargo_title',
                'short_info': 'cargo_short_info',
            },
        ],
    )

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    if tyler_exists:
        assert resp['ui']['acceptance_items'][0] == {
            'id': 'iamtyler',
            'items': [
                {
                    'id': 'activity_item',
                    'title': 'Активность',
                    'short_info': '+5',
                },
                {
                    'id': 'cargo_item',
                    'title': 'cargo_title',
                    'short_info': 'cargo_short_info',
                },
            ],
        }
    else:
        for item in resp['ui']['acceptance_items']:
            assert 'iamtyler' not in item


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler', 'skip_build_this_tyler': True},
        'activity': {'id': 'activity_item'},
        'surge': {'id': 'surge_item'},
        'cargo': {'id': 'cargo_item'},
    },
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'modifications_items': '2.00'}},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_price_activity_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
async def test_cargo_skip_build_tyler_modifications_items(
        taxi_driver_orders_builder,
        load_json,
        order_proc,
        mock_cargo_setcar_data,
        params_wo_original_setcar,
):
    order_proc.set_file(load_json, 'order_core_response_cargo.json')

    mock_cargo_setcar_data(
        taximeter_tylers=[
            {
                'name': 'cargo',
                'title': 'cargo_title',
                'short_info': 'cargo_short_info',
            },
        ],
    )

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    for item in resp['ui']['acceptance_items']:
        assert 'iamtyler' not in item


async def test_cargo_truncated_current_route(
        taxi_driver_orders_builder,
        load_json,
        order_proc,
        mock_cargo_setcar_data,
        params_wo_original_setcar,
):
    order_proc.set_file(load_json, 'order_core_response_cargo.json')

    truncated_current_route = [
        {
            'type': 'source',
            'coordinates': [50.0, 60.0],
            'number_of_parcels': 2,
        },
        {
            'type': 'destination',
            'coordinates': [20.0, 10.0],
            'number_of_parcels': 4,
        },
    ]
    mock_cargo_setcar_data(truncated_current_route=truncated_current_route)

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    assert (
        response.json()['setcar']['cargo']['truncated_current_route']
        == truncated_current_route
    )


@pytest.mark.config(
    DRIVER_ORDERS_BUILDER_SETCAR_USE_CARGO_FIXEDPRICE_ENABLED=True,
)
async def test_setcar_cargo_fixed_price(
        taxi_driver_orders_builder,
        load_json,
        order_proc,
        mock_cargo_setcar_data,
        setcar_create_params,
):
    order_proc.set_file(load_json, 'order_core_response_courier.json')
    mock_cargo_setcar_data(
        pricing={
            'price': {'total': '130', 'client_total': '150'},
            'taxi_pricing_response_parts': {
                'taximeter_meta': {
                    'max_distance_from_b': 123.0,
                    'show_price_in_taximeter': True,
                },
            },
        },
    )

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert resp['fixed_price'] == {
        'max_distance': 123,
        'price': 150.0,
        'show': True,
    }
    assert resp['driver_fixed_price'] == {
        'max_distance': 123,
        'price': 130.0,
        'show': True,
    }
