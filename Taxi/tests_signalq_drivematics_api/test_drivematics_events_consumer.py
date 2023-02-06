import json

import pytest


@pytest.mark.config(
    SIGNALQ_DRIVEMATICS_API_EVENTS_CONSUMER_SETTINGS={
        'polling_delay_ms': 1000,
        'events_chunk_size': 30,
        'enabled': True,
    },
)
async def test_consume_events(
        taxi_signalq_drivematics_api,
        taxi_signalq_drivematics_api_monitor,
        testpoint,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    @testpoint('drivematics-events-consumer-processed')
    def processed(data):
        return

    for _ in range(4):
        lb_response = await taxi_signalq_drivematics_api.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'drivematics-events-consumer',
                    'data': 'test_data',
                    'topic': '/carsharing/signalq/testing/drivematics-events',
                    'cookie': 'cookie1',
                },
            ),
        )
        assert lb_response.status_code == 200

    async with taxi_signalq_drivematics_api.spawn_task(
            'distlock/drivematics-events-consumer',
    ):
        await processed.wait_call()
        for _ in range(4):
            await commit.wait_call()

        stats = await taxi_signalq_drivematics_api_monitor.get_metrics(
            'drivematics-events-consumer',
        )
        stats = stats['drivematics-events-consumer']
        assert stats['msg']['bad_messages'] == {'count': {'1min': 4}}
        assert stats['processing']['batch_size'] == {
            '1min': {'avg': 4, 'max': 4, 'min': 4},
        }
