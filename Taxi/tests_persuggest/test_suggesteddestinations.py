import copy

import pytest

URL = '3.0/suggesteddestinations'

PA_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
}

PA_HEADERS_NO_AUTH = {
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
}

BASIC_REQUEST = {
    'id': 'b300bda7d41b4bae8d58dfa93221ef16',
    'll': [37, 55],
    'results': 30,
    'with_userplaces': True,
}


@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_suggesteddestinations_unauthorized(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in PA_HEADERS_NO_AUTH.items():
            assert request.headers[header] == value
        return {'results': []}

    response = await taxi_persuggest.post(
        URL, BASIC_REQUEST, headers=PA_HEADERS_NO_AUTH,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response_unauthorized.json')


@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_suggesteddestinations_basic(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in PA_HEADERS.items():
            assert request.headers[header] == value
        return load_json('ml_zerosuggest_response.json')

    response = await taxi_persuggest.post(
        URL, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response.json')


@pytest.mark.config(
    MODES=[
        {
            'mode': 'sdc',
            'experiment': 'enable_sdc_2',
            'zone_activation': {'zone_type': 'sdc', 'point_title': ''},
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_enable_sdc_2.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_suggesteddestinations_sdc(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['current_mode'] = 'sdc'
    request['ll'] = [37.400000, 55.400000]
    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response_sdc.json')
