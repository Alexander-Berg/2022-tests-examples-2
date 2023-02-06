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
        'filters': {'__default__': False, 'rename_return_action': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_rename_return_button(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        experiments3,
        mock_driver_tags_v1_match_profile,
):

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_claims_action_checks',
        consumers=['cargo-claims/driver'],
        clauses=[],
        default_value={'return': {'enable': True}},
    )
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_pull_dispatch['execution']['segments'][0][
        'status'
    ] = 'ready_for_delivery_confirmation'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    return_action = next((x for x in actions if x['type'] == 'return'), None)
    assert return_action is not None
    if pull_dispatch_enabled:
        return_action['title'] = 'point_label.return_label.pull_dispatch'
    else:
        assert 'title' not in return_action
