def test_service_info(api):
    api.set_host('http://grocery-api.lavka.yandex.net')

    response = api.service_info(37.371618, 55.840757)
    assert response.status_code == 200
