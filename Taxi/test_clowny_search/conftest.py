# pylint: disable=redefined-outer-name
from typing import Optional
import zlib

import pytest

import clowny_search.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from clowny_search.generated.cron import run_cron  # noqa: I100


pytest_plugins = ['clowny_search.generated.service.pytest_plugins']

CLOWNDUCTOR_SEARCH_ALL = [
    {
        'project_id': 2,
        'project_name': 'eda',
        'services': [
            {
                'id': 5,
                'name': 'eda_service_1_smth',
                'artifact_name': 'ubuntu',
                'cluster_type': 'nanny',
                'st_task': 'TAXIADMIN-100500',
                'production_ready': False,
                'requester': 'unit_test',
                'project_id': 2,
                'abc_service': 'eda1',
            },
            {
                'id': 6,
                'name': 'eda_service_3_smth',
                'artifact_name': 'ubuntu',
                'cluster_type': 'nanny',
                'st_task': 'TAXIADMIN-100500',
                'production_ready': False,
                'requester': 'unit_test',
                'project_id': 2,
                'abc_service': 'eda2',
            },
            {
                'id': 7,
                'name': 'eda_service_5_smth',
                'artifact_name': 'ubuntu',
                'cluster_type': 'nanny',
                'st_task': 'TAXIADMIN-100500',
                'production_ready': False,
                'requester': 'unit_test',
                'project_id': 2,
                'abc_service': 'eda3',
            },
        ],
    },
    {'project_id': 3, 'project_name': 'lavka_empty', 'services': []},
    {
        'project_id': 4,
        'project_name': 'project_with_deleted_services',
        'services': [],
    },
    {
        'project_id': 1,
        'project_name': 'taxi',
        'services': [
            {
                'id': 1,
                'name': 'taxi_service_1_smth',
                'artifact_name': 'ubuntu',
                'cluster_type': 'nanny',
                'st_task': 'TAXIADMIN-100500',
                'production_ready': False,
                'requester': 'unit_test',
                'project_id': 1,
                'abc_service': 'taxi1',
            },
            {
                'id': 2,
                'name': 'taxi_service_2_smth',
                'artifact_name': 'ubuntu',
                'cluster_type': 'nanny',
                'st_task': 'TAXIADMIN-100500',
                'production_ready': False,
                'requester': 'unit_test',
                'project_id': 1,
                'abc_service': 'taxi2',
            },
            {
                'id': 3,
                'name': 'taxi_service_3_smth',
                'artifact_name': 'ubuntu',
                'cluster_type': 'nanny',
                'st_task': 'TAXIADMIN-100500',
                'production_ready': False,
                'requester': 'unit_test',
                'project_id': 1,
                'abc_service': 'taxi3',
            },
            {
                'id': 4,
                'name': 'taxi_service_4_smth',
                'artifact_name': 'ubuntu',
                'cluster_type': 'nanny',
                'st_task': 'TAXIADMIN-100500',
                'production_ready': False,
                'requester': 'unit_test',
                'project_id': 1,
                'abc_service': 'taxi4',
            },
        ],
    },
]


@pytest.fixture
async def cs_web(taxi_clowny_search_web, import_clown):
    class CsWeb:
        @classmethod
        async def package_search(
                cls,
                query: Optional[dict] = None,
                cursor: Optional[str] = None,
                page_size: Optional[int] = None,
        ):
            body: dict = {}
            if query is not None:
                body['query'] = query
            if cursor is not None:
                body['cursor'] = cursor
            if page_size is not None:
                body['page-size'] = page_size
            return await taxi_clowny_search_web.post(
                '/v1/packages/search', json=body,
            )

        @classmethod
        async def package_report(
                cls, fqdn: str, package_name: str, package_version: str,
        ):
            return await taxi_clowny_search_web.put(
                '/v1/packages/report-version',
                params={'package_name': package_name, 'fqdn': fqdn},
                json={'package_version': package_version},
                headers={'content-type': 'application/json'},
            )

    # re-read settings at the test's setup stage
    await import_clown()

    return CsWeb()


@pytest.fixture
async def import_clown(mock_clown):
    async def do_import():
        await run_cron.main(['clowny_search.crontasks.import_clown'])

    return do_import


@pytest.fixture
async def mock_clown(mockserver, request):
    @mockserver.json_handler('/clownductor/api/projects')
    async def _mock_cd_projects(request):
        return [
            {'id': 1, 'name': 'proj_1', 'namespace_id': 1},
            {'id': 2, 'name': 'proj_2', 'namespace_id': 2},
        ]

    @mockserver.json_handler('/clownductor/v1/services/search/')
    async def _mock_services_search(request):
        name = request.query['name']
        projects = CLOWNDUCTOR_SEARCH_ALL
        result = []
        for project in projects:
            project_services = []
            if project.get('services'):
                for service in project['services']:
                    if name in service['name']:
                        project_services.append(service)
            if project_services:
                project['services'] = project_services
                result.append(project)
        return {'projects': result}

    @mockserver.json_handler('/clownductor/api/services')
    async def _mock_cd_services(request):
        if request.query['project_id'] == '1':
            return [
                {
                    'id': 10,
                    'name': 'alpha',
                    'cluster_type': 'uservices',
                    'project_id': 1,
                    'abc_service': 'taxiuserviceslug10',
                },
                {
                    'id': 11,
                    'name': 'beta',
                    'cluster_type': 'uservices',
                    'project_id': 1,
                    'abc_service': 'taxiuserviceslug11',
                },
                {
                    'id': 12,
                    'name': 'gamma',
                    'cluster_type': 'uservices',
                    'project_id': 1,
                },
            ]

        if request.query['project_id'] == '2':
            return [
                {
                    'id': 20,
                    'name': 'delta',
                    'cluster_type': 'uservices',
                    'project_id': 1,
                    'abc_service': 'taxiuserviceslug20',
                },
            ]

        assert False

    @mockserver.json_handler('/clownductor/v1/branches/')
    async def _mock_branches(request):
        service_id = request.query['service_id']
        return [
            {
                'endpointsets': [],
                'env': env,
                # "full_direct_link" : "https://example.com",
                'service_id': 354400,
                'direct_link': f'taxi_{service_id}',
                'configs': [],
                'name': 'stable',
                'id': (
                    zlib.crc32(service_id.encode()) + zlib.crc32(env.encode())
                ),
            }
            for env in ['stable', 'testing']
        ]

    @mockserver.json_handler('/clownductor/v1/hosts/')
    async def _mock_hosts(request):
        branch_id = request.query['branch_id']
        return [
            {
                'service_name': 'clowny-search',
                'name': (
                    f'taxi-clowny-search-{branch_id}-{i}.man.yp-c.yandex.net'
                ),
                'direct_link': 'taxi_clowny-search_pre_stable',
                'project_name': 'taxi-devops',
                'project_id': 150,
                'branch_id': int(branch_id),
                'datacenter': 'man',
                'service_id': 355944,
                'branch_name': 'pre_stable',
            }
            for i in [1, 2]
        ]

    @mockserver.json_handler('/clownductor/v1/parameters/service_values/')
    async def _mock_values(request):
        sid = request.query['service_id']
        assert sid in ['10', '11', '12', '20']

        return {
            'subsystems': [
                {
                    'subsystem_name': 'service_info',
                    'parameters': [
                        {
                            'name': 'hostnames',
                            'value': {
                                'testing': [f'{sid}.taxi.tst.yandex.net'],
                                'unstable': [f'{sid}.taxi.dev.yandex.net'],
                                'production': [f'{sid}.taxi.yandex.net'],
                            },
                        },
                    ],
                },
            ],
        }


@pytest.fixture
async def report(cs_web):
    async def do_report(
            fqdn='host11_11', package_version='1.0', package_name='pilorama',
    ) -> None:
        response = await cs_web.package_report(
            package_name=package_name,
            fqdn=fqdn,
            package_version=package_version,
        )
        assert response.status == 200
        content = await response.text()
        assert content == ''

    return do_report


@pytest.fixture
async def search(cs_web):
    async def do_search(**kwargs):
        def results_key(value: dict):
            return value['package-name'], value['hostname']

        response = await cs_web.package_search(query=kwargs)
        assert response.status == 200
        json = await response.json()
        items = json['results']
        assert len(json) == 1

        # sort for a more easy comparison
        items.sort(key=results_key)
        return items

    return do_search
