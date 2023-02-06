import copy
import json
import math
import operator

import pytest

URL = '/4.0/layers/v2/objects'

DEFAULT_APPLICATION = (
    'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=4,app_brand=yataxi'
)

USER_ID = '12345678901234567890123456789012'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-AppMetrica-UUID': 'UUID',
}


BASE_REQUEST = {
    'state': {
        'bbox': [37.5, 55.7, 37.6, 55.8],
        'location': [37.51, 55.72],
        'mode': 'normal',
        'screen': 'main',
        'pin': [37.5466, 55.7108],
        'zoom': 19.0,
    },
}

CLIENT_MESSAGES = {
    'layers.drive.no_object': {'ru': 'Нет машин поблизости'},
    'summary.drive.button.title': {'ru': 'Далее'},
    'summary.drive.button.subtitle': {
        'ru': 'Ждать %(free_reservation_duration)s бесплатно',
    },
    'summary.drive.description': {'ru': 'За %(price)s, ~%(riding_duration)s'},
    'summary.drive.estimated_waiting.message': {
        'ru': 'идти %(walking_duration)s',
    },
    'summary.drive.cashback.title': {'ru': 'Кэшбээк'},
    'summary.drive.cashback.tooltip.text': {'ru': 'кэшбээк'},
}


def isclose_lists(list_a, list_b):
    if len(list_a) != len(list_b):
        return False
    for a_elem, b_elem in zip(list_a, list_b):
        if not math.isclose(a_elem, b_elem):
            return False
    return True


def get_metric_value(object_type, metrics):
    try:
        return metrics['layers-object-types']['in_bbox'][object_type]['iphone']
    except KeyError:
        return 0


def get_metrics_diff(before, after):
    result = {}
    for object_type in after['layers-object-types']['in_bbox'].keys():
        value_before = get_metric_value(object_type, before)
        value_after = get_metric_value(object_type, after)
        diff = value_after - value_before
        if diff > 0:
            result[object_type] = diff
    return result


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_empty(taxi_layers):
    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = []
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    value = response.json()
    assert isclose_lists(value['bbox'], [37.45, 55.6, 37.7, 55.9])
    assert isclose_lists(value['zooms'], [18.0, 20.0])
    assert value['validity_sec'] == 60
    assert value['throttle_ms'] == 100
    assert value['clean_sec'] == 120
    assert value['features'] == []


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(
    filename='experiments3_layers_add_notifications.json',
)
@pytest.mark.parametrize('filt', ['off', 'zoom', 'mode', 'screen'])
@pytest.mark.translations(
    client_messages={
        'leave_on_parking_lot.subtitle': {'ru': 'ru_subtitle'},
        'leave_on_parking_lot.title': {'ru': 'ru_title'},
    },
)
async def test_v2_objects_stops(taxi_layers, mockserver, load_json, filt):
    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        request_json = json.loads(request.get_data())
        assert request_json['lang'] == 'ru'
        assert isclose_lists(request_json['bbox'], [37.45, 55.6, 37.7, 55.9])
        return load_json('response_stops.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['stop']
    if filt == 'zoom':
        request['state']['zoom'] = 10.0
    elif filt == 'mode':
        request['state']['mode'] = 'eats'
    elif filt == 'screen':
        request['state']['screen'] = 'summary'

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = []
    if filt == 'off':
        expected_features = load_json('features.json')['stops']

    assert response.status_code == 200
    assert response.json()['features'] == expected_features
    if filt == 'screen':
        assert 'status_view' in response.json()
        assert 'notifications' in response.json()['status_view']
        expected_sv = load_json('notifications.json')
        assert response.json()['status_view']['notifications'] == expected_sv
    else:
        assert 'status_view' not in response.json()


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(filename='experiments3_filter_options.json')
@pytest.mark.translations(
    client_messages={
        'layers.stops.no_object': {'ru': 'Нет остановок поблизости'},
        'shuttle_key': {'ru': 'Shuttle'},
        'bus_key': {'ru': 'Bus'},
    },
)
@pytest.mark.parametrize(
    'zoom,only_filter_options', [(15.5, False), (23, True)],
)
async def test_v2_objects_masstransit(
        taxi_layers, mockserver, load_json, zoom, only_filter_options,
):
    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        request_json = json.loads(request.get_data())
        print('bbox=', request_json['bbox'])
        assert isclose_lists(request_json['bbox'], [37.45, 55.6, 37.7, 55.9])
        mt_response = load_json('response_stops_masstransit.json')
        if 'stops' not in request_json['requested_data']:
            mt_response['stops'] = []
        if 'stops_transport_types' not in request_json['requested_data']:
            mt_response['stops_transport_types'] = []
        return mt_response

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'masstransit'
    request['state']['screen'] = 'discovery'
    request['state']['zoom'] = zoom
    request['state']['mapkit'] = {'mt_stop_id': 'stop_0'}
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = (
        []
        if only_filter_options
        else load_json('features.json')['stops_masstransit']
    )

    assert response.status_code == 200
    expected_filter_options = load_json('filter_options.json')
    assert expected_filter_options == response.json()['filter_options']
    assert (
        sorted(response.json()['features'], key=operator.itemgetter('id'))
        == expected_features
    )

    assert response.json().get('selected_object_id', None) == (
        None if only_filter_options else 'stop_0'
    )
    optimal_view = response.json().get('optimal_view', None)
    if only_filter_options:
        assert not optimal_view
    else:
        assert len(optimal_view['optimal_bbox']) == 4
        optimal_view['optimal_bbox'] = []
        assert optimal_view == load_json('stops_optimal_view.json')


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.translations(
    client_messages={
        'layers.stops.no_object': {'ru': 'Нет остановок поблизости'},
    },
)
async def test_v2_objects_masstransit_context(
        taxi_layers, mockserver, load_json,
):
    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        request_json = json.loads(request.get_data())
        print('bbox=', request_json['bbox'])
        assert isclose_lists(request_json['bbox'], [37.45, 55.6, 37.7, 55.9])
        return load_json('response_stops_masstransit.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'masstransit'
    request['state']['screen'] = 'discovery'
    request['state']['zoom'] = 15.5
    request['state']['mapkit'] = {'mt_stop_id': 'stop_0'}
    request['context'] = {'type': 'masstransit', 'filter': ['shuttle']}
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    assert response.status_code == 200
    assert len(response.json()['features']) == 1
    assert response.json()['features'][0]['id'] == 'stop_2'


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(
    filename='experiments3_layers_providers_stops_filtering.json',
)
@pytest.mark.experiments3(
    filename='experiments3_layers_object_filtering_stops.json',
)
@pytest.mark.translations(
    client_messages={
        'layers.stops.no_object': {'ru': 'Нет остановок поблизости'},
    },
)
async def test_v2_objects_masstransit_filtering_v2(
        taxi_layers, mockserver, load_json,
):
    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        request_json = json.loads(request.get_data())
        print('bbox=', request_json['bbox'])
        assert isclose_lists(
            request_json['bbox'],
            [37.44140625, 55.576171875, 37.705078125, 55.927734375],
        )
        return load_json('response_stops_masstransit.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'masstransit'
    request['state']['screen'] = 'discovery'
    request['state']['zoom'] = 16
    request['state']['mapkit'] = {'mt_stop_id': 'stop_0'}
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    all_features = load_json('features_stops_mt_filtering.json')['features']
    expected_features = all_features

    assert response.status_code == 200
    assert (
        sorted(response.json()['features'], key=operator.itemgetter('id'))
        == expected_features
    )
    assert response.json()['selected_object_id'] == 'stop_0'
    optimal_view = response.json()['optimal_view']
    assert len(optimal_view['optimal_bbox']) == 4
    optimal_view['optimal_bbox'] = []
    assert optimal_view == load_json('stops_optimal_view.json')
    assert response.json()['disable_intersection_check']


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(
    filename='experiments3_layers_providers_hidden_stops.json',
)
@pytest.mark.parametrize('mode', ['normal', 'masstransit'])
async def test_v2_objects_stops_hidden(
        taxi_layers, mockserver, load_json, mode,
):
    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        request_json = json.loads(request.get_data())
        assert request_json['lang'] == 'ru'
        assert isclose_lists(request_json['bbox'], [37.45, 55.6, 37.7, 55.9])
        return load_json('response_stops.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['stop']
    request['state']['mode'] = mode

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = []
    if mode == 'masstransit':
        expected_features = load_json('features.json')['stops']

    assert response.status_code == 200
    assert response.json()['features'] == expected_features


@pytest.mark.translations(
    client_messages={
        'sdc_point_label_key': {'ru': 'Это остановочка самоходочки'},
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_modes.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.parametrize('out_of_bbox', [False, True])
async def test_v2_objects_modes(
        taxi_layers, mockserver, load_json, out_of_bbox,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        assert request.headers['X-Request-Language'] == 'ru'
        assert json.loads(request.get_data()) == {
            'type': 'any',
            'geopoint': [37.5466, 55.7108],
            'filter': {'allowed_zone_types': ['sdc', 'boats']},
        }
        response = load_json('response_zones_v2_with_boats.json')
        if out_of_bbox:
            response['zones'][0]['points'][1]['geopoint'] = [33.3, 55.8]
            response['zones'][1]['points'][1]['geopoint'] = [33.0, 55.0]
        return response

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['mode']
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = []
    if not out_of_bbox:
        expected_features = load_json('features.json')['modes']

    assert response.status_code == 200
    assert response.json()['features'] == expected_features


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_userplaces(taxi_layers, mockserver, load_json):
    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces_list(request):
        assert json.loads(request.get_data()) == {
            'lang': 'ru',
            'app_name': 'iphone',
            'user_identity': {
                'bound_yandex_uids': ['834149473', '834149474'],
                'flags': {'is_phonish': False, 'is_portal': True},
                'phone_id': '123456789012345678901234',
                'user_id': '12345678901234567890123456789012',
                'yandex_uid': '400000000',
            },
        }
        return load_json('response_userplaces_list.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        request_data = json.loads(request.get_data())
        request_data['excluded_zone_types'].sort()
        assert request_data == {
            'points': [[37.56, 55.77]],
            'excluded_zone_types': ['boats', 'falcon', 'sdc', 'skolkovo'],
        }
        return {'results': [{'in_zone': False}]}

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['userplace']
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = [load_json('features.json')['userplaces'][1]]

    assert response.status_code == 200
    assert response.json()['features'] == expected_features


async def _check_v2_objects_promo(taxi_layers, load_json):
    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['promo']
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = load_json('features.json')['promo']

    assert response.status_code == 200
    assert response.json()['features'] == expected_features


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_promo(taxi_layers, mockserver, load_json):
    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/promos-on-map',
    )
    def _mock_promos_on_map(request):
        data = request.json
        assert data['position']
        return load_json('response_promos_on_map.json')

    await _check_v2_objects_promo(taxi_layers, load_json)


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_umlaas_points.json')
@pytest.mark.parametrize(
    'zoom,expected_indexes', [(17.5, [0, 1, 2]), (16.5, [0, 2]), (15.5, [0])],
)
async def test_v2_objects_umlaas(
        taxi_layers, mockserver, load_json, yamaps, zoom, expected_indexes,
):
    yamaps.add_fmt_geo_object(load_json('geosearch_org.json'))
    yamaps.set_checks({'business_oid': '123456'})

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/points')
    def _mock_umlaas(request):
        expected_headers = copy.deepcopy(AUTHORIZED_HEADERS)
        expected_headers.pop('X-Ya-User-Ticket')
        expected_headers.pop('X-Request-Application')
        for header, value in expected_headers.items():
            assert request.headers[header] == value

        request_json = json.loads(request.get_data())
        assert request_json['position'] == BASE_REQUEST['state']['pin']
        assert isclose_lists(
            request_json['bbox'], [37.44, 55.5968, 37.7088, 55.904],
        )
        assert request_json['zoom'] == zoom
        return load_json('response_umlaas.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return {}

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['pickuppoint']
    request['state']['zoom'] = zoom

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    all_features = load_json('features.json')['umlaas']
    expected_features = []
    for index in expected_indexes:
        expected_features.append(all_features[index])

    assert response.status_code == 200
    assert response.json()['features'] == expected_features


@pytest.mark.translations(
    client_messages={
        'sdc_point_label_key': {'ru': 'Это остановочка самоходочки'},
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_modes.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_static_objects.json')
async def test_v2_objects_all(
        taxi_layers, mockserver, load_json, taxi_layers_monitor,
):
    await taxi_layers.update_server_state()
    metrics_before = await taxi_layers_monitor.get_metrics(
        'layers-object-types',
    )

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        results = [{'in_zone': False}]
        return {'results': results}

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces_list(request):
        return load_json('response_userplaces_list.json')

    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        return load_json('response_stops.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('response_zones_v2_with_boats.json')

    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/promos-on-map',
    )
    def _mock_promos_on_map(request):
        return load_json('response_promos_on_map.json')

    request = copy.deepcopy(BASE_REQUEST)
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    features = load_json('features.json')
    expected = list()
    expected.append(features['userplaces'][1])
    expected.extend(features['modes'])
    # eda is filtered by drive_car
    # check that single provider fail doesn't affect others
    expected.extend(features['stops'])
    # promo is filtered by userplace other
    # expected.extend(features['promo'])
    expected.extend(features['static_objects'])
    assert response.status_code == 200
    assert response.json()['features'] == expected

    metrics_after = await taxi_layers_monitor.get_metrics(
        'layers-object-types',
    )
    assert get_metrics_diff(metrics_before, metrics_after) == {
        'userplace': 1,
        'scooter': 1,
        'stop': 2,
        'mode': 2,
    }


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.parametrize('multicontext', [True, False])
@pytest.mark.parametrize('providers', [[], ['stops'], ['stops', 'userplaces']])
async def test_v2_objects_provider_filter(
        taxi_layers, mockserver, load_json, multicontext, providers,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        results = [{'in_zone': False}]
        return {'results': results}

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces_list(request):
        return load_json('response_userplaces_list.json')

    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        return load_json('response_stops.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('response_zones_v2.json')

    request = copy.deepcopy(BASE_REQUEST)
    filter_context = {
        'type': 'provider_filter',
        'enabled_providers': providers,
    }
    if not multicontext:
        request['context'] = filter_context
    else:
        request['context'] = {'type': 'multi', 'objects': [filter_context]}

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200

    mocks = {'stops': _mock_stops, 'userplaces': _mock_userplaces_list}
    for provider, mock in mocks.items():
        if provider in providers:
            assert mock.times_called == 1
        else:
            assert mock.times_called == 0


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.translations(
    client_messages={'layers.drive.no_object': {'ru': 'Нет машин поблизости'}},
)
async def test_v2_objects_masstransit_empty_optimal_view(
        taxi_layers, mockserver, load_json,
):
    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        request_json = json.loads(request.get_data())
        print('bbox=', request_json['bbox'])
        assert isclose_lists(request_json['bbox'], [37.45, 55.6, 37.7, 55.9])
        return {'stops': []}

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'masstransit'
    request['state']['screen'] = 'discovery'
    request['state']['zoom'] = 17.5
    request['state']['mapkit'] = {'mt_stop_id': 'stop_0'}
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    assert response.status_code == 200
    optimal_view = response.json()['optimal_view']
    optimal_bbox = [37.565, 55.74, 37.585, 55.76]
    assert isclose_lists(optimal_view['optimal_bbox'], optimal_bbox)


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.translations(
    client_messages={
        'layers.drive.increase_zoom': {'ru': 'Приблизьте карту'},
        'layers.drive.increase_zoom_subtitle': {'ru': 'Пожалуйста'},
    },
)
async def test_v2_objects_drive_discovery_increase_zoom(
        taxi_layers, load_json,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'discovery'
    request['state']['zoom'] = 16.5

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json(
        'drive_discovery_increase_zoom_expected_response.json',
    )


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_city_mode_and_multicontext(
        taxi_layers, mockserver, load_json,
):
    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return {'places': []}

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        return mockserver.make_response(
            json=load_json('response_yandex_drive_car_list.json'),
            headers={'X-Req-Id': '123'},
        )

    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_mt_stops(request):
        return load_json('response_stops.json')

    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_yandex_scooters(request):
        return mockserver.make_response(
            json=load_json('response_yandex_drive_car_list.json'),
            headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'city'
    request['state']['screen'] = 'discovery'
    request['context'] = {
        'type': 'multi',
        'objects': [
            {
                'type': 'drive_fixpoint_offers',
                'src': [37.1, 55.2],
                'dst': [37.2, 55.3],
                'offer_count_limit': 3,
                'destination_name': 'Дом',
                'preferred_car_number': 'н587ху750',
                'previous_offer_ids': ['offer_1', 'offer_2'],
            },
            {'type': 'masstransit', 'filter': ['stops']},
        ],
    }

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.times_called == 1
    assert _mock_yandex_drive.times_called == 1
    assert _mock_yandex_scooters.times_called == 1
    assert _mock_mt_stops.times_called == 1
    for feature in response.json()['features']:
        style = feature['properties']['style']
        image = style['image']
        if feature['properties']['type'] == 'drive':
            assert image['name'] == 'city_drive_image_tag'
            assert image['anchor'] == [0.5, 0.8]
            assert not feature['properties']['style'].get('azimuth', False)
            assert feature['properties']['options']
            for opt in feature['properties']['options']:
                if opt['on'] != 'tap':
                    continue
                assert opt['actions']
                for act in opt['actions']:
                    # walk_route isn't for drive.
                    # There is clients's logic for this
                    # check only drive_sdk
                    assert act['type'] in 'drive_sdk'
        elif feature['properties']['type'] == 'stop':
            assert image['name'] == 'city_stop_image_tag'
            assert image['anchor'] == [0.12, 0.34]
            selected_img = style['selected_image']
            assert selected_img['name'] == 'city_stop_selected_stop'
            assert selected_img['anchor'] == [0.56, 0.78]
        elif feature['properties']['type'] == 'scooter':
            assert feature['properties']['options']
            for opt in feature['properties']['options']:
                if opt['on'] != 'tap':
                    continue
                assert opt['actions']
                for act in opt['actions']:
                    assert act['type'] in ('pick_scooter', 'walk_route')
        else:
            raise Exception('unexpected feature')


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_subscription_id(taxi_layers, mockserver, load_json):
    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/promos-on-map',
    )
    def _mock_promos_on_map(request):
        request_json = json.loads(request.get_data())
        assert request_json.get('plus_subscription_info')

        request_psi = {
            'plus_subscription_info': request_json['plus_subscription_info'],
        }
        expect_psi = {
            'plus_subscription_info': {
                'available_subscription_id': 'testing_subscription_id',
            },
        }
        assert request_psi == expect_psi

        return load_json('response_promos_on_map.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['state'].update(
        {
            'user': {
                'plus_subscription_info': {
                    'available_subscription_id': 'testing_subscription_id',
                },
            },
        },
    )

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    assert response.status_code == 200


@pytest.mark.parametrize('edge_gap_per_tile_size', [None, 4])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_grouping(
        taxi_layers,
        experiments3,
        load_json,
        taxi_layers_monitor,
        edge_gap_per_tile_size,
):
    statics = {
        k: {
            'position': v,
            'properties': {
                'display_settings': {'z_index': 7600.0},
                'style': {
                    'image': {
                        'anchor': [0.5, 0.786],
                        'name': 'image_scooter',
                        'type': 'tag',
                    },
                },
                'type': 'scooter',
            },
            'type': 'Point',
            'count': int(k[-1]),  # f000..f010 -> 0..9
        }
        for k, v in load_json('static_objects.json').items()
    }
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='layers_static_objects',
        consumers=['layers/objects'],
        clauses=[
            {
                'title': 'Enabled',
                'value': statics,
                'predicate': {'type': 'true'},
            },
        ],
    )
    layers_object_filtering = load_json(
        'experiments3_layers_object_filtering_groups.json',
    )['configs'][0]
    layers_object_filtering['default_value']['by_provider_name'][
        'static_objects'
    ]['groups']['edge_gap_per_tile_size'] = edge_gap_per_tile_size
    experiments3.add_config(**layers_object_filtering)
    await taxi_layers.update_server_state()
    metrics_before = await taxi_layers_monitor.get_metrics(
        'layers-object-types',
    )

    request = {
        'state': {
            'bbox': [30, 41, 31, 43],
            'location': [30.5, 42],
            'mode': 'normal',
            'pin': [30.5, 42],
            'screen': 'main',
            'zoom': 9.5,
        },
    }
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    assert response.status_code == 200
    features = response.json()['features']

    write_expected_json = False  # enable to make the diff easy to see
    if write_expected_json:
        # it will generate expected grouped.json
        # then replace the original one, make format-layers,
        # and examine the difference using ARC
        distilled = {}
        for feature in features:
            properties = feature['properties']
            value = {
                'pos': feature['geometry']['coordinates'],
                'zooms': properties['display_settings']['zooms'],
            }
            if 'overlays' in properties:
                value['overlay_texts'] = [
                    item['text']
                    for overlay in properties['overlays']
                    for item in overlay['attributed_text']['items']
                ]
            options = properties.get('options')
            if options:
                value['actions'] = [
                    action
                    for option in options
                    for action in option['actions']
                ]
            distilled[feature['id']] = value

        with open('grouped.json', 'w') as file:
            json.dump(distilled, file)

    grouped = load_json('grouped.json')

    blended = {}
    for fid, props in grouped.items():
        zooms = props['zooms']
        overlay_texts = props.get('overlay_texts')
        properties = {
            'display_settings': {'z_index': 7600.0, 'zooms': zooms},
            'style': {
                'image': {
                    'anchor': [0.5, 0.5 if overlay_texts else 0.786],
                    'name': (
                        (
                            'image_scooter_group_144'
                            if '+' in overlay_texts
                            else 'image_scooter_group_96'
                        )
                        if overlay_texts
                        else 'image_scooter'
                    ),
                    'type': 'tag',
                },
            },
            'type': 'scooter',
        }
        if overlay_texts:
            properties['overlays'] = [
                {
                    'anchor': [0.5, 0.5],
                    'attributed_text': {
                        'items': [
                            {
                                'color': '#FFFFFF',
                                'font_size': 16,
                                'text': text,
                                'type': 'text',
                            },
                        ],
                    },
                    'background': {'color': '#505E69'},
                    'shape': 'rounded_rectangle',
                    'show_states': ['unselected', 'selected'],
                    'zooms': zooms,
                }
                for text in overlay_texts
            ]
        actions = props.get('actions')
        if actions:
            properties['options'] = [{'on': 'tap', 'actions': actions}]
        blended[fid] = {
            'geometry': {'coordinates': props['pos'], 'type': 'Point'},
            'id': fid,
            'properties': properties,
            'type': 'Feature',
            'x_taxi_geometry_type': 'Point',
        }
    assert {feature['id']: feature for feature in features} == blended

    metrics_after = await taxi_layers_monitor.get_metrics(
        'layers-object-types',
    )
    assert get_metrics_diff(metrics_before, metrics_after) == {'scooter': 9}


@pytest.mark.translations(
    client_messages={
        'shuttle_start_button_key': {'ru': 'start here'},
        'shuttle_finish_button_key': {'ru': 'finish here'},
        'shuttle_card_subtitle_key': {'ru': 'this is stop'},
    },
)
@pytest.mark.experiments3(filename='exp3_shuttle_enabled_routes.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.parametrize(
    'exclude_stops_ids,optimal_bbox',
    [
        ([], None),
        (['stop_4'], [37.5197, 55.7, 37.523300000000006, 55.703]),
        (['stop_2', 'stop_3', 'stop_4'], [37.0, 55.0, 37.5, 55.5]),
        (['stop_2', 'stop_3', 'stop_4', 'stop_5'], [37.0, 55.0, 37.5, 55.5]),
    ],
)
async def test_shuttle_discovery(
        taxi_layers, mockserver, load_json, exclude_stops_ids, optimal_bbox,
):
    @mockserver.json_handler('/masstransit/v2/stops')
    def _mock_stops(request):
        resp = load_json('v2_stops_with_shuttle_response.json')
        resp['stops'] = list(
            filter(
                lambda x: x['info']['id'] not in exclude_stops_ids,
                resp['stops'],
            ),
        )
        return resp

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'shuttle'
    request['state']['screen'] = 'discovery'
    request['state']['bbox'] = [37.52, 55.7, 37.523, 55.703]

    response = await taxi_layers.post(
        URL, headers=AUTHORIZED_HEADERS, json=request,
    )

    assert response.status_code == 200

    expected = load_json('response_shuttle_discovery.json')
    if optimal_bbox:
        expected['optimal_view'] = {'optimal_bbox': optimal_bbox}
    expected['features'] = list(
        filter(
            lambda x: x['id'] not in exclude_stops_ids, expected['features'],
        ),
    )
    assert response.json() == expected
