import pytest

URL = '/queue/remove/'


@pytest.mark.fillstqdb(collections=[('stq', 'dbstq', 'example_queue_0')])
async def test_delete_remove_queue_409(web_app_client, stq_db):
    response = await web_app_client.delete(
        URL,
        json={
            'queue_name': 'example_queue',
            'version': 2,
            'dev_team': 'some_team',
        },
    )
    assert response.status == 409


@pytest.mark.parametrize('check', [False, True])
async def test_delete_remove_queue_404(web_app_client, check):
    if check:
        web_caller = web_app_client.post
    else:
        web_caller = web_app_client.delete
    response = await web_caller(
        (URL + 'check/') if check else URL,
        json={
            'queue_name': 'non_existent_queue',
            'version': 2,
            'dev_team': 'some_team',
        },
    )
    assert response.status == 404


@pytest.mark.fillstqdb(collections=[('stq', 'dbstq', 'queue_with_tasks_0')])
@pytest.mark.parametrize('check', [False, True])
async def test_delete_remove_queue_400(web_app_client, stq_db, check):
    if check:
        web_caller = web_app_client.post
    else:
        web_caller = web_app_client.delete
    response = await web_caller(
        (URL + 'check/') if check else URL,
        json={
            'queue_name': 'queue_with_tasks',
            'version': 2,
            'dev_team': 'some_team',
        },
    )
    assert response.status == 400
    assert (await response.json())[
        'message'
    ] == 'Queue queue_with_tasks is not empty'
    response = await web_caller(
        (URL + 'check/') if check else URL,
        json={
            'queue_name': 'queue_with_tasks',
            'version': 2,
            'dev_team': 'some_wrong_team',
            'ignore_tasks': True,
        },
    )
    assert (await response.json())['message'] == (
        'Queue queue_with_tasks does not belong to the dev '
        'team some_wrong_team provided in request'
    )


@pytest.mark.fillstqdb(collections=[('stq', 'dbstq', 'queue_with_tasks_0')])
@pytest.mark.parametrize(
    'request_data',
    [
        {
            'queue_name': 'queue_with_tasks',
            'version': 3,
            'ignore_tasks': True,
            'dev_team': 'some_team',
        },
        {
            'queue_name': 'example_queue',
            'version': 3,
            'ignore_tasks': False,
            'dev_team': 'some_team',
        },
    ],
)
@pytest.mark.parametrize('check', [False, True])
async def test_delete_remove_queue_200(
        web_app_client, stq_db, request_data, db, check,
):
    if check:
        web_caller = web_app_client.post
    else:
        web_caller = web_app_client.delete
    response = await web_caller(
        (URL + 'check/') if check else URL, json=request_data,
    )
    assert response.status == 200
    config = await db.stq_config.find_one(request_data['queue_name'])
    if not check:
        assert config is None
    else:
        assert config is not None


@pytest.mark.parametrize(
    'queue, namespace', [('example_queue', None), ('with_tplatform', 'lavka')],
)
async def test_check_remove_queue_with_tplatform(
        web_app_client, queue, namespace,
):
    data = {
        'queue_name': queue,
        'version': 3,
        'ignore_tasks': True,
        'dev_team': 'some_team',
    }
    response = await web_app_client.post('/queue/remove/check/', json=data)
    assert response.status == 200
    result = await response.json()
    assert result.get('tplatform_namespace') == namespace
    assert result.get('data') == data
