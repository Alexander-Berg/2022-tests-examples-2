# pylint: disable=C0302

import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'change_phones_label': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_phones_label_last_point(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_pull_dispatch['execution']['points'][2]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][3]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][4]['is_resolved'] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    current_point = response.json()['current_point']

    if pull_dispatch_enabled:
        assert (
            current_point['phones_label']
            == 'point_label.phones_label.pull_dispatch_return'
        )
    else:
        assert 'phones_label' not in current_point


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'change_phones_label': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_phones_label_middle_point(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    current_point = response.json()['current_point']
    assert len(current_point['phones']) == 2

    emergency_label = (
        'point_label.phones_label.pull_dispatch_return'
        if pull_dispatch_enabled
        else 'Контакт для экстренных случаев'
    )
    for phone in current_point['phones']:
        if phone['type'] == 'emergency':
            assert phone['label'] == emergency_label

    if pull_dispatch_enabled:
        assert (
            current_point['phones_label']
            == 'point_label.phones_label.pull_dispatch_client'
        )
    else:
        assert 'phones_label' not in current_point


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'change_phones_label': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_phones_label_first_point(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_pull_dispatch['execution']['points'][0]['is_resolved'] = False
    waybill_info_pull_dispatch['execution']['points'][1]['is_resolved'] = False

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    current_point = response.json()['current_point']
    if pull_dispatch_enabled:
        assert (
            current_point['phones_label']
            == 'point_label.phones_label.pull_dispatch_return'
        )
    else:
        assert 'phones_label' not in current_point
