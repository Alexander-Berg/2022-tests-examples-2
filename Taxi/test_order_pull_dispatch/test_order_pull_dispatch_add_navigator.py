# pylint: disable=C0302

import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 6,
                                'arg_name': 'point_visit_order',
                                'arg_type': 'int',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enable': True,
                'skip_arrive_screen': True,
                'pickup_label_tanker_key': 'actions.pickup.title',
            },
        },
    ],
    default_value={'enabled': False, 'skip_arrive_screen': False},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'add_navigator_action': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
@pytest.mark.parametrize('is_last_point', [True, False])
async def test_pull_dispatch_add_navigator(
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

    current_point = waybill_info_pull_dispatch['execution']['points'][2]
    if is_last_point:
        for i in range(5):
            waybill_info_pull_dispatch['execution']['points'][i][
                'is_resolved'
            ] = True
        current_point = waybill_info_pull_dispatch['execution']['points'][5]

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    action = next((x for x in actions if x['type'] == 'navigator'), None)
    arrive_action = next(
        (x for x in actions if x['type'] == 'arrived_at_point'), None,
    )
    if is_last_point:
        assert arrive_action is None
    else:
        assert arrive_action is not None
    if pull_dispatch_enabled:
        assert action is not None
        assert action['coordinates'] == current_point['address']['coordinates']
    else:
        assert action is None
