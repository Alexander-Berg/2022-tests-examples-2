import pytest


@pytest.mark.parametrize(
    'pickup_distance,pickup_time,expected_title',
    [
        (None, 1, '10 м · 1 мин'),
        (100, 90, '100 м · 2 мин'),
        (2650, 750, '2,7 км · 13 мин'),
    ],
)
async def test_accept_toolbar_title(
        mockserver,
        load_json,
        taxi_driver_orders_builder,
        params_wo_original_setcar,
        pickup_distance,
        pickup_time,
        expected_title,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')
    if pickup_distance:
        order_proc.order_proc['fields']['candidates'][0][
            'dist'
        ] = pickup_distance
    else:
        del order_proc.order_proc['fields']['candidates'][0]['dist']
    order_proc.order_proc['fields']['candidates'][0]['time'] = pickup_time

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert 'title' in resp['ui']['accept_toolbar_params']
    assert resp['ui']['accept_toolbar_params']['title'] == expected_title


@pytest.mark.parametrize(
    'is_antisurge,is_paid_supply,is_hiding_paid_supply,'
    'is_hiding_arrival_type,dispatch_type,expected_subtitle',
    [
        (False, True, False, False, None, 'Платная подача'),
        (False, True, False, False, 'long', 'Платная подача'),
        (True, False, False, True, None, 'Заказ туда, где спрос выше'),
        (False, False, False, False, 'short', 'Ближняя подача'),
        (False, True, True, False, 'medium', 'Средняя подача'),
        (False, False, False, False, 'long', 'Дальняя подача'),
        (False, True, True, True, 'short', ''),
    ],
)
async def test_accept_toolbar_subtitle(
        experiments3,
        mockserver,
        load_json,
        taxi_driver_orders_builder,
        params_wo_original_setcar,
        is_antisurge,
        is_paid_supply,
        is_hiding_paid_supply,
        is_hiding_arrival_type,
        dispatch_type,
        expected_subtitle,
        order_proc,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_ui_parts_settings',
        consumers=['driver-orders-builder/ui-parts-settings-experiment'],
        clauses=[],
        merge_values_by=[
            {
                'tag': 'ui_experiments',
                'consumer': (
                    'driver-orders-builder/ui-parts-settings-experiment'
                ),
                'merge_method': 'dicts_recursive_merge',
            },
        ],
        default_value={
            'hide_ui_parts': {
                'is_hiding_paid_supply': is_hiding_paid_supply,
                'is_hiding_arrival_type': is_hiding_arrival_type,
            },
            'show_ui_parts': {},
        },
    )

    order_proc.set_file(load_json, 'order_core_response.json')
    if is_paid_supply:
        order_proc.order_proc['fields']['candidates'][0]['paid_supply'] = True
        order_proc.order_proc['fields']['order']['fixed_price'] = {}
        order_proc.order_proc['fields']['order']['fixed_price'][
            'paid_supply_price'
        ] = 59.0
    if is_antisurge:
        order_proc.order_proc['fields']['order']['calc'] = {
            'alternative_type': 'explicit_antisurge',
        }
    if dispatch_type:
        order_proc.order_proc['fields']['candidates'][0]['driver_metrics'][
            'dispatch'
        ] = dispatch_type

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert 'subtitle' in resp['ui']['accept_toolbar_params']
    assert resp['ui']['accept_toolbar_params']['subtitle'] == expected_subtitle


@pytest.mark.parametrize(
    'nearest_zone,is_source_airport,is_paid_supply,dispatch_type,'
    'expected_subtitle',
    [
        ('not_airport', False, False, 'short', 'Ближняя подача'),
        ('airport', False, True, None, 'Платная подача'),
        ('airport', True, True, 'long', 'Заказ из аэропорта'),
    ],
)
async def test_accept_toolbar_airport_subtitle(
        experiments3,
        mockserver,
        load_json,
        taxi_driver_orders_builder,
        params_wo_original_setcar,
        nearest_zone,
        is_source_airport,
        is_paid_supply,
        dispatch_type,
        expected_subtitle,
        order_proc,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_ui_parts_settings',
        consumers=['driver-orders-builder/ui-parts-settings-experiment'],
        clauses=[
            {
                'title': 'clause_0',
                'predicate': {
                    'init': {
                        'value': 'airport',
                        'arg_name': 'nearest_zone',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
                'value': {
                    'hide_ui_parts': {},
                    'show_ui_parts': {'is_showing_airport_subtitle': True},
                },
            },
        ],
        merge_values_by=[
            {
                'tag': 'ui_experiments',
                'consumer': (
                    'driver-orders-builder/ui-parts-settings-experiment'
                ),
                'merge_method': 'dicts_recursive_merge',
            },
        ],
        default_value={'hide_ui_parts': {}, 'show_ui_parts': {}},
    )

    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['order']['nz'] = nearest_zone
    if is_source_airport:
        order_proc.order_proc['fields']['order']['request']['source'][
            'object_type'
        ] = 'аэропорт'
    if is_paid_supply:
        order_proc.order_proc['fields']['candidates'][0]['paid_supply'] = True
        order_proc.order_proc['fields']['order']['fixed_price'] = {}
        order_proc.order_proc['fields']['order']['fixed_price'][
            'paid_supply_price'
        ] = 59.0
    if dispatch_type:
        order_proc.order_proc['fields']['candidates'][0]['driver_metrics'][
            'dispatch'
        ] = dispatch_type

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert 'subtitle' in resp['ui']['accept_toolbar_params']
    assert resp['ui']['accept_toolbar_params']['subtitle'] == expected_subtitle
