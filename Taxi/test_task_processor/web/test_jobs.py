from typing import List
from typing import NamedTuple
from typing import Optional


import pytest


@pytest.mark.parametrize(
    'request_data, expected',
    [
        pytest.param(
            [
                {
                    'recipe_name': 'both',
                    'job_vars': {'var2': 2},
                    'provider_name': 'deoevgen',
                    'idempotency_token': 'both_353',
                    'change_doc_id': 'cdi_both_1',
                },
                {
                    'recipe_name': 'both',
                    'job_vars': {'var1': 'v1', 'var3': 2},
                    'provider_name': 'clownductor',
                    'idempotency_token': 'both_352',
                    'change_doc_id': 'cdi_both_2',
                },
                {
                    'recipe_name': 'recipe_1',
                    'job_vars': {},
                    'provider_name': 'clownductor',
                    'idempotency_token': 'token_2',
                    'change_doc_id': 'test_change_doc_id_2',
                },
                {
                    'recipe_name': 'recipe_1',
                    'job_vars': {
                        'fqdn': 'foo.bar.blah.yandex.net',
                        'service_id': 2,
                        'env': 'stable',
                        'new_service_ticket': 3,
                    },
                    'provider_name': 'clownductor',
                    'idempotency_token': 'recipe_352',
                    'change_doc_id': 'cdi_r1_2',
                },
            ],
            'expected_bulk_1.json',
            id='good_and_invalide_job',
        ),
        pytest.param(None, 'REQUEST_VALIDATION_ERROR', id='Invalid_request'),
        pytest.param(
            [
                {
                    'recipe_name': 'not_recipe',
                    'job_vars': {
                        'fqdn': 'foo.bar.blah.yandex.net',
                        'service_id': 1,
                        'env': 'unstable',
                        'new_service_ticket': 3,
                    },
                    'provider_name': 'deoevgen',
                    'idempotency_token': 'token',
                    'change_doc_id': 'test_change_doc_id_1',
                },
                {
                    'recipe_name': 'already_exist_recipe',
                    'job_vars': {
                        'fqdn': 'foo.bar.blah.yandex.net',
                        'service_id': 2,
                        'env': 'unstable',
                        'new_service_ticket': 3,
                    },
                    'provider_name': 'deoevgen',
                    'idempotency_token': 'token',
                    'change_doc_id': 'cdi_1',
                },
            ],
            'ACTIVE_JOB',
            id='several_with_active',
        ),
        pytest.param(
            [
                {
                    'recipe_name': 'not_recipe',
                    'job_vars': {
                        'fqdn': 'foo.bar.blah.yandex.net',
                        'service_id': 1,
                        'env': 'unstable',
                        'new_service_ticket': 3,
                    },
                    'provider_name': 'deoevgen',
                    'idempotency_token': 'not_exist',
                    'change_doc_id': 'test_change_doc_id_12',
                },
            ],
            'UNKNOWN_PROVIDER',
            id='request_with_unknown_provider',
        ),
        pytest.param(
            [
                {
                    'recipe_name': 'both',
                    'job_vars': {'var1': 'temp'},
                    'provider_name': 'clownductor',
                    'idempotency_token': 'not_exist',
                    'change_doc_id': 'test_change_doc_id_12',
                },
            ],
            'MISSING_PARAMETER',
            id='request_with_not_full_job_vars',
        ),
        pytest.param(
            [
                {
                    'recipe_name': 'both',
                    'job_vars': {'var1': 'temp', 'var3': 'temp'},
                    'provider_name': 'clownductor',
                    'idempotency_token': 'not_exist',
                    'change_doc_id': 'test_change_doc_id_12',
                },
                {
                    'recipe_name': 'both',
                    'job_vars': {'var1': 'temp', 'var3': 'temp'},
                    'provider_name': 'clownductor',
                    'idempotency_token': 'not_exist',
                    'change_doc_id': 'test_change_doc_id_12',
                },
            ],
            'DUPLICATE_JOB',
            id='request_with_duplicate_jobs',
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_job_start_bulk.sql'])
async def test_job_bulk_start(
        web_app_client, request_data, expected, load_json, pgsql, web_context,
):
    response = await web_app_client.post(
        f'/v1/jobs/start_bulk/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json=[data for data in request_data] if request_data else None,
    )
    if response.status == 200:
        print(await response.json())
        assert load_json(expected) == await response.json()
    else:
        assert (await response.json())['code'] == expected


@pytest.mark.parametrize(
    'provider_name, '
    'recipe_name, '
    'token, '
    'change_doc_id, '
    'expected, '
    'need_check_entity_count',
    [
        (
            'deoevgen',
            'already_exist_recipe',
            'token',
            'change_doc_id',
            None,
            True,
        ),
        (
            'not_provider',
            'already_exist_recipe',
            'token',
            'change_doc_id',
            'NOT_FOUND',
            False,
        ),
        (
            'deoevgen',
            'not_recipe',
            'token',
            'change_doc_id',
            'NOT_FOUND',
            False,
        ),
        (
            'deoevgen',
            'not_recipe',
            'token',
            'test_change_doc_id_1',
            'ACTIVE_JOB',
            False,
        ),
        (
            'deoevgen',
            'not_recipe',
            'idempotency_token',
            'test_change_doc_id_1',
            None,
            False,
        ),
        (
            'deoevgen',
            'not_recipe',
            'idempotency_token',
            'different_change_doc_id',
            'BAD_REQUEST',
            False,
        ),
    ],
)
@pytest.mark.features_on('enable_tp_add_external_entity_link')
@pytest.mark.pgsql('task_processor', files=['test_job_start.sql'])
async def test_job_start(
        taxi_task_processor_web,
        get_job,
        provider_name,
        recipe_name,
        token,
        change_doc_id,
        expected,
        need_check_entity_count,
):
    response = await taxi_task_processor_web.post(
        f'/v1/jobs/start/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json={
            'recipe_name': recipe_name,
            'job_vars': {
                'fqdn': 'foo.bar.blah.yandex.net',
                'service_id': 1,
                'env': 'unstable',
                'new_service_ticket': 3,
            },
            'provider_name': provider_name,
            'idempotency_token': token,
            'change_doc_id': change_doc_id,
            'external_entities': {'service': '1', 'branch': '1'},
        },
    )
    if response.status == 200:
        job_id = (await response.json())['job_id']
        job = await get_job(job_id)
        assert job
    else:
        assert (await response.json())['code'] == expected
    if need_check_entity_count:
        response = await taxi_task_processor_web.post(
            '/v1/jobs/entity_link/list/',
            json={'entity_type': 'service', 'external_id': '1'},
        )
        assert response.status == 200
        assert len(await response.json()) == 1


@pytest.mark.parametrize(
    'action, new_status',
    [
        ('cancel', 'canceled'),
        ('cancel', 'canceled'),
        ('finish', 'success'),
        ('finish', 'success'),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_job_terminate.sql'])
@pytest.mark.xfail(reason='Flaps')
async def test_job_terminate(
        pgsql, web_context, web_app_client, get_job, action, new_status,
):
    response = await web_app_client.post(
        f'/v1/jobs/start/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json={
            'recipe_name': 'already_exist_recipe',
            'job_vars': {
                'fqdn': 'foo.bar.blah.yandex.net',
                'service_id': 1,
                'env': 'unstable',
                'new_service_ticket': 3,
            },
            'provider_name': 'deoevgen',
            'idempotency_token': 'idempotency_token',
            'change_doc_id': 'test_change_doc_id',
        },
    )
    job_id = (await response.json())['job_id']
    cursor = pgsql['task_processor'].cursor()
    cursor.execute(
        f'select id, job_id from task_processor.tasks '
        f'where job_id = {job_id} order by id;',
    )
    tasks_rows = cursor.fetchall()
    ids_to_success = [task_row[0] for task_row in tasks_rows][:2]
    await _update_tasks_status('success', ids_to_success, web_context)

    response = await web_app_client.post(
        f'/v1/jobs/{action}/',
        json={'job_id': job_id},
        headers={'X-Yandex-Login': 'karachevda'},
    )
    assert response.status == 200
    result = (await response.json())['updated_tasks']

    assert {task['job_id'] for task in result} == {job_id}
    assert {task['old_status'] for task in result} == {'in_progress'}
    assert {task['new_status'] for task in result} == {new_status}
    assert len(result) == len(tasks_rows) - len(ids_to_success)

    job_info = await get_job(job_id)
    assert dict(job_info)['status'] == new_status


async def _update_tasks_status(status, ids, web_context):
    async with web_context.pg.master_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                update task_processor.tasks
                set status = $2::JOB_STATUS
                where id = any($1::integer[]);
                """,
                ids,
                status,
            )


async def _update_job_status(status, job_id, web_context):
    async with web_context.pg.master_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                update task_processor.jobs
                set status = $2::JOB_STATUS
                where id = $1::integer;
                """,
                job_id,
                status,
            )


@pytest.mark.pgsql('task_processor', files=['test_job_terminate.sql'])
@pytest.mark.parametrize('retry_from', [1, 2])
async def test_tasks_retry(
        pgsql, web_context, web_app_client, get_job, retry_from,
):
    response = await web_app_client.post(
        f'/v1/jobs/start/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json={
            'recipe_name': 'already_exist_recipe',
            'job_vars': {
                'fqdn': 'foo.bar.blah.yandex.net',
                'service_id': 1,
                'env': 'unstable',
                'new_service_ticket': 3,
            },
            'provider_name': 'deoevgen',
            'idempotency_token': 'idempotency_token',
            'change_doc_id': 'test_change_doc_id',
        },
    )
    job_id = (await response.json())['job_id']
    cursor = pgsql['task_processor'].cursor()
    cursor.execute(
        f'select id, job_id from task_processor.tasks '
        f'where job_id = {job_id} order by id;',
    )
    tasks_rows = cursor.fetchall()
    ids_to_success = [task_row[0] for task_row in tasks_rows][:2]
    await _update_tasks_status('success', ids_to_success, web_context)
    await _update_job_status('success', job_id, web_context)

    response = await web_app_client.post(
        f'/v1/jobs/retry/',
        json={'job_id': job_id, 'retry_from': retry_from},
        headers={'X-Yandex-Login': 'karachevda'},
    )
    assert response.status == 200
    job = await get_job(job_id)
    assert dict(job)['status'] == 'in_progress'

    result = (await response.json())['updated_tasks']

    assert {task['job_id'] for task in result} == {job_id}
    assert {task['old_status'] for task in result} == {'success'}
    assert {task['new_status'] for task in result} == {'in_progress'}
    assert len(result) == len(
        [task for task in ids_to_success if task >= retry_from],
    )

    cursor.execute(
        f'select id, job_id, status from task_processor.tasks '
        f'where job_id = {job_id} order by id;',
    )
    tasks_rows = cursor.fetchall()
    tasks = []
    for task_row in tasks_rows:
        tasks.append(
            {'id': task_row[0], 'job_id': task_row[1], 'status': task_row[2]},
        )
    for task in tasks:
        if task['id'] >= retry_from:
            assert task['status'] == 'in_progress'
        else:
            assert task['status'] == 'success'


@pytest.mark.pgsql(
    'task_processor', files=['test_get_job_by_change_doc_id.sql'],
)
@pytest.mark.config(TASK_PROCESSOR_ENABLED=False)
async def test_get_job_by_change_doc_id(
        pgsql, web_context, web_app_client, get_job,
):
    response = await web_app_client.post(
        '/v1/jobs/retrieve_by_change_doc_id/',
        json={'change_doc_id': 'test_change_doc_id_1'},
    )
    assert response.status == 200
    content = await response.json()
    jobs = content['jobs']
    for job in jobs:
        assert job.pop('created_at')
        assert job == {
            'id': 1,
            'recipe_id': 1,
            'name': 'test_create_job',
            'status': 'in_progress',
            'job_vars': {},
            'initiator': 'deoevgen',
            'change_doc_id': 'test_change_doc_id_1',
            'idempotency_token': '12345',
        }


@pytest.mark.pgsql('task_processor', files=['test_get_job.sql'])
@pytest.mark.config(TASK_PROCESSOR_ENABLED=False)
async def test_get_job(web_context, web_app_client, get_job):
    response = await web_app_client.post(
        '/v1/jobs/retrieve/', json={'job_id': 1},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'job_info': {
            'id': 1,
            'recipe_id': 1,
            'name': 'test_create_job',
            'status': 'in_progress',
            'created_at': 1586267052,
            'job_vars': {},
            'initiator': 'deoevgen',
            'idempotency_token': '12345',
            'change_doc_id': 'test_change_doc_id_1',
        },
        'tasks': [
            {
                'id': 1,
                'cube_id': 1,
                'job_id': 1,
                'name': 'CubeDeploy1',
                'status': 'in_progress',
                'sleep_until': 0,
                'payload': {},
                'retries': 0,
                'created_at': 1586267052,
                'needed_parameters': [],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'id': 2,
                'cube_id': 2,
                'job_id': 1,
                'name': 'CubeDeploy2',
                'status': 'in_progress',
                'sleep_until': 0,
                'payload': {},
                'retries': 0,
                'created_at': 1586267052,
                'needed_parameters': [],
                'optional_parameters': [],
                'output_parameters': [],
            },
        ],
    }


@pytest.mark.parametrize(
    'provider_id, job_ids, status, expected_code',
    [
        (1, None, 200, None),
        (None, [1], 200, None),
        (None, [99], 200, None),
        (2, None, 404, 'NOT_FOUND'),
    ],
)
@pytest.mark.pgsql(
    'task_processor', files=['test_get_jobs_by_provider_id.sql'],
)
@pytest.mark.config(TASK_PROCESSOR_PAGINATION={'__default__': {'limit': 20}})
@pytest.mark.config(TASK_PROCESSOR_PAGINATION={'limit_jobs': {'limit': 25}})
async def test_get_jobs_by_provider_id(
        web_context,
        web_app_client,
        provider_id,
        job_ids,
        status,
        expected_code,
):
    response = await web_app_client.post(
        f'/v1/jobs/start/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json={
            'recipe_name': 'test_create_job',
            'job_vars': {
                'test': 'test_var',
                'service_id': 1,
                'env': 'unstable',
                'new_service_ticket': 3,
            },
            'provider_name': 'deoevgen',
            'idempotency_token': 'idempotency_token',
            'change_doc_id': 'change_doc_id',
        },
    )
    assert response.status == 200
    if provider_id:
        body = {'provider_id': provider_id}
    else:
        body = {'job_ids': job_ids}
    response = await web_app_client.post('/v1/jobs/', json=body)
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        jobs = content['jobs']
        for job in jobs:
            assert job['job_info'].pop('created_at')
            assert job['job_info'] == {
                'change_doc_id': 'change_doc_id',
                'id': 1,
                'idempotency_token': 'idempotency_token',
                'initiator': 'deoevgen',
                'name': 'test_create_job',
                'recipe_id': 1,
                'status': 'in_progress',
                'job_vars': {
                    'env': 'unstable',
                    'new_service_ticket': 3,
                    'service_id': 1,
                    'test': 'test_var',
                },
            }
            tasks = job['tasks']
            assert tasks[0]['name'] == 'CubeDeploy5'
            assert tasks[1]['name'] == 'CubeDeploy4'
    else:
        assert content['code'] == expected_code


class Params(NamedTuple):
    job_ids: Optional[List] = None
    name: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[int] = None
    finished_at: Optional[int] = None
    entity: Optional[dict] = None


@pytest.mark.parametrize(
    'params, expected',
    [
        (
            Params(entity={'entity_type': 'branch', 'external_id': '100'}),
            {
                'jobs': [
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_1',
                            'created_at': 1628266318,
                            'finished_at': 1628266400,
                            'id': 1,
                            'idempotency_token': 'token_1',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_1',
                            'recipe_id': 1,
                            'status': 'success',
                        },
                        'tasks': [],
                    },
                ],
            },
        ),
        (
            Params(entity={'entity_type': 'service', 'external_id': '100'}),
            {
                'jobs': [
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_4',
                            'created_at': 1628266318,
                            'finished_at': 1628266366,
                            'id': 7,
                            'idempotency_token': 'token_7',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_4',
                            'recipe_id': 2,
                            'status': 'failed',
                        },
                        'tasks': [],
                    },
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_4',
                            'created_at': 1628266318,
                            'finished_at': 1628266366,
                            'id': 4,
                            'idempotency_token': 'token_4',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_4',
                            'recipe_id': 2,
                            'status': 'failed',
                        },
                        'tasks': [],
                    },
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_2',
                            'created_at': 1628266318,
                            'finished_at': 1628266400,
                            'id': 2,
                            'idempotency_token': 'token_2',
                            'initiator': 'elrusso',
                            'job_vars': {'a': 1},
                            'name': 'job_2',
                            'recipe_id': 1,
                            'status': 'in_progress',
                        },
                        'tasks': [],
                    },
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_1',
                            'created_at': 1628266318,
                            'finished_at': 1628266400,
                            'id': 1,
                            'idempotency_token': 'token_1',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_1',
                            'recipe_id': 1,
                            'status': 'success',
                        },
                        'tasks': [],
                    },
                ],
            },
        ),
        (
            Params(job_ids=[1]),
            {
                'jobs': [
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_1',
                            'created_at': 1628266318,
                            'finished_at': 1628266400,
                            'id': 1,
                            'idempotency_token': 'token_1',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_1',
                            'recipe_id': 1,
                            'status': 'success',
                        },
                        'tasks': [],
                    },
                ],
            },
        ),
        (
            Params(name='job_4', status='failed'),
            {
                'jobs': [
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_4',
                            'created_at': 1628266318,
                            'finished_at': 1628266366,
                            'id': 7,
                            'idempotency_token': 'token_7',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_4',
                            'recipe_id': 2,
                            'status': 'failed',
                        },
                        'tasks': [],
                    },
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_4',
                            'created_at': 1628266318,
                            'finished_at': 1628266366,
                            'id': 4,
                            'idempotency_token': 'token_4',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_4',
                            'recipe_id': 2,
                            'status': 'failed',
                        },
                        'tasks': [],
                    },
                ],
            },
        ),
        (
            Params(created_at=1628266318, finished_at=1628266399),
            {
                'jobs': [
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_4',
                            'created_at': 1628266318,
                            'finished_at': 1628266366,
                            'id': 7,
                            'idempotency_token': 'token_7',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_4',
                            'recipe_id': 2,
                            'status': 'failed',
                        },
                        'tasks': [],
                    },
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_4',
                            'created_at': 1628266318,
                            'finished_at': 1628266366,
                            'id': 4,
                            'idempotency_token': 'token_4',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_4',
                            'recipe_id': 2,
                            'status': 'failed',
                        },
                        'tasks': [],
                    },
                    {
                        'job_info': {
                            'change_doc_id': 'test_change_doc_id_3',
                            'created_at': 1628266318,
                            'finished_at': 1628266319,
                            'id': 3,
                            'idempotency_token': 'token_3',
                            'initiator': 'elrusso',
                            'job_vars': {},
                            'name': 'job_3',
                            'recipe_id': 2,
                            'status': 'inited',
                        },
                        'tasks': [],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_get_job_by.sql'])
async def test_get_jobs_by(web_app_client, params, expected):
    data = {}
    if params.job_ids:
        data['job_ids'] = params.job_ids
    if params.name:
        data['name'] = params.name
    if params.status:
        data['status'] = params.status
    if params.created_at:
        data['created_at'] = params.created_at
    if params.finished_at:
        data['finished_at'] = params.finished_at
    if params.entity:
        data['entity'] = params.entity
    response = await web_app_client.post(
        '/v1/jobs/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json=data,
    )
    assert response.status == 200
    assert await response.json() == expected


@pytest.mark.parametrize(
    'additional_data, expected',
    [
        pytest.param(
            {'external_entities': {'service': '1', 'branch': '1'}},
            {
                'external_entity_links': [
                    {
                        'entity': {
                            'entity_type': 'service',
                            'external_id': '1',
                        },
                        'id': 2,
                        'job_id': 2,
                    },
                    {
                        'entity': {
                            'entity_type': 'branch',
                            'external_id': '1',
                        },
                        'id': 3,
                        'job_id': 2,
                    },
                ],
            },
            id='external_entities_additional_data',
        ),
        pytest.param(
            {'external_entities': {'service': '1'}},
            {
                'external_entity_links': [
                    {
                        'entity': {
                            'entity_type': 'service',
                            'external_id': '1',
                        },
                        'id': 2,
                        'job_id': 2,
                    },
                ],
            },
            id='external_entities_additional_data',
        ),
        pytest.param(
            {'external_entities': {'branch': '12'}},
            {
                'external_entity_links': [
                    {
                        'entity': {
                            'entity_type': 'branch',
                            'external_id': '12',
                        },
                        'id': 2,
                        'job_id': 2,
                    },
                ],
            },
            id='external_entities_additional_data',
        ),
    ],
)
@pytest.mark.features_on('enable_tp_add_external_entity_link')
@pytest.mark.pgsql('task_processor', files=['test_job_start.sql'])
async def test_job_start_with_external_link(
        taxi_task_processor_web,
        web_app_client,
        get_job,
        additional_data,
        expected,
        pgsql,
):
    response = await taxi_task_processor_web.post(
        f'/v1/jobs/start/',
        headers={
            'Authorization': 'OAuth test_token',
            'X-Yandex-Login': 'test_username',
        },
        json={
            'recipe_name': 'already_exist_recipe',
            'job_vars': {
                'fqdn': 'foo.bar.blah.yandex.net',
                'service_id': 1,
                'env': 'unstable',
                'new_service_ticket': 3,
            },
            'provider_name': 'deoevgen',
            'idempotency_token': 'token',
            'change_doc_id': 'change_doc_id',
            **additional_data,
        },
    )
    job_id = (await response.json())['job_id']
    job = await get_job(job_id)
    assert job

    response = await taxi_task_processor_web.post(
        '/v1/jobs/entity_link/list/', json={'job_id': job_id},
    )
    assert response.status == 200
    assert expected == await response.json()
