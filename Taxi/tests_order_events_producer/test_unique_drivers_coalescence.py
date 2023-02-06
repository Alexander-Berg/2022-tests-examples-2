import json

import pytest


async def test_dms_sinks_registered(
        taxi_order_events_producer, taxi_eventus_orchestrator_mock,
):
    is_registered, error_message = (
        await taxi_eventus_orchestrator_mock.has_registered_sources(
            taxi_order_events_producer, ['grocery-adjust-events'],
        )
    )
    assert is_registered, error_message

    is_registered, error_message = (
        await taxi_eventus_orchestrator_mock.has_registered_sinks(
            taxi_order_events_producer, ['dms_unique_drivers_merge_sink'],
        )
    )
    assert is_registered, error_message


@pytest.mark.parametrize(
    'handle_part,event_key', [('merge', 'merged_unique_driver')],
)
async def test_dms_unique_drivers_id_merge(
        taxi_order_events_producer,
        testpoint,
        stq,
        taxi_eventus_orchestrator_mock,
        mockserver,
        handle_part,
        event_key,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_order_events_producer,
        [
            {
                'description': '',
                'st_ticket': '',
                'source': {'name': 'grocery-adjust-events'},
                'root': {
                    'output': {
                        'sink_name': f'dms_unique_drivers_{handle_part}_sink',
                    },
                    'operations': [],
                },
                'name': f'dms-unique_drivers-{handle_part}',
            },
        ],
    )

    @mockserver.json_handler(
        '/driver-metrics-storage/internal/v1/'
        f'unique_drivers/{handle_part}_ids',
    )
    def dms_handler(data):
        return mockserver.make_response(json={})

    for index in range(2):
        event = {
            'producer': {
                'source': 'producer-source',
                'login': 'producer-login',
            },
            'unique_driver': {
                'id': f'udid-to-{index*2+1}',
                'park_driver_profile_ids': [{'id': f'pdpi-to-{index*2+1}'}],
            },
            event_key: {
                'id': f'udid-from-{index*2+2}',
                'park_driver_profile_ids': [{'id': f'pdpi-from-{index*2+2}'}],
            },
        }

        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'grocery-adjust-events',
                    'data': json.dumps(event),
                    'topic': 'smth',
                    'cookie': f'cookie_for_dms_sink_{index}',
                },
            ),
        )
        assert response.status_code == 200

    for index in range(2):
        assert (await commit.wait_call())[
            'data'
        ] == f'cookie_for_dms_sink_{index}'

    assert (await dms_handler.wait_call())['data'].json == {
        'events': [
            {
                'unique_driver': {'id': 'udid-to-1'},
                event_key: {'id': 'udid-from-2'},
            },
            {
                'unique_driver': {'id': 'udid-to-3'},
                event_key: {'id': 'udid-from-4'},
            },
        ],
    }
