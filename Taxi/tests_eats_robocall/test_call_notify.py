import pytest


@pytest.mark.pgsql('eats_robocall', files=['add_calls.sql'])
@pytest.mark.experiments3(filename='scenarios.json')
@pytest.mark.parametrize(
    'status_code, request_body, current_action_id',
    [
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'timeout'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'originate_action',
                    'action_retry_times': 1,
                },
            },
            None,
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {'payload': {}, 'scenario_name': 'scenario_1'},
            },
            'originate_action',
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'originate_action',
                    'action_retry_times': 1,
                    'payload': {'user_name': 'Илья'},
                },
            },
            'playback_action_speak',
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'abonent-hangup'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'originate_action',
                    'action_retry_times': 1,
                },
            },
            None,
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'hangup': {
                            'cause': 'normal-clearing',
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'originate_action',
                    'action_retry_times': 1,
                },
            },
            None,
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'failed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'originate_action',
                    'action_retry_times': 1,
                },
            },
            None,
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'completed'},
                        },
                    },
                    {
                        'external_id': 'abacaba2',
                        'playback': {
                            'playback': {
                                'speak': {
                                    'text': 'Привет. Как дела, {user_name}?',
                                },
                            },
                            'status': {'state': 'timeout'},
                        },
                    },
                ],
                'last_action': 1,
                'context': {
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'playback_action_speak',
                    'action_retry_times': 1,
                    'payload': {'user_name': 'Ilya'},
                },
            },
            None,
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'ask': {
                            'allowed_dtmf': '123',
                            'immediate_input': False,
                            'input_mode': 'dtmf',
                            'no_input_timeout_ms': 15000,
                            'playback': {
                                'play': {
                                    'id': 'question1',
                                    'path': 's3:/voices/question1.wav',
                                },
                            },
                            'status': {
                                'state': 'completed',
                                'input_value': {'dtmf': 2},
                            },
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'ask_action_dtmf',
                    'action_retry_times': 1,
                },
            },
            'ask_action_text',
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'ask': {
                            'allowed_dtmf': '123',
                            'immediate_input': False,
                            'input_mode': 'text',
                            'no_input_timeout_ms': 15000,
                            'playback': {
                                'play': {
                                    'id': 'question1',
                                    'path': 's3:/voices/question1.wav',
                                },
                            },
                            'status': {
                                'state': 'completed',
                                'input_value': {'text': 'Я не знаю'},
                            },
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'ask_action_text',
                    'action_retry_times': 1,
                },
            },
            'wait_action',
        ),
        (
            400,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'ask': {
                            'allowed_dtmf': '123',
                            'immediate_input': False,
                            'input_mode': 'text',
                            'no_input_timeout_ms': 15000,
                            'playback': {
                                'play': {
                                    'id': 'question1',
                                    'path': 's3:/voices/question1.wav',
                                },
                            },
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'ask_action_text',
                    'action_retry_times': 1,
                },
            },
            None,
        ),
        (
            500,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
            },
            None,
        ),
        (
            500,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'current_action_id': 'originate_action',
                    'scenario_name': '',
                    'action_retry_times': 1,
                },
            },
            None,
        ),
        (
            200,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'action_retry_times': 0,
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'cycled_action',
                },
            },
            'default_farewell',
        ),
        (
            500,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'action_retry_times': 1,
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'wrong_next_action_id',
                },
            },
            None,
        ),
        (
            500,
            {
                'call_external_id': 'some_id',
                'ivr_flow_id': 'some_id',
                'call_guid': 'some_guid',
                'service_number': '+2615',
                'abonent_number': '+3755',
                'direction': 'outgoing',
                'actions': [
                    {
                        'external_id': 'abacaba',
                        'originate': {
                            'phone_number': '+375445571982',
                            'timeout_sec': 15,
                            'status': {'state': 'completed'},
                        },
                    },
                ],
                'last_action': 0,
                'context': {
                    'payload': {},
                    'action_retry_times': 1,
                    'scenario_name': 'scenario_1',
                    'current_action_id': 'to_empty_action_body',
                },
            },
            None,
        ),
    ],
    ids=[
        '200 abonent didn\'t answer',
        '200 response first action',
        '200 response with current_id',
        '200 abonent hangup',
        '200 scenario hangup',
        '200 status = failed ~ call ends',
        '200 action timeout',
        '200 dtmf ask action',
        '200 text ask action',
        '400 ask action',
        '500 without call context',
        '500 without scenario name',
        '200 no action retries left',
        '500 next nonexistent action',
        '500 empty action body',
    ],
)
async def test_call_notify(
        # ---- fixtures ----
        taxi_eats_robocall,
        mockserver,
        # ---- parameters ----
        status_code,
        request_body,
        current_action_id,
):
    response = await taxi_eats_robocall.post(
        '/v1/ivr-framework/call-notify',
        headers={'X-Idempotency-Token': 'Random-Idempotency-Key'},
        json=request_body,
    )

    assert response.status_code == status_code
    if current_action_id is not None:
        assert (
            response.json()['context']['current_action_id']
            == current_action_id
        )
