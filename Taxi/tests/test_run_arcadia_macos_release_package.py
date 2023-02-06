# pylint: disable=invalid-name, too-many-lines
import dataclasses
from typing import Any
from typing import Dict
from typing import List

import pytest

import run_arcadia_macos_release_package
from taxi_buildagent.clients import arcadia
from taxi_buildagent.clients import conductor
from tests.utils import pytest_wraps


@pytest.fixture(name='prepare_sandbox')
def _prepare_sandbox(sandbox):
    def _prepare_sandbox_impl(resources_id_by_packages):
        sandbox.append_resource('BUILD_LOGS', '123456')
        for package, res_id in resources_id_by_packages.items():
            sandbox.append_resource(
                'YA_PACKAGE', res_id, package, package + '_1.0.0_all.tar.gz',
            )
        sandbox.patch_all()
        return sandbox

    return _prepare_sandbox_impl


@dataclasses.dataclass
class MacParams(pytest_wraps.Params):
    tool_debug: bool = False
    resources_id_by_packages: Dict[str, int] = dataclasses.field(
        default_factory=lambda: {'taxi-graph': 1111, 'taxi-graph-dev': 2222},
    )
    create_task_calls: List[Dict[str, Any]] = dataclasses.field(
        default_factory=lambda: [
            {
                'url': 'https://sandbox.yandex-team.ru/api/v1.0/task',
                'method': 'post',
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                    'json': {
                        'custom_fields': [
                            {
                                'name': 'checkout_arcadia_from_url',
                                'value': 'arcadia-arc:/#users/pac/graph-test',
                            },
                            {
                                'name': 'packages',
                                'value': (
                                    'taxi/graph/pkg.json;'
                                    'taxi/graph/pkg-dev.json'
                                ),
                            },
                            {
                                'name': 'target_platform',
                                'value': 'CLANG12-DARWIN-X86_64',
                            },
                            {'name': 'package_type', 'value': 'tarball'},
                            {'name': 'clear_build', 'value': True},
                            {'name': 'use_aapi_fuse', 'value': True},
                            {'name': 'use_arc_instead_of_aapi', 'value': True},
                            {'name': 'strip_binaries', 'value': False},
                        ],
                        'description': (
                            'Arcadia release taxi-graph (for Darwin)'
                        ),
                        'owner': 'ROBOT_TAXI_SANDLOAD',
                        'tags': ['TAXI_GRAPH', 'DARWIN'],
                        'type': 'YA_PACKAGE',
                    },
                },
            },
        ],
    )
    resources_calls: List[Dict[str, Any]] = dataclasses.field(
        default_factory=lambda: [
            {
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                },
                'method': 'get',
                'url': (
                    'https://sandbox.yandex-team.ru/api/v1.0/task/'
                    '123456789/resources'
                ),
            },
        ],
    )
    resource_attributes_calls: List[Dict[str, Any]] = dataclasses.field(
        default_factory=lambda: [
            {
                'url': (
                    'https://sandbox.yandex-team.ru/api/v1.0/resource/'
                    '1111/attribute/ttl'
                ),
                'method': 'put',
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                    'json': {'name': 'ttl', 'value': 'inf'},
                },
            },
            {
                'url': (
                    'https://sandbox.yandex-team.ru/api/v1.0/resource/'
                    '2222/attribute/ttl'
                ),
                'method': 'put',
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                    'json': {'name': 'ttl', 'value': 'inf'},
                },
            },
        ],
    )
    set_parameters_calls: List[Dict[str, Any]] = dataclasses.field(
        default_factory=lambda: [
            {
                'name': 'env.ARCADIA_PACKAGES_RESOURCES_ID_MAC',
                'value': '1111;2222',
            },
        ],
    )
    task_calls: List[Dict[str, Any]] = dataclasses.field(
        default_factory=lambda: [
            {
                'url': (
                    'https://sandbox.yandex-team.ru/api/v1.0/task/123456789'
                ),
                'method': 'get',
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                },
            },
        ],
    )
    batch_tasks_start_calls: List[Dict[str, Any]] = dataclasses.field(
        default_factory=lambda: [
            {
                'url': (
                    'https://sandbox.yandex-team.ru/api/v1.0/batch/tasks/start'
                ),
                'method': 'put',
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                    'json': {'id': [123456789]},
                },
            },
        ],
    )
    extra_args: List[str] = dataclasses.field(default_factory=lambda: [])


PARAMS = [
    MacParams(pytest_id='simple_case'),
    MacParams(
        pytest_id='without_build_output',
        resources_id_by_packages={},
        resource_attributes_calls=[],
        set_parameters_calls=[],
    ),
    MacParams(
        pytest_id='without_frozen_revision',
        create_task_calls=[
            {
                'url': 'https://sandbox.yandex-team.ru/api/v1.0/task',
                'method': 'post',
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                    'json': {
                        'custom_fields': [
                            {
                                'name': 'checkout_arcadia_from_url',
                                'value': 'arcadia-arc:/#users/pac/graph-test',
                            },
                            {
                                'name': 'packages',
                                'value': (
                                    'taxi/graph/pkg.json;'
                                    'taxi/graph/pkg-dev.json'
                                ),
                            },
                            {
                                'name': 'target_platform',
                                'value': 'CLANG12-DARWIN-X86_64',
                            },
                            {'name': 'package_type', 'value': 'tarball'},
                            {'name': 'clear_build', 'value': True},
                            {'name': 'use_aapi_fuse', 'value': True},
                            {'name': 'use_arc_instead_of_aapi', 'value': True},
                            {'name': 'strip_binaries', 'value': False},
                        ],
                        'description': (
                            'Arcadia release taxi-graph (for Darwin)'
                        ),
                        'owner': 'ROBOT_TAXI_SANDLOAD',
                        'tags': ['TAXI_GRAPH', 'DARWIN'],
                        'type': 'YA_PACKAGE',
                    },
                },
            },
        ],
    ),
    MacParams(
        pytest_id='TOOL_DEBUG',
        tool_debug=True,
        create_task_calls=[
            {
                'url': 'https://sandbox.yandex-team.ru/api/v1.0/task',
                'method': 'post',
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                    'json': {
                        'custom_fields': [
                            {
                                'name': 'checkout_arcadia_from_url',
                                'value': 'arcadia-arc:/#users/pac/graph-test',
                            },
                            {
                                'name': 'packages',
                                'value': (
                                    'taxi/graph/pkg.json;'
                                    'taxi/graph/pkg-dev.json'
                                ),
                            },
                            {
                                'name': 'target_platform',
                                'value': 'CLANG12-DARWIN-X86_64',
                            },
                            {'name': 'package_type', 'value': 'tarball'},
                            {'name': 'clear_build', 'value': True},
                            {'name': 'use_aapi_fuse', 'value': True},
                            {'name': 'use_arc_instead_of_aapi', 'value': True},
                            {'name': 'strip_binaries', 'value': False},
                        ],
                        'description': (
                            'Arcadia release taxi-graph (for Darwin)'
                        ),
                        'owner': 'ROBOT_TAXI_SANDLOAD',
                        'tags': ['TAXI_GRAPH', 'DARWIN', 'DEBUG'],
                        'type': 'YA_PACKAGE',
                    },
                },
            },
        ],
        resource_attributes_calls=[],
    ),
    MacParams(
        pytest_id='with_strip_flag',
        create_task_calls=[
            {
                'url': 'https://sandbox.yandex-team.ru/api/v1.0/task',
                'method': 'post',
                'kwargs': {
                    'headers': {'Authorization': 'OAuth sandbox-token'},
                    'json': {
                        'custom_fields': [
                            {
                                'name': 'checkout_arcadia_from_url',
                                'value': 'arcadia-arc:/#users/pac/graph-test',
                            },
                            {
                                'name': 'packages',
                                'value': (
                                    'taxi/graph/pkg.json;'
                                    'taxi/graph/pkg-dev.json'
                                ),
                            },
                            {
                                'name': 'target_platform',
                                'value': 'CLANG12-DARWIN-X86_64',
                            },
                            {'name': 'package_type', 'value': 'tarball'},
                            {'name': 'clear_build', 'value': True},
                            {'name': 'use_aapi_fuse', 'value': True},
                            {'name': 'use_arc_instead_of_aapi', 'value': True},
                            {'name': 'strip_binaries', 'value': True},
                        ],
                        'description': (
                            'Arcadia release taxi-graph (for Darwin)'
                        ),
                        'owner': 'ROBOT_TAXI_SANDLOAD',
                        'tags': ['TAXI_GRAPH', 'DARWIN'],
                        'type': 'YA_PACKAGE',
                    },
                },
            },
        ],
        extra_args=['--strip'],
    ),
]


@pytest_wraps.parametrize(PARAMS)
def test_mac_release(
        params,
        monkeypatch,
        patch_requests,
        prepare_sandbox,
        startrek,
        teamcity_set_parameters,
        teamcity_report_build_number,
):
    args = [
        '--project-name',
        'taxi-graph',
        '--path-to-project',
        'taxi/graph',
        '--packages',
        'taxi/graph/pkg.json;taxi/graph/pkg-dev.json',
        '--branch',
        'users/pac/graph-test',
        *params.extra_args,
    ]
    monkeypatch.setenv('ARCADIA_TOKEN', 'arcadia-token')
    monkeypatch.setenv('CONDUCTOR_TOKEN', 'conductor-token')
    monkeypatch.setenv('SANDBOX_TOKEN', 'sandbox-token')
    monkeypatch.setenv('STARTREK_COMPONENT_NAME', '')
    if params.tool_debug:
        monkeypatch.setattr('run_arcadia_macos_release_package.DEBUG', '1')

    sandbox = prepare_sandbox(params.resources_id_by_packages)

    @patch_requests(arcadia.API_URL + 'tree/history/trunk/arcadia')
    def mock_arcadia_tree_history(*args, **kwargs):
        return patch_requests.response(status_code=500)

    @patch_requests(conductor.BASE_URL + 'auth_update/ticket_add')
    def mock_conductor_ticket(*args, **kwargs):
        return patch_requests.response(status_code=500)

    @patch_requests(conductor.API_BASE_URL + 'package_version')
    def mock_conductor_packages_version(*args, **kwargs):
        return patch_requests.response(status_code=500)

    run_arcadia_macos_release_package.main(args)

    assert mock_arcadia_tree_history.calls == []
    assert sandbox.task_create.calls == params.create_task_calls
    assert sandbox.task_context.calls == []
    assert sandbox.task_resources.calls == params.resources_calls
    assert sandbox.resource.calls == params.resource_attributes_calls
    assert teamcity_set_parameters.calls == params.set_parameters_calls
    assert mock_conductor_ticket.calls == []
    assert mock_conductor_packages_version.calls == []
    assert startrek.create_ticket.calls == []
    assert startrek.get_ticket.calls == []
    assert startrek.update_ticket.calls == []
    assert startrek.get_opened_releases.calls == []
    assert teamcity_report_build_number.calls == []
    assert sandbox.task.calls == params.task_calls
    assert sandbox.batch_tasks_start.calls == params.batch_tasks_start_calls
    assert sandbox.download_resource.calls == []
