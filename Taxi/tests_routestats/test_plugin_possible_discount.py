import json

import pytest

PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
    'X-AppMetrica-DeviceId': 'DeviceId',
}


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:brandings',
        'top_level:brandings:possible_discount_branding',
    ],
)
async def test_ok(taxi_routestats, mockserver, load_json):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_request = json.loads(request.get_data())
        protocol_supported = protocol_request.get('supported', [])
        service_supported = service_request.get('supported', [])
        assert len(protocol_supported) == len(service_supported)
        for i, service_supported in enumerate(service_supported):
            assert protocol_supported[i]['type'] == service_supported['type']

        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    @mockserver.json_handler(
        '/ride-discounts/v1/match-discounts/available-by-zone',
    )
    def _ride_discounts(request):
        return {'tariffs_availability': ['econom']}

    service_request = load_json('request.json')
    response = await taxi_routestats.post(
        'v1/routestats', service_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    service_levels = response.json()['service_levels']
    econom = [x for x in service_levels if x['class'] == 'econom'][0]

    assert econom['brandings'] == [{'type': 'has_possible_discount'}]
    for tariff_class in [x for x in service_levels if x['class'] != 'econom']:
        assert 'brandings' not in tariff_class
