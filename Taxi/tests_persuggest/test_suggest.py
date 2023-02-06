import copy
import json

import pytest

EMPTY_RESPONSE = {'part': '', 'results': [], 'suggest_reqid': ''}


# Parse stringified json fields to avoid problems with
# keys order inside objects
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


def _mock_suggest_geo(mockserver):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return EMPTY_RESPONSE


URL = '/4.0/persuggest/v1/suggest'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Request-Application': 'app_name=android',
    'X-Request-Language': 'en',
}
MINIMAL_REQUEST = {
    'action': 'user_input',
    'state': {'location': [37.641531, 55.734718]},
    'type': 'a',
}

SUGGEST_SERPID = '848e45285064686ed852cf5452e4fccc'


async def test_suggest_response_proxy_no_uri(
        taxi_persuggest, mockserver, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        geo_response = load_json('georesponse_no_uri.json')
        return geo_response

    response = await taxi_persuggest.post(
        URL, MINIMAL_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    suggest_response = load_json('suggestresponse_no_uri.json')
    assert jsonify(response.json()) == jsonify(suggest_response)


@pytest.mark.parametrize(
    'phone_id,exprt',
    [('0', '100'), ('1', '200'), ('2', '200,100'), ('4', None)],
)
@pytest.mark.experiments3(filename='exp3_geosuggest.json')
@pytest.mark.experiments3(filename='exp3_geosuggest_experiments.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_suggest_exps(
        taxi_persuggest, mockserver, yamaps, load_json, phone_id, exprt,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        if exprt:
            assert request.args['exprt'] == exprt
            if exprt == '100':
                assert request.args['ptops_clf_formula'] == 'a'
                assert request.args['ptops_clf_threshold'] == 'b'
            if exprt == '200,100':
                assert request.args['ptops_clf_formula'] == 'c,a'
                assert request.args['ptops_clf_threshold'] == 'd,b'
                assert float(request.args['org_results_drop_rate']) == 0.5
                assert float(request.args['toponym_results_drop_rate']) == 0.3
        else:
            assert 'exprt' not in request.args
        geo_response = load_json('suggest_response.json')
        return geo_response

    yamaps.add_fmt_geo_object(
        load_json('yamaps_geo_objects.json')['geo_objects'][0],
    )

    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-YaTaxi-PhoneId'] = phone_id

    request = copy.deepcopy(MINIMAL_REQUEST)
    request['state']['current_mode'] = 'ultima'

    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    suggest_response = load_json('suggestresponse.json')
    assert jsonify(response.json()) == jsonify(suggest_response)


@pytest.mark.parametrize('error_code', [400, 404, 414])
async def test_suggest_400(taxi_persuggest, mockserver, error_code):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return mockserver.make_response('fail', status=error_code)

    response = await taxi_persuggest.post(
        URL, MINIMAL_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 400


async def test_suggest_metric_params(taxi_persuggest, mockserver):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    async def _mock_suggest_geo(request):
        assert 'suggest_serpid' in request.args
        assert request.args['suggest_serpid'] == SUGGEST_SERPID
        assert 'event_number' in request.args
        assert request.args['event_number'] == '12'
        return EMPTY_RESPONSE

    request = copy.deepcopy(MINIMAL_REQUEST)
    request['suggest_serpid'] = SUGGEST_SERPID
    request['event_number'] = 12

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='exp3_use_userplaces_in_suggest.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
    },
)
async def test_suggest_userplaces(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        geo_response = load_json('suggest_response.json')
        return geo_response

    yamaps.add_fmt_geo_object(
        load_json('yamaps_geo_objects.json')['geo_objects'][0],
    )

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return load_json('userplaces_response.json')

    request = copy.deepcopy(MINIMAL_REQUEST)
    request['part'] = 'петр'
    request['type'] = 'b'
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    suggest_response = load_json('suggestresponse_up_2.json')
    assert jsonify(response.json()) == jsonify(suggest_response)


@pytest.mark.experiments3(filename='exp3_use_userplaces_in_suggest.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
        'work': {'en': 'Work'},
        'home': {'en': 'Home'},
    },
)
async def test_suggest_userplaces_without_lev(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        geo_response = load_json('suggest_response_2.json')
        return geo_response

    yamaps.add_fmt_geo_object(
        load_json('yamaps_geo_objects.json')['geo_objects'][0],
    )

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return load_json('userplaces_response_2.json')

    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-Yandex-UID'] = 'no_lev'
    request = copy.deepcopy(MINIMAL_REQUEST)
    request['part'] = 'петр'
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    suggest_response = load_json('suggestresponse_up_3.json')
    assert jsonify(response.json()) == jsonify(suggest_response)


@pytest.mark.experiments3(filename='exp3_use_userplaces_in_suggest.json')
@pytest.mark.parametrize(
    'point_a', ['in_position', 'in_log_uri', 'in_log_uri_json', 'in_bbox'],
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_userplaces_distance_filter_for_b(
        taxi_persuggest, mockserver, yamaps, load_json, point_a,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        geo_response = load_json('suggest_response.json')
        return geo_response

    yamaps.add_fmt_geo_object(
        load_json('yamaps_geo_objects.json')['geo_objects'][0],
    )

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return load_json('userplaces_response_for_filter.json')

    request = copy.deepcopy(MINIMAL_REQUEST)
    request['part'] = 'петр'
    request['type'] = 'b'
    request['state'] = {}
    if point_a == 'in_position':
        fields = [{'type': 'a', 'position': [37.101, 55.101], 'log': ''}]
        request['state']['fields'] = fields
    elif point_a == 'in_log_uri':
        fields = [
            {
                'type': 'a',
                'log': 'ymapsbm1://geo?ll=37.101%2C55.101&spn=0%2C0',
            },
        ]
        request['state']['fields'] = fields
    elif point_a == 'in_log_uri_json':
        fields = [
            {
                'type': 'a',
                'log': (
                    '{\"uri\":\"ymapsbm1://geo?ll=37.101%2C55.101&spn=0%2C0\"}'
                ),
            },
        ]
        request['state']['fields'] = fields
    elif point_a == 'in_bbox':
        bbox = [37.1, 55.1, 37.102, 55.102]
        request['state']['bbox'] = bbox

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    suggest_response = load_json('suggestresponse_up.json')
    assert jsonify(response.json()) == jsonify(suggest_response)


@pytest.mark.config(
    MODES=[
        {
            'mode': 'sdc',
            'experiment': 'enable_sdc_2',
            'zone_activation': {'zone_type': 'sdc', 'point_title': ''},
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_enable_sdc_2.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_suggest_sdc(
        taxi_persuggest, mockserver, yamaps_wrapper, load_json,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_for_test_in_sdc.json')

    request = {
        'action': 'user_input',
        'type': 'a',
        'part': 'krasno',
        'state': {'current_mode': 'sdc', 'bbox': [37, 55, 38, 56]},
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    suggest_response = load_json('suggestresponse_sdc.json')
    assert jsonify(response.json()) == jsonify(suggest_response)


@pytest.mark.config(
    MODES=[
        {
            'mode': 'sdc',
            'experiment': 'enable_sdc_2',
            'zone_activation': {'zone_type': 'sdc', 'point_title': ''},
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_enable_sdc_2.json')
@pytest.mark.experiments3(filename='exp3_sdc_suggest_geo_addresses.json')
@pytest.mark.now('2020-01-24T10:00:00+0300')
async def test_suggest_sdc_with_suggests(
        taxi_persuggest, mockserver, yamaps_wrapper, load_json,
):
    geopoint = [37.111, 55.111]

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return load_json('sdc_suggest_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        assert request.json['geopoint'] == geopoint
        return load_json('zones_for_test_in_sdc.json')

    request = {
        'action': 'user_input',
        'type': 'a',
        'part': 'krasno',
        'state': {
            'current_mode': 'sdc',
            'bbox': [37, 55, 38, 56],
            'fields': [
                {
                    'type': 'a',
                    'log': (
                        '{\"uri\":\"ymapsbm1://geo?ll='
                        '37.101%2C55.101&spn=0%2C0\"}'
                    ),
                    'position': geopoint,
                },
            ],
        },
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    suggest_response = load_json('response_sdc_with_suggest.json')
    assert jsonify(response.json()) == jsonify(suggest_response)


@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            'suggest_eats_response.json',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_remove_non_house_objects_enabled.json',
                ),
            ],
        ),
        pytest.param(
            'suggest_eats_response_without_remove.json',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_remove_non_house_objects_disabled.json',
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    PERSUGGEST_MODE_TO_CLIENT_ID={
        '__default__': 'taxi',
        'eats': 'eats',
        'grocery': 'grocery',
    },
)
async def test_suggest_eats(
        taxi_persuggest, mockserver, yamaps, load_json, expected_response,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.args == load_json('geosuggest_eats_request.json')
        return load_json('geosuggest_eats_response.json')

    yamaps.add_fmt_geo_object(
        load_json('yamaps_geo_objects.json')['geo_objects'][0],
    )

    response = await taxi_persuggest.post(
        URL,
        load_json('suggest_eats_request.json'),
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    assert jsonify(response.json()) == jsonify(load_json(expected_response))


async def test_suggest_user_select(taxi_persuggest, mockserver, load_json):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest(request):
        assert request.args == load_json('georequest_user_select.json')
        return {'part': '', 'results': [], 'suggest_reqid': ''}

    response = await taxi_persuggest.post(
        URL, load_json('request_user_select.json'), headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200


async def test_suggest_lang(taxi_persuggest, mockserver):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.args['lang'] == 'en'
        return EMPTY_RESPONSE

    response = await taxi_persuggest.post(
        URL, MINIMAL_REQUEST, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200, response.text


async def test_suggest_favorite(taxi_persuggest, mockserver, load_json):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.args == load_json('georequest_favorite.json')
        return EMPTY_RESPONSE

    response = await taxi_persuggest.post(
        URL, load_json('request_favorite.json'), headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'mapkit_lang_region, geo_suggest_lang',
    [('iw_IL', 'en_IL'), ('he_RU', 'en_RU')],
)
async def test_suggest_lang_country(
        taxi_persuggest,
        mockserver,
        mapkit_lang_region,
        geo_suggest_lang,
        load_json,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.args['lang'] == geo_suggest_lang
        return EMPTY_RESPONSE

    # Required parameters
    request = {
        'action': 'user_input',
        'part': 'pres',
        'type': 'a',
        'state': {
            'bbox': [30.0, 50.0, 40.0, 60.0],
            'l10n': {'mapkit_lang_region': mapkit_lang_region},
        },
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200


async def test_suggest_wrong_bbox(taxi_persuggest, mockserver, load_json):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.args['bbox'] == '179,-90,-179,90'
        return EMPTY_RESPONSE

    # Required parameters
    request = {
        'action': 'user_input',
        'part': 'pres',
        'type': 'a',
        'state': {'bbox': [-181, -180, 181, 180]},
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
