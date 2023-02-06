# pylint: disable=C0302

import pytest

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.experiments3(
    name='cargo_orders_timers_settings_lavka',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'eta_type': 'countdown'},
    is_config=True,
)
@pytest.mark.experiments3(
    name='cargo_orders_timers_settings',
    consumers=['cargo-orders/build-actions'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'hide_eta': True},
    is_config=True,
)
@pytest.mark.config(
    CARGO_ORDERS_CLIENT_KIND={
        '5e36732e2bc54e088b1466e08e31c486': {
            'client_kind': 'lavka',
            'country_iso3': 'FR',
        },
    },
)
async def test_show_eta(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        mock_driver_tags_v1_match_profile,
):
    points = waybill_info_with_same_source_point['execution']['points']
    for point in points:
        if point['visit_status'] == 'pending':
            point['eta_calculation_awaited'] = True

    expected_action = {
        'calculation_awaited': True,
        'eta': '1970-01-01T00:00:00+00:00',
        'type': 'eta',
    }

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action == expected_action


@pytest.mark.experiments3(
    name='cargo_orders_timers_settings_lavka',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'eta_type': 'countdown'},
    is_config=True,
)
@pytest.mark.experiments3(
    name='cargo_orders_timers_settings',
    consumers=['cargo-orders/build-actions'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'hide_eta': True},
    is_config=True,
)
@pytest.mark.config(
    CARGO_ORDERS_CLIENT_KIND={
        '5e36732e2bc54e088b1466e08e31c488': {
            'client_kind': 'lavka',
            'country_iso3': 'FR',
        },
    },
)
async def test_hide_eta(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        mock_driver_tags_v1_match_profile,
):
    points = waybill_info_with_same_source_point['execution']['points']
    for point in points:
        if point['visit_status'] == 'pending':
            point['visit_status'] = 'arrived'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action is None


@pytest.mark.config(
    CARGO_ORDERS_CLIENT_KIND={
        '5e36732e2bc54e088b1466e08e31c486': {
            'client_kind': 'lavka',
            'country_iso3': 'RU',
        },
    },
)
@pytest.mark.experiments3(
    name='cargo_orders_timers_settings_lavka',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'eta_type': 'countdown'},
    is_config=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'use_latest_grocery_eta': True},
    },
)
async def test_going_back_eta_use_max_eta(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        mock_driver_tags_v1_match_profile,
):
    max_eta = '2021-03-23T10:56:12.875501+00:00'
    points = waybill_info_pull_dispatch['execution']['points']
    points[0]['is_resolved'] = True
    points[1]['is_resolved'] = True
    points[2]['is_resolved'] = True
    points[3]['is_resolved'] = True
    points[4]['eta'] = '2021-03-23T10:53:12.875501+00:00'  # 3 min before
    points[5]['eta'] = max_eta

    expected_action = {
        'calculation_awaited': False,
        'eta': max_eta,
        'eta_type': 'countdown',
        'eta_times': [max_eta],
        'type': 'eta',
    }

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action == expected_action
