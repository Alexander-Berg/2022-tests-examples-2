# pylint: disable=import-only-modules
import datetime
import json

import pytest

from .utils import select_named
from .utils import select_table_named

OAUTH_HEADER = 'OAuth secret'
NIRVANA_QUOTA_PROJECT_ID = 'default'
WORKFLOW_INSTANCE_ID = 'e648e648-7b9a-496b-bf50-fd27d55326f6'
WORKFLOW_CLONE_INSTANCE_ID = 'cloned-e648e648-7b9a-496b-bf50-fd27d55326f6'


@pytest.mark.now('2018-11-11T18:00:00')
@pytest.mark.parametrize('is_check', [True, False])
@pytest.mark.filldb()
async def test_add(
        taxi_reposition_relocator, pgsql, mockserver, load_json, is_check,
):
    @mockserver.json_handler('/nirvana-reactor/api/v1/r/create')
    def _mock_create(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        assert json.loads(request.get_data()) == load_json(
            'reactor_create_request.json',
        )
        return mockserver.make_response(
            json.dumps({'reactionId': '284559', 'namespaceId': '1264598'}),
            status=200,
        )

    @mockserver.json_handler('/nirvana-reactor/api/v1/r/update')
    def _mock_update(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(json.dumps({}))

    @mockserver.json_handler('/nirvana/api/public/v1/getWorkflowMetaData')
    def _mock_metadata(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'getWorkflowMetaData_1585413223448',
                    'result': {
                        'guid': '7fda40c3-acda-4695-94c1-f9789fff6457',
                        'instanceId': WORKFLOW_CLONE_INSTANCE_ID,
                        'projectCode': 'taxi_reposition_testing',
                        'owner': 'robot-reposition-tst',
                        'instanceCreator': 'robot-reposition-tst',
                        'name': 'Dummy search source location workflow',
                        'description': 'Takes destination location',
                        'created': '2020-03-28T18:57:57+0300',
                        'updated': '2020-03-28T18:58:30+0300',
                        'started': '2020-03-28T19:18:22+0300',
                        'completed': '2020-03-28T19:18:31+0300',
                        'lifecycleStatus': 'approved',
                        'quotaProjectId': 'default',
                        'rejected': False,
                        'archived': False,
                        'tags': [],
                    },
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/nirvana/api/public/v1/cloneWorkflowInstance')
    def _mock_clone(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        request_patched = json.loads(request.get_data())
        del request_patched['id']

        assert request_patched == {
            'jsonrpc': '2.0',
            'method': 'cloneWorkflowInstance',
            'params': {
                'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                'newQuotaProjectId': NIRVANA_QUOTA_PROJECT_ID,
            },
        }

        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'cloneWorkflowInstance_1585413223448',
                    'result': WORKFLOW_CLONE_INSTANCE_ID,
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/nirvana/api/public/v1/approveWorkflow')
    def _mock_approve(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'approveWorkflow_1585413223448',
                    'result': 'ok',
                },
            ),
            status=200,
        )

    reaction = '/taxi/reposition/first-reaction'
    check_str = 'check/' if is_check else ''
    request = {
        'path': reaction,
        'cron': '0 0 7 * * ?',
        'workflow_instance_id': (
            WORKFLOW_INSTANCE_ID if is_check else WORKFLOW_CLONE_INSTANCE_ID
        ),
    }
    response = await taxi_reposition_relocator.post(
        f'v2/admin/reaction/{check_str}', json=request,
    )

    expected_check_response = {'data': request}
    expected_check_response['data'][
        'workflow_instance_id'
    ] = WORKFLOW_CLONE_INSTANCE_ID

    assert response.status_code == 200
    if is_check:
        assert response.json() == expected_check_response
        return

    assert response.json() == {'reaction_id': '284559'}
    right = select_table_named(
        'state.reactions', 'reaction_id', pgsql['reposition-relocator'],
    )
    left = [
        {
            'reaction_id': '284559',
            'namespace_id': '1264598',
            'workflow_id': '7fda40c3-acda-4695-94c1-f9789fff6457',
            'workflow_instance_id': WORKFLOW_CLONE_INSTANCE_ID,
            'path': reaction,
            'cron_string': '0 0 7 * * ?',
            'status': 'ACTIVE',
            'created_at': datetime.datetime(2018, 11, 11, 18, 00, 00),
        },
    ]
    assert left == right


@pytest.mark.now('2018-11-11T18:00:00')
@pytest.mark.parametrize('is_conflict', [True, False])
@pytest.mark.parametrize('is_override', [True, False])
@pytest.mark.parametrize('is_check', [True, False])
@pytest.mark.filldb()
async def test_put(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        load,
        is_conflict,
        is_override,
        is_check,
):
    @mockserver.json_handler('/nirvana/api/public/v1/getWorkflowMetaData')
    def mock_metadata(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'getWorkflowMetaData_1585413223448',
                    'result': {
                        'guid': '7fda40c3-acda-4695-94c1-f9789fff6457',
                        'instanceId': WORKFLOW_CLONE_INSTANCE_ID,
                        'projectCode': 'taxi_reposition_testing',
                        'owner': 'robot-reposition-tst',
                        'instanceCreator': 'robot-reposition-tst',
                        'name': 'Dummy search source location workflow',
                        'description': 'Takes destination location',
                        'created': '2020-03-28T18:57:57+0300',
                        'updated': '2020-03-28T18:58:30+0300',
                        'started': '2020-03-28T19:18:22+0300',
                        'completed': '2020-03-28T19:18:31+0300',
                        'lifecycleStatus': 'approved',
                        'quotaProjectId': 'default',
                        'rejected': False,
                        'archived': False,
                        'tags': [],
                    },
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/nirvana/api/public/v1/cloneWorkflowInstance')
    def mock_clone(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        request_patched = json.loads(request.get_data())
        del request_patched['id']

        assert request_patched == {
            'jsonrpc': '2.0',
            'method': 'cloneWorkflowInstance',
            'params': {
                'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                'newQuotaProjectId': NIRVANA_QUOTA_PROJECT_ID,
            },
        }

        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'cloneWorkflowInstance_1585413223448',
                    'result': WORKFLOW_CLONE_INSTANCE_ID,
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/nirvana/api/public/v1/approveWorkflow')
    def mock_approve(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'approveWorkflow_1585413223448',
                    'result': 'ok',
                },
            ),
            status=200,
        )

    if is_conflict:
        queries = [load('pending_reactions.sql')]
        pgsql['reposition-relocator'].apply_queries(queries)
    elif is_override:
        queries = [load('add_reactions.sql')]
        pgsql['reposition-relocator'].apply_queries(queries)
    reaction = 'reaction1'
    reaction_path = f'/taxi/reposition/{reaction}'
    request = {
        'path': reaction if is_check else reaction_path,
        'cron': ' 0 0 7 * * ? ',
        'workflow_instance_id': (
            WORKFLOW_INSTANCE_ID if is_check else WORKFLOW_CLONE_INSTANCE_ID
        ),
    }
    check_str = 'check/' if is_check else ''
    response = await taxi_reposition_relocator.put(
        f'v2/admin/reaction/{check_str}', json=request,
    )

    expected_check_response = {'data': request}
    expected_check_response['data'][
        'workflow_instance_id'
    ] = WORKFLOW_CLONE_INSTANCE_ID
    expected_check_response['data']['path'] = reaction_path

    assert mock_metadata.times_called == 1
    if is_check:
        assert response.json() == expected_check_response
        assert mock_approve.times_called == 1
        assert mock_clone.times_called == 1
        return
    if is_conflict:
        assert response.status_code == 409
        return

    assert response.status_code == 200

    assert response.json() == {}

    rows = select_table_named(
        'state.reactions', 'reaction_id', pgsql['reposition-relocator'],
    )
    right = None
    for row in rows:
        if row['status'] == 'PENDING':
            right = row
            break
    assert right

    if not is_override:
        assert 'tmp_' in right['reaction_id']
    else:
        assert right['reaction_id'] == '121'

    right.pop('reaction_id', None)

    left = {
        'namespace_id': '' if not is_override else '121',
        'workflow_id': '7fda40c3-acda-4695-94c1-f9789fff6457',
        'workflow_instance_id': WORKFLOW_CLONE_INSTANCE_ID,
        'path': f'/taxi/reposition/{reaction}',
        'cron_string': '0 0 7 * * ?',
        'status': 'PENDING',
        'created_at': (
            datetime.datetime(2018, 11, 11, 18, 00, 00)
            if not is_override
            else datetime.datetime(2018, 11, 26, 8, 00, 00)
        ),
    }
    if is_override:
        rows = select_table_named(
            'state.reactions_history', 'path', pgsql['reposition-relocator'],
        )
        assert rows == [
            {
                'path': '/taxi/reposition/reaction1',
                'workflow_id': '121',
                'workflow_instance_id': '313',
                'cron_string': '0 0 7 * * ?',
                'created_at': datetime.datetime(2018, 11, 26, 8, 0),
            },
        ]

    assert left == right


@pytest.mark.now('2018-11-11T18:00:00')
@pytest.mark.parametrize('use_random', [True, False])
@pytest.mark.filldb()
async def test_put_with_random(
        taxi_reposition_relocator, pgsql, mockserver, load, use_random,
):
    @mockserver.json_handler('/nirvana/api/public/v1/getWorkflowMetaData')
    def mock_metadata(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'getWorkflowMetaData_1585413223448',
                    'result': {
                        'guid': '7fda40c3-acda-4695-94c1-f9789fff6457',
                        'instanceId': WORKFLOW_CLONE_INSTANCE_ID,
                        'projectCode': 'taxi_reposition_testing',
                        'owner': 'robot-reposition-tst',
                        'instanceCreator': 'robot-reposition-tst',
                        'name': 'Dummy search source location workflow',
                        'description': 'Takes destination location',
                        'created': '2020-03-28T18:57:57+0300',
                        'updated': '2020-03-28T18:58:30+0300',
                        'started': '2020-03-28T19:18:22+0300',
                        'completed': '2020-03-28T19:18:31+0300',
                        'lifecycleStatus': 'approved',
                        'quotaProjectId': 'default',
                        'rejected': False,
                        'archived': False,
                        'tags': [],
                    },
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/nirvana/api/public/v1/cloneWorkflowInstance')
    def _mock_clone(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        request_patched = json.loads(request.get_data())
        del request_patched['id']

        assert request_patched == {
            'jsonrpc': '2.0',
            'method': 'cloneWorkflowInstance',
            'params': {
                'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                'newQuotaProjectId': NIRVANA_QUOTA_PROJECT_ID,
            },
        }

        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'cloneWorkflowInstance_1585413223448',
                    'result': WORKFLOW_CLONE_INSTANCE_ID,
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/nirvana/api/public/v1/approveWorkflow')
    def _mock_approve(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'approveWorkflow_1585413223448',
                    'result': 'ok',
                },
            ),
            status=200,
        )

    reaction = 'reaction1'
    reaction_path = f'/taxi/reposition/{reaction}'
    request = {
        'path': reaction_path,
        'cron': ' 0 0 7 * * ? ',
        'workflow_instance_id': WORKFLOW_CLONE_INSTANCE_ID,
        'randomize_cron_seconds': use_random,
    }
    check_str = ''
    response = await taxi_reposition_relocator.put(
        f'v2/admin/reaction/{check_str}', json=request,
    )

    expected_check_response = {'data': request}
    expected_check_response['data'][
        'workflow_instance_id'
    ] = WORKFLOW_CLONE_INSTANCE_ID
    expected_check_response['data']['path'] = reaction_path

    assert mock_metadata.times_called == 1
    assert response.status_code == 200

    assert response.json() == {}

    rows = select_table_named(
        'state.reactions', 'reaction_id', pgsql['reposition-relocator'],
    )
    right = None
    for row in rows:
        if row['status'] == 'PENDING':
            right = row
            break
    assert right

    assert 'tmp_' in right['reaction_id']

    right.pop('reaction_id', None)

    cron_suffix = ' 0 7 * * ?'
    prefix = '0' if not use_random else '34'
    left = {
        'namespace_id': '',
        'workflow_id': '7fda40c3-acda-4695-94c1-f9789fff6457',
        'workflow_instance_id': WORKFLOW_CLONE_INSTANCE_ID,
        'path': f'/taxi/reposition/{reaction}',
        'cron_string': prefix + cron_suffix,
        'status': 'PENDING',
        'created_at': (datetime.datetime(2018, 11, 11, 18, 00, 00)),
    }

    assert left == right


@pytest.mark.now('2018-11-11T18:00:00')
@pytest.mark.filldb()
async def test_update_pending(
        taxi_reposition_relocator, pgsql, mockserver, load_json, load,
):
    queries = [load('pending_reactions.sql')]
    pgsql['reposition-relocator'].apply_queries(queries)

    @mockserver.json_handler('/nirvana-reactor/api/v1/r/create')
    def mock_create(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        left = json.loads(request.get_data())
        right = load_json('reactor_create_request.json')
        instance_id = (
            left['reaction']['parametersValue']['rootNode']['nodes'][
                'sourceFlowchartId'
            ]['node']['nodes']['workflowInstanceId']['value']['genericValue'][
                'value'
            ]
        )
        out_reaction_id = {
            'cloned-e648e648-7b9a-496b-bf50-fd27d55326f6': '284559',
            '322': '284560',
        }[instance_id]
        assert left['reaction']['namespaceDescriptor']['namespaceIdentifier'][
            'namespacePath'
        ] in ['/taxi/reposition/reaction1', '/taxi/reposition/reaction2']
        assert instance_id in [
            'cloned-e648e648-7b9a-496b-bf50-fd27d55326f6',
            '322',
        ]
        left['reaction']['parametersValue']['rootNode']['nodes'][
            'sourceFlowchartId'
        ]['node']['nodes']['workflowInstanceId']['value']['genericValue'].pop(
            'value', None,
        )
        right['reaction']['parametersValue']['rootNode']['nodes'][
            'sourceFlowchartId'
        ]['node']['nodes']['workflowInstanceId']['value']['genericValue'].pop(
            'value', None,
        )
        left['reaction']['namespaceDescriptor']['namespaceIdentifier'].pop(
            'namespacePath', None,
        )
        right['reaction']['namespaceDescriptor']['namespaceIdentifier'].pop(
            'namespacePath', None,
        )
        assert left == right
        return mockserver.make_response(
            json.dumps(
                {'reactionId': out_reaction_id, 'namespaceId': '1264598'},
            ),
            status=200,
        )

    @mockserver.json_handler('/nirvana-reactor/api/v1/r/update')
    def mock_update(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(json.dumps({}))

    @mockserver.json_handler('/nirvana-reactor/api/v1/n/delete')
    def mock_delete(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(json.dumps({}))

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'reactor_manager-update-pending'},
    )
    assert response.status_code == 200
    assert mock_delete.times_called == 1
    assert mock_create.times_called == 2
    assert mock_update.times_called == 3

    right = select_table_named(
        'state.reactions', 'reaction_id', pgsql['reposition-relocator'],
    )
    left = [
        {
            'created_at': datetime.datetime(2018, 11, 11, 18, 0),
            'cron_string': '0 0 7 * * ?',
            'namespace_id': '1264598',
            'path': '/taxi/reposition/reaction1',
            'reaction_id': '284559',
            'status': 'ACTIVE',
            'workflow_id': '321',
            'workflow_instance_id': (
                'cloned-e648e648-7b9a-496b-bf50-fd27d55326f6'
            ),
        },
        {
            'created_at': datetime.datetime(2018, 11, 11, 18, 0),
            'cron_string': '0 0 7 * * ?',
            'namespace_id': '1264598',
            'path': '/taxi/reposition/reaction2',
            'reaction_id': '284560',
            'status': 'ACTIVE',
            'workflow_id': '322',
            'workflow_instance_id': '322',
        },
    ]
    assert left == right


@pytest.mark.filldb()
async def test_update_status(
        taxi_reposition_relocator, pgsql, load, mockserver, load_json,
):
    @mockserver.json_handler('/nirvana-reactor/api/v1/r/update')
    def _mock_update(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(json.dumps({}))

    queries = [load('add_reactions.sql')]
    pgsql['reposition-relocator'].apply_queries(queries)
    row = select_named(
        'SELECT status FROM state.reactions WHERE reaction_id = \'122\'',
        pgsql['reposition-relocator'],
    )
    assert row[0]['status'] == 'PAUSED'

    response = await taxi_reposition_relocator.post(
        'v2/admin/reaction/update_status',
        params={'reaction_id': 122},
        json={'status': 'ACTIVE'},
    )

    assert response.status_code == 200
    assert response.json() == {}

    row = select_named(
        'SELECT status FROM state.reactions WHERE reaction_id = \'122\'',
        pgsql['reposition-relocator'],
    )
    assert row[0]['status'] == 'ACTIVE'


@pytest.mark.filldb()
async def test_get(
        taxi_reposition_relocator, pgsql, load, mockserver, load_json,
):
    queries = [load('add_reactions.sql')]
    pgsql['reposition-relocator'].apply_queries(queries)
    response = await taxi_reposition_relocator.get('v2/admin/reaction/list')

    assert response.status_code == 200
    date = '2018-11-26T08:00:00+00:00'
    assert response.json() == {
        'reactions': [
            {
                'reaction_id': '121',
                'namespace_id': '121',
                'workflow_id': '121',
                'workflow_instance_id': '313',
                'path': '/taxi/reposition/reaction1',
                'cron_string': '0 0 7 * * ?',
                'status': 'ACTIVE',
                'created_at': date,
            },
            {
                'reaction_id': '122',
                'namespace_id': '221',
                'workflow_id': '122',
                'workflow_instance_id': '323',
                'path': '/taxi/reposition/reaction2',
                'cron_string': '0 0 7 * * ?',
                'status': 'PAUSED',
                'created_at': date,
            },
            {
                'reaction_id': '123',
                'namespace_id': '321',
                'workflow_id': '123',
                'workflow_instance_id': '333',
                'path': '/taxi/reposition/reaction3',
                'cron_string': '0 0 7 * * ?',
                'status': 'ACTIVE',
                'created_at': date,
            },
        ],
    }


@pytest.mark.filldb()
async def test_history(
        taxi_reposition_relocator, pgsql, load, mockserver, load_json,
):
    queries = [load('history_reactions.sql')]
    pgsql['reposition-relocator'].apply_queries(queries)
    path = '/home/robot-reposition-tst/reaction1'
    response = await taxi_reposition_relocator.get(
        f'v2/admin/reaction/history?path={path}',
    )

    assert response.status_code == 200
    left = sorted(
        response.json()['reactions_history'], key=lambda k: k['created_at'],
    )
    right = sorted(
        [
            {
                'workflow_id': '121',
                'workflow_instance_id': '313',
                'cron_string': '0 0 7 * * ?',
                'created_at': '2018-11-26T08:00:00+00:00',
            },
            {
                'workflow_id': '122',
                'workflow_instance_id': '323',
                'cron_string': '0 0 5 * * ?',
                'created_at': '2018-11-25T08:00:00+00:00',
            },
        ],
        key=lambda k: k['created_at'],
    )
    assert left == right


@pytest.mark.filldb()
async def test_del(
        taxi_reposition_relocator, pgsql, load, mockserver, load_json,
):
    @mockserver.json_handler('/nirvana-reactor/api/v1/r/update')
    def mock_update(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        return mockserver.make_response(json.dumps({}))

    @mockserver.json_handler('/nirvana-reactor/api/v1/n/delete')
    def mock_delete(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        row = select_named(
            'SELECT status FROM state.reactions WHERE reaction_id = \'122\'',
            pgsql['reposition-relocator'],
        )

        assert row[0]['status'] == 'PENDING'

        return mockserver.make_response(json.dumps({}))

    queries = [load('add_reactions.sql')]
    pgsql['reposition-relocator'].apply_queries(queries)
    response = await taxi_reposition_relocator.delete(
        'v2/admin/reaction/', params={'reaction_id': '122'},
    )

    assert response.status_code == 200
    assert response.json() == {}

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'reactor_manager-update-pending'},
    )

    assert mock_update.times_called == 1
    assert mock_delete.times_called == 1

    row = select_named(
        'SELECT * FROM state.reactions WHERE reaction_id = \'122\'',
        pgsql['reposition-relocator'],
    )

    assert not row
