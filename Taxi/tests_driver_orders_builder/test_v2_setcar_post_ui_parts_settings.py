import pytest


ACTIVITY = {
    'type': 'icon_detail',
    'reverse': True,
    'horizontal_divider_type': 'full',
    'accent_title': True,
    'title': 'Активность',
    'subtitle': '+5',
    'left_icon': {
        'icon_type': 'activity',
        'icon_size': 'large',
        'tint_color': '#00ca50',
    },
    'primary_text_color': '#00945e',
}

SURGE = {
    'type': 'icon_detail',
    'reverse': True,
    'horizontal_divider_type': 'full',
    'accent_title': True,
    'title': 'Цена',
    'subtitle': '+100 ₽',
    'left_icon': {
        'icon_type': 'surge',
        'icon_size': 'large',
        'tint_color': '#c81efa',
    },
    'primary_text_color': '#820abe',
}

PAID_SUPPLY = {
    'type': 'icon_detail',
    'reverse': True,
    'horizontal_divider_type': 'full',
    'accent_title': True,
    'title': 'Цена',
    'subtitle': '+59 ₽',
    'left_icon': {
        'icon_type': 'surge',
        'icon_size': 'large',
        'tint_color': '#0596fa',
    },
    'primary_text_color': '#0062c6',
}

ANTISURGE = {
    'type': 'icon_detail',
    'reverse': True,
    'horizontal_divider_type': 'full',
    'accent_title': True,
    'subtitle': 'Цена снижена',
    'left_icon': {
        'icon_type': 'anti_surge',
        'icon_size': 'large',
        'tint_color': '#5c5a57',
    },
    'primary_text_color': '#5c5a57',
}

PRICE_X1 = {
    'type': 'icon_detail',
    'reverse': True,
    'horizontal_divider_type': 'full',
    'accent_title': True,
    'title': 'Цена',
    'subtitle': '× 1',
    'left_icon': {
        'icon_type': 'surge',
        'icon_size': 'large',
        'tint_color': '#d8d8d8',
    },
    'primary_text_color': '#9e9b98',
}

ACTIVITY_TYLER = {
    'id': 'activity_item',
    'title': 'Активность',
    'short_info': '+5',
}

PRIORITY_TYLER = {
    'id': 'priority_item',
    'title': 'Приоритет',
    'short_info': '+3',
}

SURGE_TYLER = {
    'id': 'surge_item',
    'title': 'Высокая цена',
    'short_info': '+100 ₽',
}

PAID_SUPPLY_TYLER = {
    'id': 'paid_supply_item',
    'title': 'Цена',
    'short_info': '+59 ₽',
}

ANTISURGE_TYLER = {
    'id': 'antisurge_item',
    'title': 'Цена снижена',
    'short_info': '',
}

DEMAND_TYLER = {
    'id': 'demand_item',
    'title': 'Коэффициент спроса',
    'short_info': '×1.0',
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.parametrize(
    'surge_paid_supply_settings,is_surge,is_paid_supply,'
    'is_antisurge,left_item,right_item',
    [
        ('default', True, True, False, ACTIVITY, SURGE),
        ('default', False, False, False, ACTIVITY, PRICE_X1),
        ('surge_priority', True, True, False, ACTIVITY, SURGE),
        ('surge_priority', False, True, False, ACTIVITY, PAID_SUPPLY),
        ('paid_supply_priority', True, True, False, ACTIVITY, PAID_SUPPLY),
        ('paid_supply_priority', False, False, True, ACTIVITY, ANTISURGE),
        (
            'surge_and_paid_supply_priority',
            True,
            True,
            False,
            PAID_SUPPLY,
            SURGE,
        ),
        (
            'surge_and_paid_supply_priority',
            True,
            False,
            False,
            ACTIVITY,
            SURGE,
        ),
    ],
)
async def test_ui_parts_settings_without_tylers(
        taxi_driver_orders_builder,
        load_json,
        experiments3,
        mockserver,
        surge_paid_supply_settings,
        is_surge,
        is_paid_supply,
        is_antisurge,
        left_item,
        right_item,
        setcar_create_params,
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
            'hide_ui_parts': {},
            'show_ui_parts': {},
            'surge_paid_supply_settings': surge_paid_supply_settings,
        },
    )
    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, 'order_core_response.json')
    if is_surge:
        order_proc.order_proc['fields']['order']['pricing_data']['driver'][
            'meta'
        ] = {'setcar.show_surcharge': 100}
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

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert 'acceptance_items' in response_json['ui']
    assert response_json['ui']['acceptance_items'][0]['left'] == left_item
    assert response_json['ui']['acceptance_items'][0]['right'] == right_item


@pytest.mark.parametrize(
    'is_surge,is_paid_supply,is_antisurge,is_acceptance_bonus,color',
    [
        (False, False, False, True, '#0062c6'),  # acceptance_bonus
        (False, False, False, False, '#f2e15c'),  # default
        (True, False, False, False, '#820abe'),  # surge
        (False, True, False, False, '#00945e'),  # paid_supply
        (False, False, True, False, '#5c5a57'),  # antisurge
    ],
)
async def test_ui_parts_settings_acceptance_button_color(
        taxi_driver_orders_builder,
        load_json,
        experiments3,
        taxi_config,
        mockserver,
        is_surge,
        is_paid_supply,
        is_antisurge,
        is_acceptance_bonus,
        color,
        params_wo_original_setcar,
        order_proc,
):

    taxi_config.set(
        SETCAR_REBUILD_SETTINGS={'ui': {'acceptance_button_color': 'enable'}},
    )
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
            'hide_ui_parts': {},
            'show_ui_parts': {},
            'surge_paid_supply_settings': 'default',
            'acceptance_button_color': {
                'default_override': '#f2e15c',
                'surge': '#820abe',
                'antisurge': '#5c5a57',
                'paid_supply': '#00945e',
                'acceptance_bonus': '#0062c6',
            },
        },
    )

    order_proc.set_file(load_json, 'order_core_response.json')
    if is_surge:
        order_proc.order_proc['fields']['order']['pricing_data']['driver'][
            'meta'
        ] = {'setcar.show_surcharge': 100}
    if is_paid_supply:
        order_proc.order_proc['fields']['candidates'][0]['paid_supply'] = True
    if is_acceptance_bonus:
        order_proc.order_proc['fields']['candidates'][0]['driver_metrics'][
            'activity_prediction'
        ]['c'] = 1
    else:
        order_proc.order_proc['fields']['candidates'][0]['driver_metrics'][
            'activity_prediction'
        ]['c'] = 0
    if is_antisurge:
        order_proc.order_proc['fields']['order']['calc'] = {
            'alternative_type': 'explicit_antisurge',
        }

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert 'acceptance_button_params' in response_json['ui']
    assert response_json['ui']['acceptance_button_params']['bg_color'] == color


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.parametrize(
    'use_pricing_data, expected_ps_price', [(True, 2), (False, 59)],
)
async def test_paid_supply_price_source(
        taxi_driver_orders_builder,
        load_json,
        experiments3,
        mockserver,
        use_pricing_data,
        expected_ps_price,
        taxi_config,
        setcar_create_params,
        order_proc,
):
    taxi_config.set(
        SETCAR_REBUILD_SETTINGS={
            'paid_supply_price': 'enable' if use_pricing_data else 'disable',
            'ui': {},
        },
    )
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
            'hide_ui_parts': {},
            'show_ui_parts': {},
            'surge_paid_supply_settings': 'paid_supply_priority',
        },
    )
    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['candidates'][0]['paid_supply'] = True
    order_proc.order_proc['fields']['order']['pricing_data']['user'][
        'additional_prices'
    ] = {'paid_supply': {'price': {'total': 15}, 'meta': {}}}
    order_proc.order_proc['fields']['order']['pricing_data']['user']['price'][
        'total'
    ] = 2
    order_proc.order_proc['fields']['order']['pricing_data']['driver'][
        'additional_prices'
    ] = (
        {
            'paid_supply': {
                'price': {'total': expected_ps_price + 3},
                'meta': {},
            },
        }
    )
    order_proc.order_proc['fields']['order']['pricing_data']['driver'][
        'price'
    ]['total'] = 3
    order_proc.order_proc['fields']['order']['fixed_price'] = {
        'paid_supply_price': expected_ps_price,
    }

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert 'acceptance_items' in response_json['ui']
    assert (
        response_json['ui']['acceptance_items'][0]['right']['subtitle']
        == f'+{expected_ps_price} ₽'
    )


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
        'antisurge': {'id': 'antisurge_item'},
        'paid_supply': {'id': 'paid_supply_item'},
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
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.parametrize(
    'surge_paid_supply_settings,is_surge,is_paid_supply,is_antisurge,items',
    [
        (
            'default',
            True,
            True,
            False,
            [ACTIVITY_TYLER, SURGE_TYLER, PAID_SUPPLY_TYLER],
        ),
        ('default', False, False, True, [ACTIVITY_TYLER, ANTISURGE_TYLER]),
        ('default', False, True, False, [ACTIVITY_TYLER, PAID_SUPPLY_TYLER]),
        (
            'surge_priority',
            True,
            True,
            False,
            [ACTIVITY_TYLER, SURGE_TYLER, PAID_SUPPLY_TYLER],
        ),
        (
            'surge_priority',
            False,
            True,
            False,
            [ACTIVITY_TYLER, PAID_SUPPLY_TYLER],
        ),
        (
            'paid_supply_priority',
            True,
            True,
            False,
            [ACTIVITY_TYLER, PAID_SUPPLY_TYLER, SURGE_TYLER],
        ),
        (
            'paid_supply_priority',
            False,
            False,
            True,
            [ACTIVITY_TYLER, ANTISURGE_TYLER],
        ),
    ],
)
async def test_ui_parts_settings_with_tylers(
        taxi_driver_orders_builder,
        load_json,
        experiments3,
        mockserver,
        surge_paid_supply_settings,
        is_surge,
        is_paid_supply,
        is_antisurge,
        items,
        setcar_create_params,
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
            'hide_ui_parts': {},
            'show_ui_parts': {},
            'surge_paid_supply_settings': surge_paid_supply_settings,
        },
    )
    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, 'order_core_response.json')
    if is_surge:
        order_proc.order_proc['fields']['order']['pricing_data']['driver'][
            'meta'
        ] = {'setcar.show_surcharge': 100}
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

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert 'acceptance_items' in response_json['ui']
    assert 'items' in response_json['ui']['acceptance_items'][0]
    assert response_json['ui']['acceptance_items'][0]['items'] == items


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'priority': {'id': 'priority_item'},
    },
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'modifications_items': '2.00'}},
    },
)
@pytest.mark.parametrize(
    'udid,driver_metrics,expected_driver_points_tyler,is_zero_driver_point,'
    'use_priority',
    [
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'activity': 60,
                'activity_blocking': {
                    'activity_threshold': 20,
                    'duration_sec': 3600,
                },
                'activity_prediction': {'c': 5, 'n': -5, 'p': 0},
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            ACTIVITY_TYLER,
            False,
            False,
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'activity': 60,
                'activity_blocking': {
                    'activity_threshold': 20,
                    'duration_sec': 3600,
                },
                'activity_prediction': {'n': -5, 'p': 0},
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            ACTIVITY_TYLER,
            True,
            False,
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {
                    'a': -1,
                    'n': -4,
                    'o': -1,
                    'p': -1,
                    'c': 3,
                },
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            PRIORITY_TYLER,
            False,
            True,
        ),
        (
            'sdfsdfsdfsdfsdfsdfsdf',
            {
                'dispatch': 'long',
                'id': '5ec7e60784f802cbd044b047',
                'priority': 1,
                'priority_blocking': {'duration_sec': 7200, 'threshold': -3},
                'priority_prediction': {'a': -1, 'n': -4, 'o': -1, 'p': -1},
                'properties': ['dispatch_long', 'has_order_comment'],
                'type': 'dm_service',
            },
            PRIORITY_TYLER,
            True,
            True,
        ),
    ],
)
async def test_driver_points_in_tylers(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        experiments3,
        udid,
        driver_metrics,
        expected_driver_points_tyler,
        is_zero_driver_point,
        use_priority,
        setcar_create_params,
        order_proc,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='replace_activity_with_priority',
        consumers=[
            'driver-orders-builder/'
            'replace-activity-with-priority-experiment',
        ],
        clauses=[],
        default_value={'enabled': use_priority},
    )

    order_proc.set_file(load_json, 'order_core_response1.json')
    order_proc.order_proc['fields']['candidates'][0][
        'driver_metrics'
    ] = driver_metrics
    order_proc.order_proc['fields']['candidates'][0]['udid'] = udid

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert 'acceptance_items' in response_json['ui']
    assert 'items' in response_json['ui']['acceptance_items'][0]
    assert (
        len(response_json['ui']['acceptance_items'][0]['items'])
        == 1 - is_zero_driver_point
    )
    if not is_zero_driver_point:
        assert (
            response_json['ui']['acceptance_items'][0]['items'][0]
            == expected_driver_points_tyler
        )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='driver_orders_builder_modifications_items_eats',
    consumers=['driver-orders-builder/setcar'],
    clauses=[
        {
            'title': 'Show demand for flutter apps',
            'value': {
                'tyler': {
                    'id': 'tyler_id_on_flutter',
                    'type': 'tyler',
                    'padding_type': 'small_top_bottom',
                    'horizontal_divider_type': 'none',
                },
                'demand': {'id': 'demand_item'},
                'batch_order_demand': {'id': 'demand_item_{order_index}'},
            },
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': '11.0.0',
                                'arg_name': 'version',
                                'arg_type': 'version',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'value': '2.0.0',
                                'arg_name': 'version',
                                'arg_type': 'version',
                            },
                            'type': 'lte',
                        },
                    ],
                },
                'type': 'any_of',
            },
        },
        {
            'title': 'Show demand for kotlin apps',
            'value': {
                'tyler': {
                    'id': 'tyler_id_on_kotlin',
                    'type': 'tyler',
                    'padding_type': 'small_top_bottom',
                    'horizontal_divider_type': 'none',
                },
                'demand': {'id': 'demand_item'},
                'batch_order_demand': {'id': 'demand_item_{order_index}'},
            },
            'predicate': {
                'init': {
                    'value': '9.0.0',
                    'arg_name': 'version',
                    'arg_type': 'version',
                },
                'type': 'gte',
            },
        },
    ],
    default_value={},
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
    'claim_ids', [['claim_id_1'], ['claim_id_1', 'claim_id_2', 'claim_id_3']],
)
@pytest.mark.parametrize('batch_show_mode', ['general', 'separate'])
@pytest.mark.parametrize(
    ('taximeter_version', 'expected_tyler_id'),
    [('9.50', 'tyler_id_on_kotlin'), ('11.50', 'tyler_id_on_flutter')],
)
async def test_ui_parts_settings_with_tylers_for_courier(
        taxi_driver_orders_builder,
        load_json,
        experiments3,
        mockserver,
        setcar_create_params,
        mock_cargo_setcar_data,
        claim_ids,
        batch_show_mode,
        order_proc,
        taximeter_version,
        expected_tyler_id,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': request.json['id_in_set'][0],
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': taximeter_version,
                        'taximeter_version_type': '',
                        'taximeter_platform': 'android',
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    mock_cargo_setcar_data(
        claim_ids=claim_ids,
        custom_context={
            'courier_demand_level': 1.5,
            'claims_courier_demand_level': [
                {'claim_id': 'claim_id_1', 'courier_demand_multiplier': 1.4},
                {'claim_id': 'claim_id_3', 'courier_demand_multiplier': 1.6},
            ],
            'region_id': '1',
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='show_courier_demand_level',
        consumers=['driver-orders-builder/courier-demand-experiment'],
        clauses=[],
        merge_values_by=[],
        default_value={'enabled': True, 'batch_mode': batch_show_mode},
    )
    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, 'order_core_response_courier.json')

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert 'acceptance_items' in response_json['ui']
    if len(claim_ids) > 1 and batch_show_mode == 'separate':
        tylers = [
            {
                'id': 'demand_item_1',
                'title': 'Коэффициент спроса: 1 заказ',
                'short_info': '×1.4',
            },
            {
                'id': 'demand_item_3',
                'title': 'Коэффициент спроса: 3 заказ',
                'short_info': '×1.6',
            },
        ]
    else:
        tylers = [
            {
                'id': 'demand_item',
                'title': 'Коэффициент спроса',
                'short_info': '×1.5',
            },
        ]
    assert response_json['ui']['acceptance_items'] == [
        {
            'id': expected_tyler_id,
            'type': 'tyler',
            'padding_type': 'small_top_bottom',
            'horizontal_divider_type': 'none',
            'items': tylers,
        },
        {
            'type': 'default',
            'title': 'Комментарий',
            'markdown': True,
            'reverse': True,
            'background': {'type': 'balloon'},
            'subtitle': 'Какой-то комментарий',
            'primary_max_lines': 3,
            'secondary_max_lines': 1,
        },
        {
            'type': 'default',
            'title': 'Откуда:',
            'reverse': True,
            'horizontal_divider_type': 'full',
            'subtitle': (
                'Рядом с: Москва, улица 26 '
                'Бакинских Комиссаров, 8к3, подъезд 4'
            ),
        },
    ]
