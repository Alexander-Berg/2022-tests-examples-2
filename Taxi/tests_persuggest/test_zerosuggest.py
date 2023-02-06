import copy
import json

import pytest

# pylint: disable=import-only-modules
from tests_persuggest.persuggest_common import jsonify

URL = '/4.0/persuggest/v1/zerosuggest'
DEFAULT_APPLICATION = 'app_name=android,app_ver1=3,app_ver2=18,app_ver3=0'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
}

BASIC_REQUEST = {'state': {}, 'position': [37, 55], 'type': 'b'}


@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.parametrize('mid', ['mid', 'mid1', 'mid99'])
async def test_zerosuggest_mid_point(
        taxi_persuggest, mockserver, load_json, mid, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        expected_ml_request = load_json('ml_zerosuggest_request.json')
        expected_ml_request['type'] = 'mid'
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('ml_zerosuggest_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = mid
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert jsonify(data) == load_json('expected_response.json')


@pytest.mark.config(
    MODES=[
        {
            'mode': 'sdc',
            'experiment': 'enable_sdc_2',
            'zone_activation': {'zone_type': 'sdc', 'point_title': ''},
        },
    ],
)
@pytest.mark.experiments3(filename='exp3_enable_sdc_2.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_zerosuggest_sdc(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['current_mode'] = 'sdc'
    request['position'] = [37.400000, 55.400000]
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert jsonify(data) == load_json('expected_response_sdc.json')


@pytest.mark.config(
    MODES=[
        {
            'mode': 'sdc',
            'experiment': 'enable_sdc_2',
            'zone_activation': {'zone_type': 'sdc', 'point_title': ''},
        },
    ],
)
@pytest.mark.experiments3(filename='exp3_sdc_suggest_geo_addresses.json')
@pytest.mark.experiments3(filename='exp3_enable_sdc_2.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_zerosuggest_sdc_with_suggests(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('ml_sdc_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_sdc_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['current_mode'] = 'sdc'
    request['position'] = [37.400000, 55.400000]
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert _mock_umlaas_geo.times_called == 1
    assert jsonify(data) == load_json('expected_response_sdc_suggests.json')


@pytest.mark.experiments3(filename='exp3_filter_eda_zerosuggest.json')
@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.parametrize(
    'phone_id,expected',
    [
        ('no_filters', 'expected_response_eats.json'),
        ('with_filters', 'expected_response_eats_with_filters.json'),
        (
            'with_filters_umlaas_first',
            'expected_response_eats_umlaas_first.json',
        ),
        ('no_exp', 'expected_response_eats.json'),
    ],
)
async def test_zerosuggest_eats(
        taxi_persuggest,
        mockserver,
        load_json,
        phone_id,
        expected,
        yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        expected_ml_request = load_json('ml_zerosuggest_request.json')
        expected_ml_request['type'] = 'a'
        expected_ml_request['state']['current_mode'] = 'eats'
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('ml_zerosuggest_response.json')

    @mockserver.json_handler('/routehistory/routehistory/grocery-get')
    def _mock_routehistory(request):
        return load_json('routehistory_grocery_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['current_mode'] = 'eats'

    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-PhoneId'] = phone_id
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    assert jsonify(response.json()) == load_json(expected)


@pytest.mark.now('2017-01-24T10:00:00+0300')
@pytest.mark.experiments3(
    filename='exp3_remove_non_house_objects_disabled.json',
)
async def test_zerosuggest_eats_no_rm_non_houses(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        expected_ml_request = load_json('ml_zerosuggest_request.json')
        expected_ml_request['type'] = 'a'
        expected_ml_request['state']['current_mode'] = 'eats'
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('ml_zerosuggest_response.json')

    @mockserver.json_handler('/routehistory/routehistory/grocery-get')
    def _mock_routehistory(request):
        return load_json('routehistory_grocery_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['current_mode'] = 'eats'

    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    expected_response = load_json('expected_response_eats_without_remove.json')
    assert jsonify(data) == expected_response


@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_zerosuggest_new_clients(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        expected_ml_request = load_json('ml_zerosuggest_request_new.json')
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('ml_zerosuggest_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['fields'] = [
        {'type': 'a', 'position': [10.1234, 11.1234], 'log': '{}'},
        {'type': 'b', 'position': [12.1234, 13.1234], 'log': '{}'},
    ]
    request['state']['coord_providers'] = [
        {'type': 'gps', 'position': [14.1234, 15.1234], 'accuracy': 10.3},
        {
            'type': 'platform_lbs',
            'position': [16.1234, 17.1234],
            'accuracy': 4.2,
        },
    ]
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert jsonify(response.json()) == load_json(
        'expected_response_ml_zerosuggest.json',
    )


@pytest.mark.experiments3(filename='exp3_short_text_formatting.json')
@pytest.mark.translations(
    client_messages={'suggest.append.entrance': {'ru': 'подъезд'}},
    tariff={
        'detailed.kilometer': {'ru': '%(value).0f км'},
        'round.hundreds_meters': {'ru': '%(value).0f м'},
        'round.tens_meters': {'ru': '%(value).0f м'},
        'round.kilometers': {'ru': '%(value).0f км'},
    },
)
@pytest.mark.experiments3(
    filename='exp3_entrances_list_in_suggest_with_ml.json',
)
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_zerosuggest_with_entrances(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('ml_zerosuggest_response_entrances.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'a'
    request['state']['fields'] = [
        {
            'type': 'a',
            'position': [37.400001, 55.400001],
            'log': 'ymapsbm1://URI_10_10',
        },
        {'type': 'b', 'position': [12.1234, 13.1234], 'log': '{}'},
    ]
    request['state']['coord_providers'] = [
        {'type': 'gps', 'position': [14.1234, 15.1234], 'accuracy': 10.3},
        {
            'type': 'platform_lbs',
            'position': [16.1234, 17.1234],
            'accuracy': 4.2,
        },
    ]
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert jsonify(response.json()) == load_json(
        'expected_response_ml_zerosuggest_with_entrances.json',
    )


@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_zerosuggest_with_pp(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        assert sorted(data['uris']) == [
            'ytpp://Luzhniki/point1',
            'ytpp://SVO/Terminal D',
        ]
        results = load_json('zones_localize_response.json')['responses'][1][
            'results'
        ]
        results.extend(
            load_json('zones_localize_response.json')['responses'][0][
                'results'
            ],
        )
        return {'results': results}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('ml_zerosuggest_response_with_pp.json')

    @mockserver.json_handler('/pickup-points-manager/v1/points/find')
    def _mock_ppmanager(request):
        return mockserver.make_response(status=404)

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'a'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert jsonify(response.json()) == load_json(
        'expected_response_ml_zerosuggest_with_pp.json',
    )


@pytest.mark.experiments3(filename='exp3_drop_point_name_in_zero_suggest.json')
@pytest.mark.now('2024-01-24T10:00:00+0300')
async def test_zerosuggest_drop_point_name(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        assert sorted(data['uris']) == [
            'ytpp://Luzhniki/point1',
            'ytpp://SVO/Terminal D',
        ]
        results = load_json('zones_localize_response.json')['responses'][1][
            'results'
        ]
        results.extend(
            load_json('zones_localize_response.json')['responses'][0][
                'results'
            ],
        )
        return {'results': results}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('ml_zerosuggest_response_with_pp.json')

    @mockserver.json_handler('/pickup-points-manager/v1/points/find')
    def _mock_ppmanager(request):
        return mockserver.make_response(status=404)

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'b'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert jsonify(response.json()) == load_json(
        'expected_response_ml_zerosuggest_with_pp_dropped.json',
    )


@pytest.mark.experiments3(filename='exp3_short_text_formatting.json')
@pytest.mark.translations(
    client_messages={'suggest.append.entrance': {'ru': 'подъезд'}},
    tariff={
        'detailed.kilometer': {'ru': '%(value).0f км'},
        'round.hundreds_meters': {'ru': '%(value).0f м'},
        'round.tens_meters': {'ru': '%(value).0f м'},
        'round.kilometers': {'ru': '%(value).0f км'},
    },
)
@pytest.mark.experiments3(
    filename='exp3_entrances_list_in_suggest_with_ml.json',
)
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_zerosuggest_location_not_ready(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    position_bad = [0, 56.0]
    position_close = [33.0, 56.0]
    position_far = [89.0, 89.0]
    request = {
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [
                {
                    'type': 'a',
                    'position': position_far,
                    'log': 'ymapsbm1://URI_10_10',
                },
                {'type': 'b', 'position': position_far, 'log': '{}'},
            ],
            'location': position_far,
            'coord_providers': [
                {'type': 'gps', 'position': position_far, 'accuracy': 10.3},
                {
                    'type': 'platform_lbs',
                    'position': position_far,
                    'accuracy': 4.2,
                },
            ],
            'app_metrica': {'uuid': 'UUID', 'device_id': 'DeviceId'},
        },
        'position': position_far,
        'type': 'a',
    }

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        data = json.loads(request.get_data())
        assert data['state']['location'] == position_close
        return load_json('ml_zerosuggest_response_entrances.json')

    async def check():
        response = await taxi_persuggest.post(
            URL, request, headers=AUTHORIZED_HEADERS,
        )
        assert response.status_code == 200

    # for this logic to make some sense,
    # pls see TAXIBACKEND-34843 and TAXIBACKEND-26627

    # all coordinates are valid, use ull from state.location
    request['state']['location'] = position_close
    await check()

    # state.location is not ready, use best coord_provider
    request['state']['location'] = position_bad
    best_coord_provider = sorted(
        request['state']['coord_providers'], key=lambda cp: cp['accuracy'],
    )[0]
    best_coord_provider['position'] = position_close
    await check()

    # coord_providers are not ready, use bbox
    for coord_provider in request['state']['coord_providers']:
        coord_provider['position'] = position_bad
    request['state']['bbox'] = [
        position_close[0] - 1,
        position_close[1] - 1,
        position_close[0] + 1,
        position_close[1] + 1,
    ]
    await check()


async def test_zerosuggest_with_point_extra_data(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('ml_zerosuggest_response_2door.json')

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        return load_json('userplaces_item_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert jsonify(data) == load_json('expected_response_2door.json')


@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_zerosuggest_with_pp_title(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        assert sorted(data['uris']) == [
            'ytpp://Luzhniki/point1',
            'ytpp://SVO/Terminal D',
        ]
        results = load_json('zones_localize_response.json')['responses'][1][
            'results'
        ]
        results.extend(
            load_json('zones_localize_response.json')['responses'][0][
                'results'
            ],
        )
        return {'results': results}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('ml_zerosuggest_response_with_pp_title.json')

    @mockserver.json_handler('/pickup-points-manager/v1/points/find')
    def _mock_ppmanager(request):
        resp_json = load_json('pickup_points_manager_points_find_title.json')[
            'results'
        ]
        uri = request.query['uri']
        if uri == 'ytmpp://lon=59.950272,lat=10.815241':
            return resp_json[0]
        if uri == 'ytmpp://lon=59.950273,lat=10.815242':
            return resp_json[1]
        return mockserver.make_response(status=404)

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'a'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert jsonify(response.json()) == load_json(
        'expected_response_ml_zerosuggest_with_pp_title.json',
    )


@pytest.mark.now('2022-01-24T10:00:00+0300')
@pytest.mark.translations(
    client_messages={
        'userplaces.suggest.short_text_rides_count': {
            'ru': '%(rides_count)s раз',
        },
        'userplaces.suggest.short_text_weeks_count': {
            'ru': ' за %(weeks_count)s недели',
        },
        'userplaces.suggest.full_text': {
            'ru': 'Вы были здесь уже %(rides_count)s раз',
        },
    },
)
async def test_zerosuggest_userplace_suggestion(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        assert sorted(data['uris']) == [
            'ytpp://Luzhniki/point1',
            'ytpp://SVO/Terminal D',
        ]
        results = load_json('zones_localize_response.json')['responses'][1][
            'results'
        ]
        results.extend(
            load_json('zones_localize_response.json')['responses'][0][
                'results'
            ],
        )
        return {'results': results}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('ml_zerosuggest_response_userplace_suggestion.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'b'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert jsonify(response.json()) == load_json(
        'expected_response_userplace_suggestion.json',
    )


@pytest.mark.now('2022-01-24T10:00:00+0300')
@pytest.mark.translations(
    client_messages={
        'userplaces.suggest.short_text_rides_count': {
            'ru': '%(rides_count)s раз',
        },
        'userplaces.suggest.short_text_weeks_count': {
            'ru': ' за %(weeks_count)s недели',
        },
        'userplaces.suggest.full_text': {
            'ru': 'Вы были здесь уже %(rides_count)s раз',
        },
    },
)
async def test_zerosuggest_reveal_relevance(
        taxi_persuggest, mockserver, load_json, yamaps_wrapper,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        assert sorted(data['uris']) == [
            'ytpp://Luzhniki/point1',
            'ytpp://SVO/Terminal D',
        ]
        results = load_json('zones_localize_response.json')['responses'][1][
            'results'
        ]
        results.extend(
            load_json('zones_localize_response.json')['responses'][0][
                'results'
            ],
        )
        return {'results': results}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('ml_zerosuggest_response_reveal_relevance.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['type'] = 'b'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert jsonify(response.json()) == load_json(
        'expected_response_reveal_relevance.json',
    )
