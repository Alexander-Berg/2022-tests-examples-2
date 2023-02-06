import pytest


URL = '/v1/screen/shuttle'

DEFAULT_APPLICATION = 'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=1'

HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
    'X-AppMetrica-UUID': 'UUID',
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'User-Agent': 'user-agent',
    'X-Remote-IP': '10.10.10.10',
}

REQUEST = {
    'state': {'bbox': [37.59, 55.69, 37.61, 55.71]},
    'shortcuts': {
        'supported_actions': [
            {'type': 'zoom_layers_feature', 'modes': ['all_object_types']},
        ],
    },
}


@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'offer_2_title': {'ru': 'Где Шаттлы?'},
        'offer_2_overlay_text': {'ru': 'Поищем'},
        'offer_2_attr_subtitle': {'ru': 'показать на карте'},
        'offer_title': {'ru': 'Шаттл'},
        'offer_attr_subtitle': {'ru': 'Что это такое?'},
        'offer_overlay_text': {'ru': 'Го'},
        'button_attr_title': {'ru': 'Как ездить?!'},
        'button_overlay_attr_text': {'ru': 'Как?!'},
        'section_1_header_lead_title': {'ru': 'Шаттлы'},
        'section_1_header_trail_subtitle': {'ru': 'катают'},
        'section_2_typed_header_lead_title': {'ru': 'Подробнее'},
        'section_2_header_trail_subtitle': {'ru': 'узнать про Шаттлы'},
    },
)
@pytest.mark.experiments3(filename='exp3_products_screen_shuttle.json')
async def test_simple(taxi_shortcuts, load_json):
    response = await taxi_shortcuts.post(URL, headers=HEADERS, json=REQUEST)

    assert response.status_code == 200
    assert response.json() == load_json('screen_shuttle_simple_response.json')
