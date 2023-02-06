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
    names=['top_level:brandings', 'top_level:brandings:long_search_v2'],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='long_search_v2',
    consumers=['uservices/routestats/long_search_v2'],
    default_value={
        'tanker_keys': [
            {
                'key': 'popup_title',
                'tanker': {
                    'key': 'long_search_v2_popup_title',
                    'keyset': 'client_messages',
                },
                'default': 'Как мы ищем машину (заголовок, default)',
            },
            {
                'key': 'pin_hint_radius_change',
                'tanker': {
                    'key': 'long_search_v2_pin_hint_radius_change',
                    'keyset': 'client_messages',
                },
                'default': 'Изменяем радиус поиска (default)',
            },
            {
                'key': 'pin_hint_start_search',
                'tanker': {
                    'key': 'long_search_v2_pin_hint_start_search',
                    'keyset': 'client_messages',
                },
                'default': 'Начинаем поиск машины (default)',
            },
            {
                'key': 'popup_description',
                'tanker': {
                    'key': 'long_search_v2_popup_description',
                    'keyset': 'client_messages',
                },
                'default': 'Ищем машину дольше (default)',
            },
            {
                'key': 'popup_button_title',
                'tanker': {
                    'key': 'long_search_v2_popup_button_title',
                    'keyset': 'client_messages',
                },
                'default': 'Понятно (default)',
            },
            {
                'key': 'search_card_title',
                'tanker': {
                    'key': 'long_search_v2_search_card_title',
                    'keyset': 'client_messages',
                },
                'default': 'Как мы ищем машину (default)',
            },
            {
                'key': 'search_card_subtitle',
                'tanker': {
                    'key': 'long_search_v2_search_card_subtitle',
                    'keyset': 'client_messages',
                },
                'default': 'И почему цена низкая (default)',
            },
        ],
        'popup': {
            'title_key': 'popup_title',
            'description_key': 'popup_description',
            'button_title_key': 'popup_button_title',
            'search_card_title_key': 'search_card_title',
            'search_card_subtitle_key': 'search_card_subtitle',
        },
        'enabled': True,
        'pin_hint_start_search': 'pin_hint_start_search',
        'pin_hint_radius_change': 'pin_hint_radius_change',
        'polling_interval_millis': 2000,
        'collapse_search_card_timeout_millis': 5000,
    },
)
@pytest.mark.translations(
    client_messages={
        'long_search_v2_popup_title': {
            'ru': 'Как мы ищем машину (заголовок из экспа)',
        },
        'long_search_v2_pin_hint_radius_change': {
            'ru': 'Изменяем радиус поиска (из экспа)',
        },
        'long_search_v2_pin_hint_start_search': {
            'ru': 'Начинаем поиск машины (из экспа)',
        },
        'long_search_v2_popup_description': {
            'ru': 'Ищем машину дольше (из экспа)',
        },
        'long_search_v2_popup_button_title': {'ru': 'Понятно (из экспа)'},
    },
)
async def test_long_search_v2(taxi_routestats, mockserver, load_json):
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

    service_levels = response.json()['service_levels']
    for service_level in service_levels:
        assert service_level['brandings'] == [
            {
                'type': 'long_search_v2',
                'long_search_v2': {
                    'pin_hint_radius_change': (
                        'Изменяем радиус поиска (из экспа)'
                    ),
                    'pin_hint_start_search': (
                        'Начинаем поиск машины (из экспа)'
                    ),
                    'polling_interval_millis': 2000,
                    'collapse_search_card_timeout_millis': 5000,
                    'popup': {
                        'title': 'Как мы ищем машину (заголовок из экспа)',
                        'description': 'Ищем машину дольше (из экспа)',
                        'button_title': 'Понятно (из экспа)',
                        'search_card_title': 'Как мы ищем машину (default)',
                        'search_card_subtitle': (
                            'И почему цена низкая (default)'
                        ),
                    },
                },
            },
        ]
