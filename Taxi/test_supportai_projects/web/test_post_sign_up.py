import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_sign_up_400(web_app_client):
    request_body = {'username': 'test_user_2', 'password': 'test_password'}
    response = await web_app_client.post(f'/v1/auth/signup', json=request_body)
    assert response.status == 400


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_sign_up_200(web_app_client):
    request_body = {'username': 'unique_name', 'password': 'test_password'}
    response = await web_app_client.post(f'/v1/auth/login', json=request_body)
    assert response.status == 404

    response = await web_app_client.post(f'/v1/auth/signup', json=request_body)
    assert response.status == 200

    response = await web_app_client.post(f'/v1/auth/login', json=request_body)
    assert response.status == 200
