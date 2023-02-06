async def test_get_tariff_zones(web_app_client):
    response = await web_app_client.get('/api/v1/tariff_zones')
    assert response.status == 200

    content = sorted((await response.json())['tariff_zones'])
    assert content == ['ekb', 'kazan', 'moscow', 'ufa', 'vladivostok']
