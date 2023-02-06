# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import inspect
import os
from typing import Dict
from typing import Type

import pytest

import clowny_balancer.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from clowny_balancer.generated.web.pg import plugin as pg
from clowny_balancer.lib import cubes
from clowny_balancer.lib import models

pytest_plugins = ['clowny_balancer.generated.service.pytest_plugins']

from task_processor_lib import (  # noqa: E501,I100 pylint: disable=C0413
    types as tp_mock_types,
)


@pytest.fixture()
def mock_clownductor_handlers(mock_clownductor):
    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        branches = [
            {
                'id': 1,
                'env': 'stable',
                'direct_link': 'taxi_service_stable',
                'service_id': 1,
                'name': 'stable',
            },
            {
                'id': 2,
                'env': 'prestable',
                'direct_link': 'taxi_service_prestable',
                'service_id': 1,
                'name': 'prestable',
            },
            {
                'id': 3,
                'env': 'testing',
                'direct_link': 'taxi_service_testing',
                'service_id': 1,
                'name': 'testing',
            },
            {
                'id': 4,
                'env': 'stable',
                'direct_link': 'taxi_one-service_stable',
                'service_id': 2,
                'name': 'stable',
            },
            {
                'id': 5,
                'env': 'testing',
                'direct_link': 'taxi_service_tank',
                'service_id': 1,
                'name': 'tank-testing',
            },
        ]
        ids = [x['id'] for x in branches]
        if 'branch_ids' in request.query:
            ids = [int(x) for x in request.query['branch_ids'].split(',')]
        elif 'branch_id' in request.query:
            ids = [int(request.query['branch_id'])]
        elif 'service_id' in request.query:
            ids = [
                x['id']
                for x in branches
                if x['service_id'] == int(request.query['service_id'])
            ]
        return [x for x in branches if x['id'] in ids]

    @mock_clownductor('/v1/services/')
    def _services_handler(request):
        _id = int(request.query['service_id'])
        assert _id in {1, 2}
        return [
            {
                'id': _id,
                'name': 'service',
                'project_id': 1,
                'cluster_type': 'nanny',
            },
        ]

    @mock_clownductor('/api/projects')
    def _projects_handler(request):
        assert int(request.query['project_id']) == 1
        return [
            {
                'id': 1,
                'name': 'taxi',
                'namespace_id': 1,
                'env_params': {
                    'stable': {
                        'domain': 'test_stable.tst',
                        'juggler_folder': 'juggler_folder',
                    },
                    'unstable': {
                        'domain': 'test_unstable.tst',
                        'juggler_folder': 'juggler_folder',
                    },
                    'testing': {
                        'domain': 'test_test.tst',
                        'juggler_folder': 'juggler_folder',
                    },
                    'general': {
                        'project_prefix': 'taxi',
                        'docker_image_tpl': 'image/$',
                    },
                },
            },
        ]


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'ABC_OAUTH': 'abc_oauth',
            'NANNY_OAUTH': 'nanny_oauth',
            'STAFF_OAUTH': 'staff_oauth',
            'STARTRACK_API_PROFILES': {
                'robot-taxi-clown': {
                    'url': 'http://test-startrack-url/',
                    'org_id': 0,
                    'oauth_token': 'some_token',
                },
            },
        },
    )
    simple_secdist.update(
        {
            'AWACS_OAUTH': 'awacs-oauth',
            'DNS_OAUTH': 'dns-oauth',
            'L3MGR_OAUTH': 'l3mgr-oauth',
            'ROBOT_CREDENTIALS': {'login': 'robot-taxi-clown'},
        },
    )
    return simple_secdist


class _CheckCubesFixture:
    def __init__(self):
        self._cubes_by_name: Dict[str, Type[cubes.base.Cube]] = {
            x.name(): x for x in cubes.get_all()
        }
        self._cubes_called = {x: 0 for x in self._cubes_by_name.keys()}

    def inc(self, name):
        self._cubes_called[name] += 1

    def check_params(self, name, response):
        cube = self._cubes_by_name[name]
        needed_parameters = set(cube.needed_parameters())
        optional_parameters = set(cube.optional_parameters())
        assert not needed_parameters.intersection(optional_parameters)

        output_parameters = cube.output_parameters()
        if output_parameters and response['status'] == 'success':
            assert set(response['payload'].keys()) == set(output_parameters)
        if not output_parameters:
            assert (
                'payload' not in response
            ), 'payload is not empty, but no output params are specified'

    def teardown_check(self):
        not_called_cubes = [
            name for name, count in self._cubes_called.items() if not count
        ]
        assert not not_called_cubes, not_called_cubes


@pytest.fixture(scope='session')
def check_cubes():
    _fixture = _CheckCubesFixture()
    yield _fixture
    _fixture.teardown_check()


@pytest.fixture
def get_all_cubes(taxi_clowny_balancer_web):
    async def _do_it():
        response = await taxi_clowny_balancer_web.get(
            '/task-processor/v1/cubes/',
        )
        assert response.status == 200
        return await response.json()

    return _do_it


@pytest.fixture(name='call_cube_client')
def _call_cube_client(taxi_clowny_balancer_web):
    return taxi_clowny_balancer_web


@pytest.fixture
def call_cube(raw_call_cube, check_cubes):
    async def _do_it(
            name: str,
            input_data: dict,
            job_id=0,
            task_id=0,
            retries=0,
            status='in_progress',
    ):
        check_cubes.inc(name)
        response = await raw_call_cube(
            name=name,
            input_data=input_data,
            job_id=job_id,
            task_id=task_id,
            retries=retries,
            status=status,
        )
        assert response.status == 200
        data = await response.json()
        check_cubes.check_params(name, data)
        return data

    return _do_it


@pytest.fixture
def mock_task_processor_start_job(mock_task_processor):
    def do_it():
        @mock_task_processor('/v1/jobs/start/')
        async def handler(request):
            assert request.method == 'POST'
            return {'job_id': 1}

        return handler

    return do_it


@pytest.fixture
def mock_github(patch_aiohttp_session, response_mock, simple_secdist):
    def _do_it(github_responses, github_api_url=None):
        simple_secdist['settings_override'].update(
            {'GITHUB_AUTH': 'github_oauth'},
        )
        if github_api_url is None:
            github_api_url = (
                'https://github.yandex-team.ru'
                '/api/v3/repos/taxi/infra-cfg-graphs/'
            )

        @patch_aiohttp_session(github_api_url)
        def handler(method, url, **kwargs):
            method_url = url.replace(github_api_url, '').replace('/', '_')
            if method == 'post':
                if url.endswith('/blobs'):
                    content_key = kwargs['json']['content'][:4]
                    return response_mock(
                        json=github_responses[method_url]['content'][
                            content_key
                        ],
                        status=github_responses[method_url]['status'],
                    )
            return response_mock(
                json=github_responses[method_url]['content'],
                status=github_responses[method_url]['status'],
            )

        return handler

    return _do_it


@pytest.fixture
def relative_load_plaintext():
    """
    Load text from `./static/filename`.
    Raises `ValueError` if file not found or.
    """

    def _wrapper(filename):
        caller_filename = inspect.stack()[1][1]
        caller_dir = os.path.dirname(os.path.abspath(caller_filename))
        full_path = os.path.join(caller_dir, 'static', filename)
        try:
            with open(full_path) as fileobj:
                return fileobj.read()
        except FileNotFoundError as exc:
            raise ValueError('cannot load json from %s: %s' % (full_path, exc))

    return _wrapper


@pytest.fixture
async def _default_tp_init_params(
        get_all_cubes, raw_call_cube, clown_cube_caller, clown_cubes_fixture,
):
    clown_provider, clown_cubes = clown_cubes_fixture

    async def self_cube_caller(cube, stage, request_data):
        return await raw_call_cube(name=cube.name, **request_data)

    provider = tp_mock_types.Provider(
        name='clowny-balancer', id=34, cube_caller=self_cube_caller,
    )

    return {
        'providers': [clown_provider, provider],
        'cubes': [
            *(
                tp_mock_types.Cube(
                    provider=provider,
                    check_input_mappings=True,
                    check_output_mappings=True,
                    **x,
                )
                for x in (await get_all_cubes())['cubes']
            ),
            *clown_cubes,
        ],
        'recipes': [],
        'raw_recipes': [],
    }


@pytest.fixture
def get_entry_point(web_context):
    async def do_it(ep_id):
        return await models.EntryPoint.fetch_one(
            context=web_context, db_conn=web_context.pg.secondary, id=ep_id,
        )

    return do_it


@pytest.fixture
def get_namespace(web_context):
    async def do_it(ns_id):
        return await models.Namespace.fetch_one(
            context=web_context, db_conn=web_context.pg.secondary, id=ns_id,
        )

    return do_it


@pytest.fixture
def mock_get_branch(mock_clownductor):
    def do_it():
        @mock_clownductor('/v1/branches/')
        def _branches(_):
            return [
                {
                    'id': 1,
                    'name': 'branch',
                    'env': 'stable',
                    'direct_link': 'taxi_service_stable',
                    'service_id': 0,
                },
            ]

    return do_it


@pytest.fixture
def mock_get_service(mock_clownductor):
    def do_it():
        @mock_clownductor('/v1/services/')
        def _services(_):
            return [
                {
                    'id': 1,
                    'name': 'service',
                    'project_id': 1,
                    'cluster_type': 'nanny',
                    'project_name': 'project',
                },
            ]

    return do_it


@pytest.fixture
def mock_get_project(mock_clownductor):
    def do_it(project_name):
        @mock_clownductor('/api/projects')
        def _projects(_):
            return [{'id': 1, 'name': project_name, 'namespace_id': 1}]

    return do_it


@pytest.fixture(name='pg_client')
def _pg_client(web_context) -> pg.Pg:
    return web_context.pg
