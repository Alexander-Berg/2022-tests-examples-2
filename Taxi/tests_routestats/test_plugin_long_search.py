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
    names=['top_level:brandings', 'top_level:brandings:long_search_branding'],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='routestats_long_search_branding',
    consumers=['uservices/routestats'],
    default_value={
        'enabled': True,
        'class_map_branding_settings': {
            'econom': {
                'popup': {
                    'title': 'popup.title',
                    'text': 'popup.text',
                    'button_title': 'popup.button_title',
                },
                'search_screen': {
                    'title': 'ss.title',
                    'subtitle': 'ss.subtitle',
                },
                'title': 'title_key',
            },
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'title_key': {'ru': 'test_title'},
        'ss.title': {'ru': 'test_ss_title'},
        'ss.subtitle': {'ru': 'test_ss_subtitle'},
        'popup.title': {'ru': 'test_popup_title'},
        'popup.text': {'ru': 'test_popup_text'},
        'popup.button_title': {'ru': 'test_popup_button_title'},
    },
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

    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _plus_wallet(request):
        return {
            'balances': {
                'balance': '4771.0000',
                'currency': 'RUB',
                'wallet_id': 'wallet_id',
            },
        }

    service_request = load_json('request.json')
    response = await taxi_routestats.post(
        'v1/routestats', service_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    service_levels = response.json()['service_levels']
    econom = [x for x in service_levels if x['class'] == 'econom'][0]
    assert econom['search_screen'] == {
        'title': 'test_ss_title',
        'subtitle': 'test_ss_subtitle',
    }
    assert econom['brandings'] == [
        {
            'type': 'long_search',
            'title': 'test_title',
            'popup': {
                'title': 'test_popup_title',
                'text': 'test_popup_text',
                'button_title': 'test_popup_button_title',
            },
        },
    ]

    for tariff_class in [x for x in service_levels if x['class'] != 'econom']:
        assert 'brandings' not in tariff_class
