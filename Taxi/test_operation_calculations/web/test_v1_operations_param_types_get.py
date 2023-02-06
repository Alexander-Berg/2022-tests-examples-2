async def test_v1_operations_operation_param_types_get(web_app_client):
    response = await web_app_client.get('/v1/operations/param_types/')
    assert response.status == 200, await response.json()
    assert await response.json() == {
        'items': [
            'nmfg-subventions',
            'brand-nmfg-subventions',
            'nobrand-nmfg-subventions',
        ],
    }
