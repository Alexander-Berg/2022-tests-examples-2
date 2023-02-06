import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_api_working_with_auth_disabled(web_app_client):
    response = await web_app_client.get('/v1/projects?user_id=34')
    assert response.status == 200
    assert len((await response.json())['projects']) == 3
