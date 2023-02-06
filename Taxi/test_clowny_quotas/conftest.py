# pylint: disable=redefined-outer-name
import pytest

import clowny_quotas.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['clowny_quotas.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist.update({'yp_api_token': 'yp_token'})
    return simple_secdist


@pytest.fixture
def taxi_clowny_quotas_mocks(mockserver, relative_load_json):
    """Put your mocks here"""

    @mockserver.json_handler('/clownductor/api/projects')
    async def _handler_projects(request):
        return [
            {
                'id': 2,
                'name': 'taxi',
                'network_testing': '_TAXITESTNETS_',
                'network_stable': '_HWTAXINETS_',
                'service_abc': 'taxiservicesdeploymanagement',
                'yp_quota_abc': 'taxiquotaypdefault',
                'tvm_root_abc': 'taxitvmaccess',
                'owners': {
                    'logins': [
                        'eatroshkin',
                        'glush',
                        'sgrebenyukov',
                        'aesdana',
                        'nikkraev',
                        'broom',
                        'oxcd8o',
                        'sokogen',
                        'nikslim',
                        'isharov',
                    ],
                    'groups': ['svc_vopstaxi'],
                },
                'env_params': {
                    'unstable': {
                        'domain': 'taxi.dev.yandex.net',
                        'juggler_folder': '',
                    },
                    'testing': {
                        'domain': 'taxi.tst.yandex.net',
                        'juggler_folder': '',
                    },
                    'stable': {
                        'domain': 'taxi.yandex.net',
                        'juggler_folder': '',
                    },
                    'general': {
                        'project_prefix': 'taxi',
                        'docker_image_tpl': 'taxi/{{ service }}/$',
                    },
                },
                'responsible_team': {
                    'ops': ['yandex_distproducts_browserdev_mobile_taxi_mnt'],
                    'developers': [],
                    'managers': [],
                    'superusers': ['isharov', 'nikslim'],
                },
                'yt_topic': {
                    'path': 'taxi/taxi-access-log',
                    'permissions': ['WriteTopic'],
                },
                'approving_managers': {'cgroups': [352], 'logins': []},
                'approving_devs': {'cgroups': [352, 493], 'logins': []},
                'pgaas_root_abc': 'taxistoragepgaas',
            },
        ]

    @mockserver.json_handler('/clownductor/api/services')
    async def _handler_services(request):
        return [
            {
                'id': 354257,
                'project_id': 1,
                'name': 'clowny-quotas',
                'artifact_name': 'taxi/clowny-quotas/$',
                'cluster_type': 'nanny',
                'st_task': '',
                'design_review_ticket': 'TODO',
                'wiki_path': 'https://wiki.yandex-team.ru/TODO',
                'abc_service': 'taxiclownyquotas',
                'tvm_testing_abc_service': 'taxiclownyquotas',
                'tvm_stable_abc_service': 'taxiclownyquotas',
                'production_ready': False,
                'direct_link': 'taxi_clowny-quotas',
                'new_service_ticket': 'TAXIADMIN-16511',
                'requester': 'khomikki',
                'service_url': (
                    f'https://github.yandex-team.ru/taxi/'
                    f'backend-py3/blob/develop/services/'
                    f'clowny-quotas/service.yaml'
                ),
            },
        ]

    @mockserver.json_handler('/clownductor/api/branches')
    async def _handler_brahches(request):
        return [
            {
                'id': 294471,
                'service_id': 354257,
                'name': 'pre_stable',
                'env': 'prestable',
                'direct_link': 'taxi_clowny-quotas_pre_stable',
                'configs': [],
            },
            {
                'id': 294472,
                'service_id': 354257,
                'name': 'stable',
                'env': 'stable',
                'direct_link': 'taxi_clowny-quotas_stable',
                'configs': [],
            },
        ]

    @mockserver.json_handler('/clownductor/api/hosts')
    async def _handler_hosts(request):
        return [
            {
                'branch_id': 294471,
                'name': 'taxi-clowny-quotas-pre-stable-2.sas.yp-c.yandex.net',
                'datacenter': 'sas',
                'branch_name': 'pre_stable',
                'service_name': 'clowny-quotas',
                'service_id': 354257,
                'project_name': 'taxi-infra',
                'project_id': 1,
            },
        ]
