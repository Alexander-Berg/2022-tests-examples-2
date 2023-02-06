async def test_ping(web_app_client):
    """Тест ручки ping"""
    response = await web_app_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


async def test_client(test_client_ping):
    """Простой тест клиента"""
    response = await test_client_ping()
    assert response.status == 200
    assert response.body is None
