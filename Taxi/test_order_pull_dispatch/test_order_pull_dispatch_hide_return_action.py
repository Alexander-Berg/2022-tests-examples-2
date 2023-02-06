# pylint: disable=C0302

import pytest


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_action_checks',
    consumers=['cargo-claims/driver'],
    clauses=[],
    default_value={'return': {'enable': True}},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {
            '__default__': False,
            'hide_pull_back_return_action': True,
        },
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_hide_return_action(
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
    waybill_info_pull_dispatch['execution']['segments'][0][
        'status'
    ] = 'delivery_arrived'
    waybill_info_pull_dispatch['execution']['segments'][1][
        'status'
    ] = 'delivery_arrived'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    return_action = next(
        filter(lambda x: x['type'] == 'return', actions), None,
    )

    if pull_dispatch_enabled:
        assert return_action is None
    else:
        assert return_action is not None
