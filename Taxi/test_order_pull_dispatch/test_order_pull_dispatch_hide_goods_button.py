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
        'filters': {'__default__': False, 'hide_goods_button': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_hide_goods_button_last_point(
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

    waybill_info_pull_dispatch['execution']['points'][1]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][2]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][3]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][4]['is_resolved'] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    current_point = response.json()['current_point']

    if pull_dispatch_enabled:
        assert current_point['hide_goods_button']
    else:
        assert 'hide_goods_button' not in current_point


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'hide_goods_button': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_hide_goods_button_middle_point(
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
    assert 'hide_goods_button' not in current_point
