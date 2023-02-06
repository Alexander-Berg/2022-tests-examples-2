import copy
import typing

import pytest

LOAD_CREATE_AND_START_VALIDATE_URL = '/v1/load/create_and_start/validate/'
LOAD_CREATE_AND_START_URL = '/v1/load/create_and_start/'
LOAD_START_URL = '/v1/load/start/'

LOAD_DATA: typing.Dict[str, object] = {
    'service_name': 'test_service',
    'target_address': 'https://abc.yandex.net',
    'load_info': {
        'ammo_file': 'fake',
        'schedule': 'line(1,2,3)',
        'st_task': 'TAXICOMMON-2022',
    },
}

CREATE_AND_LOAD_DATA: typing.Dict[str, object] = {
    **LOAD_DATA,
    'create_branch_params': {
        'cpu': 1000,
        'ram': 1024,
        'regions': ['sas', 'vla'],
        'tank_branch_name': 'new_tank_branch',
        'copy_branch_name': 'testing_branch',
    },
}


@pytest.mark.pgsql('clownductor', ['init_services.sql'])
async def test_default_scenario(web_app_client, task_processor):
    response = await web_app_client.post(
        LOAD_START_URL,
        headers={'X-Yandex-Login': 'dyusudakov'},
        json=LOAD_DATA,
    )
    assert response.status == 200
    result = await response.json()
    assert result['job_id'] == 1


@pytest.mark.pgsql('clownductor', ['init_services.sql'])
async def test_create_and_load(web_app_client, task_processor):
    response = await web_app_client.post(
        LOAD_CREATE_AND_START_URL,
        headers={'X-Yandex-Login': 'dyusudakov'},
        json=CREATE_AND_LOAD_DATA,
    )
    assert response.status == 200
    result = await response.json()
    assert result['job_id'] == 1


@pytest.mark.pgsql('clownductor', ['init_services.sql'])
async def test_create_and_load_tank_branch_exists(
        web_app_client, task_processor,
):
    data = copy.deepcopy(CREATE_AND_LOAD_DATA)
    data['create_branch_params']['tank_branch_name'] = 'tank_branch'

    response = await web_app_client.post(
        LOAD_CREATE_AND_START_VALIDATE_URL,
        headers={'X-Yandex-Login': 'dyusudakov'},
        json=data,
    )
    assert response.status == 409
    result = await response.json()
    assert result['message'] == 'Tank branch tank_branch already exists'


@pytest.mark.pgsql('clownductor', ['init_services.sql'])
async def test_create_and_load_copy_branch_not_exists(
        web_app_client, task_processor,
):
    data = copy.deepcopy(CREATE_AND_LOAD_DATA)
    data['create_branch_params']['copy_branch_name'] = 'testing-branch'

    response = await web_app_client.post(
        LOAD_CREATE_AND_START_VALIDATE_URL,
        headers={'X-Yandex-Login': 'dyusudakov'},
        json=data,
    )
    assert response.status == 400
    result = await response.json()
    assert result['message'] == 'Copy branch testing-branch does not exists'


@pytest.mark.pgsql('clownductor', ['init_services.sql'])
async def test_service_not_found(web_app_client, task_processor):
    data = copy.deepcopy(LOAD_DATA)
    data['service_name'] = 'unknown_service'

    response = await web_app_client.post(
        LOAD_START_URL, headers={'X-Yandex-Login': 'dyusudakov'}, json=data,
    )
    assert response.status == 400
    result = await response.json()
    assert (
        result['message'] == 'Can not find service with name unknown_service'
    )


@pytest.mark.pgsql('clownductor', ['init_services.sql'])
async def test_validate_success(web_app_client, task_processor, load_json):
    data = copy.deepcopy(CREATE_AND_LOAD_DATA)
    response = await web_app_client.post(
        LOAD_CREATE_AND_START_VALIDATE_URL,
        headers={'X-Yandex-Login': 'dyusudakov'},
        json=data,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == load_json(
        'expected_response_create_and_start_validate.json',
    )


@pytest.mark.pgsql(
    'clownductor', ['init_services.sql', 'init_extra_services.sql'],
)
async def test_service_name_collision(web_app_client, task_processor):
    data = copy.deepcopy(LOAD_DATA)
    data['service_name'] = 'test_service'

    response = await web_app_client.post(
        LOAD_START_URL, headers={'X-Yandex-Login': 'dyusudakov'}, json=data,
    )
    assert response.status == 400
    result = await response.json()
    assert (
        result['message'] == 'There are more than one service with '
        'name test_service, add project name to request'
    )

    data['project_name'] = 'taxi'
    response = await web_app_client.post(
        LOAD_START_URL, headers={'X-Yandex-Login': 'dyusudakov'}, json=data,
    )
    assert response.status == 200
    result = await response.json()
    assert result['job_id'] is not None


@pytest.mark.pgsql('clownductor', ['init_services.sql'])
async def test_validate_apply(web_app_client, task_processor):
    data = copy.deepcopy(CREATE_AND_LOAD_DATA)
    response = await web_app_client.post(
        LOAD_CREATE_AND_START_VALIDATE_URL,
        headers={'X-Yandex-Login': 'dyusudakov'},
        json=data,
    )
    assert response.status == 200, await response.text()
    validate_result = await response.json()

    response = await web_app_client.post(
        LOAD_CREATE_AND_START_URL,
        headers={'X-Yandex-Login': 'dyusudakov'},
        json=validate_result['data'],
    )
    assert response.status == 200, await response.text()
