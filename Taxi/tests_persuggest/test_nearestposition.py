import copy

import pytest

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-YaTaxi-Bound-Uids': '400000000,834149473,834149474',
}
BASE_REQUEST = {
    'id': '12345678901234567890123456789012',
    'll': [37.1, 55.1],
    'dx': 140.1,
    'type': 'a',
    'supported': ['alerts'],
}


@pytest.mark.experiments3(filename='exp3_simple.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize('point_type', ['a', 'b'])
async def test_nearestposition_simple(
        taxi_persuggest, load_json, yamaps, mockserver, point_type,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('choices_for_test.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return load_json('bzf_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    request = copy.deepcopy(BASE_REQUEST)
    request['type'] = point_type
    response = await taxi_persuggest.post(
        '/3.0/nearestposition', request, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    actual = response.json()
    expect = load_json(f'expected_response_simple_{point_type}.json')
    actual['typed_experiments']['items'].sort(key=lambda o: o['name'])
    expect['typed_experiments']['items'].sort(key=lambda o: o['name'])
    assert actual == expect
