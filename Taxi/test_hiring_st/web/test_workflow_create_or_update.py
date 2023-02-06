import uuid

import pytest


async def test_creation(web_app_client, load_json, create_workflow):
    data = load_json('workflow.json')
    workflow = await create_workflow(data)
    assert workflow['workflow_id'] == data['workflow_id']


async def test_update(web_app_client, load_json, create_workflow):
    data1 = load_json('workflow_original.json')
    workflow1 = await create_workflow(data1)

    data2 = load_json('workflow_update.json')
    workflow2 = await create_workflow(data2)

    assert workflow2['workflow_id'] == workflow1['workflow_id']
    assert (
        workflow2['description'] == data2['description']
    ), 'Описание обновлено'
    assert workflow2['resolutions'] == workflow1['resolutions']
    assert workflow2['statuses'] == workflow1['statuses']
    assert workflow2['transitions'] == workflow1['transitions']


async def test_idempotency(web_app_client, load_json, create_workflow):
    request_id = uuid.uuid4().hex

    data1 = load_json('workflow_original.json')
    workflow1 = await create_workflow(data=data1, request_id=request_id)

    data2 = load_json('workflow_update.json')
    workflow2 = await create_workflow(data=data2, request_id=request_id)

    assert workflow2 == workflow1


@pytest.mark.parametrize('workflow_id', ['-/-0-//-l-', '//', '/-', '-/'])
async def test_name(web_app_client, load_json, workflow_id):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    data['workflow_id'] = workflow_id
    response = await web_app_client.post('/v1/workflow', json=data)
    assert response.status == 400, 'Дичь нельзя'
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {
            'reason': (
                f'Invalid value for workflow_id: {workflow_id!r} '
                'must match r\'^(/?\\w[-\\w]?)+$\''
            ),
        },
    }


async def test_statuses_count(web_app_client, load_json):
    data1 = load_json('workflow.json')
    data1['request_id'] = uuid.uuid4().hex
    data1['statuses'] = []
    response1 = await web_app_client.post('/v1/workflow', json=data1)
    assert response1.status == 400, 'Хотябы один статус должен быть'
    content1 = await response1.json()
    assert content1 == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {
            'reason': (
                f'Invalid value for statuses: [] '
                'number of items must be greater than or equal to 1'
            ),
        },
    }

    data2 = load_json('workflow.json')
    data2['request_id'] = uuid.uuid4().hex
    data2['statuses'] = [{'status': f'status{x}'} for x in range(101)]
    response2 = await web_app_client.post('/v1/workflow', json=data2)
    assert response2.status == 400, 'Слишком много статусов'
    content2 = await response2.json()
    reason = content2['details'].pop('reason')
    assert content2 == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {},
    }
    assert reason.startswith('Invalid value for statuses:')
    assert reason.endswith('number of items must be less than or equal to 100')


@pytest.mark.parametrize('status_name', ['-/-0-//-l-', '//', '/-', '-/'])
async def test_statuses_name(web_app_client, load_json, status_name):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    data['statuses'] = [
        {'status': status_name, 'initial': True, 'terminal': True},
    ]
    response = await web_app_client.post('/v1/workflow', json=data)
    assert response.status == 400, 'Дичь нельзя'
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {
            'reason': (
                f'Invalid value for status: '
                f'{status_name!r} must match r\'^\\w+$\''
            ),
        },
    }


async def test_statuses_missing_ends(web_app_client, load_json):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    data['statuses'] = [{'status': 'open'}]
    response = await web_app_client.post('/v1/workflow', json=data)
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'WORKFLOW_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'NO_INITIAL_STATUS'
    assert content['details']['errors'][1]['code'] == 'NO_TERMINAL_STATUS'


async def test_statuses_too_many_ends(web_app_client, load_json):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    data['statuses'] = [
        {'status': 'open', 'initial': True, 'terminal': True},
        {'status': 'close', 'initial': True, 'terminal': True},
    ]
    response = await web_app_client.post('/v1/workflow', json=data)
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'WORKFLOW_DEFINITION_ERROR'
    assert (
        content['details']['errors'][0]['code'] == 'MULTIPLE_INITIAL_STATUSES'
    )
    assert content['details']['errors'][0]['index'] == 0
    assert (
        content['details']['errors'][1]['code'] == 'MULTIPLE_INITIAL_STATUSES'
    )
    assert content['details']['errors'][1]['index'] == 1
    assert (
        content['details']['errors'][2]['code'] == 'MULTIPLE_TERMINAL_STATUSES'
    )
    assert content['details']['errors'][2]['index'] == 0
    assert (
        content['details']['errors'][3]['code'] == 'MULTIPLE_TERMINAL_STATUSES'
    )
    assert content['details']['errors'][3]['index'] == 1


async def test_transitions_unknown_status(web_app_client, load_json):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    data['transitions'] = [
        {
            'from_statuses': [{'status': 'UNKNOWN_1'}],
            'to_statuses': [{'status': 'UNKNOWN_2'}],
        },
    ]

    response = await web_app_client.post('/v1/workflow', json=data)
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'WORKFLOW_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'INVALID_STATUS'
    assert content['details']['errors'][0]['index'] == 0
    assert content['details']['errors'][1]['code'] == 'INVALID_STATUS'
    assert content['details']['errors'][1]['index'] == 0


async def test_transitions_unused_status(web_app_client, load_json):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    data['statuses'] = [
        {'status': 'open', 'initial': True},
        {'status': 'process'},
        {'status': 'close', 'terminal': True},
    ]
    data['transitions'] = [
        {
            'from_statuses': [{'status': 'open'}],
            'to_statuses': [{'status': 'close'}],
        },
    ]

    response = await web_app_client.post('/v1/workflow', json=data)
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'WORKFLOW_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'UNUSED_STATUS'
    assert content['details']['errors'][0]['index'] == 1
