import pytest


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'sample_results.sql'],
)
async def test_get_validation_results(web_app_client):
    response = await web_app_client.get(
        '/v1/validation/results?user_id=34&project_id=1&task_id=1',
    )

    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['results']) == 2
