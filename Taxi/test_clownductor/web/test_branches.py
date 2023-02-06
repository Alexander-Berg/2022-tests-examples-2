import json

from aiohttp import web
import pytest

from clownductor.generated.service.mdb_api import plugin as mdb_plugin
from clownductor.internal import services as services_module
from clownductor.internal.db import db_types
from clownductor.internal.db import flavors
from clownductor.internal.presets import presets

CREATE_DEV_BRANCH_URL = '/v1/create_dev_branch/'
CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS = {
    'components': ['duty'],
    'description_template': {
        'remove_branch': 'Параметры окружения:\n{params}',
        'remove_nanny_service': 'Параметры сервиса:\n{params}',
    },
    'summary_template': {
        'remove_branch': (
            'Delete RTC-database environment: '
            '{project_name}-{service_name} {env}'
        ),
        'remove_nanny_service': (
            'Delete RTC-service: {project_name}-{service_name}'
        ),
    },
}
ENDPOINTSETS_NAMES = [
    {'id': 'rtc_balancer_khomikki-test_man', 'regions': ['MAN', 'SAS', 'VLA']},
    {
        'id': 'awacs-rtc_balancer_khomikki-test_man',
        'regions': ['MAN', 'SAS', 'VLA'],
    },
]


# pylint: disable=too-many-locals
@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.pgsql('clownductor')
@pytest.mark.parametrize('branch_preset', [*presets.PRESETS.keys()])
async def test_branches_add_nanny(
        task_processor,
        run_job_with_meta,
        login_mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
        add_service,
        add_nanny_branch_by_api,
        get_branch,
        get_branch_jobs,
        abc_mockserver,
        solomon_mockserver,
        staff_mockserver,
        get_branches,
        cookie_monster_mockserver,
        patch_github,
        branch_preset,
):  # pylint: disable=R0913

    login_mockserver()
    nanny_yp_mockserver()
    abc_mockserver()
    solomon_mockserver()
    staff_mockserver()
    cookie_monster_mockserver()
    patch_github()

    service = await add_service(
        'taxi', 'some-service', direct_link='taxi_some-service',
    )
    branch_id = await add_nanny_branch_by_api(
        service_id=service['id'],
        branch_name='some-branch',
        preset=branch_preset,
    )
    jobs = await get_branch_jobs(branch_id)
    assert len(jobs) == 1
    job = task_processor.job(jobs[0]['job']['id'])
    await run_job_with_meta(job)

    branch = await get_branch(branch_id)
    assert branch[0]['direct_link'] == 'taxi_some-service_some-branch'

    branches = await get_branches(service['id'])
    assert len(branches) == 1


@pytest.fixture
def _add_db_branch_mocks(patch, mock_dispenser, load_json, mock_strongbox):
    def _build_fixture(slug, flavor, service_name):
        @mock_dispenser('/common/api/v1/projects')
        # pylint: disable=W0612
        async def handler(request):  # pylint: disable=unused-argument
            return web.json_response(
                {
                    'result': [
                        {
                            'key': 'taxistoragepgaas',
                            'name': 'taxistoragedbaas',
                            'description': '',
                            'abcServiceId': 2219,
                            'responsibles': {
                                'persons': [],
                                'yandexGroups': {},
                            },
                            'members': {'persons': [], 'yandexGroups': {}},
                            'parentProjectKey': 'taxistorage',
                            'subprojectKeys': [slug],
                            'person': None,
                        },
                    ],
                },
            )

        quotas_json = load_json('quotas.json')

        @mock_dispenser('/db/api/v2/quotas')
        # pylint: disable=W0612
        async def quotas_handler(request):  # pylint: disable=unused-argument
            return web.json_response(quotas_json)

        @mock_dispenser(f'/db/api/v1/quotas/{slug}/mdb/ssd/ssd-quota')
        # pylint: disable=W0612
        async def ssd_handler(request):
            assert request.json == {'maxValue': 257698037760, 'unit': 'BYTE'}
            return web.json_response({})

        @mock_dispenser(f'/db/api/v1/quotas/{slug}/mdb/ram/ram-quota')
        # pylint: disable=W0612
        async def ram_handler(request):
            actual = quotas_json['result'][0]['ownActual']
            assert request.json == {
                'maxValue': 3 * flavors.ram_for(flavor) + actual,
                'unit': 'BYTE',
            }
            return web.json_response({})

        @mock_dispenser(f'/db/api/v1/quotas/{slug}/mdb/cpu/cpu-quota')
        # pylint: disable=W0612
        async def cpu_handler(request):
            actual = quotas_json['result'][3]['ownActual']
            assert request.json == {
                'maxValue': 3 * flavors.cpu_for(flavor) + actual,
                'unit': 'PERMILLE_CORES',
            }
            return web.json_response({})

        @mock_dispenser('/db/api/v1/quotas/mock_dispenser/mdb/ssd/ssd-quota')
        def _(_):
            return {}

        @mock_dispenser('/db/api/v1/quotas/mock_dispenser/mdb/ram/ram-quota')
        def _(_):
            return {}

        @mock_dispenser('/db/api/v1/quotas/mock_dispenser/mdb/cpu/cpu-quota')
        def _(_):
            return {}

        @mock_strongbox('/v1/secrets/')
        # pylint: disable=W0612
        async def secrets_handler(request):
            assert request.json['data']['project'] == 'taxi'
            assert request.json['data']['provider_name'] == service_name
            return web.json_response(
                {
                    'yav_secret_uuid': 'sec-XXX',
                    'yav_version_uuid': 'ver-YYY',
                    'name': 'SOME_NAME',
                },
            )

        @patch('clownductor.internal.utils.startrek.find_comment')
        # pylint: disable=unused-variable
        async def find_comment(*args, **kwargs):
            return None

        @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
        # pylint: disable=unused-variable
        async def create_comment(*args, **kwargs):
            return

        @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
        # pylint: disable=unused-variable
        async def get_ticket(*args, **kwargs):
            return {}

        @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
        # pylint: disable=unused-variable
        async def execute_transition(*args, **kwargs):
            return {}

    return _build_fixture


@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.pgsql('clownductor')
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'give_secret_ro_access': True})
async def test_branches_add_postgres(
        task_processor,
        run_job_with_meta,
        abc_mockserver,
        login_mockserver,
        mdb_mockserver,
        add_service,
        solomon_mockserver,
        staff_mockserver,
        add_postgres_branch,
        get_branch_jobs,
        yav_mockserver,
        get_branch,
        patch_github,
        _add_db_branch_mocks,
):  # pylint: disable=R0913
    login_mockserver()
    solomon_mockserver()
    staff_mockserver()
    abc_mockserver(services=True)
    mdb_mockserver(
        slug='taxipgaassomeservice',
        service_type=mdb_plugin.ServiceType.POSTGRES,
    )
    yav_mockserver()
    patch_github()
    flavor = 's2.micro'
    _add_db_branch_mocks(
        slug='taxipgaassomeservice',
        flavor=flavor,
        service_name='some-service',
    )

    service = await add_service(
        'taxi',
        'some-service',
        type_='postgres',
        direct_link='some-serivice_pg',
        abc_service='mock_dispenser',
    )

    branch_id = await add_postgres_branch(
        service['id'], 'shard1', 'unstable', flavor, 50,
    )

    jobs = await get_branch_jobs(branch_id)
    assert len(jobs) == 1
    job = task_processor.job(jobs[0]['job']['id'])
    await run_job_with_meta(job)

    branch = await get_branch(branch_id)
    assert branch[0]['direct_link'] == 'mdbq9iqofu9vus91r2j9'


@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.pgsql('clownductor')
@pytest.mark.parametrize(
    'db_type, slug, flavor, service_type',
    [
        (
            db_types.DbType.Postgres,
            'taxipgaasdbservice',
            flavors.FlavorNames.s2_micro,
            mdb_plugin.ServiceType.POSTGRES,
        ),
        (
            db_types.DbType.Mongo,
            'taximongoaasdbservice',
            flavors.FlavorNames.s2_micro,
            mdb_plugin.ServiceType.MONGO,
        ),
        (
            db_types.DbType.Redis,
            'taxiredisdbservice',
            flavors.FlavorNames.m2_micro,
            mdb_plugin.ServiceType.REDIS,
        ),
    ],
)
async def test_branches_add_db(
        task_processor,
        run_job_with_meta,
        abc_mockserver,
        login_mockserver,
        mdb_mockserver,
        add_service,
        solomon_mockserver,
        staff_mockserver,
        add_db_branch,
        get_branch_jobs,
        yav_mockserver,
        get_branch,
        patch_github,
        _add_db_branch_mocks,
        db_type,
        slug,
        flavor,
        service_type,
):  # pylint: disable=R0913
    login_mockserver()
    solomon_mockserver()
    staff_mockserver()
    abc_mockserver(services=True)
    mdb_mockserver(slug=slug, service_type=service_type)
    yav_mockserver()
    patch_github()
    service_name = 'db-service'
    _add_db_branch_mocks(
        slug=slug, flavor=flavor.value, service_name=service_name,
    )

    cluster_type_map = {
        db_types.DbType.Postgres: services_module.ClusterType.POSTGRES,
        db_types.DbType.Mongo: services_module.ClusterType.MONGO_MDB,
        db_types.DbType.Redis: services_module.ClusterType.REDIS_MDB,
    }
    service = await add_service(
        'taxi',
        service_name,
        type_=cluster_type_map[db_type].value,
        direct_link='some-serivice_pg',
        abc_service='mock_dispenser',
    )

    branch_id = await add_db_branch(
        service['id'], 'shard1', 'unstable', flavor.value, 50, db_type.value,
    )

    jobs = await get_branch_jobs(branch_id)
    assert len(jobs) == 1
    job = task_processor.job(jobs[0]['job']['id'])
    await run_job_with_meta(job)

    branch = await get_branch(branch_id)
    assert branch[0]['direct_link'] == 'mdbq9iqofu9vus91r2j9'


def _access_feature(enabled=True, for_stable=True):
    return pytest.mark.config(
        CLOWNDUCTOR_FEATURES={
            'give_root_access': enabled,
            'give_stable_root': for_stable,
        },
    )


@pytest.mark.usefixtures('mocks_for_service_creation')
@pytest.mark.parametrize(
    'branch_name, owner_groups_count',
    [
        pytest.param('stable', 2, marks=_access_feature()),
        pytest.param('stable', 1, marks=_access_feature(for_stable=False)),
        pytest.param('unstable', 2, marks=_access_feature()),
        pytest.param('unstable', 2, marks=_access_feature(for_stable=False)),
        pytest.param('stable', 1, marks=_access_feature(enabled=False)),
        pytest.param('unstable', 1, marks=_access_feature(enabled=False)),
    ],
)
async def test_root_access_on_nanny_branch(
        add_service,
        add_nanny_branch,
        get_branch_jobs,
        get_job_variables,
        branch_name,
        owner_groups_count,
):
    service = await add_service(
        'taxi', 'some-service', direct_link='taxi_some-service',
    )
    branch_id = await add_nanny_branch(service['id'], branch_name, branch_name)

    jobs = await get_branch_jobs(branch_id)
    for job in jobs:
        variables = await get_job_variables(job['job']['id'])
        assert (
            len(json.loads(variables['variables'])['owner_groups'])
            == owner_groups_count
        )


@pytest.mark.usefixtures('mocks_for_service_creation')
@pytest.mark.parametrize(
    'use_branch_id, use_service_id, use_direct_link, use_branch_ids,'
    'expected_code, results_num',
    [
        (True, False, False, False, 200, 1),
        (False, True, False, False, 200, 3),
        (False, False, True, False, 200, 1),
        (False, False, False, False, 400, None),
        (True, True, True, False, 400, None),
        (False, True, True, False, 400, None),
        (True, False, True, False, 400, None),
        (True, True, False, False, 400, None),
        (False, False, False, True, 200, 2),
    ],
)
async def test_get_branches(
        add_service,
        add_nanny_branch,
        web_app_client,
        use_branch_id,
        use_service_id,
        use_direct_link,
        use_branch_ids,
        expected_code,
        results_num,
):
    service = await add_service(
        'taxi', 'some-service', direct_link='taxi_some-service',
    )
    branch_id1 = await add_nanny_branch(
        service['id'], 'unstable', direct_link='taxi_some-service_unstable',
    )
    branch_id2 = await add_nanny_branch(
        service['id'], 'stable', direct_link='taxi_some-service_stable',
    )

    params = {}

    if use_branch_id:
        params['branch_id'] = branch_id1
    if use_service_id:
        params['service_id'] = service['id']
    if use_direct_link:
        params['direct_link'] = 'taxi_some-service_unstable'
    if use_branch_ids:
        params['branch_ids'] = f'{branch_id1},{branch_id2}'

    response = await web_app_client.get('/v1/branches/', params=params)
    assert response.status == expected_code
    if response.status == 200:
        data = await response.json()
        assert len(data) == results_num
        for entry in data:
            assert entry['updated_at']
            if entry['id'] == branch_id1:
                assert entry['direct_link'] == 'taxi_some-service_unstable'
                assert entry['full_direct_link'] == (
                    'https://nanny.yandex-team.ru/ui/'
                    '#/services/catalog/taxi_some-service_unstable/'
                )
                break
        else:
            assert False, 'Cant find correct entry in response'


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.features_on('disk_profiles')
@pytest.mark.parametrize(
    'service_id,disk_profile,expected',
    [
        pytest.param(
            2,
            'default',
            'hdd',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_PROFILE_DEFAULT={'__default__': 'default'},
                ),
            ],
        ),
        pytest.param(
            2,
            'ssd-default',
            'ssd',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_PROFILE_DEFAULT={'__default__': 'default'},
                ),
            ],
        ),
    ],
)
async def test_create_branch_with_disk_profiles(
        login_mockserver,
        web_app_client,
        service_id,
        disk_profile,
        web_context,
        expected,
):
    login_mockserver()

    response = await web_app_client.post(
        f'/v2/create_nanny_branch/',
        params={'service_id': service_id},
        json={
            'name': 'unstable',
            'env': 'unstable',
            'disk_profile': disk_profile,
            'preset': 'x2micro',
        },
        headers={'X-Yandex-Login': 'elrusso'},
    )
    body = await response.json()
    job_id = body['branch']['job_id']

    job = await web_context.service_manager.jobs.get_by_id(job_id)
    assert job.get('variables', False)
    variables = job.get('variables')
    variables = json.loads(variables)
    storage_class = variables['branch_params']['root_storage_class']
    assert storage_class
    assert storage_class == expected


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_remove_nanny_branch(web_app_client, load_json, pgsql):
    response = await web_app_client.post(
        'v1/remove_nanny_branch/',
        json={'branch_id': 2},
        headers={'X-Yandex-Login': 'web-sheriff'},
    )
    assert response.status == 200
    data = await response.json()
    expected = {'job_ids': [2]}
    assert data == expected
    cursor = pgsql['clownductor'].cursor()
    cursor.execute(
        'select service_id, branch_id '
        'from task_manager.jobs '
        'where name=\'RemoveNannyBranch\'',
    )
    jobs_service_branch_ids = cursor.fetchall()
    assert jobs_service_branch_ids == [(1, 2)]


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'remove_nanny_branch_draft_ticket': True},
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_remove_nanny_branch_validate(web_app_client, load_json):
    response = await web_app_client.post(
        'v1/remove_nanny_branch/validate/',
        json={'branch_id': 2, 'info': 'test remove nanny branch'},
        headers={'X-Yandex-Login': 'deoevgen'},
    )
    assert response.status == 200
    data = await response.json()
    expected = load_json('expected_response_remove_nanny_branch_validate.json')
    assert data == expected


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_remove_nanny_service(web_app_client, load_json):
    response = await web_app_client.post(
        'v1/remove_nanny_service/',
        json={'service_id': 1, 'info': 'test remove nanny service'},
        headers={'X-Yandex-Login': 'antonvasyuk'},
    )
    assert response.status == 200
    data = await response.json()
    expected = {'job_ids': [2]}
    assert data == expected


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'remove_nanny_service_draft_ticket': True},
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_remove_nanny_service_validate(web_app_client, load_json):
    response = await web_app_client.post(
        'v1/remove_nanny_service/validate/',
        json={'service_id': 1, 'info': 'test remove nanny service'},
        headers={'X-Yandex-Login': 'deoevgen'},
    )
    assert response.status == 200
    data = await response.json()
    expected = load_json(
        'expected_response_remove_nanny_service_validate.json',
    )
    assert data == expected


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_get_batch(web_app_client):
    async def _do_it(cursor=None, count=1):
        _body = {'limit': count if count else 1}
        if cursor:
            _body['cursor'] = cursor
        _response = await web_app_client.post('/v2/branches/', json=_body)
        assert _response.status == 200, await _response.text()
        _data = await _response.json()
        assert len(_data['branches']) == count
        if not count:
            assert 'cursor' not in _data
        return _data

    data = await _do_it()
    data = await _do_it(data['cursor'], 4)
    await _do_it(data['cursor'], 0)


@pytest.mark.parametrize(
    'branch_id, resp',
    [
        pytest.param(4, 200, id='Correct branch'),
        pytest.param(3, 400, id='Erroneous branch'),
        pytest.param(9999, 404, id='Non-existent branch'),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'remove_nanny_branch_draft_ticket': True},
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_remove_dev_branch_validate(
        web_app_client, load_json, branch_id, resp,
):
    response = await web_app_client.post(
        'v1/remove_dev_branch/validate/',
        json={'branch_id': branch_id, 'info': 'test remove dev branch'},
        headers={'X-Yandex-Login': 'vstimchenko'},
    )
    assert response.status == resp
    if resp == 200:
        data = await response.json()
        expected = load_json(
            'expected_response_remove_dev_branch_validate.json',
        )
        assert data == expected


@pytest.mark.parametrize(
    'branch_id, resp, token',
    [
        pytest.param(4, 200, 'valid_teamcity_token', id='Correct branch'),
        pytest.param(5, 200, 'lavka_special_token', id='lavka_branch'),
        pytest.param(
            4, 403, 'lavka_special_token', id='comon_service_with_lavka_token',
        ),
        pytest.param(3, 400, 'valid_teamcity_token', id='Erroneous branch'),
        pytest.param(
            9999, 404, 'valid_teamcity_token', id='Non-existent branch',
        ),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'remove_nanny_branch_draft_ticket': True},
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_DEPLOY_TOKENS={
        '__default__': '',
        'lavka': {'__default__': 'lavka_token'},
    },
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_remove_dev_branch(
        web_app_client, load_json, branch_id, resp, token,
):
    response = await web_app_client.post(
        'v1/remove_dev_branch/',
        json={'branch_id': branch_id, 'info': 'test remove dev branch'},
        headers={'X-YaTaxi-Api-Key': token},
    )
    assert response.status == resp
    if resp == 200:
        data = await response.json()
        expected = load_json('expected_response_remove_dev_branch.json')
        assert data == expected


@pytest.mark.config(
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'projects': [{'datacenters': ['vla', 'sas'], 'name': '__default__'}],
    },
)
@pytest.mark.features_on(
    'disk_profiles',
    'allow_auto_unstable_creation',
    'nanny_branch_draft_ticket',
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_remove_uncreated_dev_branch(web_app_client, load_json):
    params = {'service_id': 1}
    request_body = {
        'allocate_request': {
            'branch_name': 'testing_branch',
            'regions': ['man', 'vla'],
        },
        'env': 'unstable',
    }
    headers = {
        'X-Yandex-Login': 'vstimchenko',
        'X-YaTaxi-Api-Key': 'valid_teamcity_token',
    }
    response = await web_app_client.post(
        CREATE_DEV_BRANCH_URL,
        json=request_body,
        params=params,
        headers=headers,
    )
    assert response.status == 200
    response = await response.json()
    assert response['branch']['job_id']

    response_deletion = await web_app_client.post(
        'v1/remove_dev_branch/',
        json={
            'branch_id': response['branch']['id'],
            'info': 'test remove dev branch',
        },
        headers={'X-YaTaxi-Api-Key': 'valid_teamcity_token'},
    )
    assert response_deletion.status == 409
    assert (await response_deletion.json()) == {
        'code': 'CONFLICT',
        'message': (
            'This branch has unfinished jobs: '
            'duplicate key value violates '
            'unique constraint "change_doc_id_key"'
        ),
    }
