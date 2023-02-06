import pytest

from testsuite.utils import matching

import tests_communication_scenario.common as common

SCENARIOS = {
    'eda_push': {
        'steps': [
            {
                'name': 'push',
                'channel': {
                    'type': '',
                    'settings': {'push_eats': {'ttl': 23}},
                },
                'payload': {},
                'followers': [],
            },
        ],
        'initial_steps': [{'step': 'push'}],
    },
}


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=SCENARIOS)
async def test_eater_uuid(taxi_communication_scenario, mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def push(request):
        assert request.json == {
            'service': 'eda-client',
            'client_id': '1',
            'intent': 'test',
            'data': {'abc': '123'},
            'ttl': 23,
            'return_notification_body': True,
            'meta': {
                'communication_scenario': {'launch_id': matching.uuid_string},
            },
        }
        return {'notification_id': '123123123'}

    await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'eda_push',
            'recipient': {'eater_uuid': '1'},
            'parameters': {},
            'channels': {
                'push': {
                    'channel_type': 'push_eats',
                    'intent': 'test',
                    'data': {'abc': '123'},
                },
            },
        },
    )
    await push.wait_call()


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=SCENARIOS)
async def test_eater_id(taxi_communication_scenario, mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def push(request):
        assert request.json == {
            'service': 'eda-client',
            'client_id': 'abacaba',
            'intent': 'test',
            'data': {'abc': '123'},
            'ttl': 23,
            'return_notification_body': True,
            'meta': {
                'communication_scenario': {'launch_id': matching.uuid_string},
            },
        }
        return {'notification_id': '123123123'}

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def convert(request):
        assert request.json == {
            'id': 'qwerty12345',
            'with_soft_deleted': False,
        }
        return {
            'eater': {
                'id': 'qwerty12345',
                'uuid': 'abacaba',
                'created_at': '2013-07-12T07:00:00Z',
                'updated_at': '2013-07-12T07:00:00Z',
            },
        }

    await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'eda_push',
            'recipient': {'eater_id': 'qwerty12345'},
            'parameters': {},
            'channels': {
                'push': {
                    'channel_type': 'push_eats',
                    'intent': 'test',
                    'data': {'abc': '123'},
                },
            },
        },
    )
    await push.wait_call()
    assert convert.times_called == 1
