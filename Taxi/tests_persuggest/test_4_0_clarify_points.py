# pylint: disable=C0302
import copy

import pytest

URL = '/4.0/persuggest/v1/clarify-points'

DEFAULT_APPLICATION = 'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=1'

AUTHORIZED_HEADERS = {
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


def _convert_umlaas_geo_state_to_persuggest(umlaas_geo_state):
    persuggest_state = copy.deepcopy(umlaas_geo_state)
    for field in persuggest_state['fields']:
        field['log'] = field.pop('uri')
    return persuggest_state


UMLAAS_GEO_STATE = {
    'accuracy': 20,
    'bbox': [30.1, 50.1, 40.1, 60.1],
    'fields': [
        {
            'type': 'b',
            'position': [13.37, 3.22],
            'uri': 'ymapsbm1://org?oid=126805074611',
            'metrica_action': 'foobar_action',
            'metrica_method': 'foobar_method',
            'finalsuggest_method': 'fs_foobar',
        },
    ],
    'location': [37.51, 55.72],
    'coord_providers': [
        {'type': 'gps', 'position': [14.1234, 15.1234], 'accuracy': 10.3},
        {'type': 'platform_lbs', 'position': [16.1, 17.1], 'accuracy': 4.0},
    ],
    'country': 'ru',
}

BASE_REQUEST = {
    'state': {
        **_convert_umlaas_geo_state_to_persuggest(UMLAAS_GEO_STATE),
        'wifi_networks': [{'bssid': 'a:b:c:d:e:f'}],
        'app_metrica': {'device_id': 'DeviceId'},
    },
    'summary_state': {'offer_id': '...', 'has_alternatives': True},
}

CLIENT_MESSAGES = {
    'clarify_points.point_a_text': {
        'ru': 'Астрологи объявили неделю уточнения точки A',
    },
    'clarify_points.point_a_subtitle_text': {
        'ru': 'Так как Юпитер находится в пятом доме',
    },
    'clarify_points.point_b_text': {
        'ru': 'Астрологи объявили неделю уточнения точки B',
    },
}


@pytest.mark.experiments3(
    filename='exp3_clarify_points_settings_with_stub.json',
)
@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
async def test_4_0_clarify_points_stub(taxi_persuggest):
    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'clarify_points': [
            {
                'completion_timeout_ms': 1000,
                'text': 'Астрологи объявили неделю уточнения точки A',
                'type': 'a',
            },
            {
                'text': 'Астрологи объявили неделю уточнения точки B',
                'type': 'b',
            },
        ],
    }


@pytest.mark.experiments3(filename='exp3_clarify_points_settings_no_stub.json')
@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
async def test_4_0_clarify_points_simple(taxi_persuggest, mockserver):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/clarify-points')
    async def mock_umlaas_geo(request):
        # pa_auth_context
        assert (
            request.headers['X-Yandex-UID']
            == AUTHORIZED_HEADERS['X-Yandex-UID']
        )
        # appmetrica headers
        assert (
            request.headers['X-AppMetrica-UUID']
            == AUTHORIZED_HEADERS['X-AppMetrica-UUID']
        )
        assert 'X-AppMetrica-DeviceId' not in request.headers
        # body
        assert request.json == {
            'state': UMLAAS_GEO_STATE,
            'summary_state': {'offer_id': '...', 'has_alternatives': True},
        }
        return {
            'clarify_points': [
                {
                    'settings': {
                        'title_key': 'clarify_points.point_a_text',
                        'subtitle_key': 'clarify_points.point_a_subtitle_text',
                    },
                    'type': 'a',
                },
                {
                    'completion_timeout_ms': 1337,
                    'settings': {'title_key': 'clarify_points.point_b_text'},
                    'type': 'b',
                },
            ],
        }

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert mock_umlaas_geo.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'clarify_points': [
            {
                'text': 'Астрологи объявили неделю уточнения точки A',
                'subtitle_text': 'Так как Юпитер находится в пятом доме',
                'type': 'a',
            },
            {
                'completion_timeout_ms': 1337,
                'text': 'Астрологи объявили неделю уточнения точки B',
                'type': 'b',
            },
        ],
    }
