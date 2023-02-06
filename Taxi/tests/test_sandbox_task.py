from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import pytest

import sandbox_task
from taxi_buildagent.clients import sandbox as sandbox_client


class FindResourceParams(NamedTuple):
    tc_set_parameters_calls: List[Dict[str, Any]] = []
    tc_report_build_problems_calls: List[Dict[str, Any]] = []
    resource_type: str = 'SOME_TYPE'
    resource_id: int = 12345
    resource_version: str = '88888'
    if_resource_exists: bool = True
    resource_state: str = 'READY'
    task_id: int = 67890
    set_resource_id_to: Optional[str] = None
    set_resource_version_to: Optional[str] = None
    set_task_url_to: Optional[str] = None
    assert_ready: bool = False


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(FindResourceParams(), id='simple_case'),
        pytest.param(
            FindResourceParams(
                resource_id=555,
                set_resource_id_to='env.RESOURCE_ID',
                tc_set_parameters_calls=[
                    {'name': 'env.RESOURCE_ID', 'value': '555'},
                ],
            ),
            id='set_resource_id',
        ),
        pytest.param(
            FindResourceParams(
                resource_version='99999',
                set_resource_version_to='env.RESOURCE_VERSION',
                tc_set_parameters_calls=[
                    {'name': 'env.RESOURCE_VERSION', 'value': '99999'},
                ],
            ),
            id='set_resource_version',
        ),
        pytest.param(
            FindResourceParams(
                resource_id=111,
                set_resource_id_to='env.RESOURCE_ID',
                task_id=222,
                set_task_url_to='task_url',
                tc_set_parameters_calls=[
                    {'name': 'env.RESOURCE_ID', 'value': '111'},
                    {
                        'name': 'task_url',
                        'value': sandbox_client.USER_URL + 'task/222',
                    },
                ],
            ),
            id='set_several',
        ),
        pytest.param(
            FindResourceParams(
                set_resource_id_to='some_param',
                if_resource_exists=False,
                tc_set_parameters_calls=[
                    {
                        'name': 'env.BUILD_PROBLEM',
                        'value': 'No SOME_TYPE resource found on Sandbox',
                    },
                ],
                tc_report_build_problems_calls=[
                    {
                        'description': (
                            'No SOME_TYPE resource found on Sandbox'
                        ),
                        'identity': None,
                    },
                ],
            ),
            id='no_resource_found',
        ),
        pytest.param(
            FindResourceParams(
                set_resource_id_to='some_param',
                resource_state='BROKEN',
                assert_ready=True,
                tc_set_parameters_calls=[
                    {
                        'name': 'env.BUILD_PROBLEM',
                        'value': (
                            'Last SOME_TYPE resource is BROKEN '
                            f'({sandbox_client.USER_URL}resource/12345)'
                        ),
                    },
                ],
                tc_report_build_problems_calls=[
                    {
                        'description': (
                            'Last SOME_TYPE resource is BROKEN '
                            f'({sandbox_client.USER_URL}resource/12345)'
                        ),
                        'identity': None,
                    },
                ],
            ),
            id='broken_resource',
        ),
    ],
)
def test_create_ticket(
        params, sandbox, teamcity_set_parameters, teamcity_report_problems,
):
    expected_sb_resource_calls = [
        {
            'url': sandbox_client.API_URL + 'resource',
            'method': 'get',
            'kwargs': {
                'headers': {'Authorization': 'OAuth sandbox-token'},
                'params': {
                    'type': params.resource_type,
                    'owner': sandbox_client.ROBOT_NAME,
                    'limit': 1,
                },
            },
        },
    ]

    if params.if_resource_exists:
        sandbox.append_resource(
            type_=params.resource_type,
            id_=params.resource_id,
            task_id=params.task_id,
            state=params.resource_state,
            version=params.resource_version,
        )
    sandbox.patch_all()

    argv = ['find-resource', '--type', params.resource_type]
    if params.assert_ready:
        argv.append('--assert-ready')
    if params.set_resource_id_to:
        argv += ['--set-resource-id-to', params.set_resource_id_to]
    if params.set_resource_version_to:
        argv += ['--set-resource-version-to', params.set_resource_version_to]
    if params.set_task_url_to:
        argv += ['--set-task-url-to', params.set_task_url_to]
    sandbox_task.main(argv)

    assert sandbox.resource.calls == expected_sb_resource_calls
    assert teamcity_set_parameters.calls == params.tc_set_parameters_calls
    assert (
        teamcity_report_problems.calls == params.tc_report_build_problems_calls
    )


class DownloadResourcesParams(NamedTuple):
    resources_ids: str
    resources_ids_by_packages: Dict[str, int]
    download_resource_calls: List[Dict[str, Any]]
    tc_report_build_problems_calls: List[Dict[str, Any]] = []


@pytest.fixture(name='prepare_sandbox')
def _prepare_sandbox(sandbox):
    def _prepare_sandbox_impl(resources_id_by_packages):
        for package, res_id in resources_id_by_packages.items():
            sandbox.append_resource(
                'YA_PACKAGE', res_id, package, package + '_1.0.0_all.tar.gz',
            )
        sandbox.patch_all()
        return sandbox

    return _prepare_sandbox_impl


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            DownloadResourcesParams(
                resources_ids='1111',
                resources_ids_by_packages={'taxi-graph': 1111},
                download_resource_calls=[
                    {
                        'url': sandbox_client.PROXY_URL + '1111',
                        'method': 'get',
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'stream': True,
                        },
                    },
                ],
            ),
            id='one_package',
        ),
        pytest.param(
            DownloadResourcesParams(
                resources_ids='1111;2222',
                resources_ids_by_packages={
                    'taxi-graph': 1111,
                    'taxi-graph-dev': 2222,
                },
                download_resource_calls=[
                    {
                        'url': sandbox_client.PROXY_URL + '1111',
                        'method': 'get',
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'stream': True,
                        },
                    },
                    {
                        'url': sandbox_client.PROXY_URL + '2222',
                        'method': 'get',
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'stream': True,
                        },
                    },
                ],
            ),
            id='several_packages',
        ),
        pytest.param(
            DownloadResourcesParams(
                resources_ids='9999',
                resources_ids_by_packages={},
                download_resource_calls=[
                    {
                        'url': sandbox_client.PROXY_URL + '9999',
                        'method': 'get',
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'stream': True,
                        },
                    },
                ],
                tc_report_build_problems_calls=[
                    {
                        'description': (
                            'Sandbox API '
                            f'{sandbox_client.PROXY_URL}9999 '
                            'error: status - 404, '
                            'text - {"error": "Not Found", "reason": '
                            '"Resource #9999 not found."}'
                        ),
                        'identity': None,
                    },
                ],
            ),
            id='no_resource',
        ),
    ],
)
def test_download_resources(
        tmpdir, teamcity_report_problems, prepare_sandbox, params,
):
    expected_content_files = [
        tmpdir.join(package_name + '_1.0.0_all.deb')
        for package_name in sorted(params.resources_ids_by_packages)
    ]
    expected_content_files += [
        tmpdir.join(package_name + '_1.0.0_all.changes')
        for package_name in sorted(params.resources_ids_by_packages)
    ]
    sandbox = prepare_sandbox(params.resources_ids_by_packages)

    argv = [
        'download-resources',
        '--resources-ids',
        params.resources_ids,
        '--download-dir',
        str(tmpdir),
    ]
    sandbox_task.main(argv)
    assert (
        teamcity_report_problems.calls == params.tc_report_build_problems_calls
    )
    assert sandbox.download_resource.calls == params.download_resource_calls
    content_files = [str(filename) for filename in sorted(tmpdir.listdir())]
    assert content_files == sorted(expected_content_files)


class RunTaskParams(NamedTuple):
    type: str
    tags: List[str] = []
    input_parameters: Optional[str] = None
    sb_task_create_calls: List[Dict[str, Any]] = []
    sb_batch_tasks_start_calls: List[Dict[str, Any]] = []
    sb_task_calls: List[Dict[str, Any]] = []
    tc_report_build_problems_calls: List[Dict[str, Any]] = []
    tool_debug: bool = False


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            RunTaskParams(
                type='TEST_TASK',
                sb_task_create_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'json': {
                                'custom_fields': [],
                                'description': 'Some\nmultiline description',
                                'owner': 'ROBOT_TAXI_SANDLOAD',
                                'tags': [],
                                'type': 'TEST_TASK',
                            },
                        },
                        'method': 'post',
                        'url': sandbox_client.API_URL + 'task',
                    },
                ],
                sb_batch_tasks_start_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'json': {'id': [123456789]},
                        },
                        'method': 'put',
                        'url': sandbox_client.API_URL + 'batch/tasks/start',
                    },
                ],
                sb_task_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                        },
                        'method': 'get',
                        'url': sandbox_client.API_URL + 'task/123456789',
                    },
                ],
            ),
            id='simple_case',
        ),
        pytest.param(
            RunTaskParams(
                type='TEST_TASK',
                input_parameters=(
                    'checkout_arcadia_from_url=arcadia:/arc/trunk/arcadia@666;'
                    'yet_another_param=there are spaces lol=kek;'
                    'json_too={"some_key": "some_value"}'
                ),
                sb_task_create_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'json': {
                                'custom_fields': [
                                    {
                                        'name': 'checkout_arcadia_from_url',
                                        'value': (
                                            'arcadia:/arc/trunk/arcadia@666'
                                        ),
                                    },
                                    {
                                        'name': 'yet_another_param',
                                        'value': 'there are spaces lol=kek',
                                    },
                                    {
                                        'name': 'json_too',
                                        'value': '{"some_key": "some_value"}',
                                    },
                                ],
                                'description': 'Some\nmultiline description',
                                'owner': 'ROBOT_TAXI_SANDLOAD',
                                'tags': [],
                                'type': 'TEST_TASK',
                            },
                        },
                        'method': 'post',
                        'url': sandbox_client.API_URL + 'task',
                    },
                ],
                sb_batch_tasks_start_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'json': {'id': [123456789]},
                        },
                        'method': 'put',
                        'url': sandbox_client.API_URL + 'batch/tasks/start',
                    },
                ],
                sb_task_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                        },
                        'method': 'get',
                        'url': sandbox_client.API_URL + 'task/123456789',
                    },
                ],
            ),
            id='with_input_parameters',
        ),
        pytest.param(
            RunTaskParams(
                type='TEST_TASK',
                tags=['FIRST_TAG', 'SECOND_TAG'],
                sb_task_create_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'json': {
                                'custom_fields': [],
                                'description': 'Some\nmultiline description',
                                'owner': 'ROBOT_TAXI_SANDLOAD',
                                'tags': ['FIRST_TAG', 'SECOND_TAG'],
                                'type': 'TEST_TASK',
                            },
                        },
                        'method': 'post',
                        'url': sandbox_client.API_URL + 'task',
                    },
                ],
                sb_batch_tasks_start_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'json': {'id': [123456789]},
                        },
                        'method': 'put',
                        'url': sandbox_client.API_URL + 'batch/tasks/start',
                    },
                ],
                sb_task_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                        },
                        'method': 'get',
                        'url': sandbox_client.API_URL + 'task/123456789',
                    },
                ],
            ),
            id='with_tags',
        ),
        pytest.param(
            RunTaskParams(
                type='INCORRECT_TASK',
                sb_task_create_calls=[
                    {
                        'kwargs': {
                            'headers': {
                                'Authorization': 'OAuth sandbox-token',
                            },
                            'json': {
                                'custom_fields': [],
                                'description': 'Some\nmultiline description',
                                'owner': 'ROBOT_TAXI_SANDLOAD',
                                'tags': [],
                                'type': 'INCORRECT_TASK',
                            },
                        },
                        'method': 'post',
                        'url': sandbox_client.API_URL + 'task',
                    },
                ],
                sb_batch_tasks_start_calls=[],
                sb_task_calls=[],
                tc_report_build_problems_calls=[
                    {
                        'description': (
                            f'Sandbox API {sandbox_client.API_URL}task '
                            'error: status - 400, text - '
                            '{"reason": "Incorrect task type '
                            'u\'INCORRECT_TASK\'"}'
                        ),
                        'identity': None,
                    },
                ],
            ),
            id='non_existent_task',
        ),
        pytest.param(
            RunTaskParams(type='TEST_TASK', tool_debug=True), id='TOOL_DEBUG',
        ),
    ],
)
def test_run_task(monkeypatch, teamcity_report_problems, sandbox, params):
    if params.tool_debug:
        monkeypatch.setattr('sandbox_task.DEBUG', '1')
    sandbox.patch_all()

    argv = [
        'run-task',
        '--type',
        params.type,
        '--description',
        'Some\nmultiline description',
    ]
    if params.tags:
        argv.extend(['--tags', *params.tags])
    if params.input_parameters:
        argv.extend(['--input-parameters', params.input_parameters])

    sandbox_task.main(argv)

    assert sandbox.task_create.calls == params.sb_task_create_calls
    assert sandbox.batch_tasks_start.calls == params.sb_batch_tasks_start_calls
    assert sandbox.task.calls == params.sb_task_calls
    assert (
        teamcity_report_problems.calls == params.tc_report_build_problems_calls
    )
