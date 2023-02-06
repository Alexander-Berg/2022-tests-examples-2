import urllib.parse

import pytest

import tests_communication_scenario.common as common

SCENARIOS = {
    'test_go': {
        'steps': [
            {
                'name': 'push',
                'channel': {
                    'type': 'go/push/user',
                    'settings': {'push_go': {'ttl': 30, 'ack_ttl': 45}},
                },
                'payload': {},
                'followers': [],
                'response': {'value#xget': '/response/payload/value'},
            },
        ],
        'initial_steps': [{'step': 'push'}],
    },
}


def get_statuses_steps(pgsql):
    cursor = pgsql['communication_scenario'].cursor()
    cursor.execute('SELECT step FROM statuses;')
    return list(cursor)


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=SCENARIOS)
@pytest.mark.config(
    COMMUNICATION_SCENARIO_STATUSES_CLEANUP_SETTINGS={
        'delete_interval_ms': 0,
        'response_ttl_seconds': 0,
    },
)
async def test_statuses_cleanup(
        taxi_communication_scenario, mock_ucommunications, pgsql, testpoint,
):
    @testpoint('run-steps/processed-step')
    def processed_step(_):
        pass

    await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'test_go',
            'recipient': {'go_user_id': '1'},
            'parameters': {},
            'channels': {
                'push': {'channel_type': 'push_go', 'intent': 'test'},
            },
        },
    )

    await processed_step.wait_call()
    [(step,)] = get_statuses_steps(pgsql)
    assert step == 'push'

    await taxi_communication_scenario.run_task(
        'distlock/statuses-cleanup-worker',
    )
    assert not get_statuses_steps(pgsql)


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=SCENARIOS)
async def test_status_change(
        taxi_communication_scenario, mockserver, testpoint,
):
    @testpoint('run-steps/processed-step')
    def processed_step(_):
        pass

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _push(request):
        url = request.json['callback']['url']
        parse_result = urllib.parse.urlparse(url)
        queries = urllib.parse.parse_qs(parse_result.query)
        nonlocal event_id
        event_id = queries['event_id']
        return {'payload': {'value': 1234}}

    event_id = None
    start_response = await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'test_go',
            'recipient': {'go_user_id': '1'},
            'parameters': {},
            'channels': {
                'push': {'channel_type': 'push_go', 'intent': 'test'},
            },
        },
    )
    await processed_step.wait_call()

    await taxi_communication_scenario.get(
        '/v1/report-event',
        params={'event_id': event_id, 'event_name': 'delivered'},
    )
    await processed_step.wait_call()

    response = await taxi_communication_scenario.post(
        'v1/status', json=start_response.json(),
    )
    assert response.json() == {
        'steps': [
            {
                'step': 'push',
                'status': 'delivered',
                'response': {'value': 1234},
            },
        ],
    }
