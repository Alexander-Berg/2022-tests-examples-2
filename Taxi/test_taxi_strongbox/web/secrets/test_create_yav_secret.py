async def test_creating_yav_secret(taxi_strongbox_web, vault_mockserver):
    vault_session = vault_mockserver()
    response = await taxi_strongbox_web.post(
        '/v1/secretes/yav/',
        json={
            'env': 'production',
            'type': 'tvm',
            'data': {
                'project': 'market',
                'provider_name': 'some-market-service',
                'tvm_id': '123456',
                'secret': 'SECRET',
            },
        },
    )
    assert response.status == 200, await response.text()
    data = await response.json()
    assert data == {
        'yav_secret_uuid': 'secret_uuid_1',
        'yav_version_uuid': 'version_uuid_1',
    }
    assert vault_session.versions == {
        'version_uuid_1': {
            'value': [
                {'key': 'project', 'value': 'market'},
                {'key': 'provider_name', 'value': 'some-market-service'},
                {'key': 'secret', 'value': 'SECRET'},
                {'key': 'tvm_id', 'value': '123456'},
            ],
        },
    }
