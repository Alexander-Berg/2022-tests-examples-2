import dateutil
import pytest

from tests_eats_pro_orders_bdu import models


def find_action_by_tag(actions, tag):
    for action in actions:
        if 'tag' in action and action['tag'] == tag:
            return action
    return None


@pytest.mark.parametrize('cancelled', [True, False])
@pytest.mark.translations()
async def test_order_cancelled(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        cargo,
        mocked_time,
        cancelled,
        mock_driver_tags_v1_match_profile,
):
    if cancelled:
        cargo.waybill['execution']['segments'][0][
            'status'
        ] = 'cancelled_with_items_on_hands'

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    tag = 'order_external_order_id_1_cancelled'
    action = {
        'button': '',
        'buttons': [
            {
                'action': {'type': 'close_dialog'},
                'appearance': 'main',
                'text': 'Хорошо',
            },
        ],
        'message': 'Заказ отменён диспетчером',
        'tag': tag,
        'show_mode': 'notification_and_dialog',
        'title': 'Заказ снят',
        'type': 'show_dialog',
    }
    assert response.status_code == 200
    actions = response.json()['state']['point']['actions']
    if cancelled:
        assert find_action_by_tag(actions, tag) == action
    else:
        assert find_action_by_tag(actions, tag) != action


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_pro_orders_bdu_actions_when_performer_late',
    consumers=['eats-pro-orders-bdu/performer-late'],
    clauses=[],
    default_value={
        'actions': [
            {
                'action_type': 'late_popup',
                'delay_between_attempts': 60,
                'tanker_key_with_message': (
                    'constructor.actions.performer_late.message'
                ),
                'time_after_timer_expire': 600,
                'time_before_client_promise': 300,
                'try_count': 5,
            },
        ],
    },
)
@pytest.mark.parametrize(
    ('current_time', 'is_showed_action'),
    [
        ('2022-07-21T16:39:53+03:00', False),
        ('2022-07-21T16:43:23+03:00', True),
    ],
)
async def test_send_action_when_performer_late_to_rest(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        current_time,
        is_showed_action,
        cargo,
        mock_driver_tags_v1_match_profile,
        mocked_time,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))
    cargo.waybill['execution']['points'][0][
        'due'
    ] = '2022-07-21T13:43:53+00:00'
    cargo.waybill['execution']['points'][0][
        'eta'
    ] = '2022-07-21T13:33:22.942+00:00'

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    tag = 'performer_late_source_external_order_id_1'
    action = {
        'button': '',
        'buttons': [
            {
                'action': {'type': 'close_dialog'},
                'appearance': 'main',
                'text': 'Ок, уже бегу',
            },
        ],
        'message': 'Вы опаздываете по заказу external_order_id_1',
        'show_mode': 'notification_and_dialog',
        'tag': tag,
        'title': 'Опоздание',
        'type': 'show_dialog',
    }
    assert response.status_code == 200
    actions = response.json()['state']['point']['actions']
    if is_showed_action:
        assert find_action_by_tag(actions, tag) == action
    else:
        assert find_action_by_tag(actions, tag) != action


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_pro_orders_bdu_actions_when_performer_late',
    consumers=['eats-pro-orders-bdu/performer-late'],
    clauses=[],
    default_value={
        'actions': [
            {
                'action_type': 'late_popup',
                'delay_between_attempts': 60,
                'tanker_key_with_message': (
                    'constructor.actions.performer_late.message'
                ),
                'time_after_timer_expire': 600,
                'time_before_client_promise': 300,
                'try_count': 5,
            },
        ],
    },
)
@pytest.mark.parametrize(
    ('current_time', 'is_showed_action'),
    [
        ('2022-07-21T14:57:25+03:00', False),
        ('2022-07-21T14:57:51+03:00', True),
    ],
)
async def test_send_action_when_performer_late_to_client(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        current_time,
        is_showed_action,
        cargo,
        mock_driver_tags_v1_match_profile,
        mocked_time,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    cargo.waybill['execution']['points'][0]['is_resolved'] = True
    cargo.waybill['execution']['segments'][0]['custom_context'] = {
        **cargo.waybill['execution']['segments'][0]['custom_context'],
        'promise_min_at': '2022-07-21T14:56:26+03:00',
    }
    cargo.waybill['execution']['segments'][0]['status'] = 'pickuped'
    cargo.waybill['execution']['points'][1][
        'eta'
    ] = '2022-07-21T11:47:50.886+00:00'

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    tag = 'performer_late_destination_external_order_id_1'
    action = {
        'button': '',
        'buttons': [
            {
                'action': {'type': 'close_dialog'},
                'appearance': 'main',
                'text': 'Ок, уже бегу',
            },
        ],
        'message': 'Вы опаздываете по заказу external_order_id_1',
        'show_mode': 'notification_and_dialog',
        'tag': tag,
        'title': 'Опоздание',
        'type': 'show_dialog',
    }
    assert response.status_code == 200
    actions = response.json()['state']['point']['actions']
    if is_showed_action:
        assert find_action_by_tag(actions, tag) == action
    else:
        assert find_action_by_tag(actions, tag) != action


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_pro_orders_bdu_actions_when_performer_late',
    consumers=['eats-pro-orders-bdu/performer-late'],
    clauses=[],
    default_value={
        'actions': [
            {
                'action_type': 'drop_off_popup',
                'delay_between_attempts': 60,
                'tanker_key_with_message': 'constructor.long_drop_off.text',
                'time_after_timer_expire': 60,
                'try_count': 5,
            },
        ],
    },
)
@pytest.mark.parametrize(
    ('current_time', 'is_showed_action'),
    [
        ('2022-07-21T14:57:25+03:00', False),
        ('2022-07-21T14:57:27+03:00', True),
    ],
)
async def test_send_action_when_performer_long_drop_off(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        current_time,
        is_showed_action,
        cargo,
        mock_driver_tags_v1_match_profile,
        mocked_time,
        robocall_actions,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    cargo.waybill['execution']['points'][0]['is_resolved'] = True
    cargo.waybill['execution']['points'][1]['visit_status'] = 'arrived'
    cargo.waybill['execution']['segments'][0]['custom_context'] = {
        **cargo.waybill['execution']['segments'][0]['custom_context'],
        'promise_max_at': '2022-07-21T14:56:26+03:00',
    }
    cargo.waybill['execution']['segments'][0]['status'] = 'delivery_arrived'
    cargo.waybill['execution']['points'][1][
        'eta'
    ] = '2022-07-21T11:47:50.886+00:00'

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    tag = 'drop_off_destination_external_order_id_1'
    action = {
        'button': '',
        'buttons': [
            {
                'action': {'type': 'close_dialog'},
                'appearance': 'main',
                'text': 'Уже отдаю',
            },
        ],
        'message': 'Вы долго в состоянии отдачи заказа, это наказуемо',
        'show_mode': 'notification_and_dialog',
        'tag': tag,
        'title': 'Быстрее',
        'type': 'show_dialog',
    }
    assert response.status_code == 200
    actions = response.json()['state']['point']['actions']
    if is_showed_action:
        assert find_action_by_tag(actions, tag) == action
    else:
        assert find_action_by_tag(actions, tag) != action
