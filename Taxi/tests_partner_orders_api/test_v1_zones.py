import copy
import json

import pytest

HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}

EKB_AIRPORT_POINT = [60.80503137898187, 56.7454424257098]


def normalize_zone(zone_info):
    tariffs = zone_info['tariffs']
    tariffs.sort(key=lambda x: x['class'])
    zone_info['supported_feedback_choices']['canceled_reason'].sort(
        key=lambda x: x['name'],
    )
    for tariff in tariffs:
        tariff['payment_types'].sort()
        supported_reqs = tariff['supported_requirements']
        supported_reqs.sort(key=lambda x: x['name'])
        for req in supported_reqs:
            if 'select' in req:
                options = req['select']['options']
                options.sort(key=lambda x: x['name'])


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_v1_zones_point_fast_invalid_cases(taxi_partner_orders_api):
    for invalid_request in [
            {'zone_names': ['ekb_airport'], 'geopoint': EKB_AIRPORT_POINT},
            {'zone_names': ['']},
            {'zone_names': []},
    ]:
        response = await taxi_partner_orders_api.post(
            'agent/partner-orders-api/v1/zones',
            headers=HEADERS,
            json=invalid_request,
        )
        assert response.status_code == 400
        r_json = response.json()
        assert r_json == {
            'message': 'Specify either \'zone_names\' or \'geopoint\'',
            'code': 'BAD_REQUEST',
        }

    request = {'geopoint': [1.0, 1.0]}
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/zones', headers=HEADERS, json=request,
    )
    assert response.status_code == 404
    r_json = response.json()
    assert r_json == {
        'message': 'Zone or point not found',
        'code': 'ZONE_NOT_FOUND',
    }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize('error_code', [400, 401, 429, 500])
async def test_v1_zones_invalid(
        taxi_partner_orders_api, mockserver, load_json, error_code,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _int_api_v1_zoneinfo(request):
        if request.json.get('zone_name') == 'kamenskuralsky_airport':
            return mockserver.make_response(
                response=json.dumps({}), status=error_code,
            )
        return load_json('ekb_airport_int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/zones', headers=HEADERS, json={},
    )
    r_json = response.json()
    if error_code == 400:
        assert response.status_code == error_code
        assert r_json == {
            'message': 'Specify either \'zone_names\' or \'geopoint\'',
            'code': 'BAD_REQUEST',
        }
    elif error_code == 401:
        assert response.status_code == 500
        assert r_json == {'message': 'Unknown error', 'code': 'INTERNAL_ERROR'}
    elif error_code == 429:
        assert response.status_code == error_code
        assert r_json == {
            'message': 'Too many requests',
            'code': 'TOO_MANY_REQUESTS',
        }
    else:
        assert response.status_code == error_code
        assert r_json == {'message': 'Unknown error', 'code': 'INTERNAL_ERROR'}


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_v1_zones_experiment_not_found(
        taxi_partner_orders_api, mockserver, load_json,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _int_api_v1_zoneinfo(request):
        if request.json.get('zone_name') == 'kamenskuralsky_airport':
            return load_json('kamenskuralsky_airport_int_api_response.json')
        return load_json('ekb_airport_int_api_response.json')

    for request in [
            {'zone_names': ['ekb_airport']},
            {'geopoint': EKB_AIRPORT_POINT},
    ]:
        response = await taxi_partner_orders_api.post(
            'agent/partner-orders-api/v1/zones', headers=HEADERS, json=request,
        )
        r_json = response.json()
        assert response.status_code == 404
        assert r_json == {
            'message': 'Zone ekb_airport not found',
            'code': 'ZONE_NOT_FOUND',
        }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize('zones_passed_by_partner', [True, False])
async def test_v1_zones_point_not_found(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        zones_passed_by_partner,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _int_api_v1_zoneinfo(request):
        if request.json.get('zone_name') == 'kamenskuralsky_airport':
            return mockserver.make_response(
                response=json.dumps({}), status=404,
            )
        return load_json('ekb_airport_int_api_response.json')

    request = {}
    if zones_passed_by_partner:
        request = {'zone_names': ['kamenskuralsky_airport', 'ekb_airport']}
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/zones', headers=HEADERS, json=request,
    )
    r_json = response.json()
    if zones_passed_by_partner:
        assert response.status_code == 404
        assert r_json == {
            'message': 'Zone or point not found',
            'code': 'ZONE_NOT_FOUND',
        }
    else:
        assert response.status_code == 200
        assert set({zone['zone_name'] for zone in r_json['zones']}) == set(
            {'ekb_airport_waiting', 'ekb_airport', 'ekb_airport_notification'},
        )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_v1_zones_point(taxi_partner_orders_api, mockserver, load_json):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _int_api_v1_zoneinfo(request):
        return load_json('ekb_airport_int_api_response.json')

    request = {'geopoint': EKB_AIRPORT_POINT}
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/zones', headers=HEADERS, json=request,
    )
    assert response.status_code == 200
    r_json = response.json()
    normalize_zone(r_json['zones'][0])
    assert r_json == {'zones': [load_json('ekb_airport_response.json')]}


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(PARTNER_ORDERS_API_SIMULTANEOUS_ZONES_REQUESTS_COUNT=1)
async def test_v1_zones_all(taxi_partner_orders_api, mockserver, load_json):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _int_api_v1_zoneinfo(request):
        if request.json.get('zone_name') == 'kamenskuralsky_airport':
            return load_json('kamenskuralsky_airport_int_api_response.json')
        return load_json('ekb_airport_int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/zones', headers=HEADERS, json={},
    )
    assert response.status_code == 200
    r_json = response.json()
    zones = r_json['zones']
    assert len(zones) == 4
    for zone in zones:
        normalize_zone(zone)
    zones.sort(key=lambda x: x['zone_name'])

    etalon_1 = load_json('ekb_airport_response.json')
    etalon_2 = copy.deepcopy(etalon_1)
    etalon_2['zone_name'] = 'ekb_airport_notification'
    etalon_3 = copy.deepcopy(etalon_1)
    etalon_3['zone_name'] = 'ekb_airport_waiting'

    assert r_json == {
        'zones': [
            etalon_1,
            etalon_2,
            etalon_3,
            load_json('kamenskuralsky_airport_response.json'),
        ],
    }
