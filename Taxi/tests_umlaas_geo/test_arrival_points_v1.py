import pytest
URL = 'umlaas-geo/v1/arrival-points'
USER_ID = 'user_id'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_brand=yango,app_name=yango_android',
}


@pytest.mark.experiments3(filename='exp_params.json')
async def test_ok(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')


@pytest.mark.experiments3(filename='fake_exp.json')
async def test_fake_exp_ok(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == {'arrival_points': []}


@pytest.mark.experiments3(filename='excluded_app_exp.json')
async def test_excluded_app_ok(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == {'arrival_points': []}


@pytest.mark.experiments3(filename='exp_params_popular_point.json')
async def test_ok_popular_point(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_popular_point.json')


@pytest.mark.experiments3(filename='exp_params_closest_point.json')
async def test_ok_closest_point(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_closest_point.json')


@pytest.mark.experiments3(filename='exp_params_not_suitable_method.json')
async def test_ok_not_suitable_method(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_empty_candidates.json',
    )


@pytest.mark.experiments3(filename='exp_params_empty_candidates.json')
async def test_ok_empty_candidates(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_empty_candidates.json',
    )
