import json

import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates

DRIVER_CAR_NUMBER = 'test_car_X'
UNIQUE_DRIVER_ID = 'unique_driver_id_X'
DRIVER_LICENSE_ID = 'license-1234'
LICENSE_NUMBER_PREFIX = 'number-'
POINT_A = [37.63, 55.80]


@pytest.mark.parametrize(
    'max_route_distance,max_route_time,paid_supply_price,decoupling',
    [
        (None, None, 50.1, False),
        (10000, 500, 50.5, True),
        (16000, 1000, 50.3, False),
        (50000, 5000, 50.8, True),
        (50000, 5000, None, False),
    ],
)
async def test_direct_request(
        acquire_candidate,
        mockserver,
        load_json,
        testpoint,
        max_route_distance,
        max_route_time,
        paid_supply_price,
        decoupling,
        dispatch_settings_mocks,
):
    dispatch_settings_mocks.set_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'QUERY_LIMIT_FREE_PREFERRED': 27,
                            'QUERY_LIMIT_LIMIT': 37,
                            'QUERY_LIMIT_MAX_LINE_DIST': 15000,
                            'MAX_ROBOT_DISTANCE': 15000,
                            'MAX_ROBOT_TIME': 900,
                        },
                    },
                ],
            },
        ],
    )

    fail_ordering = False

    def driver_dist():
        return 30000 if paid_supply else 300

    def driver_point():
        return [POINT_A[0] + driver_dist() * 0.000005, POINT_A[1]]

    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def _metadata_for_order(request):
        return load_json('metadata_response.json')

    @mockserver.json_handler('/candidates/profiles')
    def profiles(request):
        driver = json.loads(request.get_data())['driver_ids'][0]
        return {
            'drivers': [
                {
                    'uuid': driver['uuid'],
                    'dbid': driver['dbid'],
                    'position': [0, 0],
                    'classes': ['econom', 'business'],
                    'car_model': 'Audi A6',
                },
            ],
        }

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        body = json.loads(request.get_data())
        assert set(body.get('allowed_classes')) == {'econom', 'business'}
        # some sample answer from testing
        result = mock_candidates.make_candidates()
        result_driver = result['candidates'][2]
        result_driver['position'] = driver_point()
        result_driver['route_info']['distance'] = driver_dist()
        result_driver['unique_driver_id'] = UNIQUE_DRIVER_ID
        result_driver['car_number'] = DRIVER_CAR_NUMBER
        result_driver['license_id'] = DRIVER_LICENSE_ID
        result_driver['metadata'] = {
            'reposition': {'mode': 'home-2'},
            'some-key-2': 'some-value-2',
        }
        return result

    @testpoint('ordering-response')
    def _ordering_response(request):
        if fail_ordering:
            return {'change_response': True, 'data': 'fail'}
        return {}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def ordering(request):
        if fail_ordering:
            return mockserver.make_response('', 500)
        # do minimal sort by time
        body = json.loads(request.get_data())['request']
        # should conform driver-scoring api
        order_dict = body['search'].get('order', {})
        assert (
            body['search'].get('order_id'),
            order_dict.get('nearest_zone'),
        ) == (order['_id'], 'moscow')
        assert (
            order_dict.get('request', {}).get('source').get('geopoint')
            == POINT_A
        )
        candidates = [
            {
                'id': candidate['id'],
                'score': float(candidate['route_info']['time']),
            }
            for candidate in body['candidates']
        ]
        ordered_candidates = {
            'candidates': sorted(
                candidates, key=lambda candidate: candidate['score'],
            ),
            'source': 'scoring',
        }
        ordered_candidates['candidates'][2]['metadata'] = {
            'some-key-2': 'modified-value-2',
            'more-key-2': 'value-2',
        }
        return ordered_candidates

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        body = json.loads(request.get_data())
        if (body.get('unique_driver_id'), body.get('car_id')) == (
                UNIQUE_DRIVER_ID,
                DRIVER_CAR_NUMBER,
        ):
            return {'freezed': True}
        return {'freezed': False, 'reason': 'invalid udid'}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        assert False, 'should not be called'

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def personal_license_retrieve(request):
        body = json.loads(request.get_data())
        license_id = body['id']
        license_number = LICENSE_NUMBER_PREFIX + license_id
        return {'id': license_id, 'value': license_number}

    @mockserver.json_handler('/driver-trackstory/position')
    def trackstory_position(request):
        return {
            'position': {
                'direction': 214.5,
                'lat': 55.4183979995,
                'lon': 37.8954151234,
                'speed': 35.4,
                'timestamp': 1533817820,
            },
            'type': 'adjusted',
        }

    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/update')
    def meta_update(request):
        body = json.loads(request.get_data())
        assert body['metadata']['lookup']['mode'] == 'direct'
        return mockserver.make_response()

    order = lookup_params.create_params(
        tariffs=['econom'],
        max_route_distance=max_route_distance,
        max_route_time=max_route_time,
    )
    order['order']['surge_upgrade_classes'] = ['business']
    order['order']['request']['source'].update({'geopoint': POINT_A})
    if decoupling:
        order['order']['fixed_price']['paid_supply_price'] = 0
        order['order']['decoupling'] = {
            'success': True,
            'user_price_info': {'paid_supply_price': 0},
            'driver_price_info': {'paid_supply_price': paid_supply_price},
        }
    else:
        order['order']['fixed_price']['paid_supply_price'] = paid_supply_price
        order['order']['decoupling'] = {
            'success': True,
            'user_price_info': {'paid_supply_price': 1},
            'driver_price_info': {'paid_supply_price': 0},
        }

    paid_supply = True

    candidate = await acquire_candidate(order)

    await order_search.wait_call(timeout=1)
    await ordering.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    await trackstory_position.wait_call(timeout=1)
    await profiles.wait_call(timeout=1)
    await personal_license_retrieve.wait_call(timeout=1)
    await meta_update.wait_call(timeout=1)

    assert candidate['driver_classes'] == ['econom', 'business']
    assert (
        candidate.get('car_number'),
        candidate.get('udid'),
        candidate.get('driver_license_personal_id'),
    ) == (DRIVER_CAR_NUMBER, UNIQUE_DRIVER_ID, DRIVER_LICENSE_ID)
    assert (
        candidate.get('driver_license')
        == LICENSE_NUMBER_PREFIX + DRIVER_LICENSE_ID
    )
    assert candidate.get('reposition', {}) == {'mode': 'home-2'}

    assert (
        candidate['line_dist'] > 7000
        and candidate['dist'] >= 7000
        and (candidate['paid_supply'] is True or paid_supply_price is None)
    )
    assert candidate.get('adjusted_point') == {
        'avg_speed': 35,
        'direction': 214,
        'geopoint': [37.8954151234, 55.4183979995],
        'time': 1533817820,
    }
    assert candidate['cp'] == {
        'dest': [55.0, 35.0],
        'left_dist': 100,
        'left_time': 10,
        'id': 'some_order_id',
    }
    assert candidate['tags'] == ['tag0', 'tag1', 'tag2', 'tag3']
    assert candidate['gprs_time'] == 20.0
    assert candidate['metrica_device_id'] == '112233'

    paid_supply = False
    candidate = await acquire_candidate(order)
    assert (
        candidate['line_dist'] < 500
        and candidate['dist'] < 500
        and candidate['paid_supply'] is False
    )

    fail_ordering = True
    # should not be error
    candidate = await acquire_candidate(order)
    assert candidate
    fail_ordering = False


async def test_non_car_direct_request(
        acquire_candidate, mockserver, load_json,
):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def _metadata_for_order(request):
        return load_json('metadata_response.json')

    @mockserver.json_handler('/candidates/profiles')
    def profiles(request):
        driver = json.loads(request.get_data())['driver_ids'][0]
        return {
            'drivers': [
                {
                    'uuid': driver['uuid'],
                    'dbid': driver['dbid'],
                    'position': [1, 1],
                    'classes': ['econom', 'business'],
                    'car_model': 'Audi A6',
                },
            ],
        }

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        body = json.loads(request.get_data())
        assert set(body.get('excluded_car_numbers')) == {'car1', 'car2'}
        # some sample answer from testing
        result = mock_candidates.make_candidates()
        result_driver = result['candidates'][2]
        result_driver['position'] = [37.63, 55.80001]
        result_driver['route_info']['distance'] = 300
        result_driver['unique_driver_id'] = UNIQUE_DRIVER_ID
        result_driver['car_number'] = DRIVER_CAR_NUMBER
        result_driver['license_id'] = DRIVER_LICENSE_ID
        result_driver['metadata'] = {
            'reposition': {'mode': 'home-2'},
            'some-key-2': 'some-value-2',
        }
        return result

    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def ordering(request):
        # do minimal sort by time
        body = json.loads(request.get_data())['request']
        candidates = [
            {
                'id': candidate['id'],
                'score': float(candidate['route_info']['time']),
            }
            for candidate in body['candidates']
        ]
        ordered_candidates = {
            'candidates': sorted(
                candidates, key=lambda candidate: candidate['score'],
            ),
            'source': 'scoring',
        }
        ordered_candidates['candidates'][2]['metadata'] = {
            'some-key-2': 'modified-value-2',
            'more-key-2': 'value-2',
        }
        return ordered_candidates

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        body = json.loads(request.get_data())
        if (body.get('unique_driver_id'), body.get('car_id')) == (
                UNIQUE_DRIVER_ID,
                DRIVER_CAR_NUMBER,
        ):
            return {'freezed': True}
        return {'freezed': False, 'reason': 'invalid udid'}

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def personal_license_retrieve(request):
        body = json.loads(request.get_data())
        license_id = body['id']
        license_number = LICENSE_NUMBER_PREFIX + license_id
        return {'id': license_id, 'value': license_number}

    @mockserver.json_handler('/driver-trackstory/position')
    def trackstory_position(request):
        return {
            'position': {
                'direction': 214.5,
                'lat': 55.4183979995,
                'lon': 37.8954151234,
                'speed': 35.4,
                'timestamp': 1533817820,
            },
            'type': 'adjusted',
        }

    order = lookup_params.create_params(tariffs=['econom', 'business'])
    order['order']['request']['source'].update({'geopoint': POINT_A})
    order['candidates'] = [
        {
            'car_number': 'car1',
            'db_id': 'db_id1',
            'driver_id': 'driver_id1',
            'driver_license_personal_id': 'pesonal_id1',
        },
        {
            'car_number': 'car2',
            'db_id': 'db_id2',
            'driver_id': 'driver_id2',
            'driver_license_personal_id': 'pesonal_id2',
        },
    ]

    candidate = await acquire_candidate(order)

    await order_search.wait_call(timeout=1)
    await ordering.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    await trackstory_position.wait_call(timeout=1)
    await profiles.wait_call(timeout=1)
    await personal_license_retrieve.wait_call(timeout=1)

    assert candidate['driver_classes'] == ['econom', 'business']
    assert (
        candidate.get('car_number'),
        candidate.get('udid'),
        candidate.get('driver_license_personal_id'),
    ) == (DRIVER_CAR_NUMBER, UNIQUE_DRIVER_ID, DRIVER_LICENSE_ID)
    assert (
        candidate.get('driver_license')
        == LICENSE_NUMBER_PREFIX + DRIVER_LICENSE_ID
    )
