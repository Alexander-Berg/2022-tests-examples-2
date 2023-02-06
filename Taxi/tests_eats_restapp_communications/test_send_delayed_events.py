import pytest

SEND_DELAYED_EVENTS_CONFIG = {
    'enabled': True,
    'period': 10,
    'chunk_size': 2,
    'max_time_from_creation': 600,
    'min_non_update_time': 120,
}


@pytest.mark.now('2022-05-01T10:00:00+0300')
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_SEND_DELAYED_EVENTS=SEND_DELAYED_EVENTS_CONFIG,
)
@pytest.mark.pgsql(
    'eats_restapp_communications',
    files=('test_send_delayed_events_data.sql',),
)
async def test_send_delayed_eventts(
        pgsql, taxi_eats_restapp_communications, testpoint, stq,
):
    @testpoint('send-delayed-events-finished')
    async def handle_finished(arg):
        stq_calls = [
            stq.eats_restapp_communications_event_sender.next_call()['id']
            for _ in range(
                stq.eats_restapp_communications_event_sender.times_called,
            )
        ]
        assert sorted(stq_calls) == ['4', '6', '7', '8']

    async with taxi_eats_restapp_communications.spawn_task(
            'send-delayed-events',
    ):
        await handle_finished.wait_call()
