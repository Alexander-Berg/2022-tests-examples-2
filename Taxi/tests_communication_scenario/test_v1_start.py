import pytest

import tests_communication_scenario.common as common

CONFIG = {
    'push_sms': {
        'steps': [
            {
                'name': 'push',
                'channel': {
                    'type': 'go/push/user',
                    'settings': {'push_go': {'ttl': 30, 'ack_ttl': 45}},
                },
                'payload': {
                    'text#xget': '/parameters/push_text',
                    'id#xget': '/parameters/id/push',
                },
                'followers': [],
                'recipients': {
                    'go_user_id': {
                        'applications': ['android'],
                        'max_age_hours': 1000 * 1000,
                    },
                },
            },
            {
                'name': 'sms',
                'channel': {
                    'type': 'go/sms/user',
                    'settings': {'sms': {'ttl': 30}},
                },
                'payload': {'text#xget': '/parameters/sms_text'},
                'followers': [],
                'response': {'message#xget': '/response/message'},
            },
        ],
        'initial_steps': [{'step': 'push'}, {'step': 'sms'}],
    },
    'push_then_sms': {
        'steps': [
            {
                'name': 'push',
                'channel': {
                    'type': 'go/push/user',
                    'settings': {'push_go': {'ttl': 30, 'ack_ttl': 45}},
                },
                'payload': {'payload': {}},
                'followers': [
                    {
                        'step': 'sms',
                        'event': 'sent',
                        'start_if#and': [
                            {'value#xget': '/parameters/start/sms'},
                            {
                                'value#equal': [
                                    {'value#string': 'eats'},
                                    {'value#xget': '/parameters/application'},
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                'name': 'sms',
                'channel': {
                    'type': 'go/sms/user',
                    'settings': {'sms': {'ttl': 30}},
                },
                'payload': {'text': '123'},
                'followers': [],
            },
        ],
        'initial_steps': [
            {'step': 'push'},
            {
                'step': 'sms',
                'start_if#xget': '/parameters/start/sms_immediately',
            },
        ],
    },
}

DEFAULT_PARAMETERS = {
    'sms_text': 'sms!',
    'push_text': 'push!',
    'id': {'push': '123'},
}

DEFAULT_BODY = {
    'scenario': 'push_sms',
    'recipient': {'go_user_id': '1'},
    'parameters': DEFAULT_PARAMETERS,
    'channels': {
        'push': {'channel_type': 'push_go', 'intent': 'test'},
        'sms': {'channel_type': 'sms', 'intent': 'test'},
    },
}


async def test_unknown_scenario(
        taxi_communication_scenario, mock_ucommunications,
):
    response = await common.start(taxi_communication_scenario, DEFAULT_BODY)
    assert response.status_code == 404


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=CONFIG)
async def test_deprecated_parameters(
        taxi_communication_scenario, pgsql, mock_ucommunications,
):
    response = await common.start(taxi_communication_scenario, DEFAULT_BODY)
    assert response.status_code == 200
    cursor = pgsql['communication_scenario'].cursor()
    cursor.execute('SELECT parameters FROM launches;')
    [(params,)] = list(cursor)
    assert params == {
        'sms': {'text': 'sms!'},
        'push': {'text': 'push!', 'id': '123'},
    }


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=CONFIG)
async def test_start_parameters(
        taxi_communication_scenario, pgsql, mock_ucommunications,
):
    response = await common.start(taxi_communication_scenario, DEFAULT_BODY)
    assert response.status_code == 200
    cursor = pgsql['communication_scenario'].cursor()
    cursor.execute('SELECT start_parameters FROM launches;')
    [(params,)] = list(cursor)
    assert params == DEFAULT_PARAMETERS


@pytest.mark.parametrize('start_sms', [True, False])
@pytest.mark.parametrize('application', ['eats', 'go'])
@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=CONFIG)
async def test_start_if(
        taxi_communication_scenario, mockserver, start_sms, application,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _push(_):
        return {}

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _sms(_):
        assert start_sms and application == 'eats'
        return {
            'message': 'OK',
            'code': '200',
            'content': 'content',
            'message_id': '12f7ccb4dcf14f8ca1fd1da2f994dc99',
            'status': 'sent',
        }

    response = await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'push_then_sms',
            'recipient': {'go_user_id': '1'},
            'parameters': {
                'start': {'sms': start_sms, 'sms_immediately': False},
                'application': application,
            },
            'channels': {
                'push': {'channel_type': 'push_go', 'intent': 'test'},
                'sms': {'channel_type': 'sms', 'intent': 'test'},
            },
        },
    )
    assert response.status_code == 200


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=CONFIG)
@pytest.mark.parametrize(
    'header', [({'X-Idempotency-Token': '123'}, 1), (None, 4)],
)
async def test_idempotency_completed(
        taxi_communication_scenario, mock_ucommunications, header,
):
    token, expected_count = header
    launch_ids = set()
    for _ in range(4):
        response = await common.start(
            taxi_communication_scenario, DEFAULT_BODY, headers=token,
        )
        assert response.status_code == 200
        launch_ids.add(response.json()['launch_id'])
    assert None not in launch_ids
    assert len(launch_ids) == expected_count


@pytest.mark.pgsql('communication_scenario', files=['idempotency_pending.sql'])
@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=CONFIG)
async def test_idempotency_pending(
        taxi_communication_scenario, mock_ucommunications,
):
    response = await common.start(
        taxi_communication_scenario,
        DEFAULT_BODY,
        headers={'X-Idempotency-Token': '123'},
    )
    assert response.status_code == 409


@pytest.mark.pgsql('communication_scenario', files=['idempotency_failed.sql'])
@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=CONFIG)
async def test_idempotency_failed(
        taxi_communication_scenario, mock_ucommunications,
):
    response = await common.start(
        taxi_communication_scenario,
        DEFAULT_BODY,
        headers={'X-Idempotency-Token': '123'},
    )
    assert response.status_code == 200


@pytest.mark.pgsql('communication_scenario', files=['idempotency_expired.sql'])
@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=CONFIG)
async def test_idempotency_pending_expired(
        taxi_communication_scenario, mock_ucommunications,
):
    response = await common.start(
        taxi_communication_scenario,
        DEFAULT_BODY,
        headers={'X-Idempotency-Token': '123'},
    )
    assert response.status_code == 200


@pytest.mark.config(COMMUNICATION_SCENARIO_SCENARIOS=CONFIG)
async def test_yandex_uid(taxi_communication_scenario, mockserver):
    items = [
        {
            'id': '123',
            'application': 'android',
            'created': '2022-04-18T07:00:00Z',
            'updated': '2013-04-18T07:00:00Z',
        },
        {
            'id': '124',
            'application': 'android',
            'created': '2022-04-18T06:00:00Z',
            'updated': '2022-04-18T06:00:00Z',
        },
        {
            'id': '125',
            'application': 'unknown',
            'created': '2022-04-18T07:00:00Z',
            'updated': '2022-04-18T07:00:00Z',
        },
    ]

    @mockserver.json_handler('/user-api/users/search')
    def _convert(request):
        cursor = request.json.get('cursor')
        item_index = int(cursor) if cursor else 0
        response = {'items': items[item_index : item_index + 1]}
        if item_index + 1 < len(items):
            response.update(cursor=str(item_index + 1))

        return response

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def push(request):
        assert request.json['user'] == '123'
        return {}

    await common.start(
        taxi_communication_scenario,
        {
            'scenario': 'push_sms',
            'recipient': {'yandex_uid': '1'},
            'parameters': DEFAULT_PARAMETERS,
            'channels': {
                'push': {'channel_type': 'push_go', 'intent': 'test'},
                'sms': {'channel_type': 'sms', 'intent': 'test'},
            },
        },
    )
    await push.wait_call()
