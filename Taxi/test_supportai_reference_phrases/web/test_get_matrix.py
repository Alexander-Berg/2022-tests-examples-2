import pytest


@pytest.mark.pgsql('supportai_reference_phrases', files=['matrix.sql'])
async def test_get_matrix(web_app_client):
    response = await web_app_client.get(
        '/v1/matrix?project_slug=project_1&version=release',
    )

    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['matrix']) == 4

    response = await web_app_client.get(
        '/v1/matrix?project_slug=project_1&version=draft',
    )

    assert response.status == 200
    response_json = await response.json()
    assert not response_json['matrix']

    response = await web_app_client.get('/v1/matrix?&version=draft')

    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 5

    response = await web_app_client.get(
        '/v1/matrix?project_slug=project_1&version=release&topic_slug=topic1',
    )

    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['matrix']) == 3
