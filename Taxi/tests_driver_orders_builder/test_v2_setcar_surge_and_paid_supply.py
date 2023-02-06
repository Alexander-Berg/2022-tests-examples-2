import copy
import json

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
ACTIVITY_BONUS_FIELDS = {
    'subtitle': '+5',
    'primary_text_color': '#00945e',
    'left_icon': {
        'icon_type': 'activity',
        'tint_color': '#00ca50',
        'icon_size': 'large',
    },
}

DOUBLE_SECTION_RIGHT = {
    'accent_title': True,
    'horizontal_divider_type': 'full',
    'left_icon': {
        'icon_size': 'large',
        'icon_type': 'surge',
        'tint_color': '#d8d8d8',
    },
    'primary_text_color': '#9e9b98',
    'reverse': True,
    'subtitle': '× 1',
    'title': 'Цена',
    'type': 'icon_detail',
}

PAID_SUPPLY_FIELDS = {
    'left_icon': {
        'tint_color': '#0596fa',
        'icon_type': 'surge',
        'icon_size': 'large',
    },
    'primary_text_color': '#0062c6',
    'subtitle': '+59 ₽',
}

SURGE_FIELDS = {
    'subtitle': '×1.95',
    'primary_text_color': '#820abe',
    'left_icon': {
        'icon_type': 'surge',
        'tint_color': '#c81efa',
        'icon_size': 'large',
    },
}


@pytest.mark.parametrize(
    'pricing_data_driver_meta, case_name, right_fields',
    [
        (
            {'setcar.show_surge': 1.95},
            'get_surge_new_pricing_surge',
            SURGE_FIELDS,
        ),
        (None, 'paid_supply_only', PAID_SUPPLY_FIELDS),
    ],
)
async def test_surge_and_paid_supply_combination(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        pricing_data_driver_meta,
        case_name,
        right_fields,
        params_wo_original_setcar,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    if pricing_data_driver_meta:
        order_proc.order_proc['fields']['order']['pricing_data']['driver'][
            'meta'
        ] = pricing_data_driver_meta

    # add paid_supply
    order_proc.order_proc['fields']['candidates'][0]['paid_supply'] = True
    order_proc.order_proc['fields']['order']['fixed_price'] = {}
    order_proc.order_proc['fields']['order']['fixed_price'][
        'paid_supply_price'
    ] = 59.0

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200
    redis_str = redis_store.hget(
        'Order:SetCar:Items:park1', PARAMS['driver']['alias_id'],
    )
    redis_dict = json.loads(redis_str)
    expected_right = copy.deepcopy(DOUBLE_SECTION_RIGHT)
    expected_right.update(right_fields)

    assert expected_right == redis_dict['ui']['acceptance_items'][0]['right']


@pytest.mark.parametrize('hiding_paid_supply', [True, False])
@pytest.mark.parametrize('surge', [True, False])
async def test_hide_paid_supply(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        experiments3,
        hiding_paid_supply,
        surge,
        params_wo_original_setcar,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    if surge:
        order_proc.order_proc['fields']['order']['pricing_data']['driver'][
            'meta'
        ] = {'setcar.show_surge': 1.95}
    # add paid_supply
    order_proc.order_proc['fields']['candidates'][0]['paid_supply'] = True
    order_proc.order_proc['fields']['order']['fixed_price'] = {}
    order_proc.order_proc['fields']['order']['fixed_price'][
        'paid_supply_price'
    ] = 59.0

    order_proc.order_proc['fields']['candidates'][0]['driver_metrics'] = {
        'dispatch': 'short',
    }

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
            'hide_ui_parts': {'is_hiding_paid_supply': hiding_paid_supply},
            'show_ui_parts': {},
        },
    )
    await taxi_driver_orders_builder.invalidate_caches()

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200
    redis_str = redis_store.hget(
        'Order:SetCar:Items:park1', PARAMS['driver']['alias_id'],
    )
    expected_right = copy.deepcopy(DOUBLE_SECTION_RIGHT)
    redis_dict = json.loads(redis_str)
    redis_right = redis_dict['ui']['acceptance_items'][0].get('right')

    if not hiding_paid_supply:
        expected_right.update(PAID_SUPPLY_FIELDS)

    if surge:
        expected_right.update(SURGE_FIELDS)

    subtitle = 'Платная подача' if not hiding_paid_supply else 'Ближняя подача'
    assert expected_right == redis_right
    assert redis_dict['ui']['accept_toolbar_params']['subtitle'] == subtitle


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': True},
)
@pytest.mark.parametrize(
    'new_paid_supply_rounding, paid_supply_price',
    [
        ('enabled', 79.9),
        ('enabled', 79.3),
        ('enabled', 79.0),
        ('dryrun', 67.6),
        ('dryrun', 67.4),
        ('disabled', 45.9),
    ],
)
async def test_paid_supply_rounding(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        experiments3,
        new_paid_supply_rounding,
        paid_supply_price,
        params_wo_original_setcar,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    # add paid_supply
    order_proc.order_proc['fields']['candidates'][0]['paid_supply'] = True
    order_proc.order_proc['fields']['order']['fixed_price'] = {}
    order_proc.order_proc['fields']['order']['fixed_price'][
        'paid_supply_price'
    ] = paid_supply_price

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_ui_paid_supply_rounding',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={'new_paid_supply_rounding': new_paid_supply_rounding},
    )
    await taxi_driver_orders_builder.invalidate_caches()

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200
    paid_supply_subtitle = response.json()['setcar']['ui']['acceptance_items'][
        0
    ]['right']['subtitle']
    if new_paid_supply_rounding == 'enabled':
        assert (
            paid_supply_subtitle == '+' + str(round(paid_supply_price)) + ' ₽'
        )
    else:
        assert paid_supply_subtitle == '+' + str(int(paid_supply_price)) + ' ₽'
