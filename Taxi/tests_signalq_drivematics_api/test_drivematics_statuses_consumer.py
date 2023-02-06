import json

import pytest


@pytest.mark.config(
    SIGNALQ_DRIVEMATICS_API_STATUSES_CONSUMER_SETTINGS_V2={
        'polling_delay_ms': 1000,
        'statuses_chunk_size': 30,
        'is_starting_sessions_enabled': True,
        'enabled': True,
    },
    SIGNALQ_DRIVEMATICS_API_REDIS_TIMEOUTS={
        '__default__': {'timeout_all_ms': 1000, 'timeout_single_ms': 500},
    },
)
async def test_consume_statuses(
        taxi_signalq_drivematics_api,
        taxi_signalq_drivematics_api_monitor,
        testpoint,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    @testpoint('drivematics-statuses-consumer-processed')
    def processed(data):
        return

    for _ in range(4):
        lb_response = await taxi_signalq_drivematics_api.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'drivematics-statuses-consumer',
                    'data': 'test_data',
                    'topic': (
                        '/carsharing/signalq/testing/drivematics-statuses'
                    ),
                    'cookie': 'cookie1',
                },
            ),
        )
        assert lb_response.status_code == 200

    async with taxi_signalq_drivematics_api.spawn_task(
            'distlock/drivematics-statuses-consumer',
    ):
        await processed.wait_call()
        for _ in range(4):
            await commit.wait_call()

        stats = await taxi_signalq_drivematics_api_monitor.get_metrics(
            'drivematics-statuses-consumer',
        )
        stats = stats['drivematics-statuses-consumer']
        assert stats['msg']['bad_messages'] == {'count': {'1min': 4}}
        assert stats['processing']['batch_size'] == {
            '1min': {'avg': 4, 'max': 4, 'min': 4},
        }
