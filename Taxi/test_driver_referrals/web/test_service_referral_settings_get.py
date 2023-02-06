async def test_service_referral_settings_get(web_app_client):
    response = await web_app_client.get('/service/referral-settings')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'cities': ['Москва', 'Тверь', 'Санкт-Петербург', 'Рига'],
    }
