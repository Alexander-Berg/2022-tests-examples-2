import copy
import json

import pytest

from tests_persuggest import persuggest_common
# pylint: disable=import-only-modules
from tests_persuggest.persuggest_common import jsonify

URL = '/4.0/persuggest/v1/finalsuggest'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Request-Application': 'app_name=iphone',
    'X-Request-Language': 'ru',
    'X-AppMetrica-UUID': 'UUID',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-Remote-IP': '10.10.10.10',
}

FIX_ENTRANCES_EXP = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'fix_entrances',
    'consumers': ['persuggest/finalsuggest'],
    'clauses': [
        {
            'title': 'always',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
    'default_value': True,
}

POINT_EXTRA = {
    'comment_courier': 'knock twice',
    'doorphone_number': 'admin',
    'entrance': 'wide',
    'floor_number': 'even',
    'quarters_number': 'one',
    'person_name': 'Vasya',
    'person_phone_id': '+7000',
}


@pytest.mark.parametrize('with_geo_address', [True, False])
@pytest.mark.parametrize('with_point_extra_details', [True, False])
async def test_finalize_uri(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        with_point_extra_details,
        with_geo_address,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    geo_org_search_response = [load_json('orggeosearch.json')]

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'uri' in request.args:
            return geo_org_search_response
        return []

    request = {
        'action': 'finalize',
        'position': [34.7, 32.1],
        'prev_log': 'ymapsbm1://userplace_uri',
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'type': 'b',
    }
    if with_geo_address:
        expected_ans = load_json('uri_expected_ans.json')
    else:
        geo_org_search_response = []
        expected_ans = load_json('uri_not_found_expected_ans.json')
    if with_point_extra_details:
        persuggest_common.add_data_to_log(
            request, {'point_extra_details': POINT_EXTRA},
        )
        if with_geo_address:
            expected_ans['results'][0].update(POINT_EXTRA)
            expected_ans['results'][0].pop('person_name')
            expected_ans['results'][0].pop('person_phone_id')
            persuggest_common.add_data_to_log(
                expected_ans['results'][0],
                {'point_extra_details': POINT_EXTRA},
            )
            expected_ans['results'][0]['contact'] = {
                'name': 'Vasya',
                'phone_number': '+7000',
            }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(expected_ans)


@pytest.mark.parametrize('with_uri', [True, False])
async def test_finalize_org(
        taxi_persuggest, mockserver, load_json, yamaps, with_uri,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    ull = '55.749923,37.534253'
    orggeosearch_response = load_json('orggeosearch.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        assert 'biz' in request.args.get('type')
        assert request.args.get('ull') == ull
        result = orggeosearch_response
        if not with_uri:
            result.pop('uri')
        return [result]

    org_prev_log = {
        'type': 'org1',
        'user_params': {'ll': '37.6425841, 55.734939', 'ull': ull},
        'what': {'id': '1'},
    }

    request = {
        'action': 'finalize',
        'prev_log': json.dumps(org_prev_log),
        'position': [37.6425841, 55.734939],
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': tuple(map(float, ull.split(','))),
        },
        'type': 'b',
    }
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    response = await taxi_persuggest.post(URL, request, headers=headers)
    expected_ans = load_json('org_expected_ans.json')
    expected_log = expected_ans['results'][0]['log']
    expected_log['user_params']['ull'] = ull
    expected_ans['results'][0]['log'] = expected_log
    response_json = response.json()
    if not with_uri:
        response_log = response_json['results'][0]['log']
        assert json.loads(response_log)['type'] == 'org1'
        expected_ans['results'][0].pop('uri')
        expected_ans['results'][0]['log'] = response_log
    expected_ans['results'][0]['subtitle']['text'] = orggeosearch_response[
        'description'
    ]
    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(expected_ans)


@pytest.mark.parametrize('with_uri', [True, False])
async def test_finalize_toponym(
        taxi_persuggest, mockserver, load_json, yamaps, with_uri,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    geo_object = load_json('yamaps_simple_geo_object.json')
    if not with_uri:
        geo_object.pop('uri')

    yamaps.add_fmt_geo_object(geo_object)

    toponym_prev_log = {
        'type': 'toponym',
        'user_params': {'ll': '37.6425841, 55.734939'},
        'where': {
            'entrance': '42',
            'name': 'Россия, Москва, Садовническая улица',
        },
    }

    request = {
        'action': 'finalize',
        'position': [34.7, 32.1],
        'prev_log': json.dumps(toponym_prev_log),
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = load_json('toponym_expected_ans.json')
    response_json = response.json()
    if not with_uri:
        response_log = response_json['results'][0]['log']
        assert json.loads(response_log)['type'] == 'toponym'
        expected_ans['results'][0].pop('uri')
        expected_ans['results'][0]['log'] = response_log
    assert response.status_code == 200
    assert jsonify(response_json) == jsonify(expected_ans)


@pytest.mark.parametrize(
    'position, output_method',
    [
        ([37.615928, 55.757333], 'fs_finalize_toponym'),
        ([37.615928, 55.757030], 'np_entrances'),
    ],
)
async def test_finalize_toponym_entrance(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        position,
        output_method,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    geo_object = load_json('entrance_geosearch.json')
    geo_object['geometry'] = position
    yamaps.add_fmt_geo_object(geo_object)

    toponym_prev_log = {
        'type': 'toponym',
        'user_params': {'ll': '37.6425841, 55.734939'},
        'where': {'name': 'Россия, Москва, Садовническая улица'},
    }

    request = {
        'action': 'finalize',
        'position': position,
        'prev_log': json.dumps(toponym_prev_log),
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = load_json('entrance_expected_ans.json')
    expected_ans['results'][0]['method'] = output_method
    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(expected_ans)


@pytest.mark.parametrize(
    'userplace_entrance, expected_entrance',
    [
        pytest.param('2', '2', id='dont_fix_entrance'),
        pytest.param(
            '1',
            '1',
            id='good_entrance',
            marks=[pytest.mark.experiments3(**FIX_ENTRANCES_EXP)],
        ),
        pytest.param(
            '2',
            None,
            id='bad_entrance',
            marks=[pytest.mark.experiments3(**FIX_ENTRANCES_EXP)],
        ),
        pytest.param(
            '3',
            '3',
            id='custom_entrance',
            marks=[pytest.mark.experiments3(**FIX_ENTRANCES_EXP)],
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_finalize_userplace(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        userplace_entrance,
        expected_entrance,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    @yamaps.set_fmt_geo_objects_callback
    def _mock_yamaps(request):
        return [load_json('yamaps_userplace.json')]

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        assert json.loads(request.get_data()) == load_json(
            'userplaces_request.json',
        )
        result = load_json('userplaces_response.json')
        if userplace_entrance:
            result['porchnumber'] = userplace_entrance
        return result

    request = {
        'action': 'finalize',
        'position': [37.1, 55.1],
        'prev_log': (
            '{"type":"userplace","userplace_id":'
            '"00000004-AAAA-AAAA-AAAA-000000000001"}'
        ),
        'state': {
            'accuracy': 40,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = load_json('userplace_expected_ans.json')
    ans = expected_ans['results'][0]
    if expected_entrance:
        ans['entrance'] = expected_entrance
    if userplace_entrance != expected_entrance:
        ans['subtitle']['text'] = 'Садовническая улица, 82с2'
        ans['text'] = 'Россия, Москва, Садовническая улица, 82с2'
    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(expected_ans)


@pytest.mark.parametrize(
    'name, short_text, expected_title, expected_subtitle',
    [
        pytest.param(
            'Serebryanaya Highway, 13',
            'Serebryanaya Highway, 13',
            'Serebryanaya 13',
            'Садовническая улица, 82с2, подъезд 1',
        ),
        pytest.param(
            '',
            'Serebryanaya Highway, 13',
            'Садовническая 82с2, подъезд 1',
            'Москва, Россия',
        ),
        pytest.param(
            'My Highway, 13',
            'Serebryanaya Highway, 13',
            'My Highway, 13',
            'Садовническая улица, 82с2, подъезд 1',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_short_text_formatting.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_finalize_userplace_short_formatting(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        name,
        short_text,
        expected_title,
        expected_subtitle,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    @yamaps.set_fmt_geo_objects_callback
    def _mock_yamaps(request):
        return [load_json('yamaps_userplace.json')]

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        assert json.loads(request.get_data()) == load_json(
            'userplaces_request.json',
        )
        result = load_json('userplaces_response.json')
        result['name'] = name
        result['short_text'] = short_text
        return result

    request = {
        'action': 'finalize',
        'position': [37.1, 55.1],
        'prev_log': (
            '{"type":"userplace","userplace_id":'
            '"00000004-AAAA-AAAA-AAAA-000000000001"}'
        ),
        'state': {
            'accuracy': 40,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = load_json('userplace_expected_ans.json')
    ans = expected_ans['results'][0]
    ans['subtitle']['text'] = expected_subtitle
    ans['title']['text'] = expected_title

    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(expected_ans)


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_check_userplaces.json')
@pytest.mark.translations(client_messages={'work': {'ru': 'Работа'}})
async def test_finalize_userplace_by_uri(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return load_json('userplaces_list_response.json')

    request = {
        'action': 'finalize',
        'position': [37.1, 55.1],
        'prev_log': 'ymapsbm1://geo?exit1',
        'state': {
            'accuracy': 40,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = load_json('userplace_by_uri_expected_ans.json')
    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(expected_ans)


@pytest.mark.experiments3(filename='exp3_geo_magnet_finalized_entrance.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_finalize_entrance_localized(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if request.args['ll'] == '37.615928,55.757333':
            return [load_json('entrance_geosearch_for_geomagnet.json')]
        json_response = load_json('entrance_geosearch.json')
        json_response['geometry'] = [37.615928, 55.756330]
        return [json_response]

    toponym_prev_log = {
        'type': 'toponym',
        'user_params': {'ll': '37.6425841, 55.734939'},
        'where': {'name': 'Россия, Москва, Садовническая улица'},
    }

    request = {
        'action': 'finalize',
        'position': [37.615928, 55.756330],
        'prev_log': json.dumps(toponym_prev_log),
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = load_json('entrance_expected_ans_with_geomagnet.json')
    expected_ans['results'][0]['method'] = 'np_entrances'
    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(expected_ans)


@pytest.mark.experiments3(filename='exp3_arrival_points_simple.json')
async def test_finalize_arrival_points_simple(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'uri' in request.args:
            return [load_json('orggeosearch.json')]
        return []

    request = {
        'action': 'finalize',
        'position': [34.7, 32.1],
        'prev_log': 'ymapsbm1://userplace_uri',
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [
                {
                    'entrance': '',
                    'log': (
                        'ymapsbm1://geo?ll=37.793%2C55.789&'
                        'spn=0.001%2C0.001&'
                        'text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%'
                        'D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%98%'
                        'D0%B7%D0%BC%D0%B0%D0%B9%D0%BB%D0%BE%D0%B2%D1%81%'
                        'D0%BA%D0%B8%D0%B9%20%D0%BF%D1%80%D0%BE%D1%81%D0%'
                        'BF%D0%B5%D0%BA%D1%82%2C%2073%D0%90'
                    ),
                    'position': [37.792569118131546, 55.78931411727519],
                    'type': 'a',
                },
            ],
            'location': [0, 0],
        },
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = load_json('uri_expected_ans.json')
    expected_ans['results'][0]['position'] = [35.5, 55.5]
    expected_ans['results'][0]['method'] = 'fs_finalize_arrival_points'
    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(expected_ans)


@pytest.mark.experiments3(filename='exp3_arrival_points_umlaas.json')
async def test_finalize_arrival_points_umlaas(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/arrival-points')
    def _mock_umlaas_geo_ap(request):
        for header, value in AUTHORIZED_HEADERS.items():
            if header == 'X-Ya-User-Ticket':
                continue
            assert request.headers[header] == value

        assert (
            json.loads(request.get_data())['uri']
            == 'ymapsbm1://org?oid=126805074611'
        )
        assert 'method' in json.loads(request.get_data())
        return {
            'arrival_points': [
                {'position': [35, 55]},
                {'position': [35.5, 55.5]},
            ],
        }

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'uri' in request.args:
            return [load_json('orggeosearch.json')]
        return []

    request = {
        'action': 'finalize',
        'position': [34.7, 32.1],
        'prev_log': (
            '{"uri":"ymapsbm1://userplace_uri",'
            '"method":"suggest.geosuggest"}'
        ),
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [
                {
                    'entrance': '',
                    'log': (
                        'ymapsbm1://geo?ll=37.793%2C55.789&'
                        'spn=0.001%2C0.001&'
                        'text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%'
                        'D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%98%'
                        'D0%B7%D0%BC%D0%B0%D0%B9%D0%BB%D0%BE%D0%B2%D1%81%'
                        'D0%BA%D0%B8%D0%B9%20%D0%BF%D1%80%D0%BE%D1%81%D0%'
                        'BF%D0%B5%D0%BA%D1%82%2C%2073%D0%90'
                    ),
                    'position': [37.792569118131546, 55.78931411727519],
                    'type': 'a',
                },
            ],
            'location': [0, 0],
        },
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = jsonify(load_json('uri_expected_ans.json'))
    expected_ans['results'][0]['position'] = [35.5, 55.5]
    expected_ans['results'][0]['method'] = 'fs_finalize_arrival_points'
    expected_ans['results'][0]['log']['method'] = 'suggest.geosuggest'
    assert _mock_umlaas_geo_ap.has_calls
    assert response.status_code == 200
    assert jsonify(response.json()) == expected_ans


@pytest.mark.config(MAX_ENTRANCE_STICK_DISTANCE=10)
async def test_finalize_entrance_too_far_to_stick_to(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    # geo_object = load_json('yamaps_simple_geo_object.json')
    geo_object = load_json('entrance_geosearch.json')
    geo_object['geometry'] = [37.615928, 55.757030]
    yamaps.add_fmt_geo_object(geo_object)

    toponym_prev_log = {
        'type': 'toponym',
        'user_params': {'ll': '37.6425841, 55.734939'},
        'where': {'name': 'Россия, Москва, Садовническая улица'},
    }

    request = {
        'action': 'finalize',
        'position': geo_object['geometry'],
        'prev_log': json.dumps(toponym_prev_log),
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'type': 'b',
    }

    # geo_object = load_json('yamaps_simple_geo_object.json')
    geo_object = load_json('entrance_geosearch.json')
    geo_object['geometry'] = request['position']
    yamaps.add_fmt_geo_object(geo_object)

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = load_json('toponym_no_entrance_expected_ans.json')
    response_json = response.json()
    assert response.status_code == 200
    assert jsonify(response_json) == jsonify(expected_ans)
