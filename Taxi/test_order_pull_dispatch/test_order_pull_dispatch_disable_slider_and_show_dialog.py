# pylint: disable=C0302

import pytest


def setup_starting_points(waybill_info):
    """
    Point A1 == A2
    Skip action 'arrive_at_point'
    """
    coordinates = [1, 2]
    waybill_info['execution']['points'][0]['location'][
        'coordinates'
    ] = coordinates
    waybill_info['execution']['points'][1]['location'][
        'coordinates'
    ] = coordinates
    waybill_info['execution']['segments'][1]['status'] = 'performer_found'
    waybill_info['dispatch']['is_pull_dispatch'] = True

    waybill_info['execution']['points'][0][
        'was_ready_at'
    ] = '2020-08-18T13:40:49.939497+00:00'
    waybill_info['execution']['points'][1][
        'was_ready_at'
    ] = '2020-08-18T13:43:49.939497+00:00'


def check_action_disabled(action, is_disabled):
    disable_condition = next(
        filter(lambda x: x['type'] == 'always_disabled', action['conditions']),
        None,
    )
    if is_disabled:
        assert disable_condition is not None
    else:
        assert disable_condition is None


def add_order_ready_experiment(experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
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
                                    'value': True,
                                    'arg_name': 'is_order_ready',
                                    'arg_type': 'bool',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'value': True,
                                    'arg_name': 'is_pull_dispatch',
                                    'arg_type': 'bool',
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
                    'dialog_after_order_ready': {
                        'title_tanker_key': (
                            'actions.show_dialog.pick_up_title'
                        ),
                        'message_tanker_key': (
                            'actions.show_dialog.pick_up_message'
                        ),
                        'button_tanker_key': (
                            'actions.show_dialog.default_batch_button'
                        ),
                    },
                },
            },
        ],
        default_value={'enabled': True, 'skip_arrive_screen': True},
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'disable_pickup_action': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_show_slider_and_dialog(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        experiments3,
        my_batch_waybill_info,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    add_order_ready_experiment(experiments3)
    setup_starting_points(my_batch_waybill_info)
    my_batch_waybill_info['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    pickup_action = next(
        filter(lambda x: x['type'] == 'pickup', actions), None,
    )
    check_action_disabled(pickup_action, False)
    dialog_action = next(
        filter(lambda x: x['type'] == 'show_dialog', actions), None,
    )
    if pull_dispatch_enabled:
        expected_action = {
            'type': 'show_dialog',
            'tag': 'order_ready_point_notify',
            'message': 'Можете идти забирать заказ',
            'button': 'Ок',
            'title': 'Заказ собран',
        }

        assert dialog_action == expected_action
    else:
        assert dialog_action is None


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'disable_pickup_action': True},
    },
)
@pytest.mark.parametrize('not_ready_points', [[0], [1], [0, 1]])
async def test_pull_dispatch_disable_pickup_when_points_not_ready(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        experiments3,
        my_batch_waybill_info,
        not_ready_points,
        mock_driver_tags_v1_match_profile,
):

    add_order_ready_experiment(experiments3)
    setup_starting_points(my_batch_waybill_info)

    for idx in not_ready_points:
        del my_batch_waybill_info['execution']['points'][idx]['was_ready_at']

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    pickup_action = next(
        filter(lambda x: x['type'] == 'pickup', actions), None,
    )
    check_action_disabled(pickup_action, True)
    dialog_action = next(
        filter(lambda x: x['type'] == 'show_dialog', actions), None,
    )
    assert dialog_action is None


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'disable_pickup_action': True},
    },
)
@pytest.mark.parametrize('not_ready_points', [[0], [1]])
async def test_pull_dispatch_enable_pickup_when_points_not_ready_skipped(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        experiments3,
        my_batch_waybill_info,
        not_ready_points,
        mock_driver_tags_v1_match_profile,
):
    add_order_ready_experiment(experiments3)
    setup_starting_points(my_batch_waybill_info)

    my_batch_waybill_info['execution']['points'][0]['visit_status'] = 'skipped'
    my_batch_waybill_info['execution']['points'][0][
        'is_segment_skipped'
    ] = True

    for idx in not_ready_points:
        del my_batch_waybill_info['execution']['points'][idx]['was_ready_at']

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    pickup_action = next(
        filter(lambda x: x['type'] == 'pickup', actions), None,
    )
    if not_ready_points == [0]:
        check_action_disabled(pickup_action, False)
    else:
        check_action_disabled(pickup_action, True)
