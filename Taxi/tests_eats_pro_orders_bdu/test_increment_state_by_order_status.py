import datetime

import pytest


@pytest.mark.experiments3(filename='eats_pro_orders_bdu_order_not_ready.json')
@pytest.mark.experiments3(
    filename='eats_pro_orders_bdu_orders_preparation_late.json',
)
@pytest.mark.parametrize(
    'cargo_event_status', ['performer_found', 'order_ready'],
)
async def test_send_increment_state(
        stq, stq_runner, default_order_id, cargo_event_status,
):

    await stq_runner.eats_pro_orders_bdu_cargo_events_handler.call(
        task_id='claim/123',
        kwargs={
            'cargo_order_id': default_order_id,
            'park_id': 'park_id1',
            'driver_profile_id': 'driver_id1',
            'zone_id': '1',
            'corp_client_id': '1',
            'cargo_event_status': cargo_event_status,
            'custom_context': {'order_flow_type': 'retail'},
            'due': '2022-05-27T09:00:00+0000',
            'was_ready_at': '2022-05-27T09:00:00+0000',
        },
    )

    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )

    result = stq.cargo_increment_and_update_setcar_state_version.next_call()

    if cargo_event_status == 'performer_found':
        assert result['eta'] == datetime.datetime(2022, 5, 27, 9, 0, 5)
    else:
        assert result['eta'] == datetime.datetime(2022, 5, 27, 9, 0, 10)
    assert result['kwargs']['cargo_order_id'] == default_order_id
    assert result['kwargs']['park_id'] == 'park_id1'
    assert result['kwargs']['driver_profile_id'] == 'driver_id1'
