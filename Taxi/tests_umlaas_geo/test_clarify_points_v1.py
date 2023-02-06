import pytest

URL = 'umlaas-geo/v1/clarify-points'
USER_ID = 'user_id'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_brand=yandex,app_name=iphone',
}

PA_HEADERS_NO_AUTH = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
}


ROUTEHISTORY_SETTINGS_ENABLED = {
    '/umlaas-geo/v1/clarify-points': {
        'enabled': True,
        'max_size': 80,
        'protobuf': True,
    },
    '__default__': {'enabled': True, 'max_size': 80, 'protobuf': True},
}

ROUTEHISTORY_SETTINGS_DISABLED = {
    '/umlaas-geo/v1/clarify-points': {
        'enabled': False,
        'max_size': 80,
        'protobuf': True,
    },
    '__default__': {'enabled': True, 'max_size': 80, 'protobuf': True},
}


def _mock_routehistory(mockserver, load_json):
    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock(request):
        for header, value in PA_HEADERS.items():
            if header == 'X-Request-Application':
                # Compare ignoring key-value pair order
                assert set(request.headers[header].split(',')) == set(
                    value.split(','),
                )
            elif header != 'X-Ya-User-Ticket':
                assert request.headers[header] == value
        return load_json('routehistory_get_response.json')


@pytest.mark.experiments3(filename='exp_metrica.json')
async def test_metrica_rules(taxi_umlaas_geo, load_json, _mock_routehistory):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('a_response.json')


@pytest.mark.experiments3(filename='exp_geo.json')
async def test_location_rule(taxi_umlaas_geo, load_json, _mock_routehistory):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('a_response.json')


@pytest.mark.config(
    UMLAAS_GEO_ROUTEHISTORY_SETTINGS=ROUTEHISTORY_SETTINGS_DISABLED,
)
@pytest.mark.experiments3(filename='exp_model.json')
async def test_model_rule(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('a_response.json')


@pytest.mark.config(
    UMLAAS_GEO_ROUTEHISTORY_SETTINGS=ROUTEHISTORY_SETTINGS_DISABLED,
)
@pytest.mark.experiments3(filename='exp_new_model.json')
async def test_new_model_rule(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('a_response.json')


@pytest.mark.config(
    UMLAAS_GEO_ROUTEHISTORY_SETTINGS=ROUTEHISTORY_SETTINGS_ENABLED,
)
@pytest.mark.experiments3(filename='exp_exploration_mode.json')
async def test_exploration(taxi_umlaas_geo, load_json, _mock_routehistory):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('a_response.json')
