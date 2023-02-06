import copy

import pytest

from tests_persuggest import persuggest_common

URL = '/4.0/persuggest/v1/finalsuggest'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Request-Application': 'app_name=iphone',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '10.10.10.10',
}

USERPLACE_PREVLOG = (
    '{"type":"userplace","userplace_id":'
    '"00000004-AAAA-AAAA-AAAA-000000000001"}'
)


@pytest.mark.config(EDA_CATALOG_POLYGONS_CACHE_ENABLED=True)
@pytest.mark.experiments3(filename='exp3_show_eda_zones.json')
@pytest.mark.experiments3(filename='exp3_use_bbox_position.json')
@pytest.mark.parametrize(
    'mode,sticky,expected_ans',
    [
        pytest.param('eats', True, 'pin_drop_expected_ans.json', id='eats'),
        pytest.param(
            'grocery', False, 'pin_drop_expected_ans_groc.json', id='grocery',
        ),
    ],
)
@pytest.mark.parametrize('input_position', [[37.0, 55.0], [-1.83, 51.18]])
@pytest.mark.config(MAX_ENTRANCE_STICK_DISTANCE=130000)
async def test_finalsuggest_eats_pindrop(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        mode,
        sticky,
        expected_ans,
        input_position,
):
    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _mock_core(request):
        if mode == 'eats':
            return load_json('eats_regions_response.json')
        raise mockserver.TimeoutError()

    yamaps.add_fmt_geo_object(load_json('geosearch_house.json'))

    @mockserver.json_handler('/eda-catalog/v1/catalog-polygons')
    def _mock_polygons(request):
        return load_json('zones.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_eats(request):
        return {}

    request = {
        'action': 'pin_drop',
        'position': input_position,
        'state': {
            'accuracy': 10,
            'bbox': [37, 55, 37, 55],
            'current_mode': mode,
            'location': [0, 0],
        },
        'sticky': sticky,
        'type': 'b',
    }

    if mode != 'eats':
        await taxi_persuggest.invalidate_caches()

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    persuggest_common.compare_responses(
        mode=mode, actual=response, expected=load_json(expected_ans),
    )


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
@pytest.mark.parametrize(
    'prev_log,'
    'expected_response,'
    'userplace_call_expected,'
    'userplace_has_house_uri,'
    'maps_house_uri_expected,'
    'maps_house_kind_expected,'
    'maps_house_fail,'
    'geosuggest_empty,'
    'method,',
    [
        pytest.param(
            '',
            'finalize_expected_ans.json',
            False,  # userplace_call_expected
            None,  # userplace_has_house_uri
            False,  # maps_house_uri_expected
            True,  # maps_house_kind_expected
            False,  # maps_house_fail
            None,  # geosuggest_empty
            'fs_finalize_entrance_eats',
            id='by_coords_only',
        ),
        pytest.param(
            'ymapsbm1://uri_street',
            'finalize_expected_ans.json',
            False,  # userplace_call_expected
            None,  # userplace_has_house_uri
            False,  # maps_house_uri_expected
            True,  # maps_house_kind_expected
            False,  # maps_house_fail
            None,  # geosuggest_empty
            'fs_finalize_entrance_eats',
            id='by_uri_not_a_house',
        ),
        pytest.param(
            'ymapsbm1://uri_house',
            'finalize_expected_uri_ans.json',
            False,  # userplace_call_expected
            None,  # userplace_has_house_uri
            True,  # maps_house_uri_expected
            False,  # maps_house_kind_expected
            False,  # maps_house_fail
            None,  # geosuggest_empty
            'fs_finalize_entrance_eats',
            id='by_uri_a_house',
        ),
        pytest.param(
            USERPLACE_PREVLOG,
            'finalize_expected_userplace_ans.json',
            True,  # userplace_call_expected
            True,  # userplace_has_house_uri
            True,  # maps_house_uri_expected
            False,  # maps_house_kind_expected
            False,  # maps_house_fail
            None,  # geosuggest_empty
            'fs_finalize_userplace_eats',
            id='by_userplace_a_house',
        ),
        pytest.param(
            '',
            'finalize_expected_ans.json',
            False,  # userplace_call_expected
            None,  # userplace_has_house_uri
            False,  # maps_house_uri_expected
            True,  # maps_house_kind_expected
            True,  # maps_house_fail
            False,  # geosuggest_empty
            'fs_finalize_entrance_eats',
            id='geosuggest_hack_good',
        ),
        pytest.param(
            '',
            'finalize_bad_address.json',
            False,  # userplace_call_expected
            None,  # userplace_has_house_uri
            False,  # maps_house_uri_expected
            True,  # maps_house_kind_expected
            True,  # maps_house_fail
            True,  # geosuggest_empty
            None,
            id='geosuggest_hack_empty',
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.config(MAX_ENTRANCE_STICK_DISTANCE=60000)
@pytest.mark.parametrize('mode', ['eats', 'grocery'])
async def test_finalsuggest_eats_finalize(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        expected_response,
        prev_log,
        userplace_call_expected,
        userplace_has_house_uri,
        maps_house_uri_expected,
        maps_house_kind_expected,
        maps_house_fail,
        geosuggest_empty,
        method,
        mode,
):
    userplace_called = False
    maps_house_kind_called = False
    maps_house_uri_called = 0
    maps_house_uri_calls_expected = 1 if maps_house_uri_expected else 0
    maps_geosuggest_uri_called = False
    geosuggest_called = False

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        nonlocal maps_house_uri_called
        nonlocal maps_house_kind_called
        nonlocal maps_geosuggest_uri_called
        if 'uri' not in request.args and not maps_house_kind_called:
            maps_house_kind_called = True
            if maps_house_fail:
                return [load_json('geosearch_street.json')]
            return [load_json('geosearch_house.json')]
        if request.args.get('uri', '') == 'ymapsbm1://uri_house':
            maps_house_uri_called += 1
            return [load_json('geosearch_house.json')]
        if request.args.get('uri', '') == 'ymapsbm1://geosuggest_good_result':
            maps_geosuggest_uri_called = True
            return [load_json('geosearch_house.json')]
        return [load_json('geosearch_street.json')]

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        nonlocal userplace_called
        userplace_called = True
        response = load_json('userplaces_response.json')
        if userplace_has_house_uri:
            response['uri'] = 'ymapsbm1://uri_house'
        return response

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        nonlocal geosuggest_called
        geosuggest_called = True
        assert request.args == load_json('geosuggest_hack_request.json')
        if geosuggest_empty:
            return load_json('geosuggest_empty_response.json')
        return load_json('geosuggest_hack_response.json')

    @mockserver.json_handler('/eda-catalog/v1/catalog-polygons')
    def _mock_polygons(request):
        return {}

    request = {
        'action': 'finalize',
        'position': [37.5, 55.5],
        'prev_log': prev_log,
        'state': {
            'accuracy': 10,
            'bbox': [30, 50, 40, 60],
            'current_mode': mode,
            'location': [0, 0],
        },
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_json = load_json(expected_response)
    effective_json = response.json()
    if not geosuggest_empty:
        expected_json['results'][0]['method'] = method
    assert userplace_called == userplace_call_expected
    assert maps_house_uri_called == maps_house_uri_calls_expected
    assert maps_house_kind_called == maps_house_kind_expected
    assert geosuggest_called == maps_house_fail
    assert maps_geosuggest_uri_called == (
        maps_house_fail and not geosuggest_empty
    )
    assert response.status_code == 200 if not geosuggest_empty else 404
    persuggest_common.compare_responses(
        mode=mode, actual=effective_json, expected=expected_json,
    )


@pytest.mark.parametrize('building_id_source', ['maps_uri', 'point'])
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.parametrize(
    'building_address_fname,building_id',
    [
        pytest.param(
            'geosearch_house.json',
            '38e87a8e35f4f35ec80f85a45cd216e5763b58560860ceab2b4949562f18ced8',
            id='addr0',
        ),
        pytest.param(
            'geosearch_house_1.json',
            '69a6c62db7538a37427cc678b9245cc124a90b160605cb0303745ca8c7e3ffe0',
            id='addr1',
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.config(MAX_ENTRANCE_STICK_DISTANCE=60000)
async def test_finalsuggest_grocery_building_id(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        building_id_source,
        locale,
        building_address_fname,
        building_id,
):
    const_locale = 'ru'  # hard-coded in persuggest
    maps_calls = 0
    maps_calls_expected = 1
    if locale != const_locale:
        maps_calls_expected += 1  # localize for building_id

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        nonlocal maps_calls
        maps_calls += 1
        assert request.args['lang'] in (locale, const_locale)
        if request.args['lang'] != const_locale:
            return [load_json('geosearch_house_neporusski.json')]
        return [load_json(building_address_fname)]

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        response = load_json('userplaces_response.json')
        if building_id_source == 'maps_uri':
            response['uri'] = 'ymapsbm1://uri_house'
        return response

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return load_json('geosuggest_hack_response.json')

    @mockserver.json_handler('/eda-catalog/v1/catalog-polygons')
    def _mock_polygons(request):
        return {}

    request = {
        'action': 'finalize',
        'position': [37.5, 55.5],
        'prev_log': (
            'ymapsbm1://uri_house' if building_id_source == 'maps_uri' else ''
        ),
        'state': {
            'accuracy': 10,
            'bbox': [30, 50, 40, 60],
            'current_mode': 'grocery',
            'location': [0, 0],
        },
        'type': 'b',
    }
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-Request-Language'] = locale
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    assert list(r['building_id'] for r in response.json()['results']) == [
        building_id,
    ] * len(response.json()['results'])
    assert maps_calls == maps_calls_expected


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.config(MAX_ENTRANCE_STICK_DISTANCE=60000)
async def test_finalsuggest_eda_entrances(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        resp = load_json('geosearch_entr_resps.json')
        if request.args['ll'] == '37.500000,55.500000':
            return [resp['base']]
        return [resp['entr']]

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        return {}

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return {}

    @mockserver.json_handler('/eda-catalog/v1/catalog-polygons')
    def _mock_polygons(request):
        return {}

    request = {
        'action': 'pin_drop',
        'position': [37.5, 55.5],
        'state': {
            'accuracy': 10,
            'bbox': [30, 50, 40, 60],
            'current_mode': 'grocery',
            'location': [0, 0],
        },
        'type': 'b',
    }
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    assert response.json()['results'][0]['uri'] == 'ymapsbm1://uri_correct'
