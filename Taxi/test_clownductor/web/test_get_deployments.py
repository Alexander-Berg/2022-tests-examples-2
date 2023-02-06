import pytest


FIRST_DEPLOYMENT = {
    'branch_id': 1,
    'deployment_id': 1,
    'image': 'image_name',
    'service_id': 1,
    'status': 'canceled',
    'branch_name': 'unstable_branch',
    'env': 'unstable',
    'created_at': 1,
}

SECOND_DEPLOYMENT = {
    'branch_id': 2,
    'deployment_id': 2,
    'image': 'image_name',
    'service_id': 1,
    'status': 'success',
    'branch_name': 'testing_branch',
    'env': 'testing',
    'created_at': 1631618831,
}

THIRD_DEPLOYMENT = {
    'branch_id': 3,
    'deployment_id': 3,
    'image': 'image_name',
    'service_id': 1,
    'status': 'canceled',
    'taxirel_ticket': 'release_ticket_st',
    'branch_name': 'stable_branch',
    'env': 'stable',
    'created_at': 2,
}

ALL_DEPLOYMENTS = [THIRD_DEPLOYMENT, SECOND_DEPLOYMENT, FIRST_DEPLOYMENT]
MAIN_SERVICE_ID = 1
DEPENDENT_SERVICE_ID = 2


async def _get_deployments(web_app_client, query: dict):
    response = await web_app_client.get(
        f'/v1/service/deployments/',
        params=query,
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert response.status == 200
    result = await response.json()
    return result['deployments']


@pytest.mark.parametrize('service_id', [MAIN_SERVICE_ID, DEPENDENT_SERVICE_ID])
@pytest.mark.pgsql(
    'clownductor', files=['add_test_data.sql', 'add_wait_deploy_jobs.sql'],
)
async def test_get_deployments_all(web_app_client, patch, service_id):
    query = {'service_id': service_id}
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == ALL_DEPLOYMENTS


@pytest.mark.parametrize('service_id', [MAIN_SERVICE_ID, DEPENDENT_SERVICE_ID])
@pytest.mark.pgsql(
    'clownductor', files=['add_test_data.sql', 'add_wait_deploy_jobs.sql'],
)
async def test_get_deployments_filter_id(web_app_client, patch, service_id):
    query = {'service_id': service_id, 'deployment_id': 1}
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == [FIRST_DEPLOYMENT]


@pytest.mark.parametrize('service_id', [MAIN_SERVICE_ID, DEPENDENT_SERVICE_ID])
@pytest.mark.pgsql(
    'clownductor', files=['add_test_data.sql', 'add_wait_deploy_jobs.sql'],
)
async def test_get_deployments_filter_branch(
        web_app_client, patch, service_id,
):
    query = {'service_id': service_id, 'branch_id': 3}
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == [THIRD_DEPLOYMENT]


@pytest.mark.pgsql('clownductor', files=['add_test_data_alias.sql'])
@pytest.mark.parametrize(
    'service_id,branch_id,expected',
    [
        (
            1,
            1,
            [
                {
                    'deployment_id': 1,
                    'service_id': 1,
                    'branch_id': 1,
                    'status': 'success',
                    'taxirel_ticket': 'release_ticket_st',
                    'image': 'image_name',
                    'branch_name': 'stable_main',
                    'env': 'stable',
                    'created_at': 3,
                },
            ],
        ),
        (
            2,
            2,
            [
                {
                    'deployment_id': 1,
                    'service_id': 1,
                    'branch_id': 1,
                    'status': 'success',
                    'taxirel_ticket': 'release_ticket_st',
                    'image': 'image_name',
                    'branch_name': 'stable_main',
                    'env': 'stable',
                    'created_at': 3,
                },
            ],
        ),
    ],
)
async def test_get_deployments_filter(
        web_app_client, service_id, branch_id, expected,
):
    query = {'service_id': service_id, 'branch_id': branch_id}
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == expected


@pytest.mark.parametrize('service_id', [MAIN_SERVICE_ID, DEPENDENT_SERVICE_ID])
@pytest.mark.pgsql(
    'clownductor', files=['add_test_data.sql', 'add_wait_deploy_jobs.sql'],
)
async def test_get_deployments_filter_status(
        web_app_client, patch, service_id,
):
    query = {'service_id': service_id, 'status': 'canceled'}
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == [THIRD_DEPLOYMENT, FIRST_DEPLOYMENT]


@pytest.mark.parametrize('service_id', [MAIN_SERVICE_ID, DEPENDENT_SERVICE_ID])
@pytest.mark.pgsql(
    'clownductor', files=['add_test_data.sql', 'add_wait_deploy_jobs.sql'],
)
async def test_get_deployments_filter_ticket(
        web_app_client, patch, service_id,
):
    query = {'service_id': service_id, 'taxirel_ticket': 'release_ticket_st'}
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == [THIRD_DEPLOYMENT]


@pytest.mark.parametrize('service_id', [MAIN_SERVICE_ID, DEPENDENT_SERVICE_ID])
@pytest.mark.pgsql(
    'clownductor', files=['add_test_data.sql', 'add_wait_deploy_jobs.sql'],
)
async def test_get_deployments_pagination_limit(
        web_app_client, patch, service_id,
):
    query = {'service_id': service_id, 'limit': 1}
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == [THIRD_DEPLOYMENT]


@pytest.mark.parametrize('service_id', [MAIN_SERVICE_ID, DEPENDENT_SERVICE_ID])
@pytest.mark.pgsql(
    'clownductor', files=['add_test_data.sql', 'add_wait_deploy_jobs.sql'],
)
async def test_get_deployments_pagination_limit_page_2(
        web_app_client, patch, service_id,
):
    query = {
        'service_id': service_id,
        'limit': 1,
        'deployment_id_less_than': 3,
    }
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == [SECOND_DEPLOYMENT]


@pytest.mark.parametrize(
    'start_date,end_date,expected',
    [
        pytest.param(
            '2021-09-14T14:27:00+0300',
            '2021-09-14T14:28:00+0300',
            [SECOND_DEPLOYMENT],
            id='filter range has deployment',
        ),
        pytest.param(
            '2021-09-14T17:27:00+0300',
            '2021-09-14T17:28:00+0300',
            [],
            id='filter range has no deployments',
        ),
    ],
)
@pytest.mark.pgsql(
    'clownductor', files=['add_test_data.sql', 'add_wait_deploy_jobs.sql'],
)
async def test_get_deployments_filter_time(
        web_app_client, patch, start_date, end_date, expected,
):
    query = {'service_id': 1, 'start_date': start_date, 'end_date': end_date}
    deployments = await _get_deployments(web_app_client, query)
    assert deployments == expected
