import copy
import json

import pytest

URL = '4.0/persuggest/v1/widgets'

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
    'X-AppMetrica-DeviceId': 'DeviceId',
}

BASIC_REQUEST = {
    'state': {
        'accuracy': 20,
        'selected_class': 'econom',
        'location': [34.85, 32.11],
    },
}

YAMAPS_ADDRESS = [
    {
        'business': {
            'address': {
                'formatted_address': 'Russia, Moscow',
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'name': 'One-door community',
            'closed': 'UNKNOWN',
            'class': 'restaurant',
            'id': '1088700971',
        },
        'uri': 'ymapsbm1://URI_0_0',
        'name': 'One-door community',
        'description': 'Moscow, Russia',
        'geometry': [37.0, 55.0],
    },
    {
        'business': {
            'address': {
                'formatted_address': 'Russia, Moscow',
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'name': 'Murakame',
            'closed': 'TEMPORARY',
            'id': '1088700971',
            'class': 'restaurant',
        },
        'uri': 'ymapsbm1://URI_1_1',
        'name': 'Murakame',
        'description': 'Moscow, Russia',
        'geometry': [37.01, 55.01],
    },
    {
        'll': '37.300000,55.300000',
        'geocoder': {
            'address': {
                'formatted_address': (
                    'Russia, Moscow, 2nd Krasnogvardeysky Drive, 10'
                ),
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'id': '1',
        },
        'uri': 'ymapsbm1://URI_3_3',
        'name': '2nd Krasnogvardeysky Drive, 10',
        'description': 'Russia, Moscow',
        'geometry': [37.3, 55.3],
    },
    {
        'll': '37.700000,55.700000',
        'geometry': [37.7, 55.7],
        'description': 'Russia, Moscow',
        'uri': 'ymapsbm1://URI_7_7',
        'name': 'Tverskaya Zastava Square, 7',
        'geocoder': {
            'address': {
                'formatted_address': (
                    'Russia, Moscow, Tverskaya Zastava Square, 7'
                ),
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'id': '1',
        },
    },
]


@pytest.fixture(autouse=True)
def yamaps_wrapper(yamaps):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        for addr in YAMAPS_ADDRESS:
            if 'uri' in request.args and addr['uri'] == request.args['uri']:
                return [addr]
        return []


def _remove_fields(obj: dict, *args):
    for arg in args:
        assert arg in obj, f'{arg} exists check failed'
        obj.pop(arg)


def validate_response(response, expected):
    for widget in response['widgets']:
        _remove_fields(widget, 'id')
    assert response == expected


@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'restaurant_type': {'shortcut': 'shortcuts_restaurant_tag'},
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
        'default_type': {'shortcut': 'shortcuts_default_tag'},
    },
    ORG_RUBRIC_TO_IMAGE_TYPE={'restaurant': 'restaurant_type'},
)
@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
        'widget_subtitle_key': {'ru': 'subtitle'},
    },
)
@pytest.mark.experiments3(filename='exp3_filter_closed_orgs.json')
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
@pytest.mark.experiments3(filename='exp3_widget_settings.json')
@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.tariff_settings(filename='tariff_settings_telaviv.json')
@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.tariffs(filename='tariffs_tel_aviv.json')
async def test_4_0_widgets_ml_zerosuggest(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    headers = copy.deepcopy(PA_HEADERS)

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in headers.items():
            assert request.headers[header] == value
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('uml_zerosuggest_response.json')

    response = await taxi_persuggest.post(URL, BASIC_REQUEST, headers=headers)
    assert response.status_code == 200
    validate_response(
        response.json(),
        {
            'widgets': [
                {
                    'action': {
                        'deeplink': (
                            'yandextaxi://'
                            'route?end-lat=55.4321&end-lon=37.1234'
                        ),
                        'type': 'deeplink',
                    },
                    'background': {'color': '#000000'},
                    'overlays': [
                        {
                            'background': {'color': '#000001'},
                            'image_tag': 'shortcuts_default_tag',
                            'shape': 'poi',
                        },
                        {'image_tag': 'widget_econom_car', 'shape': 'car'},
                    ],
                    'subtitle': 'subtitle',
                    'title': '2nd Krasnogvardeysky Drive, 10',
                },
            ],
            'internal': {
                'pricing_data_preparer_request': {
                    'categories': ['econom'],
                    'classes_requirements': {},
                    'modifications_scope': 'taxi',
                    'waypoints': [[34.85, 32.11], [37.1234, 55.4321]],
                    'zone': 'tel_aviv',
                    'tolls': 'DENY',
                    'user_info': {
                        'user_id': USER_ID,
                        'application': {
                            'name': 'yango_android',
                            'version': '0.0.0',
                            'platform_version': '0.0.0',
                        },
                    },
                },
            },
        },
    )
