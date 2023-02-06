import pytest

URL = 'umlaas-geo/v1/scenario-prediction'
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

PA_HEADERS_NO_AUTH = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
}


@pytest.mark.experiments3(filename='exp_heuristics_params.json')
async def test_response(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_eats_ordershistory,
):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert _mock_eats_ordershistory.has_calls
    assert len(response.json()['results']) == 7
    for item in response.json()['results']:
        assert item in load_json('expected_response.json')['results']
    for item in load_json('expected_response.json')['results']:
        assert item in response.json()['results']


async def test_unauthorized(taxi_umlaas_geo, mockserver, load_json):
    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return {'places': []}

    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock_routehistory(request):
        return {'results': []}

    @mockserver.json_handler('/routehistory/routehistory/search-get')
    def _mock_searchhistory(request):
        return {'results': []}

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eats_ordershistory(request):
        return {'orders': []}

    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(
        URL, request, headers=PA_HEADERS_NO_AUTH,
    )
    assert response.status_code == 200
    assert not _mock_userplaces.has_calls
    assert not _mock_routehistory.has_calls
    assert not _mock_searchhistory.has_calls
    assert not _mock_eats_ordershistory.has_calls
