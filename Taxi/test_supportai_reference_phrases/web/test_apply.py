import pytest


@pytest.mark.pgsql('supportai_reference_phrases', files=['apply_matrix.sql'])
async def test_apply_of_draft(web_app_client, web_context):
    response = await web_app_client.get('/v1/matrix?version=draft')

    assert response.status == 200
    draft_response_json = await response.json()

    assert len(draft_response_json['matrix']) == 5

    response = await web_app_client.post(
        '/supportai-reference-phrases/v1/apply-new-version?project_id=',
    )

    assert response.status == 200

    response = await web_app_client.get('/v1/matrix?version=release')

    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['matrix']) == 5
    assert len(response_json['matrix']) == len(draft_response_json['matrix'])
