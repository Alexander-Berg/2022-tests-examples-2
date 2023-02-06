# pylint: disable=C0302

import pytest


def add_cancel_order_experiment(experiments3):
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
                                'init': {'arg_name': 'is_pull_dispatch'},
                                'type': 'bool',
                            },
                            {
                                'init': {
                                    'arg_name': 'is_batch_order_canceled',
                                },
                                'type': 'bool',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'enable': True,
                    'skip_arrive_screen': True,
                    'pickup_label_tanker_key': 'actions.pickup.title',
                    'dialog_part_of_batch_order_canceled': {
                        'title_tanker_key': (
                            'actions.show_dialog.order_in_batch_canceled_title'
                        ),
                        'message_tanker_key': (
                            'actions.'
                            'show_dialog.'
                            'order_in_batch_canceled_message'
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
@pytest.mark.parametrize('segment_skipped_points', [[0], [1], [], [0, 1]])
async def test_pull_dispatch_dialog_part_of_batch_order_canceled(
        get_driver_cargo_state,
        default_order_id,
        experiments3,
        my_batch_waybill_info,
        pull_dispatch_enabled,
        segment_skipped_points,
        mock_driver_tags_v1_match_profile,
):
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    for idx in segment_skipped_points:
        my_batch_waybill_info['execution']['points'][idx][
            'is_segment_skipped'
        ] = True
        segment_id = my_batch_waybill_info['execution']['points'][idx][
            'segment_id'
        ]
        for segment in my_batch_waybill_info['execution']['segments']:
            if segment['id'] == segment_id:
                segment['status'] = 'cancelled'

    add_cancel_order_experiment(experiments3)
    my_batch_waybill_info['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    dialog_action = next(
        filter(lambda x: x['type'] == 'show_dialog', actions), None,
    )
    if (
            pull_dispatch_enabled
            and segment_skipped_points != []
            and segment_skipped_points != [0, 1]
    ):
        expected_action = {
            'type': 'show_dialog',
            'tag': 'batch_order_part_canceled_notify',
            'message': 'Один из заказов переназначили на другого курьера',
            'button': 'Ок',
            'title': 'Заказ снят',
        }

        assert dialog_action == expected_action
    else:
        assert dialog_action is None


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': False},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'disable_pickup_action': True},
    },
)
async def test_pull_dispatch_filters_exp_not_matched(
        get_driver_cargo_state,
        default_order_id,
        experiments3,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    my_batch_waybill_info['execution']['points'][0][
        'is_segment_skipped'
    ] = True
    segment_id = my_batch_waybill_info['execution']['points'][0]['segment_id']
    for segment in my_batch_waybill_info['execution']['segments']:
        if segment['id'] == segment_id:
            segment['status'] = 'cancelled'

    add_cancel_order_experiment(experiments3)
    my_batch_waybill_info['dispatch']['is_pull_dispatch'] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    dialog_action = next(
        filter(lambda x: x['type'] == 'show_dialog', actions), None,
    )

    expected_action = {
        'type': 'show_dialog',
        'tag': 'batch_order_part_canceled_notify',
        'message': 'Один из заказов переназначили на другого курьера',
        'button': 'Ок',
        'title': 'Заказ снят',
    }

    assert dialog_action == expected_action


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': False},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'disable_pickup_action': True},
    },
)
async def test_pull_dispatch_dialog_pickup_arrived(
        get_driver_cargo_state,
        default_order_id,
        experiments3,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'pickup_arrived'

    my_batch_waybill_info['execution']['points'][0][
        'is_segment_skipped'
    ] = True
    segment_id = my_batch_waybill_info['execution']['points'][0]['segment_id']
    for segment in my_batch_waybill_info['execution']['segments']:
        if segment['id'] == segment_id:
            segment['status'] = 'cancelled'

    add_cancel_order_experiment(experiments3)
    my_batch_waybill_info['dispatch']['is_pull_dispatch'] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    dialog_action = next(
        filter(lambda x: x['type'] == 'show_dialog', actions), None,
    )

    expected_action = {
        'type': 'show_dialog',
        'tag': 'batch_order_part_canceled_notify',
        'message': 'Один из заказов переназначили на другого курьера',
        'button': 'Ок',
        'title': 'Заказ снят',
    }

    assert dialog_action == expected_action
