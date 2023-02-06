async def test_get_classes(web_app_client):
    response = await web_app_client.get('/api/classes')
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['en'])
    assert len(content) == 3

    assert content[0] == {'en': 'business', 'ru': 'Комфорт'}
