import pytest

from testsuite.utils import matching

import tests_communication_scenario.common as common

SCENARIOS = {
    'all_channels': {
        'steps': [
            {
                'name': 'go',
                'channel': {
                    'type': 'go/push/user',
                    'settings': {'push_go': {'ttl': 30, 'ack_ttl': 45}},
                },
                'payload': {},
                'followers': [],
            },
            {
                'name': 'sms',
                'channel': {
                    'type': 'go/sms/user',
                    'settings': {'sms': {'ttl': 30}},
                },
                'payload': {'text': 'abacaba'},
                'followers': [],
                'response': {},
            },
            {
                'name': 'eats',
                'channel': {
                    'type': '',
                    'settings': {'push_eats': {'ttl': 23}},
                },
                'payload': {},
                'followers': [],
            },
        ],
        'initial_steps': [{'step': 'go'}, {'step': 'sms'}, 'eats'],
    },
}


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=SCENARIOS)
async def test_meta(taxi_communication_scenario, mockserver):
    def check_request(request):
        assert request.json['meta'] == {
            'communication_scenario': {'launch_id': matching.uuid_string},
            'abacaba': 123,
        }

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def push_go(request):
        check_request(request)
        return {}

    @mockserver.json_handler('/client-notify/v2/push')
    def push_eats(request):
        check_request(request)
        return {'notification_id': '123123123'}

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def sms(request):
        check_request(request)
        return {
            'message': 'OK',
            'code': '200',
            'content': 'content',
            'message_id': '12f7ccb4dcf14f8ca1fd1da2f994dc99',
            'status': 'sent',
        }

    meta = {'abacaba': 123}
    await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'all_channels',
            'recipient': {
                'go_user_id': '1',
                'personal_phone_id': '1',
                'eater_uuid': '123',
                'eater_id': '123',
            },
            'parameters': {},
            'channels': {
                'go': {
                    'channel_type': 'push_go',
                    'intent': 'test',
                    'meta': meta,
                },
                'sms': {'channel_type': 'sms', 'intent': 'test', 'meta': meta},
                'eats': {
                    'channel_type': 'push_eats',
                    'intent': 'test',
                    'meta': meta,
                },
            },
        },
    )
    await push_go.wait_call()
    await push_eats.wait_call()
    await sms.wait_call()
