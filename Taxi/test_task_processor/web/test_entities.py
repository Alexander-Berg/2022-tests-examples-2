import pytest


def get_external_entities_links(pgsql):
    cursor = pgsql['task_processor'].cursor()
    cursor.execute(f'select * from task_processor.external_entities_links;')
    return cursor.fetchall()


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_create_200(web_app_client, pgsql):
    external_entities_links = get_external_entities_links(pgsql)
    assert len(external_entities_links) == 8
    response = await web_app_client.post(
        '/v1/jobs/entity_link/create/',
        json={'entity_type': 'service', 'external_id': '142', 'job_id': 1},
    )
    assert response.status == 200
    external_entities_links = get_external_entities_links(pgsql)
    assert len(external_entities_links) == 9
    data = await response.json()
    assert data['external_entity_link'] == {
        'entity': {'entity_type': 'service', 'external_id': '142'},
        'job_id': 1,
        'id': 9,
    }


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_create_404(web_app_client, pgsql):
    external_entities_links = get_external_entities_links(pgsql)
    assert len(external_entities_links) == 8
    response = await web_app_client.post(
        '/v1/jobs/entity_link/create/',
        json={'entity_type': 'bad_service', 'external_id': '142', 'job_id': 1},
    )
    assert response.status == 404
    external_entities_links = get_external_entities_links(pgsql)
    assert len(external_entities_links) == 8


@pytest.mark.parametrize(
    'input_data, expected_data',
    [
        (
            {
                'entity_link_id': 1,
                'new_external_id': '142',
                'new_entity_type': 'branch',
            },
            {
                'entity': {'entity_type': 'branch', 'external_id': '142'},
                'id': 1,
                'job_id': 1,
            },
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_update_200(
        web_app_client, pgsql, input_data, expected_data,
):
    response = await web_app_client.post(
        '/v1/jobs/entity_link/update/', json=input_data,
    )
    assert response.status == 200
    data = await response.json()
    assert data['external_entity_link'] == expected_data


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_update_404(web_app_client, pgsql):
    response = await web_app_client.post(
        '/v1/jobs/entity_link/update/',
        json={
            'entity_link_id': 199,
            'new_external_id': '142',
            'new_entity_type': 'branch',
        },
    )
    assert response.status == 404
    data = await response.json()
    assert data == {
        'code': 'ENTITY_TYPE_NOT_FOUND',
        'message': 'entity link with id  199 was not found',
    }


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_update_400(web_app_client, pgsql):
    response = await web_app_client.post(
        '/v1/jobs/entity_link/update/',
        json={
            'entity_link_id': 1,
            'new_external_id': '142',
            'new_entity_type': 'bad_name',
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'INVALID_PARAMETERS',
        'message': (
            'cannot update parameters, new_entity_type bad_name not found in '
            'entity_types table'
        ),
    }


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_delete_200(web_app_client, pgsql):
    external_entities_links = get_external_entities_links(pgsql)
    assert len(external_entities_links) == 8
    response = await web_app_client.post(
        '/v1/jobs/entity_link/delete/', json={'entity_link_id': 1},
    )
    assert response.status == 200
    external_entities_links = get_external_entities_links(pgsql)
    assert len(external_entities_links) == 7


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_delete_404(web_app_client, pgsql):
    external_entities_links = get_external_entities_links(pgsql)
    assert len(external_entities_links) == 8
    response = await web_app_client.post(
        '/v1/jobs/entity_link/delete/', json={'entity_link_id': 56},
    )
    assert response.status == 404
    external_entities_links = get_external_entities_links(pgsql)
    assert len(external_entities_links) == 8


@pytest.mark.parametrize(
    'request_params, expected',
    [
        pytest.param(
            {'job_id': 1},
            'expected_entity_retrieve_job_id.json',
            id='retrieve_by_job_id',
        ),
        pytest.param(
            {'entity_type': 'service', 'external_id': '1'},
            'expected_entity_retrieve_entity_id_type.json',
            id='retrieve_by_entity_id_entity_type',
        ),
        pytest.param(
            {'ids': [1, 2, 3]},
            'expected_entity_list_ids.json',
            id='retrieve_by_job_id',
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_list_200(
        web_app_client, pgsql, request_params, load_json, expected,
):
    response = await web_app_client.post(
        '/v1/jobs/entity_link/list/', json=request_params,
    )
    assert response.status == 200
    assert load_json(expected) == await response.json()


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_list_404(
        web_app_client, pgsql, load_json,
):
    response = await web_app_client.post(
        '/v1/jobs/entity_link/list/', json={'job_id': 20},
    )
    assert response.status == 404


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_retrieve_200(
        web_app_client, pgsql, load_json,
):
    response = await web_app_client.get(
        '/v1/jobs/entity_link/retrieve/', params={'id': 1},
    )
    assert response.status == 200
    assert await response.json() == {
        'external_entity_link': {
            'entity': {'entity_type': 'service', 'external_id': '100'},
            'id': 1,
            'job_id': 1,
        },
    }


@pytest.mark.pgsql('task_processor', files=['test_entities.sql'])
async def test_external_entity_links_retrieve_404(
        web_app_client, pgsql, load_json,
):
    response = await web_app_client.get(
        '/v1/jobs/entity_link/retrieve/', params={'id': 20},
    )
    assert response.status == 404
