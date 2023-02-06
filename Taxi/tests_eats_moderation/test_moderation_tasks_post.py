import pytest


@pytest.fixture(name='mock_processing', autouse=True)
def _mock_processing(mockserver):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event(request):

        return mockserver.make_response(status=200, json={'event_id': '123'})

    return _create_event


async def test_moderation_tasks_post_happy_path(
        taxi_eats_moderation,
        mock_processing,
        get_moderation_task_by_tag,
        get_context,
        get_payload,
):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks',
        json={
            'context': '{}',
            'payloads': ['{"data": "1"}', '{"data": "2"}', '{"data": "3"}'],
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 200
    json = response.json()
    assert 'tag' in json
    task = get_moderation_task_by_tag(json['tag'])
    assert task[0]['task_id']
    assert task[0]['context_id'] == 1
    assert task[0]['payload_id'] == 1
    assert task[0]['created_at']
    assert task[0]['updated_at']
    assert task[0]['tag'] == json['tag']
    assert task[1]['task_id']
    assert task[1]['context_id'] == 1
    assert task[1]['payload_id'] == 2
    assert task[1]['created_at']
    assert task[1]['updated_at']
    assert task[1]['tag'] == json['tag']
    assert task[2]['task_id']
    assert task[2]['context_id'] == 1
    assert task[2]['payload_id'] == 3
    assert task[2]['created_at']
    assert task[2]['updated_at']
    assert task[2]['tag'] == json['tag']

    context = get_context(1)
    assert context['context_id'] == 1
    assert context['value'] == '{}'

    payload = get_payload(1)
    assert payload['payload_id'] == 1
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{"data":"1"}'
    payload = get_payload(2)
    assert payload['payload_id'] == 2
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{"data":"2"}'
    payload = get_payload(3)
    assert payload['payload_id'] == 3
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{"data":"3"}'

    response2 = await taxi_eats_moderation.post(
        '/moderation/v1/tasks',
        json={
            'context': '{}',
            'payloads': [
                '{"data": "1", "external_id": "1"}',
                '{"data": "2"}',
                '{"data": "3"}',
            ],
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response2.status_code == 200
    json = response2.json()
    assert 'tag' in json
    task = get_moderation_task_by_tag(json['tag'])
    assert task[0]['task_id']
    assert task[0]['context_id'] == 1
    assert task[0]['payload_id'] == 4
    assert task[0]['created_at']
    assert task[0]['updated_at']
    assert task[0]['tag'] == json['tag']
    assert task[1]['task_id']
    assert task[1]['context_id'] == 1
    assert task[1]['payload_id'] == 5
    assert task[1]['created_at']
    assert task[1]['updated_at']
    assert task[1]['tag'] == json['tag']
    assert task[2]['task_id']
    assert task[2]['context_id'] == 1
    assert task[2]['payload_id'] == 6
    assert task[2]['created_at']
    assert task[2]['updated_at']
    assert task[2]['tag'] == json['tag']

    context = get_context(1)
    assert context['context_id'] == 1
    assert context['value'] == '{}'

    payload = get_payload(4)
    assert payload['payload_id'] == 4
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert payload['external_id'] == '1'
    assert payload['value'] == '{"data":"1","external_id":"1"}'
    payload = get_payload(5)
    assert payload['payload_id'] == 5
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{"data":"2"}'
    payload = get_payload(6)
    assert payload['payload_id'] == 6
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{"data":"3"}'


async def test_moderation_tasks_post_parse_error(
        taxi_eats_moderation, mock_processing,
):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks',
        json={
            'context': '{}',
            'payloads': ['{"data": "1","}', '{"data": "2"}', '{"data": "3"}'],
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'JSON parse error at line 1 column 16: '
            'Missing a closing quotation mark in string.'
        ),
    }


async def test_moderation_tasks_post_error_400(
        taxi_eats_moderation, mockserver,
):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event_400(request):

        return mockserver.make_response(
            status=400, json={'code': 'invalid_payload', 'message': 'error'},
        )

    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks',
        json={
            'context': '{}',
            'payloads': ['{}'],
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'error'}


async def test_moderation_tasks_post_error_409(
        taxi_eats_moderation, mockserver,
):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event_409(request):

        return mockserver.make_response(
            status=409, json={'code': 'race_condition', 'message': 'error'},
        )

    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks',
        json={
            'context': '{}',
            'payloads': ['{}'],
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'error'}


async def test_moderation_tasks_post_error_404(
        taxi_eats_moderation, mockserver,
):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event_404(request):

        return mockserver.make_response(
            status=404, json={'code': 'race_condition', 'message': 'error'},
        )

    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks',
        json={
            'context': '{}',
            'payloads': ['{}'],
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Unexpected HTTP response code \'404\' '
            'for \'POST /v1/scope/queue/create-event\''
        ),
    }
