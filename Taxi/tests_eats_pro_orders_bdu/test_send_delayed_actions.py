# flake8: noqa
import datetime
import dateutil

import pytest


@pytest.mark.now('2022-07-18T11:23:44+00:00')
@pytest.mark.experiments3(
    filename='eats_pro_orders_bdu_actions_when_performer_late.json',
)
@pytest.mark.parametrize(
    ('cargo_event_status', 'current_time', 'is_schedule_action'),
    [
        ('performer_found', '2022-07-18T11:23:44+00:00', True),
        ('performer_found', '2022-07-18T11:27:40+00:00', False),
    ],
)
async def test_send_delayed_action_popup_for_performer_found(
        stq,
        stq_runner,
        default_order_id,
        cargo_event_status,
        current_time,
        is_schedule_action,
        cargo,
        mock_driver_tags_v1_match_profile,
        mocked_time,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))
    cargo.waybill['execution']['points'][0][
        'due'
    ] = '2022-07-18T11:27:44+00:00'
    cargo.waybill['execution']['points'][0][
        'eta'
    ] = '2022-07-18T11:17:44+00:00'

    await stq_runner.eats_pro_orders_bdu_delayed_actions.call(
        task_id='claim/123',
        kwargs={
            'cargo_order_id': default_order_id,
            'park_id': 'park_id1',
            'driver_profile_id': 'driver_id1',
            'cargo_event_status': cargo_event_status,
            'action_type': 'late_popup',
        },
    )

    result = None
    if is_schedule_action:
        assert stq.eats_pro_orders_bdu_delayed_actions.times_called == 1

        result = stq.eats_pro_orders_bdu_delayed_actions.next_call()
    else:
        assert (
            stq.cargo_increment_and_update_setcar_state_version.times_called
            == 1
        )
        result = (
            stq.cargo_increment_and_update_setcar_state_version.next_call()
        )

    if is_schedule_action:
        assert result['eta'] == datetime.datetime(2022, 7, 18, 11, 27, 34)
    else:
        assert result['eta'] == datetime.datetime(2022, 7, 18, 11, 27, 40)
    assert result['kwargs']['cargo_order_id'] == default_order_id
    assert result['kwargs']['park_id'] == 'park_id1'
    assert result['kwargs']['driver_profile_id'] == 'driver_id1'


@pytest.mark.now('2022-07-18T11:23:44+00:00')
@pytest.mark.experiments3(
    filename='eats_pro_orders_bdu_actions_when_performer_late.json',
)
@pytest.mark.parametrize(
    ('cargo_event_status', 'current_time', 'is_schedule_action'),
    [
        ('pickuped', '2022-07-18T11:23:44+00:00', True),
        ('pickuped', '2022-07-18T11:27:40+00:00', False),
    ],
)
async def test_send_delayed_action_popup_for_pickuped(
        stq,
        stq_runner,
        default_order_id,
        cargo_event_status,
        current_time,
        is_schedule_action,
        cargo,
        mock_driver_tags_v1_match_profile,
        mocked_time,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))
    cargo.waybill['execution']['segments'][0]['custom_context'][
        'promise_min_at'
    ] = '2022-07-18T11:27:44+00:00'
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    cargo.waybill['execution']['points'][0]['is_resolved'] = True
    cargo.waybill['execution']['points'][1][
        'eta'
    ] = '2022-07-18T11:17:44+00:00'

    await stq_runner.eats_pro_orders_bdu_delayed_actions.call(
        task_id='claim/123',
        kwargs={
            'cargo_order_id': default_order_id,
            'park_id': 'park_id1',
            'driver_profile_id': 'driver_id1',
            'cargo_event_status': cargo_event_status,
            'action_type': 'late_popup',
        },
    )

    result = None
    if is_schedule_action:
        assert stq.eats_pro_orders_bdu_delayed_actions.times_called == 1

        result = stq.eats_pro_orders_bdu_delayed_actions.next_call()
    else:
        assert (
            stq.cargo_increment_and_update_setcar_state_version.times_called
            == 1
        )
        result = (
            stq.cargo_increment_and_update_setcar_state_version.next_call()
        )

    if is_schedule_action:
        assert result['eta'] == datetime.datetime(2022, 7, 18, 11, 27, 34)
    else:
        assert result['eta'] == datetime.datetime(2022, 7, 18, 11, 27, 40)
    assert result['kwargs']['cargo_order_id'] == default_order_id
    assert result['kwargs']['park_id'] == 'park_id1'
    assert result['kwargs']['driver_profile_id'] == 'driver_id1'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_pro_orders_bdu_actions_when_performer_late',
    consumers=['eats-pro-orders-bdu/performer-late'],
    clauses=[],
    default_value={
        'actions': [
            {
                'action_type': 'chatterbox',
                'delay_between_attempts': 60,
                'tanker_key_with_message': (
                    'constructor.actions.performer_late.message'
                ),
                'time_after_timer_expire': 10,
                'time_before_client_promise': 10,
                'try_count': 5,
            },
        ],
    },
)
@pytest.mark.parametrize(
    ('cargo_event_status', 'current_time', 'is_sent_action'),
    [
        ('pickuped', '2022-07-18T11:23:44+00:00', False),
        ('pickuped', '2022-07-18T11:27:40+00:00', True),
    ],
)
async def test_send_delayed_action_chatterbox_for_pickuped(
        mockserver,
        stq,
        stq_runner,
        default_order_id,
        cargo_event_status,
        current_time,
        is_sent_action,
        cargo,
        mock_driver_tags_v1_match_profile,
        mocked_time,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))
    cargo.waybill['execution']['segments'][0]['custom_context'][
        'promise_min_at'
    ] = '2022-07-18T11:27:44+00:00'
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    cargo.waybill['execution']['points'][0]['is_resolved'] = True
    cargo.waybill['execution']['points'][1][
        'eta'
    ] = '2022-07-18T11:17:44+00:00'

    @mockserver.json_handler('/chatterbox/v2/tasks/init_with_tvm/driver')
    def _mock_chatterbox_init_with_tvm(request):
        return {'id': 'some_id', 'status': 'new'}

    @mockserver.json_handler(
        '/chatterbox/v1/tasks/some_id/hidden_comment_with_tvm',
    )
    def _mock_chatterbox_hidden_comment_with_tvm(request):
        return {}

    await stq_runner.eats_pro_orders_bdu_delayed_actions.call(
        task_id='claim/123',
        kwargs={
            'cargo_order_id': default_order_id,
            'park_id': 'park_id1',
            'driver_profile_id': 'driver_id1',
            'cargo_event_status': cargo_event_status,
            'action_type': 'chatterbox',
        },
    )

    if is_sent_action:
        assert _mock_chatterbox_init_with_tvm.times_called == 1
        assert _mock_chatterbox_hidden_comment_with_tvm.times_called == 1
    else:
        assert _mock_chatterbox_init_with_tvm.times_called == 0
        assert _mock_chatterbox_hidden_comment_with_tvm.times_called == 0
