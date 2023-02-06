import pytest


@pytest.mark.pgsql('supportai_reference_phrases', files=['release_draft.sql'])
async def test_release_draft_version(web_app_client, web_context):

    response = await web_app_client.get('/v1/matrix?project_slug=test_project')

    assert response.status == 200
    draft_response_json = await response.json()

    assert len(draft_response_json['matrix']) == 5

    response = await web_app_client.post(
        '/supportai-reference-phrases/v1/apply-new-version?project_id=test_project',  # noqa pylint: disable=line-too-long
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/matrix?project_slug=test_project&version=release',
    )

    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['matrix']) == 5
    assert {phrase['text'] for phrase in response_json['matrix']} == {
        phrase['text'] for phrase in draft_response_json['matrix']
    }


@pytest.mark.pgsql('supportai_reference_phrases', files=['delete_release.sql'])
async def test_delete_release_version(web_app_client, web_context):

    response = await web_app_client.get(
        '/v1/matrix?project_slug=test_project&version=release',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['matrix']) == 9

    response = await web_app_client.post(
        '/supportai-reference-phrases/v1/delete-version?project_id=test_project',  # noqa pylint: disable=line-too-long
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/matrix?project_slug=test_project&version=release',
    )
    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['matrix']) == 3
