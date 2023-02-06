import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_capabilities(web_app_client):
    repeated_capability = {'slug': 'admin_capability'}
    new_capability = {'slug': 'test_capability_6'}

    response = await web_app_client.post(
        f'/v1/capabilities', json=repeated_capability,
    )
    assert response.status == 400

    response = await web_app_client.post(
        f'/v1/capabilities', json=new_capability,
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body == new_capability

    response = await web_app_client.get('/v1/capabilities')
    response_json = await response.json()
    assert new_capability in response_json['capabilities']
