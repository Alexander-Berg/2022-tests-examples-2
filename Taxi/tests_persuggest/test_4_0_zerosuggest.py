import copy
import json

import pytest

from tests_persuggest import persuggest_common


ZEROSUGGEST_URL = '4.0/persuggest/v1/zerosuggest'
INTEGRATION_ZEROSUGGEST_URL = 'taxi/persuggest/v1/zerosuggest'

URLS_TO_TEST = [ZEROSUGGEST_URL, INTEGRATION_ZEROSUGGEST_URL]

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
}

BASIC_REQUEST = {
    'state': {
        'accuracy': 20,
        'bbox': [30, 50, 40, 60],
        'fields': [
            {'type': 'a', 'position': [10.1234, 11.1234], 'log': '{}'},
            {'type': 'b', 'position': [12.1234, 13.1234], 'log': '{}'},
        ],
        'location': [37.1, 55.1],
        'coord_providers': [
            {'type': 'gps', 'position': [14.1234, 15.1234], 'accuracy': 10.3},
            {
                'type': 'platform_lbs',
                'position': [16.1, 17.1],
                'accuracy': 4.2,
            },
        ],
        'app_metrica': {'uuid': 'UUID', 'device_id': 'DeviceId'},
    },
    'position': [37, 55],
    'type': 'b',
}

DRIVE_USER_ID = 'ddddDD'

FIX_ENTRANCES_EXP = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'fix_entrances',
    'consumers': ['persuggest/zerosuggest'],
    'clauses': [
        {
            'title': 'always',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
    'default_value': True,
}

DELIVERY_NDD_EXP = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'enable_delivery_ndd_zone',
    'consumers': ['persuggest/zerosuggest'],
    'clauses': [
        {
            'title': 'always',
            'value': {
                'enabled': True,
                'zerosuggest': {
                    'point_a_settings': {
                        'search_rectangle_around_pin': {
                            'longitude_interval': 0.05,
                            'latitude_interval': 0.06,
                        },
                    },
                    'point_b_settings': {
                        'pin': [30, 50],
                        'search_rectangle_around_pin': {
                            'longitude_interval': 0.05,
                            'latitude_interval': 0.06,
                        },
                    },
                },
            },
            'predicate': {'type': 'true'},
        },
    ],
    'default_value': True,
}


async def _logparse(obj):
    for result in obj['results']:
        if 'log' not in result:
            continue
        if isinstance(result['log'], dict):
            if 'tags' in result['log']:
                result['log']['tags'].sort()
            continue
        if not result['log'].startswith('{'):
            continue
        result['log'] = json.loads(result['log'])
        if 'tags' in result['log']:
            result['log']['tags'].sort()
    return obj


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_add_events_to_zerosuggest.json')
@pytest.mark.experiments3(filename='exp3_add_distance_to_zerosuggest.json')
@pytest.mark.translations(
    client_messages={'suggest.append.entrance': {'ru': 'подъезд'}},
    tariff={
        'detailed.kilometers': {'ru': '%(value).0f км'},
        'round.few_kilometers': {'ru': '%(value).1f км'},
        'round.hundreds_meters': {'ru': '%(value).0f м'},
        'round.tens_meters': {'ru': '%(value).0f м'},
        'round.kilometers': {'ru': '%(value).0f км'},
    },
)
async def test_4_0_zerosuggest_basic_with_events(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper, url,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in PA_HEADERS.items():
            assert request.headers[header] == value
        assert request.headers['X-AppMetrica-UUID'] == 'UUID'
        assert request.headers['X-AppMetrica-DeviceId'] == 'DeviceId'
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('uml_zerosuggest_response_basic.json')

    @mockserver.json_handler('/userplaces/userplaces/events')
    def _mock_userplaces_events(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['X-Yandex-UID'] == '4003514353'
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        assert json.loads(request.get_data()) == load_json(
            'userplaces_events_request.json',
        )
        return load_json('userplaces_events_response.json')

    response = await taxi_persuggest.post(
        url, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response_with_events.json')


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.translations(client_messages={'go_home': {'ru': 'Go home'}})
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            'expected_response_dont_fix_entrances.json',
            id='dont_fix_entrances',
        ),
        pytest.param(
            'expected_response_fix_entrances.json',
            id='fix_entrances',
            marks=[pytest.mark.experiments3(**FIX_ENTRANCES_EXP)],
        ),
    ],
)
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_zerosuggest_fix_entrances(
        taxi_persuggest, mockserver, load_json, yamaps, expected_response, url,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response_fix_entrances.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        return [load_json('yamaps_object_with_entrance.json')]

    response = await taxi_persuggest.post(
        url, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    data = await _logparse(response.json())
    assert data == await _logparse(load_json(expected_response))


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.translations(client_messages={'go_home': {'ru': 'Go home'}})
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            'expected_response_dont_fix_entrances.json',
            id='dont_fix_entrances',
        ),
        pytest.param(
            'expected_response_fix_entrances.json',
            id='fix_entrances',
            marks=[pytest.mark.experiments3(**FIX_ENTRANCES_EXP)],
        ),
    ],
)
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_zerosuggest_double_entrances(
        taxi_persuggest, mockserver, load_json, yamaps, expected_response, url,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response_fix_entrances.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        return [load_json('yamaps_object_with_double_entrance.json')]

    response = await taxi_persuggest.post(
        url, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    data = await _logparse(response.json())
    assert data == await _logparse(load_json(expected_response))


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'restaurant_type': {
            'suggest': 'suggest_restaurant_tag',
            'shortcut': 'shortcuts_restaurant_tag',
        },
        'work_userplace_type': {
            'suggest': 'suggest_work_userplace_tag',
            'shortcut': 'shortcuts_work_userplace_tag',
        },
        'default_type': {
            'suggest': 'suggest_default_tag',
            'shortcut': 'shortcuts_default_tag',
        },
        'zero_default_type': {
            'suggest': 'suggest_zero_default_tag',
            'shortcut': 'shortcuts_zero_default_tag',
        },
        'railway_station_type': {
            'suggest': 'suggest_railway_tag',
            'shortcut': 'shortcut_railway_tag',
        },
    },
    ORG_RUBRIC_TO_IMAGE_TYPE={'restaurant': 'restaurant_type'},
    ZONE_TYPE_TO_IMAGE_TYPE={'railway_stations': 'railway_station_type'},
)
@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
        'work': {'ru': 'Работа'},
        'home': {'ru': 'Дом'},
    },
)
@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.parametrize('user_id', ['0', DRIVE_USER_ID])
@pytest.mark.parametrize('point_type', ['a', 'b'])
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
async def test_4_0_zerosuggest_ml_zerosuggest(
        taxi_persuggest,
        mockserver,
        load_json,
        user_id,
        point_type,
        yamaps_wrapper,
        url,
):
    headers = copy.deepcopy(PA_HEADERS)
    headers['X-YaTaxi-UserId'] = user_id

    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_pickuppoints(request):
        return {
            'results': [
                {
                    'zone_name': 'Kazansky vokzal',
                    'zone_type': 'railway_stations',
                    'point_name': 'main entrance',
                },
            ],
        }

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in headers.items():
            assert request.headers[header] == value
        assert request.headers['X-AppMetrica-UUID'] == 'UUID'
        assert request.headers['X-AppMetrica-DeviceId'] == 'DeviceId'
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        if user_id == DRIVE_USER_ID:
            expected_ml_request['source'] = 'drive'
        expected_ml_request['type'] = point_type
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('uml_zerosuggest_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = point_type
    response = await taxi_persuggest.post(url, request, headers=headers)
    assert response.status_code == 200
    data = await _logparse(response.json())
    response_json = load_json('expected_response_ml_zerosuggest.json')
    if point_type == 'a':
        response_json = load_json('expected_response_ml_zerosuggest_a.json')
    assert data == await _logparse(response_json)


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.experiments3(filename='exp3_restore_comment.json')
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_zerosuggest_restore_comment(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper, url,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response_restore_comment.json')

    response = await taxi_persuggest.post(
        url, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response_ml_zerosuggest_comment.json')


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
    },
)
@pytest.mark.parametrize(
    'yandex_uid', ['only_log', 'change_position', 'remove'],
)
@pytest.mark.experiments3(filename='exp3_filter_zerosuggest_addresses.json')
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_zerosuggest_filter_addresses(
        taxi_persuggest,
        mockserver,
        load_json,
        yandex_uid,
        yamaps_wrapper,
        url,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_pickuppoints(request):
        return {
            'results': [
                {
                    'zone_name': 'Kazansky vokzal',
                    'zone_type': 'railway_stations',
                    'point_name': 'main entrance',
                },
            ],
        }

    headers = copy.deepcopy(PA_HEADERS)
    headers['X-Yandex-UID'] = yandex_uid
    response = await taxi_persuggest.post(url, BASIC_REQUEST, headers=headers)
    assert response.status_code == 200
    expected = load_json('expected_response_ml_zerosuggest.json')
    for res in expected['results']:
        res.pop('image_tag')
    if yandex_uid == 'change_position':
        expected['results'][0]['position'] = [37.3, 55.3]
    elif yandex_uid == 'remove':
        expected['results'].pop(0)
    assert await _logparse(expected) == await _logparse(response.json())


@pytest.mark.parametrize('url', URLS_TO_TEST)
async def test_4_0_zerosuggest_bad_position(taxi_persuggest, url):
    request = copy.deepcopy(BASIC_REQUEST)
    request['position'] = [0, 91]
    response = await taxi_persuggest.post(url, request, headers=PA_HEADERS)
    assert response.status_code == 400


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_state(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper, url,
):
    request_to_check = {'uris': ['ytpp://Kazansky/main']}

    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_special_zones(request):
        assert json.loads(request.get_data()) == request_to_check
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        expected_ml_request['state']['current_mode'] = 'delivery'
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('uml_zerosuggest_response.json')

    headers = copy.deepcopy(PA_HEADERS)
    # use umlaas
    headers['X-YaTaxi-UserId'] = '2'

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['current_mode'] = 'delivery'
    response = await taxi_persuggest.post(url, request, headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.experiments3(filename='exp3_eats_addrs_from_umlaas.json')
async def test_4_0_zerosuggest_ml_zerosuggest_eats(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper, url,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_pickuppoints(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        ml_request = json.loads(request.get_data())
        assert ml_request == load_json('uml_zerosuggest_request_eats.json')
        return load_json('uml_zerosuggest_response_eats.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'b'
    request['state']['current_mode'] = 'eats'

    response = await taxi_persuggest.post(url, request, headers=PA_HEADERS)

    assert response.status_code == 200
    assert (
        persuggest_common.jsonify(response.json())
        == persuggest_common.jsonify(
            load_json('expected_response_ml_zerosuggest_eats.json'),
        )
    )


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.parametrize(
    'routehistory_response, not_empty',
    [
        pytest.param({'has_orders': False}, False, id='no_orders'),
        pytest.param({'has_orders': True}, True, id='orders_exist'),
    ],
)
@pytest.mark.experiments3(filename='exp3_drive_newbies_show_hint.json')
async def test_4_0_zerosuggest_ml_zerosuggest_drive(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps_wrapper,
        routehistory_response,
        not_empty,
        url,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response_basic.json')

    @mockserver.json_handler('/routehistory/routehistory/drive-has-orders')
    def _mock_drive_has_orders(request):
        return routehistory_response

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'b'
    request['state']['current_mode'] = 'drive'

    response = await taxi_persuggest.post(url, request, headers=PA_HEADERS)

    assert response.status_code == 200
    assert bool(response.json()['results']) is not_empty


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                PERSUGGEST_UMLAAS_GEO_SWITCH={
                    'enabled': True,
                    'zerosuggest_v1': False,
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                PERSUGGEST_UMLAAS_GEO_SWITCH={
                    'enabled': False,
                    'zerosuggest_v1': True,
                },
            ),
        ),
    ],
)
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_zerosuggest_ml_disabled(
        taxi_persuggest, mockserver, yamaps_wrapper, url,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        assert False

    response = await taxi_persuggest.post(
        url, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'restaurant_type': {
            'suggest': 'suggest_restaurant_tag',
            'shortcut': 'shortcuts_restaurant_tag',
        },
        'work_userplace_type': {
            'suggest': 'suggest_work_userplace_tag',
            'shortcut': 'shortcuts_work_userplace_tag',
        },
        'default_type': {
            'suggest': 'suggest_default_tag',
            'shortcut': 'shortcuts_default_tag',
        },
        'zero_default_type': {
            'suggest': 'suggest_zero_default_tag',
            'shortcut': 'shortcuts_zero_default_tag',
        },
        'railway_station_type': {
            'suggest': 'suggest_railway_tag',
            'shortcut': 'shortcut_railway_tag',
        },
    },
    ORG_RUBRIC_TO_IMAGE_TYPE={'restaurant': 'restaurant_type'},
    ZONE_TYPE_TO_IMAGE_TYPE={'railway_stations': 'railway_station_type'},
)
@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
        'work': {'ru': 'Работа'},
        'home': {'ru': 'Дом'},
    },
)
@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_suggest_icons_disabled.json')
async def test_4_0_zerosuggest_disabled_images(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper, url,
):
    headers = copy.deepcopy(PA_HEADERS)
    headers['X-YaTaxi-UserId'] = '0'

    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_pickuppoints(request):
        return {
            'results': [
                {
                    'zone_name': 'Kazansky vokzal',
                    'zone_type': 'railway_stations',
                    'point_name': 'main entrance',
                },
            ],
        }

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response.json')

    response = await taxi_persuggest.post(url, BASIC_REQUEST, headers=headers)
    assert response.status_code == 200
    data = await _logparse(response.json())
    response_json = await _logparse(
        load_json('expected_response_ml_zerosuggest_wo_images.json'),
    )
    assert data == response_json


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.config(LOG_SUGGESTED_TARIFFS_MATCHING_INFO=True)
@pytest.mark.translations(
    client_messages={
        'persuggest.uberkids_suggest_button_title': {
            'ru': 'Выбрать тариф $TARIFF$',
        },
        'go_to_work': {'ru': 'На работу'},
    },
)
@pytest.mark.experiments3(filename='exp3_suggested_tariffs_settings.json')
@pytest.mark.experiments3(
    filename='exp3_suggested_tariffs_matching_rules.json',
)
async def test_4_0_zerosuggest_add_suggested_tariff(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper, url,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_pickuppoints(request):
        return {
            'results': [
                {
                    'zone_name': 'Kazansky vokzal',
                    'zone_type': 'railway_stations',
                    'point_name': 'main entrance',
                },
            ],
        }

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response.json')

    response = await taxi_persuggest.post(
        url, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    data = await _logparse(response.json())
    assert data == await _logparse(
        load_json('expected_response_suggested_tariff.json'),
    )


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.translations(client_messages={'go_home': {'ru': 'Go home'}})
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_zerosuggest_userplace_stay(
        taxi_persuggest, mockserver, load_json, yamaps, experiments3, url,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='fix_entrances',
        consumers=['persuggest/zerosuggest'],
        clauses=[
            {
                'title': 'always',
                'value': {'enabled': True},
                'predicate': {'type': 'true'},
            },
        ],
        default_value=True,
    )

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response_userplace_stay.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        return []

    response = await taxi_persuggest.post(
        url, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response_userplace_stay.json')


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.translations(
    cargo_client_messages={
        'ndd.suggest.dropoff.title': {'ru': 'Пункт приема, %(city)s'},
    },
)
async def test_4_0_zerosuggest_delivery_ndd_point_a(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps_wrapper,
        url,
        experiments3,
):
    experiments3.add_experiment(**DELIVERY_NDD_EXP)

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/c2c/platform/pickup-points/list',
    )
    def _mock_lp(request):
        assert request.json == {
            'longitude': {'from': 36.95, 'to': 37.05},
            'latitude': {'from': 54.94, 'to': 55.06},
            'available_for_c2c_dropoff': True,
        }
        return load_json('default_logistic_platform_list_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['current_mode'] = 'delivery'
    request['state']['selected_class'] = 'ndd'
    request['type'] = 'a'
    response = await taxi_persuggest.post(url, request, headers=PA_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response_delivery_ndd_point_a.json')


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.translations(
    cargo_client_messages={
        'ndd.suggest.pickup.title': {'ru': 'Пункт выдачи, %(city)s'},
    },
)
async def test_4_0_zerosuggest_delivery_ndd_point_b(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps_wrapper,
        url,
        experiments3,
):
    experiments3.add_experiment(**DELIVERY_NDD_EXP)

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/c2c/platform/pickup-points/list',
    )
    def _mock_lp(request):
        assert request.json == {
            'longitude': {'from': 29.95, 'to': 30.05},
            'latitude': {'from': 49.94, 'to': 50.06},
        }
        return load_json('default_logistic_platform_list_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['current_mode'] = 'delivery'
    request['state']['selected_class'] = 'ndd'
    request['type'] = 'b'
    response = await taxi_persuggest.post(url, request, headers=PA_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('expected_response_delivery_ndd_point_b.json')


@pytest.mark.parametrize('url', URLS_TO_TEST)
@pytest.mark.parametrize(
    'routehistory_response, not_empty',
    [
        pytest.param({'has_orders': False}, False, id='no_orders'),
        pytest.param({'has_orders': True}, True, id='orders_exist'),
    ],
)
@pytest.mark.experiments3(filename='exp3_drive_newbies_show_hint.json')
async def test_4_0_zerosuggest_ml_tag_rules(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps_wrapper,
        routehistory_response,
        not_empty,
        url,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        tag_rules = json.loads(request.get_data())['tag_rules']
        assert tag_rules
        assert tag_rules[0]['name'] == 'call_center_ok'
        assert tag_rules[0]['min_relevance'] == 0.718
        return load_json('uml_zerosuggest_response_basic.json')

    @mockserver.json_handler('/routehistory/routehistory/drive-has-orders')
    def _mock_drive_has_orders(request):
        return routehistory_response

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'b'
    request['tag_rules'] = [{'name': 'call_center_ok', 'min_relevance': 0.718}]

    response = await taxi_persuggest.post(url, request, headers=PA_HEADERS)

    assert response.status_code == 200
