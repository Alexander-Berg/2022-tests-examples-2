import pytest

from client_supportai_models import constants


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_phrase(web_app_client, client_supportai_models_mock):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    remove_id = 3
    response = await web_app_client.delete(
        f'/v1/matrix/{remove_id}?project_slug=test_project',
    )
    assert response.status == 200

    response = await web_app_client.get('/v1/matrix?project_slug=test_project')
    response_json = await response.json()
    assert len(response_json['matrix']) == 4
    assert remove_id not in {
        int(phrase['id']) for phrase in response_json['matrix']
    }


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_phrase_common_project(
        web_app_client, client_supportai_models_mock,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    remove_id = 7
    response = await web_app_client.delete(f'/v1/matrix/{remove_id}')
    assert response.status == 200

    response = await web_app_client.get('/v1/matrix')
    response_json = await response.json()
    assert len(response_json['matrix']) == 3
    assert remove_id not in {
        int(phrase['id']) for phrase in response_json['matrix']
    }


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_unexisting_phrase(
        web_app_client, client_supportai_models_mock,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    remove_id = 399
    response = await web_app_client.delete(
        f'/v1/matrix/{remove_id}?project_slug=test_project',
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()
    assert len(response_json['matrix']) == 5
    assert remove_id not in {
        int(phrase['id']) for phrase in response_json['matrix']
    }


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_phrase_no_project(
        web_app_client, client_supportai_models_mock,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    remove_id = 399
    project_id = 'unexisting_project'
    response = await web_app_client.delete(
        f'/v1/matrix/{remove_id}?project_slug={project_id}',
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'/v1/matrix?project_slug={project_id}',
    )
    response_json = await response.json()
    assert not response_json['matrix']


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_phrase_empty_project(
        web_app_client, client_supportai_models_mock,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    remove_id = 124
    project_id = 'empty_project'
    response = await web_app_client.delete(
        f'/v1/matrix/{remove_id}?project_slug={project_id}',
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'/v1/matrix?project_slug={project_id}',
    )
    response_json = await response.json()
    assert not response_json['matrix']


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_phrases_bulk(
        web_app_client, client_supportai_models_mock,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    ids2delete = [1, 3, 5]
    response = await web_app_client.delete(
        '/v1/matrix/bulk?project_slug=test_project',
        json={'ids': [str(id_) for id_ in ids2delete]},
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()
    assert len(response_json['matrix']) == 2
    for remove_id in ids2delete:
        assert remove_id not in {
            int(phrase['id']) for phrase in response_json['matrix']
        }


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_phrases_bulk_doubling(
        web_app_client, client_supportai_models_mock,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    ids2delete = [1, 3, 3]
    response = await web_app_client.delete(
        '/v1/matrix/bulk?project_slug=test_project',
        json={'ids': [str(id_) for id_ in ids2delete]},
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()
    assert len(response_json['matrix']) == 3
    for remove_id in ids2delete:
        assert remove_id not in {
            int(phrase['id']) for phrase in response_json['matrix']
        }


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_phrases_bulk_extra(
        web_app_client, client_supportai_models_mock,
):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    ids2delete = [1, 3, 123, 124]
    response = await web_app_client.delete(
        '/v1/matrix/bulk?project_slug=test_project',
        json={'ids': [str(id_) for id_ in ids2delete]},
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()
    assert len(response_json['matrix']) == 3
    for remove_id in ids2delete:
        assert remove_id not in {
            int(phrase['id']) for phrase in response_json['matrix']
        }


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_no_phrases(web_app_client, client_supportai_models_mock):
    client_supportai_models_mock(
        constants.TEXT_EMBEDDING,
        {'embedding': {'embedding': [0.1, 0.1, 0.1, 0.1]}},
    )
    ids2delete = []
    response = await web_app_client.delete(
        '/v1/matrix/bulk?project_slug=test_project',
        json={'ids': [str(id_) for id_ in ids2delete]},
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()
    assert len(response_json['matrix']) == 5


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_topic(web_app_client, client_supportai_models_mock):
    response = await web_app_client.delete(
        '/v1/matrix/topic/test_topic2?project_slug=test_project',
    )
    assert response.status == 200
    response = await web_app_client.post(
        '/v1/matrix/topic/test_topic2/confirm?project_slug=test_project',
    )
    assert response.status == 200
    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()
    assert len(response_json['matrix']) == 3


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_empty_topic(
        web_app_client, client_supportai_models_mock,
):
    response = await web_app_client.delete(
        '/v1/matrix/topic/test_topic10?project_slug=test_project',
    )
    assert response.status == 204

    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()
    assert len(response_json['matrix']) == 5


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_phrases.sql'])
async def test_delete_restore_topic(
        web_app_client, client_supportai_models_mock,
):

    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()

    response = await web_app_client.delete(
        '/v1/matrix/topic/test_topic2?project_slug=test_project',
    )
    assert response.status == 200
    response = await web_app_client.post(
        '/v1/matrix/topic/test_topic2/confirm?project_slug=test_project&restore=true',  # noqa E501
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'/v1/matrix?project_slug=test_project',
    )
    response_json = await response.json()
    assert len(response_json['matrix']) == 5
