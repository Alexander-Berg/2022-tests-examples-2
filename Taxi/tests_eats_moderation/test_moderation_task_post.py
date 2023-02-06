import pytest

CONFIG = [
    {
        'scope': 'eda',
        'types': [
            {
                'queue': 'restapp_moderation_hero',
                'reason_groups': [],
                'fields_for_merge': {'context': ['place_id'], 'payload': []},
            },
        ],
    },
]


@pytest.fixture(name='mock_processing', autouse=True)
def _mock_processing(mockserver):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event(request):

        return mockserver.make_response(status=200, json={'event_id': '123'})

    return _create_event


@pytest.fixture(name='mock_core', autouse=True)
def _mock_core_restapp(mockserver):
    @mockserver.json_handler('/eats-core-restapp/v1/moderation-tasks/hide')
    def _mock_core(request):

        return mockserver.make_response(status=204)

    return _mock_core


@pytest.mark.config(EATS_MODERATION_OBJECTS=CONFIG)
async def test_moderation_task_post_happy_path(
        taxi_eats_moderation,
        mock_processing,
        get_moderation_task,
        get_context,
        get_payload,
        get_moderation,
        stq,
):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/task',
        json={
            'context': '{"place_id":"12345"}',
            'payload': '{}',
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 200
    json = response.json()
    assert 'task_id' in json
    task = get_moderation_task(json['task_id'])
    assert task['task_id'] == json['task_id']
    assert task['context_id'] == 1
    assert task['payload_id'] == 1
    assert task['created_at']
    assert task['updated_at']
    assert not task['tag']
    context = get_context(1)
    assert context['context_id'] == 1
    assert context['value'] == '{"place_id":"12345"}'
    payload = get_payload(1)
    assert payload['payload_id'] == 1
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{}'
    assert stq.eats_moderation_hide_old_moderation.times_called == 1
    arg = stq.eats_moderation_hide_old_moderation.next_call()
    assert arg['args'] == []
    assert arg['kwargs']['context'] == '{"place_id":"12345"}'
    assert arg['kwargs']['queue'] == 'restapp_moderation_hero'
    assert arg['kwargs']['status'] == 'new'
    assert arg['kwargs']['task_id'] == json['task_id']

    response = await taxi_eats_moderation.post(
        '/internal/v1/moderator',
        json={'task_id': json['task_id'], 'context': {'subject': 'subject'}},
    )

    moderations = get_moderation(json['task_id'])
    assert len(moderations) == 2
    assert moderations[0]['status'] == 'new'
    assert moderations[1]['status'] == 'process'

    await taxi_eats_moderation.invalidate_caches(clean_update=False)

    response = await taxi_eats_moderation.post(
        '/moderation/v1/task',
        json={
            'context': '{"place_id":"12345"}',
            'payload': '{"field":"value"}',
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 200
    json2 = response.json()
    assert 'task_id' in json
    task = get_moderation_task(json2['task_id'])
    assert task['task_id'] == json2['task_id']
    assert task['context_id'] == 1
    assert task['payload_id'] == 2
    assert task['created_at']
    assert task['updated_at']
    assert not task['tag']
    context = get_context(1)
    assert context['context_id'] == 1
    assert context['value'] == '{"place_id":"12345"}'
    payload = get_payload(1)
    assert payload['payload_id'] == 1
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{}'

    moderations = get_moderation(json['task_id'])
    assert len(moderations) == 3
    assert moderations[0]['status'] == 'new'
    assert moderations[1]['status'] == 'process'
    assert moderations[2]['status'] == 'deleted'
    moderations = get_moderation(json2['task_id'])
    assert moderations[0]['status'] == 'new'

    assert stq.eats_moderation_hide_old_moderation.times_called == 1
    arg = stq.eats_moderation_hide_old_moderation.next_call()
    assert arg['args'] == []
    assert arg['kwargs']['context'] == '{"place_id":"12345"}'
    assert arg['kwargs']['queue'] == 'restapp_moderation_hero'
    assert arg['kwargs']['status'] == 'new'
    assert arg['kwargs']['task_id'] == json2['task_id']


async def test_moderation_task_post_parse_error(
        taxi_eats_moderation, get_moderation_task, get_context, get_payload,
):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/task',
        json={
            'context': '{}',
            'payload': '{"}',
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'JSON parse error at line 1 column 4: '
            'Missing a closing quotation mark in string.'
        ),
    }


@pytest.mark.pgsql(
    'eats_moderation', files=['pg_eats_moderation_task_post.sql'],
)
async def test_moderation_task_post_already_closed(
        taxi_eats_moderation, get_moderation_task, get_context, get_payload,
):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/task',
        json={
            'context': '{}',
            'payload': '{}',
            'task_id': '123',
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 400


async def test_moderation_task_post_404(taxi_eats_moderation, mock_processing):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/task',
        json={
            'context': '{}',
            'payload': '{}',
            'task_id': '123',
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )
    assert response.status_code == 404


async def test_moderation_task_post_update(
        taxi_eats_moderation,
        mock_processing,
        get_moderation_task,
        get_context,
        get_payload,
):
    response = await taxi_eats_moderation.post(
        '/moderation/v1/task',
        json={
            'context': '{"abc":"def"}',
            'payload': '{}',
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 200
    json = response.json()
    task_id = json['task_id']
    assert 'task_id' in json
    task = get_moderation_task(task_id)
    assert task['task_id'] == task_id
    assert task['context_id'] == 1
    assert task['payload_id'] == 1
    assert task['created_at']
    assert task['updated_at']
    assert not task['tag']
    context = get_context(1)
    assert context['context_id'] == 1
    assert context['value'] == '{"abc":"def"}'
    payload = get_payload(1)
    assert payload['payload_id'] == 1
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{}'

    response = await taxi_eats_moderation.post(
        '/moderation/v1/task',
        json={
            'context': '{"abc":"def"}',
            'payload': '{"abc":"def"}',
            'task_id': task_id,
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )
    assert response.status_code == 200
    json = response.json()
    assert json['task_id'] == task_id
    task = get_moderation_task(task_id)
    assert task['task_id'] == task_id
    assert task['context_id'] == 1
    assert task['payload_id'] == 2
    assert task['created_at']
    assert task['updated_at']
    assert not task['tag']
    context = get_context(1)
    assert context['context_id'] == 1
    assert context['value'] == '{"abc":"def"}'
    payload = get_payload(1)
    assert payload['payload_id'] == 1
    assert payload['scope'] == 'eda'
    assert payload['queue'] == 'restapp_moderation_hero'
    assert not payload['external_id']
    assert payload['value'] == '{}'
    payload2 = get_payload(2)
    assert payload2['payload_id'] == 2
    assert payload2['scope'] == 'eda'
    assert payload2['queue'] == 'restapp_moderation_hero'
    assert not payload2['external_id']
    assert payload2['value'] == '{"abc":"def"}'


async def test_moderation_task_post_error_400(
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
        '/moderation/v1/task',
        json={
            'context': '{}',
            'payload': '{}',
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'error'}


async def test_moderation_task_post_error_409(
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
        '/moderation/v1/task',
        json={
            'context': '{}',
            'payload': '{}',
            'scope': 'eda',
            'queue': 'restapp_moderation_hero',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'error'}


async def test_moderation_task_post_error_404(
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
        '/moderation/v1/task',
        json={
            'context': '{}',
            'payload': '{}',
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


async def test_hide_old_stq(stq_runner, mock_core):
    await stq_runner.eats_moderation_hide_old_moderation.call(
        task_id='fake_task',
        kwargs={
            'task_id': 'moderation_task_id',
            'queue': 'restapp_moderation_hero',
            'status': 'new',
            'context': '{"place_id":"12345"}',
        },
    )

    assert mock_core.times_called == 1
    assert mock_core.next_call()['request'].json == {
        'items': [
            {
                'context': '{"place_id":"12345"}',
                'queue': 'restapp_moderation_hero',
                'status': 'new',
                'task_id': 'moderation_task_id',
            },
        ],
    }
