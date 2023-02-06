import json

import pytest

# pylint: disable=import-only-modules
from tests_persuggest.persuggest_common import jsonify

URL = '/3.0/suggest'

USER_ID = '12345678901234567890123456789012'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
    'X-Request-Application': 'app_name=yango_android',
    'X-Request-Language': 'ru',
    'X-Ya-User-Ticket': 'user_ticket',
}

PP_USER_IDENTITY = {
    'bound_yandex_uids': ['834149473', '834149474'],
    'flags': {'has_ya_plus': False, 'is_phonish': False, 'is_portal': True},
    'phone_id': '123456789012345678901234',
    'user_id': '12345678901234567890123456789012',
    'yandex_uid': '400000000',
}


@pytest.mark.experiments3(filename='exp3_typed_experiments.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_3_0_suggest_finalsuggest(
        taxi_persuggest, load_json, mockserver, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response.json')

    yamaps.add_fmt_geo_object(
        {
            'geocoder': {
                'address': {
                    'formatted_address': 'Россия, Москва, Садовническая улица',
                    'country': 'Россия',
                    'locality': 'Москва',
                    'street': 'Садовническая улица',
                },
                'id': '8063585',
            },
            'uri': 'ymapsbm1://geo?exit1',
            'name': 'Садовническая улица, 82с2',
            'description': 'Москва, Россия',
            'geometry': [37.615928, 55.757333],
        },
    )

    request = {
        'action': 'pin_drop',
        'id': '12345678901234567890123456789012',
        'position': [37.5, 55.71],
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [
                {'type': 'a', 'position': [10.1234, 11.1234], 'log': '{}'},
                {'type': 'b', 'position': [12.1234, 13.1234], 'log': '{}'},
            ],
            'location': [37.1, 55.1],
        },
        'supported': ['alerts'],
        'sticky': True,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    actual = jsonify(response.json())
    expect = load_json('expected_response_finalsuggest.json')
    actual['typed_experiments']['items'].sort(key=lambda o: o['name'])
    expect['typed_experiments']['items'].sort(key=lambda o: o['name'])
    assert actual == expect


async def test_3_0_suggest_zerosuggest(
        taxi_persuggest, mockserver, yamaps, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in AUTHORIZED_HEADERS.items():
            if header.startswith('X'):
                assert request.headers[header] == value
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('uml_zerosuggest_response.json')

    request = {
        'id': USER_ID,
        'action': 'zero_suggest',
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [
                {'type': 'a', 'position': [10.1234, 11.1234], 'log': '{}'},
                {'type': 'b', 'position': [12.1234, 13.1234], 'log': '{}'},
            ],
            'location': [37.1, 55.1],
            'coord_providers': [
                {'type': 'gps', 'position': [14.12, 15.12], 'accuracy': 10.3},
            ],
        },
        'position': [37, 55],
        'type': 'b',
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response_zerosuggest.json')


async def test_3_0_suggest_zerosuggest_with_no_user_id_in_body(
        taxi_persuggest, mockserver, yamaps, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in AUTHORIZED_HEADERS.items():
            if header.startswith('X'):
                assert request.headers[header] == value
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('uml_zerosuggest_response.json')

    request = {
        'action': 'zero_suggest',
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [
                {'type': 'a', 'position': [10.1234, 11.1234], 'log': '{}'},
                {'type': 'b', 'position': [12.1234, 13.1234], 'log': '{}'},
            ],
            'location': [37.1, 55.1],
            'coord_providers': [
                {'type': 'gps', 'position': [14.12, 15.12], 'accuracy': 10.3},
            ],
        },
        'position': [37, 55],
        'type': 'b',
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_zerosuggest.json')


async def test_3_0_suggest_suggest(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request.json')
        return load_json('suggest_response.json')

    yamaps.add_fmt_geo_object(
        load_json('yamaps_geo_objects.json')['geo_objects'][0],
    )

    request = {
        'id': USER_ID,
        'action': 'user_input',
        'part': 'presn',
        'type': 'a',
        'state': {
            'accuracy': 20.2,
            'bbox': [30.3, 50.5, 40.4, 60.6],
            'fields': [
                {
                    'type': 'b',
                    'log': '{\"type\":\"coords\",\"pos\":[37.5368,55.7495]}',
                    'position': [37.5368, 55.7495],
                    'entrance': 'entr_b',
                },
            ],
            'location': [37.1, 55.1],
        },
        'suggest_serpid': '123456',
        'event_number': 3,
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_suggest.json')
    assert jsonify(response.json()) == expected


async def test_3_0_suggest_confirm(taxi_persuggest, mockserver):
    @mockserver.json_handler('/yamaps-suggest-personal/suggest-personal-add')
    def _mock_suggest_personal_add(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == {
            'client': 'taxi',
            'timestamp': '1501599600',
            'action': 'route',
            'drive': '1',
            'pointa': '{\"a\": 1}',
            'pointb': '{\"b\": 2}',
            'pointmid9': 'mid_e',
            'entrancemid9': 'mid_e',
        }
        return {}

    request = {
        'id': USER_ID,
        'action': 'confirm',
        'state': {
            'accuracy': 20,
            'bbox': [30.3, 50.5, 40.4, 60.6],
            'fields': [
                {'type': 'a', 'position': [10.12, 11.12], 'log': '{\"a\": 1}'},
                {'type': 'b', 'position': [12.12, 13.12], 'log': '{\"b\": 2}'},
                {
                    'type': 'mid9',
                    'position': [13.12, 14.12],
                    'log': '{\"mid9\": 3}',
                    'entrance': 'mid_e',
                },
            ],
            'location': [37.1, 55.1],
        },
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}
