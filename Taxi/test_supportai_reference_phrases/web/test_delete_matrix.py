import pytest


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_matrix.sql'])
async def test_delete_matrix(web_app_client):

    response = await web_app_client.post(
        '/supportai-reference-phrases/v1/delete-version?project_id=project_1',
    )
    assert response.status == 200
    response = await web_app_client.get(
        '/v1/matrix?project_slug=project_1&version=release',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 5

    response = await web_app_client.post(
        '/supportai-reference-phrases/v1/delete-version?project_id=project_1',
    )
    assert response.status == 200
    response = await web_app_client.get(
        '/v1/matrix?project_slug=project_1&version=release',
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['matrix']
