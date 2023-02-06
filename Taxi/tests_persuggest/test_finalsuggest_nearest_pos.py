import json

import pytest

from tests_persuggest import persuggest_common

URL = '/4.0/persuggest/v1/finalsuggest'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Request-Application': 'app_name=android',
    'X-Request-Language': 'ru',
}


WHERE_ARE_YOU_TRANSLATIONS = {
    'client_messages': {
        'where_am_i.bubble.close_button': {'ru': 'Да'},
        'where_am_i.other_text': {'ru': 'Указать другой адрес'},
        'where_am_i.bubble.edit_button': {'ru': 'Нет'},
        'where_am_i.i_am_here': {'ru': 'Я здесь'},
        'where_am_i.skip_button_text': {'ru': 'Пропустить'},
        'where_am_i.subtitle': {
            'ru': (
                'Из-за GPS-ошибки мы вас потеряли -- '
                'пожалуйста, нажмите на одну из точек на карте:'
            ),
        },
        'where_am_i.bubble.text': {'ru': 'Вы находитесь здесь?'},
        'where_am_i.title': {'ru': 'Уточните, где вы'},
    },
}


@pytest.mark.parametrize(
    'type_,expected_persistent_requested', [('b', False), ('favorite', True)],
)
async def test_finalsuggest_np_blocked_zone(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        type_,
        expected_persistent_requested,
):
    persistent_requested = False

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        filter_ = data.get('filter', {})
        if filter_.get('persistent_only', False):
            nonlocal persistent_requested
            persistent_requested = True
        return load_json('zones_for_test.json')

    request = {
        'action': 'pin_drop',
        'position': [34.7, 32.1],
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': type_,
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    expected_ans = persuggest_common.logparse(
        load_json('zones_expected_ans.json'),
    )
    assert response.status_code == 200
    assert persistent_requested == expected_persistent_requested
    assert persuggest_common.logparse(response.json()) == expected_ans


@pytest.mark.translations(
    client_messages={'pickup_point.is_last.label': {'ru': 'You were here'}},
)
@pytest.mark.experiments3(filename='exp3_use_pickup_point_as_org.json')
@pytest.mark.parametrize('pickup_point_type', ['a', 'mid1', 'b'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_finalsuggest_np_pickup_points(
        taxi_persuggest, mockserver, load_json, yamaps, pickup_point_type,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_finalsuggest_points.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        assert json.loads(request.get_data()) == load_json(
            'bzf_expected_req.json',
        )
        return load_json('bzf_response_none.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'business_oid' in request.args:
            return [load_json('geosearch_org.json')]
        return [load_json('yamaps_simple_geo_object.json')]

    request = {
        'action': 'pin_drop',
        'position': [37.57, 55.72],
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': pickup_point_type,
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected_ans = persuggest_common.logparse(
        load_json(
            'points_expected_ans_a.json'
            if pickup_point_type == 'a'
            else 'points_expected_ans.json',
        ),
    )
    assert persuggest_common.logparse(response.json()) == expected_ans


@pytest.mark.parametrize('hide_choice', [True, False])
async def test_finalsuggest_np_choices(
        taxi_persuggest, mockserver, load_json, yamaps, hide_choice,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        response = load_json('choices_for_test.json')
        if hide_choice:
            response['zones'][0]['points'][0].pop('name')
        return response

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    request = {
        'action': 'pin_drop',
        'position': [34.7, 32.1],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    if hide_choice:
        expected_ans = load_json('choices_expected_ans_wo_name.json')
    else:
        expected_ans = load_json('choices_expected_ans.json')

    expected_ans = persuggest_common.logparse(expected_ans)
    assert response.status_code == 200
    assert persuggest_common.logparse(response.json()) == expected_ans


@pytest.mark.translations(
    client_messages={'pickup_point.is_last.label': {'ru': 'Ты здесь был'}},
)
@pytest.mark.parametrize(
    'sticky,bad_accuracy,accuracy,ml_expected',
    [
        (False, True, -100, 'ml_expected_response_on_not_sticky.json'),
        (False, False, 0, 'ml_expected_response_on_not_sticky.json'),
        (True, False, 20, 'ml_expected_response_on_sticky.json'),
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_finalsuggest_np_ml(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        sticky,
        bad_accuracy,
        accuracy,
        ml_expected,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if not sticky and 'll' in request.args:
            if request.args['ll'] == '37.605789,55.656474':
                if bad_accuracy:
                    assert 'spn' not in request.args
                else:
                    assert 'spn' in request.args
        return [load_json('geosearch_ph_hist.json')]

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return load_json('bzf_response_none.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas(request):
        expected_request = load_json('uml_finalsuggest_request.json')
        uml_resp = 'uml_finalsuggest_not_sticky.json'
        if sticky:
            expected_request['actions'].append('stick')
            uml_resp = 'uml_finalsuggest_sticky.json'
        expected_request['state']['accuracy'] = accuracy
        coord_prov = expected_request['state']['coord_providers'][0]
        coord_prov['accuracy'] = accuracy
        assert json.loads(request.get_data()) == expected_request
        return load_json(uml_resp)

    request = {
        'action': 'pin_drop',
        'position': [37.605789, 55.656474],
        'state': {
            'accuracy': accuracy,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [39.1, 55.9],
        },
        'sticky': sticky,
        'type': 'a',
    }

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected_response = load_json(ml_expected)
    assert response.json() == expected_response


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_finalsuggest_not_sticky_layers_log(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        return load_json('userplaces_item_response.json')

    request = {
        'action': 'pin_drop',
        'sticky': False,
        'position': [37.1, 55.1],
        'layers_log': (
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
    expected_ans = load_json('not_sticky_log_expected_ans.json')
    assert response.json() == expected_ans


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_finalsuggest_np_pull_out_of_zone(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    zones_call_counter = 0

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        result = load_json('zones_for_test.json')
        nonlocal zones_call_counter
        if zones_call_counter == 0:
            del result['pin_point_id']
        zones_call_counter = zones_call_counter + 1
        return result

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        return {
            'adjusted': [
                {
                    'longitude': 37.5566,
                    'latitude': 55.7172,
                    'geo_distance': 100,
                },
            ],
        }

    request = {
        'action': 'pin_drop',
        'position': [37.5366, 55.7172],
        'state': {
            'accuracy': 10000,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    results_json = response.json()['results']
    assert len(results_json) == 1
    points_json = response.json()['points']
    assert points_json
    assert zones_call_counter == 2


@pytest.mark.experiments3(filename='exp3_use_pickup_point_as_org.json')
async def test_finalsuggest_np_bzf_failure(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_finalsuggest_points.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        assert json.loads(request.get_data()) == load_json(
            'bzf_expected_req.json',
        )
        return mockserver.make_response('fail', status=500)

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'business_oid' in request.args:
            return [load_json('geosearch_org.json')]
        return [load_json('yamaps_simple_geo_object.json')]

    request = {
        'action': 'pin_drop',
        'position': [34.7, 32.1],
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )

    expected_ans = persuggest_common.logparse(
        load_json('points_expected_ans_without_filter.json'),
    )
    assert response.status_code == 200
    assert persuggest_common.logparse(response.json()) == expected_ans


@pytest.mark.config(
    MODES=[
        {
            'mode': 'sdc',
            'experiment': 'enable_sdc_2',
            'zone_activation': {'zone_type': 'sdc', 'point_title': ''},
        },
    ],
)
@pytest.mark.translations(
    client_messages={
        'sdc_bubble_text_key': {'ru': 'Остановочка беспилотника'},
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_modes_points_settings.json')
@pytest.mark.experiments3(filename='exp3_sdc_whitelist_zones.json')
@pytest.mark.experiments3(filename='exp3_enable_sdc_2.json')
@pytest.mark.parametrize(
    'fields, position, expected_position, expected_title, expected_subtitle',
    [
        (
            [],
            [37.547, 55.711],
            [37.546, 55.7108],
            'Selfdriving stop 2',
            'Садовническая улица, 82с2',
        ),
        (
            [
                {
                    'type': 'a',
                    'log': {
                        'id': 'sdt_2',
                        'geometry': [37.546, 55.7108],
                        'uri': 'ytpp://test_sdt/sdt_2',
                    },
                },
            ],
            [37.547, 55.711],
            [37.546, 55.7272],
            'Selfdriving stop 1',
            'Садовническая улица, 82с2',
        ),
        (
            [
                {
                    'type': 'b',
                    'log': {
                        'id': 'sdt_2',
                        'geometry': [37.546, 55.7108],
                        'uri': 'ytpp://test_sdt/sdt_2',
                    },
                },
            ],
            [37.48, 55.7],
            [37.546, 55.7108],
            'Selfdriving stop 2',
            'Садовническая улица, 82с2',
        ),
    ],
)
async def test_finalsuggest_np_sdc_sticking(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        fields,
        position,
        expected_position,
        expected_title,
        expected_subtitle,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        assert data['filter']['allowed_ids'] == ['test_sdt']
        if data['geopoint'][0] < 37.5:
            return load_json('zones_empty_response.json')
        return load_json('zones_for_test_in_sdc.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    field_point_uri = ''
    if fields:
        field_point_uri = fields[0]['log']['uri']
    for field in fields:
        field['log'] = json.dumps(field['log'])

    request = {
        'action': 'pin_drop',
        'position': position,
        'state': {
            'accuracy': 10,
            'bbox': [30, 50, 40, 60],
            'current_mode': 'sdc',
            'fields': fields,
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    points = load_json('expected_sdc_points.json')
    expected_points = [p for p in points if p['uri'] != field_point_uri]
    resp_data = response.json()
    first_result = resp_data['results'][0]
    assert first_result['position'] == expected_position
    assert first_result['title']['text'] == expected_title
    assert first_result['subtitle']['text'] == expected_subtitle
    assert first_result['method'] == 'zone_mode_address'
    for point in resp_data['points']:
        assert point['bubble']['id']
        point['bubble'].pop('id')
    if position[0] < 37.5:
        assert resp_data['points'] == points
    else:
        assert resp_data['points']
        assert resp_data['points'] == expected_points


@pytest.mark.config(
    MODES=[
        {
            'mode': 'sdc',
            'experiment': 'enable_sdc_2',
            'zone_activation': {'zone_type': 'sdc', 'point_title': ''},
        },
    ],
    ZONEINFO_TARIFFS_SETTINGS_BY_MODES_IN_ZONES={
        '__default__': {'econom': ['sdc']},
        'moscow': {'econom': ['sdc']},
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_enable_sdc_2.json')
async def test_finalsuggest_np_sdc_single_tariff(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        if data['geopoint'][0] < 37.5:
            return load_json('zones_empty_response.json')
        return load_json('zones_for_test_in_sdc.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    request = {
        'action': 'pin_drop',
        'position': [37.547, 55.711],
        'state': {
            'accuracy': 10,
            'bbox': [30, 50, 40, 60],
            'current_mode': '',
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    first_result = response.json()['results'][0]
    assert first_result['position'] == [37.546, 55.7108]
    assert first_result['title']['text'] == 'Selfdriving stop 2'
    assert first_result['subtitle']['text'] == 'Садовническая улица, 82с2'
    assert first_result['method'] == 'zone_mode_address'
    assert response.json()['immediate_actions']


@pytest.mark.config(
    MODES=[
        {
            'mode': 'sdc',
            'experiment': 'enable_sdc_2',
            'zone_activation': {'zone_type': 'sdc', 'point_title': ''},
        },
    ],
    ZONEINFO_TARIFFS_SETTINGS_BY_MODES_IN_ZONES={
        '__default__': {'econom': ['sdc']},
        'moscow': {'econom': ['sdc']},
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_enable_sdc_2.json')
@pytest.mark.experiments3(filename='exp3_sdc_suggest_geo_addresses.json')
async def test_finalsuggest_np_sdc_from_prev_log(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        if data['geopoint'][0] < 37.5:
            return load_json('zones_empty_response.json')
        return load_json('zones_for_test_in_sdc.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    request = {
        'action': 'finalize',
        'prev_log': '{"uri":"ymapsbm1://some_uri","comment":"ovr"}',
        'position': [37.547, 55.711],
        'state': {
            'accuracy': 10,
            'bbox': [30, 50, 40, 60],
            'current_mode': 'sdc',
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_zones.times_called == 1

    first_result = response.json()['results'][0]
    assert first_result['position'] == [37.547, 55.711]


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
@pytest.mark.experiments3(filename='exp3_mode_hack.json')
async def test_finalsuggest_np_sdc_sticking_exp_hack(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        data = json.loads(request.get_data())
        if data['geopoint'][0] < 37.5:
            return load_json('zones_empty_response.json')
        return load_json('zones_for_test_in_sdc.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    request = {
        'action': 'pin_drop',
        'position': [37.547, 55.711],
        'state': {
            'accuracy': 10,
            'bbox': [30, 50, 40, 60],
            'current_mode': '',
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    first_result = response.json()['results'][0]
    assert first_result['position'] == [37.546, 55.7108]
    assert first_result['title']['text'] == 'Selfdriving stop 2'
    assert first_result['subtitle']['text'] == 'Садовническая улица, 82с2'
    assert first_result['method'] == 'zone_mode_address'


@pytest.mark.translations(**WHERE_ARE_YOU_TRANSLATIONS)
@pytest.mark.experiments3(filename='cfg3_choose_where_you_are.json')
@pytest.mark.experiments3(filename='exp3_entrances_list_in_suggest.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    'is_bubble_shown', [False, True], ids=['no_bubble', 'bubble'],
)
@pytest.mark.parametrize(
    'allow_closures',
    [
        pytest.param(False, id='forbid_closures'),
        pytest.param(
            True,
            id='allow_closures',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_where_am_i_in_closures.json',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'zones_resp,expected_response_file,have_closure',
    [
        pytest.param(
            'zones_empty_response.json',
            'expected_ans_where_am_i_aurora_no_zones.json',
            False,
            id='no_zones',
        ),
        pytest.param(
            'choices_for_test.json',  # aurora closure
            'expected_ans_where_am_i_aurora_zone.json',
            True,
            id='closure',
        ),
    ],
)
async def test_choose_where_you_are(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        allow_closures,
        zones_resp,
        expected_response_file,
        have_closure,
        is_bubble_shown,
):
    umlaas_geo_response = load_json('uml_response_corrected_bad_location.json')
    umlaas_geo_response['show_bubble'] = is_bubble_shown

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        assert (
            request.json['geopoint']
            == umlaas_geo_response['stick_result']['position']
        )

        return load_json(zones_resp)

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return umlaas_geo_response

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return load_json('bzf_response_none.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'business_oid' in request.args:
            return [load_json('geosearch_org.json')]
        return [load_json('yamaps_simple_geo_object.json')]

    request = {
        'action': 'pin_drop',
        'position': [37.57, 55.72],
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'a',
    }

    def get_the_action(response):
        return next(
            filter(
                lambda a: a['type'] == 'choose_where_you_are',
                response['immediate_actions'],
            ),
        )

    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    expected_ans = load_json(expected_response_file)

    if not allow_closures and have_closure:
        expected_ans['immediate_actions'] = [
            action
            for action in expected_ans['immediate_actions']
            if action['type'] != 'choose_where_you_are'
        ]
        if not expected_ans['immediate_actions']:
            # delete empty list
            del expected_ans['immediate_actions']
        expected_ans['results'] = expected_ans['results'][
            : -len(umlaas_geo_response['alternatives'])
        ]
    else:
        get_the_action(expected_ans)['ask_for_edit'] = is_bubble_shown
        if not is_bubble_shown:
            del get_the_action(expected_ans)['bubble']

    assert persuggest_common.jsonify(
        response.json(),
    ) == persuggest_common.jsonify(expected_ans)


@pytest.mark.config(
    YANDEX_MAPS_TEXT_FORMATS={
        'by_country_format': {
            'RU': {
                'full_text': [
                    {'format': 'full {HOUSE}', 'required_fields': ['HOUSE']},
                ],
                'short_text': [
                    {
                        'format': 'short {STREET}',
                        'required_fields': ['STREET'],
                    },
                ],
            },
            '__default__': {},
        },
        'enabled': True,
    },
)
async def test_finalsuggest_format_address(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    toponym = load_json('yamaps_simple_geo_object.json')
    yamaps.add_fmt_geo_object(toponym)

    request = {
        'action': 'pin_drop',
        'position': [37.57, 55.72],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': False,
        'type': 'b',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    result = response.json()['results'][0]
    toponym_address = toponym['geocoder']['address']
    assert result['title']['text'] == f'short {toponym_address["street"]}'
    assert result['text'] == f'full {toponym_address["house"]}'
