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
        'top_level:brandings:brandings_intercity_tariff_tooltip',
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='intercity',
    consumers=['uservices/routestats'],
    default_value={
        'enabled': True,
        'tariff_tooltip': {
            'title': 'routestats.brandings.intercity.tariff_tooltip.title',
            'enabled': True,
            'tariffs_to_show': ['econom'],
            'search_time_delta_sec': 60,
            'min_eta_sec_to_show': 60,
        },
        'min_ride_m_distance': 6000,
        'allowed_zones_for_point_b': ['moscow'],
    },
)
@pytest.mark.translations(
    client_messages={
        'routestats.brandings.intercity.tariff_tooltip.title': {
            'ru': 'Поиск и подача %(eta_min)s мин',
        },
    },
)
async def test_branding_intercity_tariff_tooltip(
        taxi_routestats, mockserver, load_json,
):
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

    service_request = load_json('request.json')
    response = await taxi_routestats.post(
        'v1/routestats', service_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    #
    service_levels = response.json()['service_levels']
    for service_level in service_levels:
        if service_level['class'] != 'econom':
            continue
        assert service_level['brandings'] == [
            {'title': 'Поиск и подача 4 мин', 'type': 'tariff_tooltip'},
        ]
