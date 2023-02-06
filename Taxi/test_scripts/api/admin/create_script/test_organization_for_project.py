from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest


class Case(NamedTuple):
    url: str
    organization: str
    extra_params: Optional[Dict] = None


@pytest.mark.parametrize(
    'url, organization, extra_params',
    [
        Case(
            url=(
                'https://github.yandex-team.ru/taxi/tools/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
            organization='taxi',
        ),
        Case(
            url=(
                'https://github.yandex-team.ru/taximeter/taxi-cloud-yandex/'
                'blob/a27746b6d836de3b10563ce9794ac890b870553a/src/'
                'Yandex.Taximeter.ScriptRunner/Scripts/ReplicateQcHistory.cs'
            ),
            organization='taximeter',
        ),
        Case(
            url=(
                'https://github.yandex-team.ru/taxi/tools-py3/blob/'
                '0ce7ba7f3b38e91dc288b093db005eeb6282aa2a/'
                'corp-orders/corp_orders/storage/postgresql/schemas/v5.sql'
            ),
            organization='taxi',
        ),
        Case(
            url=(
                'https://github.yandex-team.ru/taxi/'
                'hiring_billing_yql_scripts/'
                'blob/30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'taxi_hiring_billing/m4326_debugging_script.py'
            ),
            organization='hiring_billing_yql_scripts',
        ),
        Case(
            url=(
                'https://github.yandex-team.ru/taxi/tools-py3/'
                'blob/a27746b6d836de3b10563ce9794ac890b870553a/'
                'taxi_scripts/test.py'
            ),
            organization='taxi',
        ),
        Case(
            url=(
                'https://github.yandex-team.ru/taxi/tools-py3/'
                'blob/a27746b6d836de3b10563ce9794ac890b870553a/'
                'taxi_clowny-balancer/test.py'
            ),
            organization='taxi-infra',
        ),
        Case(
            url=(
                'https://github.yandex-team.ru/taxi/tools-py3/'
                'blob/a27746b6d836de3b10563ce9794ac890b870553a/'
                'lavka_grocery-coupons/test.py'
            ),
            organization='lavka',
        ),
        Case(
            url=(
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            organization='lavka',
            extra_params={
                'cgroup': 'lavka_grocery-coupons',
                'execute_type': 'psql',
            },
        ),
        Case(
            url=(
                'https://bb.yandex-team.ru/projects/eda/repos/'
                'infrastructure_admin_scripts/browse/eda_prod_mysql_galera/'
                '2020_02/2020_02_17_17_12_EDADEV-26922.sql?'
                'at=bc7e8cbedd62ff050b42d82e57ce0355aae2f366'
            ),
            organization='eda',
        ),
        Case(
            url=(
                'https://github.yandex-team.ru/taxi-dwh/dwh-migrations/blob/'
                '985bafd30ece0e4720cfd77d49e953c1afa45ff1/'
                'taxi_dmp_taxi_etl/migrations/TAXIDWH-5300_test_os_user.py'
            ),
            organization='taxi-dwh',
        ),
        Case(
            url=(
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'dwh-migrations/browse/'
                'taxi_dmp-meta-etl/migrations/test_script.py'
            ),
            organization='taxi-dwh',
        ),
        Case(
            url=(
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'dwh-migrations/browse/'
                'taxi_dmp-meta-etl/migrations/test_script.py'
            ),
            organization='taxi-dwh',
            extra_params={'execute_type': 'dmp-runner'},
        ),
        Case(
            url=(
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'dwh-migrations/browse/taxi_dmp_taxi_etl/taxi_etl/'
                'migrations/DMPDEV_5319.py?'
                'at=f11237383fb9cab3ac30d3b78ac6382f95213191'
            ),
            organization='taxi-dwh',
            extra_params={'execute_type': 'dmp-runner'},
        ),
        Case(
            url=(
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'dwh-migrations/browse/taxi_dmp_taxi_etl/taxi_etl/'
                'migrations/DMPDEV_5319.py?'
                'at=f11237383fb9cab3ac30d3b78ac6382f95213191'
            ),
            organization='taxi-dwh',
        ),
        Case(
            url=(
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'hiring_billing_yql_scripts/browse/'
                'taxi_hiring_taxiparks_gambling/'
                'scouts_billing_yql/new_billing.yql?'
                'at=1af8f24457fc0f1b5881c0620d44e311567f187f'
            ),
            organization='hiring_billing_yql_scripts',
        ),
    ],
)
@pytest.mark.config(
    SCRIPTS_FEATURES={
        'try_get_real_organization': True,
        'convert_gh_to_bb': False,
    },
    SCRIPTS_ALLOW_MASTER_BLOB=True,
    SCRIPTS_CHECK_SERVICE_NAME_SETTINGS={
        'enabled': True,
        'specific_names': [],
    },
)
async def test_organizations(
        patch, find_script, scripts_client, url, organization, extra_params,
):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def _check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def _create_draft_mock(*args, **kwargs):
        params = kwargs.get('params')
        assert organization == params.get('organization')
        return {}

    @patch('taxi.clients.taximeter.TaximeterApiClient.script_check')
    async def _script_check_taximeter_mock(*args, **kwargs):
        pass

    @patch('scripts.lib.vcs_utils.github_utils._check_py3_project')
    async def _check_py3_project(github_client, user, project, log_extra=None):
        pass

    @patch('scripts.lib.clients.conductor.Client.find_project_name')
    async def _conductor_find_project_name(group):
        if group in {'taxi_scripts'}:
            return 'taxi'
        if group in {'eda_prod_mysql_galera'}:
            return 'eda'

    @patch('scripts.lib.clients.clownductor.Client.search_clownductor_service')
    async def _search_clownductor_service(service_name):
        projects = []
        if service_name in {'grocery-coupons'}:
            projects = [
                {
                    'project_name': 'lavka',
                    'project_id': 10,
                    'services': [
                        {'name': 'grocery-coupons', 'cluster_type': 'nanny'},
                    ],
                },
                {
                    'project_name': 'taxi',
                    'project_id': 2,
                    'services': [
                        {'name': 'grocery-coupons', 'cluster_type': 'nanny'},
                    ],
                },
            ]
        if service_name in {'clowny-balancer'}:
            projects = [
                {
                    'project_name': 'taxi-infra',
                    'project_id': 1,
                    'services': [
                        {'name': 'clowny-balancer', 'cluster_type': 'nanny'},
                        {'name': 'clowny-balancer', 'cluster_type': 'mongo'},
                    ],
                },
            ]
        if service_name in {'dmp-meta-etl'}:
            projects = [
                {
                    'project_name': 'taxi-dmp',
                    'project_id': 3,
                    'services': [
                        {'name': service_name, 'cluster_type': 'nanny'},
                    ],
                },
            ]
        return {'projects': projects}

    @patch('scripts.lib.clients.conductor.Client.check_cgroup_exists')
    async def _check_cgroup_exists(group, log_extra=None):
        return group in {
            'taxi_scripts',
            'taxi_hiring_billing',
            'taxi_hiring_taxiparks_gambling',
            'eda_prod_mysql_galera',
            'taxi_dmp_taxi_etl',
        }

    params = {
        'url': url,
        'arguments': [],
        'request_id': '123',
        'comment': '',
        'ticket': 'TAXIPLATFORM-1',
    }
    if extra_params is not None:
        params.update(extra_params)
    response = await scripts_client.post(
        '/scripts/', json=params, headers={'X-Yandex-Login': 'd1mbas'},
    )
    data = await response.json()
    assert response.status == 200, data
    script = await find_script(data['id'])
    assert script['organization'] == organization
    assert len(_create_draft_mock.calls) == 1
