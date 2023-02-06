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
        'filters': {'__default__': False, 'show_skip_point_dialog': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
@pytest.mark.parametrize('point_index', [2, 5])
async def test_pull_dispatch_skip_point_dialog(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        point_index,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_pull_dispatch['execution']['points'][point_index][
        'visit_status'
    ] = 'skipped'
    waybill_info_pull_dispatch['execution']['points'][point_index][
        'is_resolved'
    ] = True
    waybill_info_pull_dispatch['execution']['points'][point_index][
        'changelog'
    ].append(
        {
            'cargo_order_id': 'fdf82e90-38dc-4891-b06b-e704b320c9cb',
            'driver_id': '315e2ea16fe9db2887642ee93825019a',
            'status': 'skipped',
            'timestamp': '2021-03-23T10:20:17.384156+00:00',
        },
    )

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    action = next((x for x in actions if x['type'] == 'show_dialog'), None)
    if pull_dispatch_enabled:
        assert action == {
            'button': 'Ок',
            'message': 'actions.show_dialog.point_skipped_message',
            'title': 'actions.show_dialog.point_skipped_title',
            'type': 'show_dialog',
            'tag': 'lavka_point_skipped_notify',
            'show_mode': 'notification_and_dialog',
            'notification': {
                'title': 'actions.show_dialog.point_skipped_title',
                'body': 'actions.show_dialog.point_skipped_message',
            },
        }
    else:
        assert action is None
