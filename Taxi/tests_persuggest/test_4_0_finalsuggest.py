# pylint: disable=C0302

import copy
import hashlib
import json

from google.protobuf import json_format
import pytest
# pylint: disable=import-error
from yabs.proto import user_profile_pb2  # noqa: F401

# pylint: disable=import-only-modules
# from tests_persuggest.persuggest_common import jsonify, compare_responses
from tests_persuggest import persuggest_common

URL = '/4.0/persuggest/v1/finalsuggest'

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

BASE_REQUEST = {
    'action': 'pin_drop',
    'position': [37.5, 55.71],
    'state': {
        'accuracy': 20,
        'bbox': [30.1, 50.1, 40.1, 60.1],
        'fields': [],
        'location': [37.51, 55.72],
        'location_available': True,
        'coord_providers': [
            {'type': 'gps', 'position': [14.1234, 15.1234], 'accuracy': 10.3},
            {
                'type': 'platform_lbs',
                'position': [16.1, 17.1],
                'accuracy': 4.0,
                'altitude': 123.4,
                'altitude_accuracy': 1.2,
                'location_update_time': '2018-01-28T12:08:48.372+03:00',
            },
        ],
        'wifi_networks': [{'bssid': 'a:b:c:d:e:f'}],
        'app_metrica': {'device_id': 'DeviceId'},
    },
    'sticky': True,
    'type': 'a',
}


@pytest.mark.parametrize('geocoder', ['google', 'yamaps_over_osm', None])
@pytest.mark.experiments3(filename='exp3_typed_experiments.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_simple(
        taxi_persuggest, load_json, yamaps, mockserver, geocoder, experiments3,
):
    if geocoder is not None:
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='choose_geocoder',
            consumers=['persuggest/finalsuggest'],
            clauses=[
                {
                    'title': 'always',
                    'value': {'geocoder_type': geocoder},
                    'predicate': {'type': 'true'},
                },
            ],
            default_value=True,
        )

    @mockserver.json_handler('/gg/google/maps/api/geocode/json')
    def _mock_gg(request):
        return load_json('gg_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))
    if geocoder == 'yamaps_over_osm':
        yamaps.set_checks({'use_osm': '1'})

    @mockserver.json_handler('/v1/consumers/kwargs/')
    def _mock_consumers_kwargs(request):
        consumer = request.json['consumer']
        kwargs = request.json['kwargs']
        if consumer == 'persuggest/finalsuggest':
            assert {'name': 'point_eda_region_id', 'type': 'int'} in kwargs
            assert {'name': 'point_services', 'type': 'set_string'} in kwargs
            assert {'name': 'point_type', 'type': 'string'} in kwargs

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )

    if geocoder == 'google':
        assert _mock_gg.times_called > 0
    elif geocoder == 'yamaps_over_osm':
        assert yamaps.times_called() > 0

    assert response.status_code == 200
    actual = persuggest_common.jsonify(response.json())
    expect = persuggest_common.jsonify(
        load_json('expected_response_simple.json'),
    )
    actual['typed_experiments']['items'].sort(key=lambda o: o['name'])
    expect['typed_experiments']['items'].sort(key=lambda o: o['name'])
    assert actual == expect


@pytest.mark.experiments3(filename='exp3_typed_experiments.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_condition_actions.json')
@pytest.mark.experiments3(
    filename='exp3_finalsuggest_zones_tariff_points.json',
)
@pytest.mark.translations(
    client_messages={
        'city_ultima_title': {'ru': 'Крутите новый барабан!'},
        'city_ultima_subtitle': {'ru': 'Because this is ULTIMA!'},
    },
)
async def test_4_0_finalsuggest_tariff_choices(
        taxi_persuggest, load_json, yamaps, mockserver,
):
    tariffs = ['vip', 'cargo']

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        assert request.json == {
            'geopoint': [37.5, 55.71],
            'type': 'a',
            'filter': {
                'excluded_zone_types': [],
                'persistent_only': False,
                'selected_tariff': 'vip',
            },
        }
        response = load_json('pp_zones_v2_response.json')
        response['zones'][0]['points'][1]['supported_tariffs'] = tariffs
        return response

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['selected_class'] = 'vip'

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    actual = persuggest_common.jsonify(response.json())
    expected = persuggest_common.jsonify(
        load_json('expected_response_simple.json'),
    )
    del actual['typed_experiments']
    del expected['typed_experiments']
    expected['position_choices'] = {
        **expected['position_choices'],
        'title': {
            'items': [
                {
                    'font_size': 42,
                    'font_weight': 'bold',
                    'text': 'Крутите новый барабан!',
                    'type': 'text',
                },
            ],
        },
        'subtitle': {
            'items': [{'text': 'Because this is ULTIMA!', 'type': 'text'}],
        },
    }
    expected['condition_actions'] = []  # not supported in v1
    expected['conditional_actions_v2'] = [
        {
            'actions': [{'type': 'repeat_request'}],
            'conditions': [
                [
                    {
                        'tariff_whitelist': tariffs,
                        'type': 'change_to_unwhitelisted_tariff',
                    },
                ],
            ],
        },
    ]
    assert actual == expected


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_filter_bad_points(
        taxi_persuggest, load_json, yamaps, mockserver,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response_with_bad_point.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert (
        persuggest_common.jsonify(response.json())
        == persuggest_common.jsonify(
            load_json('expected_response_wo_bad_point.json'),
        )
    )


async def test_4_0_finalsuggest_no_taxi_service(
        taxi_persuggest, load_json, mockserver, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))
    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    expected_response = {
        'services': {
            'taxi': {
                'available': False,
                'unavailability_reason': {
                    'message': 'This region is not supported yet',
                },
            },
        },
        'results': [],
        'zones': {'nearest_zones': []},
        'points': [],
        'typed_experiments': {'version': -1, 'items': []},
        'points_icon_image_tag': '',
    }
    assert response.json() == expected_response


async def test_4_0_finalsuggest_not_valid_position(taxi_persuggest):
    request = copy.deepcopy(BASE_REQUEST)
    request['position'] = [182.0, 1.0]
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='exp3_add_bigb_coordinate.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_umlaas(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    request_to_check = {
        'excluded_zone_types': ['skolkovo'],
        'points': [[37.5763, 55.7272], [37.5466, 55.7108]],
    }

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/bigb/bigb')
    def _mock_bigb(request):
        assert request.args['client'] == 'taxi'
        assert request.args['format'] == 'protobuf'
        assert request.args['puid'] == '4003514353'
        msg = user_profile_pb2.Profile()
        json_dict = load_json('bigb_response.json')
        json_format.ParseDict(json_dict, msg)
        return mockserver.make_response(
            msg.SerializeToString(deterministic=True),
        )

    yamaps.add_fmt_geo_object(load_json('yamaps_response_ml.json'))

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_sz_bzf(request):
        assert json.loads(request.get_data()) == request_to_check
        response = {'results': [{'in_zone': False}, {'in_zone': False}]}
        return response

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        for header, value in AUTHORIZED_HEADERS.items():
            if header == 'X-Request-Application':
                assert set(request.headers[header].split(',')) == set(
                    value.split(','),
                )
            elif header.startswith('X'):
                assert request.headers[header] == value
        assert request.headers['X-AppMetrica-UUID'] == 'UUID'
        assert request.headers['X-AppMetrica-DeviceId'] == 'DeviceId'
        assert request.headers['X-Request-Language'] == 'ru'
        request = json.loads(request.get_data())
        assert request == load_json('umlaas_finalsuggest_request.json')
        return load_json('umlaas_finalsuggest_response.json')

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_fs_ml.json')


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_umlaas_extra(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    request_to_check = {
        'excluded_zone_types': ['skolkovo'],
        'points': [[37.5763, 55.7272], [37.5466, 55.7108]],
    }

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_response_ml.json'))

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_sz_bzf(request):
        assert json.loads(request.get_data()) == request_to_check
        response = {'results': [{'in_zone': False}, {'in_zone': False}]}
        return response

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        for header, value in AUTHORIZED_HEADERS.items():
            if header == 'X-Request-Application':
                assert set(request.headers[header].split(',')) == set(
                    value.split(','),
                )
            elif header.startswith('X'):
                assert request.headers[header] == value
        assert request.headers['X-AppMetrica-UUID'] == 'UUID'
        assert request.headers['X-AppMetrica-DeviceId'] == 'DeviceId'
        assert request.headers['X-Request-Language'] == 'ru'
        return load_json('umlaas_finalsuggest_response_extra.json')

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_fs_ml_extra.json')


@pytest.mark.experiments3(filename='exp3_stick_to_eats.json')
@pytest.mark.experiments3(
    filename='exp3_eats_umlaas_address_localization.json',
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize('fallback', [False, True])
@pytest.mark.parametrize('by_type', [False, True])
@pytest.mark.parametrize(
    'exp_non_houses',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_remove_non_house_objects_disabled.json',
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_remove_non_house_objects_enabled.json',
                ),
            ],
        ),
    ],
)
async def test_4_0_finalsuggest_stick_to_eats(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        fallback,
        by_type,
        exp_non_houses,
):
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-UserId'] = '2'

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_eats(request):
        if fallback:
            return {}
        return load_json('eats_umlaas_response.json')

    if fallback:
        yamaps.add_fmt_geo_object(
            load_json('yamaps_response_for_eats_fallback.json'),
        )
    else:
        yamaps.add_fmt_geo_object(load_json('yamaps_response_for_eats.json'))

    request = copy.deepcopy(BASE_REQUEST)
    request['position'] = [37.6001, 55.6001]
    if by_type:
        request['type'] = 'eats'
    else:
        request['state']['current_mode'] = 'eats'
    if fallback:
        request['state']['fields'] = [
            {
                'type': 'a',
                'position': [37.6001, 55.6001],
                'log': 'ymapsbm1://URI_1_1',
            },
        ]
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200

    if exp_non_houses:
        check_data = (
            load_json('expected_response_fs_stick_to_eats_fallback.json')
            if fallback
            else load_json('expected_response_fs_stick_to_eats.json')
        )
    else:
        check_data = (
            load_json('expected_resp_fs_stick_to_eats_no_exp_fb.json')
            if fallback
            else load_json('expected_resp_fs_stick_to_eats_no_exp.json')
        )
    assert persuggest_common.jsonify(
        response.json(),
    ) == persuggest_common.jsonify(check_data)


@pytest.mark.experiments3(filename='exp3_stick_to_eats.json')
@pytest.mark.experiments3(
    filename='exp3_eats_umlaas_address_localization.json',
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_rnho_enabled.json')
async def test_4_0_finalsuggest_stick_to_eats_finalize(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-UserId'] = '2'

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_eats(request):
        return load_json('eats_umlaas_response.json')

    yamaps.add_fmt_geo_object(
        load_json('yamaps_response_for_eats_no_house.json'),
    )

    request = copy.deepcopy(BASE_REQUEST)
    request.pop('position')
    request['action'] = 'finalize'
    request['prev_log'] = 'ymapsbm1://eats1_uri'
    request['state']['current_mode'] = 'eats'
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    assert yamaps.times_called() == 1
    check_data = load_json('expected_response_fs_stick_to_eats_nh.json')
    assert persuggest_common.jsonify(
        response.json(),
    ) == persuggest_common.jsonify(check_data)


@pytest.mark.experiments3(filename='exp3_restore_comment.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize('comment_exp', [True, False])
@pytest.mark.parametrize(
    'action,sticky,in_log',
    [
        ('pin_drop', True, False),
        ('pin_drop', False, False),
        ('finalize', False, False),
        ('finalize', False, True),
    ],
)
async def test_4_0_finalsuggest_comment(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        comment_exp,
        action,
        sticky,
        in_log,
):
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    if not comment_exp:
        headers['X-Yandex-UID'] = 'no_comment'

    request = copy.deepcopy(BASE_REQUEST)
    request['action'] = action
    request['sticky'] = sticky
    if action == 'finalize':
        request['position'] = [37.606737, 55.65653]
        request['prev_log'] = (
            '{"uri":"ymapsbm1://some_uri","comment":"ovr"}'
            if in_log
            else 'ymapsbm1://some_uri'
        )

    umlaas_response = load_json('umlaas_finalsuggest_response_comment.json')
    if not sticky:
        del umlaas_response['stick_result']

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response_ml.json'))

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        response = {'results': [{'in_zone': False}, {'in_zone': False}]}
        return response

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return umlaas_response

    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    expected = load_json('expected_response_fs_ml_comment.json')
    if action == 'finalize':
        expected['results'][0]['method'] = 'fs_finalize_uri'
        expected['results'][0]['position'] = [37.606737, 55.65653]
        expected['results'][0]['comment'] = 'ovr' if in_log else 'comment2'
        uri = expected['results'][0]['uri']
        log_json = {'uri': uri}
        if in_log:
            log_json['comment'] = 'ovr'
            expected['results'][0]['log'] = log_json
        else:
            expected['results'][0]['log'] = uri
    elif not sticky:
        expected['results'][0]['method'] = 'fs_not_sticky'
        expected['results'][0]['comment'] = 'comment1'
    if not comment_exp and not in_log:
        del expected['results'][0]['comment']
    response_json = response.json()
    for result in response_json['results']:
        if result['log'].startswith('{'):
            result['log'] = json.loads(result['log'])
    assert response_json == expected


@pytest.mark.experiments3(filename='exp3_check_lbs_position.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_check_lbs_position(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        request = json.loads(request.get_data())
        assert request['position'] == [37.7, 55.8]
        uml_response = load_json('umlaas_finalsuggest_response.json')
        uml_response['points'] = []
        return uml_response

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    @mockserver.json_handler('/lbs-cloud-proxy/lbs')
    def _mock_lbs_cloud_proxy(request):
        expected_request = {
            'common': {'version': '1.0'},
            'ip': {'address_v4': '10.10.10.10'},
            'wifi_networks': [{'mac': '0A0B0C0D0E0F'}],
        }
        request_body = json.loads(request.get_data())
        assert expected_request == request_body
        response = {
            'position': {
                'latitude': 55.8,
                'longitude': 37.7,
                'altitude': 10.0,
                'precision': 100.0,
                'altitude_precision': 1000.0,
                'type': 'wifi',
            },
        }
        return response

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='exp3_superapp_screens.json')
@pytest.mark.experiments3(filename='exp3_use_layers.json')
@pytest.mark.experiments3(filename='exp3_map_objects_layer.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    'uuid, device_id, expected_types',
    [
        ('UUID', 'DeviceId', {'stop', 'userplace'}),
        (
            'MAP_OBJECTS_LAYER_DISABLED',
            'DeviceId',
            {'stop', 'userplace', 'mode'},
        ),
        ('UUID', 'DEVICE_ID_EMPTY_FILTER', None),
    ],
)
async def test_4_0_finalsuggest_with_layers(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        uuid,
        device_id,
        expected_types,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('umlaas_finalsuggest_no_stick_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return {'results': [{'in_zone': True}, {'in_zone': False}]}

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    @mockserver.json_handler('/layers/layers/v1/objects')
    def _mock_layers(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['X-AppMetrica-UUID'] == uuid
        assert request.headers['X-AppMetrica-DeviceId'] == device_id
        request = json.loads(request.get_data())
        assert set(request['types']) == expected_types
        return load_json('layers_response.json')

    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-AppMetrica-UUID'] = uuid
    headers['X-AppMetrica-DeviceId'] = device_id

    response = await taxi_persuggest.post(URL, BASE_REQUEST, headers=headers)
    assert response.status_code == 200
    expected_response = load_json('expected_response_layers.json')
    if expected_types:
        assert _mock_layers.times_called == 1
        assert response.json() == expected_response
    else:
        assert _mock_layers.times_called == 0


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_timeouts(taxi_persuggest, yamaps, mockserver):
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-UserId'] = '2'

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        raise mockserver.TimeoutError()

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        raise mockserver.TimeoutError()

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        raise mockserver.TimeoutError()

    response = await taxi_persuggest.post(URL, BASE_REQUEST, headers=headers)
    assert _mock_zones.has_calls
    assert _mock_graph.has_calls
    assert _mock_umlaas_geo.has_calls
    assert response.status_code == 200


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_500(taxi_persuggest, yamaps, mockserver):
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-UserId'] = '2'

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return mockserver.make_response('fail', status=500)

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        return mockserver.make_response('fail', status=500)

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return mockserver.make_response('fail', status=500)

    response = await taxi_persuggest.post(URL, BASE_REQUEST, headers=headers)
    assert _mock_zones.has_calls
    assert _mock_graph.has_calls
    assert _mock_umlaas_geo.has_calls
    assert response.status_code == 200


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_entrances_list_in_suggest.json')
@pytest.mark.translations(
    client_messages={'suggest.append.entrance': {'ru': 'подъезд'}},
    tariff={
        'detailed.kilometers': {'ru': '%(value).0f км'},
        'round.hundreds_meters': {'ru': '%(value).0f м'},
        'round.tens_meters': {'ru': '%(value).0f м'},
        'round.kilometers': {'ru': '%(value).0f км'},
    },
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.parametrize('show_no_entrances_label', [True, False])
async def test_4_0_finalsuggest_entrances_info(
        taxi_persuggest,
        load_json,
        mockserver,
        yamaps,
        show_no_entrances_label,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps_response = load_json('yamaps_response_entrances_info.json')
    if not show_no_entrances_label:
        yamaps_response['arrival_points'].pop()

    yamaps.add_fmt_geo_object(yamaps_response)

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200

    expected_response = load_json('expected_response_entrances_info.json')
    if not show_no_entrances_label:
        exp_entrances = expected_response['results'][0]['entrances_info']
        exp_entrances.pop('show_no_entrances_label')
        exp_entrances['suggested_entrances'].pop()
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='exp3_geoadjust_entrances.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    ['position', 'nearest_entrance'],
    [
        ([37.621256, 55.745940], None),  # Too far to magnetize
        ([37.616364, 55.757189], '10'),
        ([37.616900, 55.757777], '6'),
    ],
)
@pytest.mark.parametrize(
    ['strategy', 'moveaway'],
    [
        ('dont_move_pin', False),
        ('move_pin_to_entrance', False),
        ('move_pin_to_entrance', True),
        ('move_pin_to_road', False),
        ('move_pin_to_road', True),
    ],
)
async def test_4_0_finalsuggest_pin_drop_geoadjust_entrances(
        taxi_persuggest,
        load_json,
        mockserver,
        yamaps,
        position,
        nearest_entrance,
        strategy,
        moveaway,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {'points': []}

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        response = load_json('yamaps_response_with_entrances.json')
        for ent_num, ent_coord in entrances.items():
            if ','.join(map(str, ent_coord)) == request.args['ll']:
                response['name'] += ', подъезд ' + ent_num
                break
        return [response]

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        assert strategy == 'move_pin_to_road' or not should_adjust
        lonlat = [request.json['longitude'], request.json['latitude']]

        if nearest_entrance is None or moveaway:
            assert lonlat == position
            return {'adjusted': []}

        assert lonlat == entrances[nearest_entrance]
        return {
            'adjusted': [
                {
                    'longitude': road_point[0],
                    'latitude': road_point[1],
                    'geo_distance': 100,
                },
            ],
        }

    entrances = {'6': [37.617283, 55.757864], '10': [37.616469, 55.757339]}

    road_point = [37.5566, 55.7172]

    # should adjust if good entrance is found and user didn't
    # move pin away previously
    should_adjust = nearest_entrance is not None and not moveaway

    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-PhoneId'] = strategy  # used by experiment

    request = copy.deepcopy(BASE_REQUEST)
    request['position'] = position
    request['sticky'] = False
    if moveaway:
        request['state']['fields'] = [
            {
                'type': 'a',
                'entrance': nearest_entrance,
                'position': [1, 2],
                'log': 'ymapsbm1://URI_1_1',
            },
        ]

    response = await taxi_persuggest.post(URL, request, headers=headers)

    expected = load_json('expected_response_geoadjust_entrances.json')
    result = expected['results'][0]

    if strategy == 'dont_move_pin' or not should_adjust:
        result['position'] = position
    elif strategy == 'move_pin_to_entrance':
        result['position'] = entrances[nearest_entrance]
    elif strategy == 'move_pin_to_road':
        result['position'] = road_point
    else:
        assert False

    if should_adjust:
        result['title']['text'] += ', подъезд ' + nearest_entrance
        result['method'] = 'fs_semi_sticky_geoadjust'

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.experiments3(filename='exp3_use_layers.json')
@pytest.mark.experiments3(filename='exp3_geoadjust_stops.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    ['position', 'layers_request_failed', 'adjusted'],
    [
        ([37.5160, 55.7172], False, True),
        ([37.1, 55.1], False, False),
        ([37.5160, 55.7172], True, False),
    ],
)
@pytest.mark.translations(
    client_messages={'geoadjust.comment_mt_stop': {'ru': 'Моя остановочка!'}},
)
async def test_4_0_finalsuggest_pin_drop_geoadjust_stops(
        taxi_persuggest,
        load_json,
        mockserver,
        yamaps,
        position,
        layers_request_failed,
        adjusted,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {'points': []}

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response_with_entrances.json'))

    @mockserver.json_handler('/layers/layers/v1/objects')
    def _mock_layers(request):
        if layers_request_failed:
            return mockserver.make_response(status=500)
        assert set(request.json['types']) == {'userplace', 'stop', 'mode'}
        return load_json('layers_response.json')

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        return mockserver.make_response(status=500)

    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-PhoneId'] = 'dont_move_pin'

    request = copy.deepcopy(BASE_REQUEST)
    request['position'] = position
    request['sticky'] = False

    response = await taxi_persuggest.post(URL, request, headers=headers)

    expected = load_json('expected_response_geoadjust_stops.json')
    expected['results'][0]['position'] = position
    if layers_request_failed:
        expected['points'] = []
    if not adjusted:
        del expected['results'][0]['comment']
        expected['results'][0]['method'] = 'fs_not_sticky'
    assert response.json() == expected


@pytest.mark.parametrize(
    'yandex_drive_response,unavailability_code',
    [
        ('response_yandex_drive.json', None),
        (None, 'no_drive_response'),
        ('response_yandex_drive_no_offers.json', 'bad_dst'),
    ],
)
@pytest.mark.translations(
    client_messages={'drive.no_service': {'ru': 'Драйв недоступен'}},
)
async def test_4_0_finalsuggest_drive_pin_drop(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        yandex_drive_response,
        unavailability_code,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'4003514353').hexdigest()
        )
        assert request.headers['UUID'] == 'UUID'
        assert request.headers['DeviceId'] == 'DeviceId'
        assert (
            request.headers['X-YaTaxi-UserId']
            == AUTHORIZED_HEADERS['X-YaTaxi-UserId']
        )
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.args == {
            'src': '37.1 55.2',
            'dst': '37.5 55.71',
            'lang': 'ru',
            'offer_count_limit': '5',
            'destination_name': 'Садовническая улица, 82с2',
        }
        if not yandex_drive_response:
            return mockserver.make_response('fail', status=500)
        return mockserver.make_response(
            json=load_json(yandex_drive_response), headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASE_REQUEST)
    request['type'] = 'b'
    request['sticky'] = False
    request['state']['current_mode'] = 'drive'
    request['state']['fields'] = [
        {'type': 'a', 'position': [37.1, 55.2], 'log': 'ymapsbm1://URI_1_1'},
    ]
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_drive_pin_drop.json')
    if unavailability_code:
        expected['services']['drive'] = {
            'available': False,
            'unavailability_reason': {
                'message': 'Драйв недоступен',
                'code': unavailability_code,
            },
        }
    assert response.json() == expected


async def test_4_0_finalsuggest_drive_pin_drop_selected_car(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    request = copy.deepcopy(BASE_REQUEST)
    request['type'] = 'b'
    request['sticky'] = False
    request['state']['current_mode'] = 'drive'
    request['state']['fields'] = [
        {'type': 'a', 'position': [37.1, 55.2], 'log': 'ymapsbm1://URI_1_1'},
    ]
    request['state']['drive'] = {'selected_car_number': '123456'}
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_drive_pin_drop.json')
    expected['services']['drive'].pop('layers_context')
    assert response.json() == expected


@pytest.mark.translations(
    client_messages={'drive.no_service': {'ru': 'Драйв недоступен'}},
)
async def test_4_0_finalsuggest_drive_finalize(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        return mockserver.make_response(
            json=load_json('response_yandex_drive.json'),
            headers={'X-Req-Id': '123'},
        )

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        return load_json('userplaces_item_response.json')

    request = {
        'action': 'finalize',
        'position': [37.51, 55.72],
        'prev_log': (
            '{"type":"userplace","userplace_id":'
            '"00000004-AAAA-AAAA-AAAA-000000000001"}'
        ),
        'state': {
            'accuracy': 20,
            'bbox': [30.1, 50.1, 40.1, 60.1],
            'fields': [
                {
                    'type': 'a',
                    'position': [37.1, 55.2],
                    'log': 'ymapsbm1://URI_1_1',
                },
            ],
            'location': [37.51, 55.72],
            'current_mode': 'drive',
        },
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_drive_finalize.json')
    assert response.json() == expected


@pytest.mark.experiments3(filename='exp3_condition_actions.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.config(
    TARIFF_CATEGORIES_ORDER_FLOW={
        'courier': {'order_flow': 'delivery'},
        'drive': {'order_flow': 'drive'},
        'express': {'order_flow': 'delivery'},
        'shuttle': {'order_flow': 'shuttle'},
    },
)
@pytest.mark.parametrize(
    ['has_exp', 'current_mode', 'selected_class', 'has_zones'],
    (
        [True, 'main', 'econom', True],
        [True, '', 'courier', False],  # on summary
        [
            True,
            'delivery',
            'econom',
            False,
        ],  # on card after summary with client bug
        [False, '', 'courier', True],  # fallback to old behavior with exp
    ),
)
async def test_4_0_finalsuggest_no_closures_for_delivery(
        taxi_persuggest,
        load_json,
        mockserver,
        yamaps,
        experiments3,
        has_exp,
        current_mode,
        selected_class,
        has_zones,
):
    if has_exp:
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='closures_disable_for_delivery',
            consumers=['persuggest/finalsuggest'],
            default_value={'enabled': True},
        )

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        response = load_json('pp_zones_v2_response.json')
        if not has_zones:
            del response['pin_point_id']
            del response['pin_zone_id']
        return response

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    request = copy.deepcopy(BASE_REQUEST)

    request['state']['current_mode'] = current_mode
    request['state']['selected_class'] = selected_class
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200

    assert ('position_choices' in response.json()) == has_zones
    if has_zones:
        return
    actions = response.json()['conditional_actions_v2']
    actions[0]['conditions'][0][0]['tariff_whitelist'].sort()
    assert actions == [
        {
            'actions': [{'type': 'repeat_request'}],
            'conditions': [
                [
                    {
                        'tariff_whitelist': ['courier', 'express'],
                        'type': 'change_to_unwhitelisted_tariff',
                    },
                ],
            ],
        },
    ]


@pytest.mark.experiments3(filename='exp3_main_mode_for_adjust_to_road.json')
@pytest.mark.experiments3(filename='exp3_condition_actions.json')
@pytest.mark.experiments3(filename='exp3_short_text_formatting.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    ['current_mode', 'response_filename'],
    (
        ['', 'expected_response_simple.json'],  # regular choices for taxi
        ['main', 'expected_response_simple.json'],  # choices for disabled main
        pytest.param(
            'main',
            'expected_response_main_disabled_choices.json',
            marks=pytest.mark.experiments3(
                filename='exp3_main_mode_for_closures_taxi_flow.json',
            ),
        ),
    ),
)
async def test_4_0_finalsuggest_main_mode_for_closures_disable_choices(
        taxi_persuggest,
        load_json,
        mockserver,
        yamaps,
        current_mode,
        response_filename,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        # has_choices_on_main = false
        return load_json('pp_zones_v2_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    request = copy.deepcopy(BASE_REQUEST)

    request['state']['current_mode'] = current_mode
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    assert _mock_umlaas.times_called == 1

    expected_response = persuggest_common.jsonify(load_json(response_filename))
    # no typed experiments in ...simple.json
    expected_response['typed_experiments'] = {'items': [], 'version': -1}
    assert persuggest_common.jsonify(response.json()) == expected_response


@pytest.mark.translations(
    client_messages={
        'tanker_key_for_title': {'ru': 'Title'},
        'tanker_key_for_content': {'ru': 'Content'},
        'tanker_key_for_button_text': {'ru': 'Button text'},
    },
)
@pytest.mark.experiments3(filename='exp3_main_mode_for_adjust_to_road.json')
@pytest.mark.experiments3(filename='exp3_condition_actions.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_main_mode_for_adjust(
        taxi_persuggest, load_json, mockserver, yamaps_wrapper,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        graph_request = json.loads(request.get_data())
        if 'roads_struct_filter' in graph_request:
            roads_filter = graph_request['roads_struct_filter']
            if roads_filter.get('tunnels', True):
                return load_json('yaga_adjust_response_no_filter.json')
            return load_json('yaga_adjust_response_filter.json')
        return {'adjusted': []}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('umlaas_finalsuggest_no_stick_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return {'results': [{'in_zone': True}, {'in_zone': False}]}

    request = copy.deepcopy(BASE_REQUEST)
    request['position'] = [37.1, 55.1]
    request['state']['current_mode'] = 'main'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_condition_actions_adjust.json',
    )

    request['state']['current_mode'] = ''
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == load_json(
        'expected_response_adjust_to_good_road.json',
    )


@pytest.mark.experiments3(filename='exp3_short_text_formatting.json')
@pytest.mark.experiments3(
    filename='exp3_main_mode_for_closures_taxi_flow.json',
)
@pytest.mark.experiments3(filename='exp3_main_mode_for_adjust_to_road.json')
@pytest.mark.experiments3(filename='exp3_condition_actions.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_main_mode_for_closures_taxi_flow(
        taxi_persuggest, load_json, mockserver, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response_without_choices.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('umlaas_finalsuggest_no_stick_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return {'results': [{'in_zone': True}, {'in_zone': False}]}

    request = copy.deepcopy(BASE_REQUEST)

    request['state']['current_mode'] = 'main'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert (
        persuggest_common.jsonify(response.json())
        == persuggest_common.jsonify(
            load_json('expected_response_condition_actions_main_tf.json'),
        )
    )

    request['state']['current_mode'] = ''
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert (
        persuggest_common.jsonify(response.json())
        == persuggest_common.jsonify(
            load_json('expected_response_condition_actions_taxi.json'),
        )
    )


@pytest.mark.experiments3(filename='exp3_eats_addrs_from_umlaas.json')
@pytest.mark.experiments3(filename='exp3_stick_to_eats.json')
@pytest.mark.experiments3(
    filename='exp3_eats_umlaas_address_localization.json',
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    'entrance,position', [('1', [37.1001, 55.1001]), ('3', [37.1, 55.1])],
)
async def test_4_0_finalsuggest_umlaas_eats(
        taxi_persuggest, mockserver, yamaps, load_json, entrance, position,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    yamaps.add_fmt_geo_object(
        load_json('yamaps_response_ml_with_entrances.json'),
    )

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        response = {'results': [{'in_zone': False}, {'in_zone': False}]}
        return response

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        ml_request = json.loads(request.get_data())
        assert ml_request == load_json('umlaas_finalsuggest_request_eats.json')
        resp = load_json('umlaas_finalsuggest_response_eats.json')
        resp['stick_result']['entrance'] = entrance
        return resp

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['current_mode'] = 'eats'
    request['type'] = 'b'

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected_resp = persuggest_common.jsonify(
        load_json('expected_response_fs_ml_eats.json'),
    )
    result = expected_resp['results'][0]
    result['entrance'] = entrance
    result['position'] = position
    result['log']['point_extra_details']['entrance'] = str(entrance)
    assert persuggest_common.jsonify(response.json()) == expected_resp


@pytest.mark.parametrize(
    'config_value, expectd_exp',
    [
        ({'contains': [], 'regex': []}, None),
        ({'contains': ['user-agent'], 'regex': []}, 'onboarding'),
        ({'contains': [], 'regex': ["""(\\w+)-(\\w+)"""]}, 'onboarding'),
    ],
)
@pytest.mark.experiments3(filename='exp3_typed_experiments.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_supported_devices(
        taxi_persuggest,
        load_json,
        mockserver,
        yamaps,
        taxi_config,
        config_value,
        expectd_exp,
):
    taxi_config.set_values(
        dict(ONBOARDING_UNSUPPORTED_LIST_DEVICES=config_value),
    )
    await taxi_persuggest.invalidate_caches()

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'typed_experiments' in data
    items = data['typed_experiments']['items']
    experiment_names = [val['name'] for val in items]

    if expectd_exp:
        assert expectd_exp in experiment_names
    else:
        assert expectd_exp not in experiment_names


@pytest.mark.experiments3(filename='exp3_arrival_points_umlaas.json')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                PERSUGGEST_UMLAAS_GEO_SWITCH={
                    'enabled': True,
                    'finalsuggest_v1': False,
                    'arrival_points_v1': False,
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                PERSUGGEST_UMLAAS_GEO_SWITCH={
                    'enabled': False,
                    'finalsuggest_v1': True,
                    'arrival_points_v1': True,
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize('mode', ['', 'eats'])
async def test_finalize_4_0_ml_disabled(
        taxi_persuggest, mockserver, load_json, yamaps, mode,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        assert False

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/arrival-points')
    def _mock_umlaas_geo_ap(request):
        assert False

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    request = {
        'action': 'finalize',
        'position': [34.7, 32.1],
        'prev_log': (
            '{"uri": "ymapsbm1://userplace_uri",'
            '"point_extra_details": {"entrance": "13"} }'
        ),
        'current_mode': mode,
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
    assert response.status_code == 200
    assert response.json()['results'][0]['position'] == [34.7, 32.1]
    if mode == '':
        assert response.json()['results'][0]['entrance'] == '13'


@pytest.mark.experiments3(filename='exp3_unbaraban.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_unbaraban(
        taxi_persuggest, load_json, mockserver, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert (
        persuggest_common.jsonify(response.json())
        == persuggest_common.jsonify(
            load_json('expected_response_simple_unbaraban.json'),
        )
    )


@pytest.mark.experiments3(
    filename='exp3_main_mode_for_closures_eats_flow.json',
)
@pytest.mark.experiments3(filename='exp3_condition_actions.json')
@pytest.mark.experiments3(filename='exp3_short_text_formatting.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_main_mode_eats_flow_404(
        taxi_persuggest, load_json, mockserver, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response_without_choices.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('umlaas_finalsuggest_no_stick_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return {'results': [{'in_zone': True}, {'in_zone': False}]}

    request = copy.deepcopy(BASE_REQUEST)
    request['sticky'] = False
    request['state']['current_mode'] = 'main'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_unbaraban_1_point(
        taxi_persuggest, load_json, mockserver, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('pp_zones_v2_response_1_point.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    response = await taxi_persuggest.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert 'position_choices' not in response.json()


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_userplace_adjust.json')
@pytest.mark.parametrize('is_sticky', [True, False])
async def test_4_0_finalsuggest_userplace_adjust(
        taxi_persuggest, load_json, mockserver, yamaps, is_sticky,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('umlaas_finalsuggest_no_stick_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return {'results': [{'in_zone': True}, {'in_zone': False}]}

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return load_json('userplaces_response.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['sticky'] = is_sticky
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected_resp = persuggest_common.jsonify(
        load_json('expected_response_userplace_adjust.json'),
    )
    if is_sticky:
        expected_resp['results'][0]['comment'] = 'test_comment'
    assert persuggest_common.jsonify(response.json()) == expected_resp


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_userplace_adjust_url.json')
async def test_4_0_finalsuggest_userplace_adjust_url(
        taxi_persuggest, load_json, mockserver, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('umlaas_finalsuggest_no_stick_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return {'results': [{'in_zone': True}, {'in_zone': False}]}

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return load_json('userplaces_response_url.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['sticky'] = False
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert (
        persuggest_common.jsonify(response.json())
        == persuggest_common.jsonify(
            load_json('expected_response_userplace_adjust_uri.json'),
        )
    )


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_4_0_finalsuggest_grocery_finalize(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    request = load_json('finalize_grocery_request.json')
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_grocery_finalize.json')
    assert response.json() == expected


@pytest.mark.parametrize(
    'prev_log',
    [
        '{"uri": "ytmpp://lon=59.950272,lat=10.815241"}',
        'ytmpp://lon=59.950272,lat=10.815241',
    ],
)
async def test_4_0_finalsuggest_pickup_points_manager(
        taxi_persuggest, mockserver, yamaps, load_json, prev_log,
):
    yamaps.add_fmt_geo_object(
        {
            'description': 'Oslo, Норвегия',
            'geocoder': {
                'address': {
                    'country': 'Норвегия',
                    'formatted_address': (
                        'Østreheimsveien 27, 0590 Oslo, Норвегия'
                    ),
                    'house': '27',
                    'locality': 'Oslo',
                    'street': 'Østreheimsveien',
                },
                'id': '8063585',
            },
            'geometry': [37.615928, 55.757333],
            'name': 'Østreheimsveien 27',
            'uri': 'gmaps://place_id=ChIJZeYI0dRvQUYRmyciVeuexuM',
        },
    )

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {'notification_params': {}, 'zones': []}

    @mockserver.json_handler('/pickup-points-manager/v1/points/find')
    def _mock_ppmanager(request):
        return {
            'coordinates': [10.815241, 59.950272],
            'id': 1024,
            'title': 'My cool Oslo POI',
            'title_fallback': 'title_fallback',
        }

    request = load_json('finalize_ppm.json')
    request['prev_log'] = prev_log

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['results'][0]['title']['text'] == 'My cool Oslo POI'
    assert (
        resp_json['results'][0]['uri'] == 'ytmpp://lon=59.950272,lat=10.815241'
    )
