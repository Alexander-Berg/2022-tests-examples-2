async def test_get_warning(web_app_client):
    response = await web_app_client.get('/api/warning')
    assert response.status == 200

    content = await response.json()

    assert content[0] == {
        '_id': '5a1d2a7f395cbe40f245eefd',
        'created': 1511863200,
        'text': 'testing warning',
        'valid': 21600,
    }
