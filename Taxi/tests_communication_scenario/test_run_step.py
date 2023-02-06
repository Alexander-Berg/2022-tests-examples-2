import pytest

import tests_communication_scenario.common as common

SCENARIOS = {
    'push_continues_push': {
        'steps': [
            {
                'name': 'first_push',
                'channel': {
                    'type': 'go/push/user',
                    'settings': {'push_go': {'ttl': 30, 'ack_ttl': 45}},
                },
                'payload': {'payload': {}},
                'followers': [{'step': 'second_push', 'event': 'sent'}],
            },
            {
                'name': 'second_push',
                'channel': {
                    'type': 'go/sms/user',
                    'settings': {'push_go': {'ttl': 30}},
                },
                'payload': {'payload': {}},
                'followers': [],
            },
        ],
        'initial_steps': [{'step': 'first_push'}],
    },
    'push_or_sms': {
        'steps': [
            {
                'name': 'push',
                'channel': {
                    'type': 'go/push/user',
                    'settings': {'push_go': {'ttl': 30, 'ack_ttl': 45}},
                },
                'payload': {'payload': {}},
                'followers': [
                    {'step': 'sms', 'event': 'deadline'},
                    {'step': 'sms_error', 'event': 'error'},
                ],
            },
            {
                'name': 'sms',
                'channel': {
                    'type': 'go/sms/user',
                    'settings': {'sms': {'ttl': 30}},
                },
                'payload': {'text': 'abracadabra'},
                'followers': [],
            },
            {
                'name': 'sms_error',
                'channel': {
                    'type': 'go/sms/user',
                    'settings': {'sms': {'ttl': 30}},
                },
                'payload': {'text': 'abracadabra'},
                'followers': [],
            },
        ],
        'initial_steps': [{'step': 'push'}],
    },
}


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=SCENARIOS)
async def test_serial_push(taxi_communication_scenario, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def push(_):
        return {}

    await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'push_continues_push',
            'recipient': {'go_user_id': '1'},
            'parameters': {},
            'channels': {
                'first_push': {'channel_type': 'push_go', 'intent': 'test'},
                'second_push': {'channel_type': 'push_go', 'intent': 'test'},
            },
        },
    )
    await push.wait_call()
    await push.wait_call()


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=SCENARIOS)
async def test_push_or_sms(taxi_communication_scenario, mockserver, testpoint):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def push(request):
        callback_deadline = request.json['callback']['url'].replace(
            'event_name=delivered', 'event_name=deadline',
        )
        assert callback_deadline.startswith(mockserver.base_url)
        nonlocal callback
        callback = callback_deadline.replace(mockserver.base_url, '')
        return {}

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def sms(_):
        return {
            'message': 'OK',
            'code': '200',
            'content': 'content',
            'message_id': '12f7ccb4dcf14f8ca1fd1da2f994dc99',
            'status': 'sent',
        }

    @testpoint('run-steps/processed-step')
    def processed_step(_):
        pass

    callback = None
    await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'push_or_sms',
            'recipient': {'go_user_id': '1'},
            'parameters': {},
            'channels': {
                'push': {'channel_type': 'push_go', 'intent': 'test'},
                'sms': {'channel_type': 'sms', 'intent': 'test'},
                'sms_error': {'channel_type': 'sms', 'intent': 'test'},
            },
        },
    )

    await push.wait_call()
    await processed_step.wait_call()
    await taxi_communication_scenario.get(callback)
    await sms.wait_call()
    await processed_step.wait_call()


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=SCENARIOS)
async def test_push_error(
        taxi_communication_scenario,
        mockserver,
        mock_ucommunications,
        testpoint,
):
    @testpoint('run-steps/processed-step')
    def processed_step(data):
        assert data.get('step') == expected_calls.pop(0)

    @mockserver.json_handler('user-api/user_phones/by_personal/retrieve_bulk')
    def _user_api(_):
        return {'items': []}

    expected_calls = ['push', 'sms_error']
    await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'push_or_sms',
            'recipient': {'personal_phone_id': '1'},
            'parameters': {},
            'channels': {
                'push': {'channel_type': 'push_go', 'intent': 'test'},
                'sms': {'channel_type': 'sms', 'intent': 'test'},
                'sms_error': {'channel_type': 'sms', 'intent': 'test'},
            },
        },
    )
    assert await processed_step.wait_call()
    assert await processed_step.wait_call()
