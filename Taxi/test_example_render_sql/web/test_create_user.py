async def test_revision_on_creation(web_app_client):
    data = {'login': 'dmkurilov', 'name': 'Dmitry Kurilov'}
    response = await web_app_client.post('/v1/user', json=data)
    assert response.status == 200
    response_body = await response.json()
    assert response_body['revision'] == '1'


async def test_idempotency(create_user):
    login = 'dmkurilov'
    name = 'Dmitry Kurilov'
    first_revision = await create_user(login, name)
    second_revision = await create_user(login, name)
    assert first_revision == second_revision == '1'


async def test_conflict(web_app_client, create_user):
    await create_user('dmkurilov', 'Dmitry')
    data = {'login': 'dmkurilov', 'name': 'Kurilov'}
    response = await web_app_client.post('/v1/user', json=data)
    assert response.status == 409
