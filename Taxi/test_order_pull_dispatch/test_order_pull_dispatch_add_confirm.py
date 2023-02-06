# pylint: disable=C0302

import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enable': True,
        'skip_arrive_screen': True,
        'pickup_label_tanker_key': '123',
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'add_dropoff_confirm_action': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
@pytest.mark.parametrize('is_last_point', [True, False])
async def test_pull_dispatch_add_dropoff_confirm(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        is_last_point,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    if is_last_point:
        for i in range(5):
            waybill_info_pull_dispatch['execution']['points'][i][
                'is_resolved'
            ] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    action = next((x for x in actions if x['type'] == 'confirm'), None)
    if pull_dispatch_enabled:
        if is_last_point:
            assert action is None
        else:
            assert action == {
                'button': 'actions.confirm.default_button',
                'cancel_button': 'actions.confirm.cancel_button',
                'message': 'actions.confirm.dropoff_message',
                'title': 'actions.confirm.dropoff_title',
                'type': 'confirm',
            }
    else:
        assert action is None
