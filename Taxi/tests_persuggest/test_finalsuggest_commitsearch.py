import json

import pytest


URL = '/4.0/persuggest/v1/finalsuggest'

USER_ID = '12345678901234567890123456789012'
YANDEX_UID = '400000000'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': YANDEX_UID,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Request-Application': 'app_name=iphone,app_brand=some_brand',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '10.10.10.10',
}


@pytest.mark.parametrize('current_mode', [None, 'drive'])
@pytest.mark.parametrize(
    'has_banned_actions_exp, banned_actions, expect_calls',
    [
        (False, ['pin_drop', 'finalize'], True),
        (True, [], True),
        (True, ['pin_drop'], True),
        (True, ['finalize'], False),
    ],
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.config(FINALSUGGEST_COMMIT_SEARCH='sync')
async def test_finalize_commitsearch(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        experiments3,
        has_banned_actions_exp,
        banned_actions,
        expect_calls,
        current_mode,
):
    experiments3.add_experiment(
        name='search_history_banned_actions',
        consumers=['persuggest/finalsuggest'],
        match={
            'enabled': has_banned_actions_exp,
            'predicate': {'type': 'true'},
        },
        clauses=[
            {
                'title': 'banned_actions',
                'value': banned_actions,
                'predicate': {'type': 'true'},
            },
        ],
        default_value={},
    )

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        return mockserver.make_response(
            json={
                'app_link': '',
                'cars': [],
                'is_registred': True,
                'is_service_available': True,
                'offers': [],
                'views': [],
            },
            headers={'X-Req-Id': '123'},
        )

    @mockserver.json_handler('/routehistory/routehistory/search-add')
    def _mock_routehistory(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        assert request.headers['X-Yandex-UID'] == YANDEX_UID
        assert request.json == load_json('expected_searchadd_request.json')
        return {'id': ''}

    @mockserver.json_handler('/userplaces/userplaces/item')
    def _mock_userplaces(request):
        assert json.loads(request.get_data()) == load_json(
            'userplaces_request.json',
        )
        return load_json('userplaces_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_pp_localize(request):
        assert json.loads(request.get_data()) == load_json(
            'pickuppoints_request.json',
        )
        return load_json('pickuppoints_response.json')

    request = {
        'action': 'finalize',
        'position': [34.7, 32.1],
        'prev_log': 'ymapsbm1://some_uri1',
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [
                {
                    'type': 'a',
                    'log': json.dumps(
                        {
                            'type': 'userplace',
                            'userplace_id': '0123456789abcdef0123456789abcdef',
                        },
                    ),
                    'position': [34.71, 32.13],
                    'entrance': '',
                },
                {
                    'type': 'mid1',
                    'log': json.dumps({'uri': 'ytpp://some_pickup_point'}),
                    'position': [10.0, 12.0],
                },
            ],
            'location': [0, 0],
        },
        'type': 'b',
    }
    if current_mode:
        request['state']['current_mode'] = current_mode
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_routehistory.has_calls == expect_calls


@pytest.mark.parametrize('point_type', ['a', 'b'])
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.config(FINALSUGGEST_COMMIT_SEARCH='sync')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_finalize_commitsearch_choices(
        taxi_persuggest, mockserver, load_json, yamaps, point_type,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    @mockserver.json_handler('/routehistory/routehistory/search-add')
    def _mock_routehistory(request):
        assert request.json == load_json(
            'expected_searchadd_request_choices.json',
        )
        return {'id': ''}

    request = {
        'action': 'finalize',
        'position': [34.7, 32.1],
        'prev_log': 'ymapsbm1://some_uri1',
        'state': {
            'accuracy': 20,
            'bbox': [30, 50, 40, 60],
            'fields': [
                {
                    'type': 'a',
                    'log': 'ymapsbm1://uri_a',
                    'position': [34.71, 32.13],
                    'entrance': '',
                },
                {
                    'type': 'b',
                    'log': 'ymapsbm1://uri_b',
                    'position': [10.0, 12.0],
                },
            ],
            'location': [0, 0],
        },
        'type': point_type,
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    if point_type != 'a':
        assert _mock_routehistory.has_calls
    else:
        assert not _mock_routehistory.has_calls
