import copy
import json

import pytest

URL = '4.0/persuggest/v1/suggest'

PA_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-YaTaxi-Pass-Flags': 'phonish',
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
    'X-Ya-User-Ticket': 'user_ticket',
}

PA_HEADERS_NO_AUTH = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
}

YAMAPS_ADDRESS = [
    {
        'geocoder': {
            'address': {
                'formatted_address': 'Russia, Moscow, Petrovskiy alley, 21',
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'id': '1',
        },
        'uri': 'ymapsbm1://URI_1_1',
        'name': 'Petrovskiy alley, 21',
        'description': 'Russia, Moscow',
        'geometry': [37.1, 55.1],
    },
    {
        'geocoder': {
            'address': {
                'formatted_address': 'Russia, Kursk, Levoberezhnaya alley, 2',
                'country': 'Russia',
                'locality': 'Kursk',
                'street': 'Levoberezhnaya alley',
                'house': '2',
            },
        },
        'arrival_points': [
            {'point': [37, 55], 'name': 'F2'},
            {'point': [37.0001, 55.0001], 'name': 'F3'},
        ],
        'uri': 'ymapsbm1://URI_2_2',
        'name': 'Levoberezhnaya alley, 2',
        'description': 'Kursk, Russia',
        'geometry': [36.192653, 51.730366],
    },
    {
        'geocoder': {
            'address': {
                'formatted_address': 'Russia, Moscow, Petrovskiy alley, 21',
                'country': 'Russia',
                'locality': 'Moscow',
                'entrance': '1',
                'level': 'level 2',
                'apartment': 'apt 3',
            },
            'id': '1',
        },
        'uri': 'ymapsbm1://URI_1_1',
        'name': 'Petrovskiy alley, 21',
        'description': 'Russia, Moscow',
        'geometry': [37.1, 55.1],
    },
]

DELIVERY_NDD_EXP = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'enable_delivery_ndd_zone',
    'consumers': ['persuggest/suggest'],
    'clauses': [
        {
            'title': 'always',
            'value': {
                'enabled': True,
                'suggest': {
                    'limit': 8,
                    'point_b_allowed_zones': ['moscow'],
                    'min_street_levenstein_distanse': 5,
                    'search_rectangle_around_address': {
                        'latitude_interval': 0.02,
                        'longitude_interval': 0.02,
                    },
                },
            },
            'predicate': {'type': 'true'},
        },
    ],
    'default_value': True,
}


def jsonify(obj):
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


@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'railway_type': {
            'suggest': 'suggest_railway_tag',
            'shortcut': 'shortcut_railway_tag',
        },
        'default_type': {
            'suggest': 'suggest_default_tag',
            'shortcut': 'shortcut_default_tag',
        },
    },
    SUGGEST_GEO_TAG_TO_IMAGE_TYPE={
        'railway': 'railway_type',
        'other': 'default_type',
    },
)
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
@pytest.mark.experiments3(filename='exp3_add_method_to_log.json')
async def test_4_0_suggest_basic(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request.json')
        return load_json('suggest_geo_response.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS[0])

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response.json')
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.experiments3(filename='exp3_add_method_to_log.json')
async def test_4_0_suggest_basic_google(
        taxi_persuggest, mockserver, yamaps, load_json, experiments3,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='use_google_geocoder',
        consumers=['persuggest/suggest'],
        clauses=[
            {
                'title': 'always',
                'value': {'enabled': True},
                'predicate': {'type': 'true'},
            },
        ],
        default_value=True,
    )

    @mockserver.json_handler('/api-proxy-external-geo/google/suggest-geo')
    def _mock_suggest_google(request):
        return load_json('suggest_google_response.json')

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_google_response.json')
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.experiments3(filename='exp3_add_method_to_log.json')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='yamaps_over_osm_geosuggest_settings',
    consumers=['persuggest/suggest'],
    clauses=[
        {
            'title': 'always',
            'value': {
                'enabled': True,
                'osm_vertical': 'only',
                'enable_osm_toponyms': True,
            },
            'predicate': {'type': 'true'},
        },
    ],
    default_value=True,
)
async def test_4_0_suggest_yamaps_over_osm(
        taxi_persuggest, mockserver, yamaps, load_json, experiments3,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args['osm_vertical'] == 'only'
        assert request.args['enable_osm_toponyms'] == '1'
        return load_json('suggest_geo_response.json')

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_suggest_geo.times_called == 1


@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'map_search_image_type': {
            'suggest': 'suggest_map_search_tag',
            'shortcut': 'shortcut_map_search_tag',
        },
        'default_type': {
            'suggest': 'suggest_default_tag',
            'shortcut': 'shortcut_default_tag',
        },
    },
)
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
@pytest.mark.experiments3(filename='exp3_suggest_chains.json')
async def test_4_0_suggest_chains(taxi_persuggest, mockserver, load_json):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert dict(request.args) == load_json(
            'suggest_geo_request_chains.json',
        )
        return load_json('suggest_geo_response_chains.json')

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_chains.json')
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'railway_type': {'suggest': 'suggest_railway_tag'},
        'default_type': {'suggest': 'suggest_default_tag'},
    },
    SUGGEST_GEO_TAG_TO_IMAGE_TYPE={
        'railway': 'railway_type',
        'other': 'default_type',
    },
)
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
@pytest.mark.experiments3(filename='exp3_add_method_to_log.json')
async def test_4_0_suggest_no_auth(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert 'X-Ya-User-Ticket' not in request.headers
        assert request.args == load_json('suggest_geo_request_no_auth.json')
        return load_json('suggest_geo_response.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS[0])

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS_NO_AUTH,
    )
    assert response.status_code == 200
    expected = load_json('expected_response.json')
    assert jsonify(response.json()) == jsonify(expected)


async def test_4_0_suggest_bad_position(taxi_persuggest, load_json):
    request = load_json('request.json')
    request['state']['location'] = [0, 91]
    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 400


@pytest.mark.experiments3(filename='exp3_entrances_list_in_suggest.json')
@pytest.mark.translations(
    client_messages={'suggest.append.entrance': {'ru': 'подъезд'}},
    tariff={
        'detailed.kilometer': {'ru': '%(value).0f км'},
        'round.hundreds_meters': {'ru': '%(value).0f м'},
        'round.tens_meters': {'ru': '%(value).0f м'},
        'round.kilometers': {'ru': '%(value).0f км'},
    },
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_4_0_suggest_with_entrances(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request.json')
        return load_json('suggest_geo_response_2.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS[1])

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_2.json')
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.experiments3(filename='exp3_entrances_list_in_suggest.json')
@pytest.mark.translations(
    client_messages={'suggest.append.entrance': {'ru': 'подъезд'}},
    tariff={
        'detailed.kilometer': {'ru': '%(value).0f км'},
        'round.hundreds_meters': {'ru': '%(value).0f м'},
        'round.tens_meters': {'ru': '%(value).0f м'},
        'round.kilometers': {'ru': '%(value).0f км'},
    },
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_4_0_suggest_with_empty_entrances(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request.json')
        return load_json('suggest_geo_response_2.json')

    geo_object = copy.deepcopy(YAMAPS_ADDRESS[1])
    geo_object.pop('arrival_points')
    yamaps.add_fmt_geo_object(geo_object)

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_2.json')
    expected['results'][0]['entrances_info']['suggested_entrances'] = []
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.experiments3(filename='exp3_entrances_list_in_suggest.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_4_0_suggest_without_entrances(
        taxi_persuggest, mockserver, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request.json')
        resp = load_json('suggest_geo_response_2.json')
        resp['results'][0]['entrance'] = '7'
        return resp

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_2.json')
    expected['results'][0].pop('entrances_info')
    expected['results'][0]['entrance'] = '7'
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.experiments3(filename='exp3_add_geosearch_to_suggest.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_4_0_suggest_with_geosearch(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    request = load_json('request.json')
    request_field = request['state']['fields'][0]

    expected_geosuggest_args = load_json('suggest_geo_request.json')
    expected_geosuggest_args[
        'suggest_experimental'
    ] = 'ranking_formula=new_shiny_ranking'

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert dict(request.args) == expected_geosuggest_args
        return load_json('suggest_geo_response_2.json')

    yamaps.set_fmt_geo_objects(
        load_json('yamaps_response_geosearch.json')['geo_objects'],
    )

    async def check():
        response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)
        assert response.status_code == 200
        expected = load_json('expected_response_with_geosearch.json')
        assert jsonify(response.json()) == jsonify(expected)

    await check()

    # https://github.yandex-team.ru/taxi/uservices/pull/31599
    # field position and log are not set
    del request_field['position']
    del request_field['log']
    del expected_geosuggest_args['pointb']
    del expected_geosuggest_args['entranceb']

    await check()


@pytest.mark.config(SUGGEST_MAX_BBOX_SIZE_M=1000)
async def test_4_0_suggest_normilize_bbox(
        taxi_persuggest, mockserver, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert (
            request.args['bbox'] == '37.09444889,55.09682396,'
            '37.10555111,55.10317604'
        )
        assert request.args['order_type'] == 'eats'
        assert request.args['point_type'] == 'a'
        assert request.args['ull'] == '37.1000000000,55.1000000000'
        return load_json('suggest_geo_response.json')

    request = load_json('request.json')
    request['state']['bbox'] = [
        16.875,
        -68.31872153058742,
        163.125,
        85.0840588829382,
    ]
    request['state']['current_mode'] = 'eats'
    request['state']['location'] = [37.1, 55.1]

    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200


@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'railway_type': {
            'suggest': 'suggest_railway_tag',
            'shortcut': 'shortcut_railway_tag',
        },
        'default_type': {
            'suggest': 'suggest_default_tag',
            'shortcut': 'shortcut_default_tag',
        },
    },
    SUGGEST_GEO_TAG_TO_IMAGE_TYPE={
        'railway': 'railway_type',
        'other': 'default_type',
    },
)
@pytest.mark.experiments3(filename='exp3_suggest_icons_disabled.json')
async def test_4_0_suggest_disabled_images(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request.json')
        return load_json('suggest_geo_response.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS[0])

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_wo_images.json')
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.config(LOG_SUGGESTED_TARIFFS_MATCHING_INFO=True)
@pytest.mark.translations(
    client_messages={
        'persuggest.uberkids_suggest_button_title': {
            'ru': 'Выбрать тариф $TARIFF$',
        },
    },
)
@pytest.mark.experiments3(filename='exp3_suggested_tariffs_settings.json')
@pytest.mark.experiments3(
    filename='exp3_suggested_tariffs_matching_rules.json',
)
async def test_4_0_suggest_add_suggested_tariff(
        taxi_persuggest, mockserver, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request.json')
        return load_json('suggest_geo_response.json')

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_suggested_tariff.json')
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.config(LOG_SUGGESTED_TARIFFS_MATCHING_INFO=True)
@pytest.mark.translations(
    client_messages={
        'persuggest.uberkids_suggest_button_title': {
            'ru': 'Выбрать тариф $TARIFF$',
        },
    },
)
@pytest.mark.experiments3(filename='exp3_suggested_tariffs_settings.json')
@pytest.mark.experiments3(
    filename='exp3_suggested_tariffs_matching_rules.json',
)
@pytest.mark.experiments3(filename='exp3_suggest_search_by_coords.json')
async def test_4_0_suggest_search_by_coords(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request_coords.json')
        return load_json('suggest_geo_response.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS[0])
    response = await taxi_persuggest.post(
        URL, load_json('request_coords.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_coords.json')
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.parametrize('suggest_point_type', ['a', 'b'])
async def test_4_0_suggest_location_not_ready(
        taxi_persuggest, mockserver, yamaps, load_json, suggest_point_type,
):
    request_body = load_json('request.json')
    expected_geo_request = load_json('suggest_geo_request.json')

    request_body['type'] = suggest_point_type
    expected_geo_request['point_type'] = suggest_point_type

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert dict(request.args.items()) == expected_geo_request
        return load_json('suggest_geo_response.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS[0])

    async def check():
        response = await taxi_persuggest.post(
            URL, request_body, headers=PA_HEADERS,
        )
        assert response.status_code == 200

    def format_coords(coords):
        return ','.join('{:.10f}'.format(c) for c in coords)

    def mean(*nums):
        return sum(nums) / len(nums)

    # all coordinates are valid, use the position as it is
    await check()

    # state.location is not ready, use best coord_provider
    request_body['state']['location'][0] = 0
    best_coords = sorted(
        request_body['state']['coord_providers'],
        key=lambda cp: cp['accuracy'],
    )[0]['position']
    expected_geo_request['ull'] = format_coords(best_coords)

    await check()

    # no coord_providers, use bbox
    request_body['state'].pop('coord_providers')
    bbox = request_body['state']['bbox']
    bbox_center = [mean(bbox[0], bbox[2]), mean(bbox[1], bbox[3])]
    expected_geo_request['ull'] = format_coords(bbox_center)

    await check()


@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'railway_type': {
            'suggest': 'suggest_railway_tag',
            'shortcut': 'shortcut_railway_tag',
        },
        'default_type': {
            'suggest': 'suggest_default_tag',
            'shortcut': 'shortcut_default_tag',
        },
    },
    SUGGEST_GEO_TAG_TO_IMAGE_TYPE={
        'railway': 'railway_type',
        'other': 'default_type',
    },
)
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
@pytest.mark.experiments3(filename='exp3_add_method_to_log.json')
@pytest.mark.experiments3(filename='exp3_persuggest_process_flat.json')
@pytest.mark.translations(
    client_messages={
        'suggest.append.entrance': {'ru': 'подъезд'},
        'flat_tanker_key': {'ru': 'apt'},
        'level_tanker_key': {'ru': 'level'},
    },
)
async def test_4_0_suggest_with_flat(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == load_json('suggest_geo_request.json')
        return load_json('suggest_geo_response.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS[2])

    response = await taxi_persuggest.post(
        URL, load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    expected = load_json('expected_response_with_flat.json')
    assert jsonify(response.json()) == jsonify(expected)


@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'railway_type': {
            'suggest': 'suggest_railway_tag',
            'shortcut': 'shortcut_railway_tag',
        },
        'default_type': {
            'suggest': 'suggest_default_tag',
            'shortcut': 'shortcut_default_tag',
        },
    },
    SUGGEST_GEO_TAG_TO_IMAGE_TYPE={
        'railway': 'railway_type',
        'other': 'default_type',
    },
)
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
@pytest.mark.experiments3(filename='exp3_add_method_to_log.json')
@pytest.mark.experiments3(filename='exp3_persuggest_filter_by_geo.json')
async def test_4_0_suggest_filter_by_geo(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return load_json('suggest_geo_response.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS[2])

    request = load_json('request.json')
    request['state'] = {'location': [8.608724, 50.157442]}

    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)

    assert response.status_code == 200
    assert not response.json()['results']


@pytest.mark.translations(client_messages={'key': {'ru': 'Blue'}})
@pytest.mark.experiments3(filename='exp3_title_adder.json')
async def test_4_0_suggest_change_title(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return load_json('suggest_geo_response.json')

    request = load_json('request.json')

    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)

    assert response.status_code == 200
    title = {'text': 'Blue', 'hl': []}
    assert response.json()['results'][1]['title'] == title


@pytest.mark.translations(client_messages={'key': {'ru': 'Blue'}})
@pytest.mark.translations(
    cargo_client_messages={
        'ndd.suggest.dropoff.title': {'ru': 'Пункт приема, %(city)s'},
    },
)
async def test_4_0_suggest_delivery_ndd_point_a(
        taxi_persuggest, mockserver, yamaps, load_json, experiments3,
):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/c2c/platform/pickup-points/list',
    )
    def _mock_lp(request):
        return load_json('default_logistic_platform_list_response.json')

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return load_json('suggest_geo_delivery_ndd_reponse.json')

    experiments3.add_experiment(**DELIVERY_NDD_EXP)

    request = load_json('request.json')
    request['state']['current_mode'] = 'delivery'
    request['state']['selected_class'] = 'ndd'
    request['type'] = 'a'
    request['part'] = 'Хорошевс'
    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)

    assert response.status_code == 200
    assert response.json() == load_json(
        'delivery_ndd_point_a_expected_response.json',
    )


@pytest.mark.translations(client_messages={'key': {'ru': 'Blue'}})
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.translations(
    cargo_client_messages={
        'ndd.suggest.pickup.title': {'ru': 'Пункт выдачи, %(city)s'},
    },
)
async def test_4_0_suggest_delivery_ndd_point_b(
        taxi_persuggest, mockserver, yamaps, load_json, experiments3,
):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/c2c/platform/pickup-points/list',
    )
    def _mock_lp(request):
        return load_json('default_logistic_platform_list_response.json')

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return load_json('suggest_geo_delivery_ndd_reponse.json')

    experiments3.add_experiment(**DELIVERY_NDD_EXP)

    request = load_json('request.json')
    request['state']['current_mode'] = 'delivery'
    request['state']['selected_class'] = 'ndd'
    request['type'] = 'b'
    request['part'] = 'Хорошевс'
    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)

    assert response.status_code == 200
    assert response.json() == load_json(
        'delivery_ndd_point_b_expected_response.json',
    )
