import pytest


@pytest.mark.parametrize('specify_login', [(True,), (False,)])
async def test_find(specify_login, web_app_client, create_user):
    login = 'dmkurilov'
    name = 'Dmitry Kurilov'
    await create_user(login, name)

    data = {'login': login} if specify_login else {'name': name}
    response = await web_app_client.post('/v1/find-user', json=data)
    assert response.status == 200
    response_body = await response.json()

    assert response_body['login'] == login
    assert response_body['name'] == name
    assert response_body['revision'] == '1'


async def test_search_object_required(web_app_client, create_user):
    response = await web_app_client.post('/v1/find-user', json={})
    assert response.status == 400
    response_body = await response.json()
    assert response_body['code'] == 'LOGIN_OR_NAME_REQUIRED'


async def test_not_found(web_app_client, create_user):
    await create_user('dmkurilov', 'Dmitry Kurilov')
    data = {'name': 'Dmitry'}
    response = await web_app_client.post('/v1/find-user', json=data)
    assert response.status == 404
    response_body = await response.json()
    assert response_body['code'] == 'USER_NOT_FOUND'
