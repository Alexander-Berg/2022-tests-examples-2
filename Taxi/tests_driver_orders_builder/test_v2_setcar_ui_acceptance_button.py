# pylint: disable=too-many-lines
import pytest


NEW_BUTTON = {
    'bg_color': '#f2e15c',
    'progress_text_color': '#ffffff',
    'subtitle': 'Эконом',
    'text_color': '#21201f',
    'title': 'Принять',
}

SURGE_BUTTON = {
    'bg_color': '#820abe',
    'progress_text_color': '#ffffff',
    'subtitle': 'Эконом',
    'text_color': '#ffffff',
    'title': 'Принять',
}
PAID_SUPPLY_BUTTON = {
    'bg_color': '#0062c6',
    'progress_text_color': '#ffffff',
    'subtitle': 'Эконом',
    'text_color': '#ffffff',
    'title': 'Принять',
}
PAID_SUPPLY_BUTTON_EMPTY_SUBTITLE = {
    'bg_color': '#0062c6',
    'progress_text_color': '#ffffff',
    'subtitle': '',
    'text_color': '#ffffff',
    'title': 'Принять',
}
ANTISURGE_BUTTON = {
    'bg_color': '#5c5a57',
    'progress_text_color': '#ffffff',
    'subtitle': 'Эконом',
    'text_color': '#ffffff',
    'title': 'Принять',
}
ACCEPTANCE_BUTTON = {
    'bg_color': '#00945e',
    'progress_text_color': '#ffffff',
    'subtitle': 'Эконом',
    'text_color': '#ffffff',
    'title': 'Принять',
}
PAYMENT_TYPE_ONLY_SUBTITLE = {
    'bg_color': '#f2e15c',
    'progress_text_color': '#ffffff',
    'subtitle': 'Корпоративный',
    'text_color': '#21201f',
    'title': 'Принять',
}
PAYMENT_TYPE_TARIFF_SUBTITLE = {
    'bg_color': '#f2e15c',
    'progress_text_color': '#ffffff',
    'subtitle': 'Корпоративный · Эконом',
    'text_color': '#21201f',
    'title': 'Принять',
}

MOCKED_NOW = '2021-08-18T09:00:00+03:00'


@pytest.mark.parametrize(
    'config_value,expected_subtitle',
    [
        ({'__default__': {'__default__': False}}, ''),
        ({'__default__': {'__default__': True}}, 'Эконом'),
        (
            {
                '__default__': {'__default__': False},
                'moscow': {'econom': True, '__default__': False},
            },
            'Эконом',
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
@pytest.mark.now(MOCKED_NOW)
async def test_acceptance_button_subtitle(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        taxi_config,
        config_value,
        expected_subtitle,
        params_wo_original_setcar,
        order_proc,
):
    taxi_config.set(SHOW_LOCALIZED_TARIFF_TO_DRIVER=config_value)

    order_proc.set_file(load_json, 'order_core_response.json')

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert (
        resp['ui']['acceptance_button_params']['subtitle'] == expected_subtitle
    )


@pytest.mark.parametrize(
    'pricing_meta,paid_supply,antisurge,acceptance_bonus,'
    'tariff_class,payment_type,expected_button',
    [
        ({}, False, False, False, 'econom', 'cash', NEW_BUTTON),
        (
            {'setcar.show_surcharge': 2},
            False,
            False,
            False,
            'econom',
            'cash',
            SURGE_BUTTON,
        ),
        (
            {'setcar.show_surge': 2},
            False,
            False,
            False,
            'econom',
            'cash',
            SURGE_BUTTON,
        ),
        (
            {'setcar.show_surge': 2},
            True,
            False,
            False,
            'econom',
            'cash',
            PAID_SUPPLY_BUTTON,
        ),
        ({}, True, False, False, 'econom', 'cash', PAID_SUPPLY_BUTTON),
        ({}, False, True, False, 'econom', 'cash', ANTISURGE_BUTTON),
        ({}, False, False, True, 'econom', 'cash', ACCEPTANCE_BUTTON),
        (
            {'setcar.show_surge': 2},
            True,
            True,
            True,
            'econom',
            'cash',
            PAID_SUPPLY_BUTTON,
        ),
        (
            {'setcar.show_surge': 2},
            True,
            True,
            True,
            'uberlux',
            'cash',
            PAID_SUPPLY_BUTTON_EMPTY_SUBTITLE,
        ),
        (
            {},
            False,
            False,
            False,
            'uberlux',
            'corp',
            PAYMENT_TYPE_ONLY_SUBTITLE,
        ),
        (
            {},
            False,
            False,
            False,
            'econom',
            'corp',
            PAYMENT_TYPE_TARIFF_SUBTITLE,
        ),
    ],
    ids=[
        'default',
        'surge_surcharge',
        'surge_surge',
        'surge_and_paid_supply',
        'paid_supply',
        'antisurge',
        'acceptance_bonus',
        'all_modifiers',
        'uberlux_hidden_class',
        'corp_hidden_class',
        'corp_shown_class',
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
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_orders_builder_ui_parts_settings',
    is_config=True,
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    clauses=[],
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    default_value={'hide_ui_parts': {}, 'show_ui_parts': {}},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='ui_experiments_show_payment_type',
    is_config=True,
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    clauses=[
        {
            'title': 'corp_payment_type',
            'predicate': {
                'init': {
                    'value': 'corp',
                    'arg_name': 'payment_type',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'hide_ui_parts': {},
                'show_ui_parts': {},
                'acceptance_button_corp_modifications_enabled': True,
            },
        },
    ],
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    default_value={'hide_ui_parts': {}, 'show_ui_parts': {}},
)
@pytest.mark.config(
    SHOW_LOCALIZED_TARIFF_TO_DRIVER={
        '__default__': {'__default__': True, 'uberlux': False},
    },
)
@pytest.mark.now(MOCKED_NOW)
async def test_acceptance_button_builder(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        pricing_meta,
        paid_supply,
        antisurge,
        acceptance_bonus,
        tariff_class,
        payment_type,
        expected_button,
        params_wo_original_setcar,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')
    order = order_proc.order_proc['fields']['order']
    candidate = order_proc.order_proc['fields']['candidates'][0]
    order['pricing_data']['driver']['meta'] = pricing_meta
    order['request']['payment'] = {'type': payment_type}
    candidate['tariff_class'] = tariff_class
    if paid_supply:
        candidate['paid_supply'] = True
    else:
        assert 'paid_supply' not in candidate
    if antisurge:
        order['calc']['alternative_type'] = 'explicit_antisurge'
    else:
        assert 'alternative_type' not in order['calc']
    if acceptance_bonus:
        candidate['driver_metrics']['activity_prediction']['c'] = 1
    else:
        candidate['driver_metrics']['activity_prediction']['c'] = 0

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200, response.text
    resp = response.json()['setcar']
    assert resp['ui']['acceptance_button_params'] == expected_button
