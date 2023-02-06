import json

import pytest


@pytest.mark.config(
    SIGNAL_DEVICE_TRACKS_SIGNALQ_EVENTS_CONSUMER_SETTINGS={
        'polling_delay_ms': 1000,
        'events_chunk_size': 30,
        'save_events_to_pg_attempts': 3,
        'save_to_pg_retry_ms': 100,
        'enabled': True,
    },
)
async def test_consume_events(
        taxi_signal_device_tracks,
        taxi_signal_device_tracks_monitor,
        testpoint,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    @testpoint('signalq-events-consumer-processed')
    def processed(data):
        return

    for _ in range(4):
        lb_response = await taxi_signal_device_tracks.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'signalq-events-consumer',
                    'data': 'hahalolfuckpython',
                    'topic': '/taxi/signalq/testing/events',
                    'cookie': 'cookie1',
                },
            ),
        )
        assert lb_response.status_code == 200

    # Клятый питон не умеет отправлять бинарные данные в LB,
    # так что протестить сейчас можно только нераспарсившиеся сообщения

    async with taxi_signal_device_tracks.spawn_task('signalq-events-consumer'):
        await processed.wait_call()
        for _ in range(4):
            await commit.wait_call()

        stats = await taxi_signal_device_tracks_monitor.get_metrics(
            'signalq-events-consumer',
        )
        stats = stats['signalq-events-consumer']
        assert stats['msg']['skipped'] == {'unparsed': {'1min': 4}}
        assert stats['processing']['batch_size'] == {
            '1min': {'avg': 4, 'max': 4, 'min': 4},
        }
