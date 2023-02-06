async def test_tst(taxi_authproxy_manager):
    response = await taxi_authproxy_manager.post(
        '/v1/hints/url',
        json={'url': 'http://authproxy-manager.taxi.tst.yandex.net/'},
        headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    assert response.json() == {
        'url-adjusted': 'http://authproxy-manager.taxi.yandex.net/',
    }
