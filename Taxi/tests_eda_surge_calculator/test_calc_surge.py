# pylint: disable=redefined-outer-name, unused-variable
import json

import pytest


TEST_FEATURE_FLAGS = {
    'eda_surge_calculator_use_resource_lru_cache': {
        'description': (
            'use lru caches in eda surge calculator' ' candidates resources'
        ),
        'enabled': True,
    },
}

CANDIDATES_RESPONSE = {
    'drivers': [
        {
            'position': [10.002, 10.002],
            'id': 'dbid0_uuid0',
            'dbid': 'dbid0',
            'uuid': 'uuid0',
            'eats_shift': {
                'shift_id': '9854223',
                'started_at': '2020-10-07T04:57:30+0000',
                'closes_at': '2020-10-07T09:00:00+0000',
                'zone_id': '5121',
                'status': 'in_progress',
                'updated_ts': '2020-10-07T04:57:31+0000',
                'is_high_priority': True,
                'zone_group_id': '12',
                'meta_group_id': None,
            },
            'status': {
                'status': 'busy',
                'orders': [],
                'driver': 'verybusy',
                'taximeter': 'busy',
            },
        },
        {
            # skipped repeat
            'position': [10.000, 10.000],
            'id': 'dbid0_uuid0',
            'dbid': 'dbid0',
            'uuid': 'uuid0',
            'eats_shift': {
                'shift_id': '9854223',
                'started_at': '2020-10-07T04:57:30+0000',
                'closes_at': '2020-10-07T09:00:00+0000',
                'zone_id': '5121',
                'status': 'in_progress',
                'updated_ts': '2020-10-07T04:57:31+0000',
                'is_high_priority': True,
                'zone_group_id': '12',
                'meta_group_id': None,
            },
            'status': {
                'status': 'busy',
                'orders': [],
                'driver': 'verybusy',
                'taximeter': 'busy',
            },
            'chain_info': {},
        },
        {
            # skipped too_far
            'position': [10.020, 10.020],
            'id': 'dbid0_uuid1',
            'dbid': 'dbid0',
            'uuid': 'uuid1',
            'eats_shift': {
                'shift_id': '9854223',
                'started_at': '2020-10-07T04:57:30+0000',
                'closes_at': '2020-10-07T09:00:00+0000',
                'zone_id': '5121',
                'status': 'in_progress',
                'updated_ts': '2020-10-07T04:57:31+0000',
                'is_high_priority': True,
                'zone_group_id': '12',
                'meta_group_id': None,
            },
            'status': {
                'status': 'busy',
                'orders': [],
                'driver': 'verybusy',
                'taximeter': 'busy',
            },
            'chain_info': {
                'destination': [10.021, 10.021],
                'left_dist': 20,
                'left_time': 900,
            },
        },
        {
            # inside id-108
            'position': [10.005, 10.001],
            'id': 'dbid0_uuid2',
            'dbid': 'dbid0',
            'uuid': 'uuid2',
            'eats_shift': {
                'shift_id': '9854223',
                'started_at': '2020-10-07T04:57:30+0000',
                'closes_at': '2020-10-07T09:00:00+0000',
                'zone_id': '5121',
                'status': 'in_progress',
                'updated_ts': '2020-10-07T04:57:31+0000',
                'is_high_priority': True,
                'zone_group_id': '12',
                'meta_group_id': None,
            },
            'status': {
                'status': 'busy',
                'orders': [],
                'driver': 'verybusy',
                'taximeter': 'busy',
            },
            'chain_info': {
                'destination': [10.001, 10.001],
                'left_dist': 20,
                'left_time': 900,
            },
        },
    ],
}


@pytest.fixture
def candidates(mockserver):
    @mockserver.json_handler('/candidates/list-profiles')
    def candidates_handler(request):
        return CANDIDATES_RESPONSE


class Context:
    def __init__(self):
        self.count = 0

    def call(self):
        self.count += 1

    def get_count(self):
        return self.count


@pytest.fixture
def courier_activity_context():
    return Context()


@pytest.fixture
def eda_courier_activity(mockserver, courier_activity_context):
    class Mocks:
        @mockserver.json_handler('/eats-core-surge/v1/surge/courier-activity')
        @staticmethod
        def _courier_activity_handler(request):
            courier_activity_context.call()
            if courier_activity_context.get_count == 1:
                return {
                    'payload': [
                        {
                            'courierId': 22,
                            'regionId': 1,
                            'activeDeliveries': [],
                        },
                    ],
                    'meta': {'count': 1},
                }
            if courier_activity_context.get_count == 2:
                return mockserver.make_response('bad request', status=400)

            return {
                'payload': [
                    {
                        'courierId': 108,
                        'regionId': 1,
                        'activeDeliveries': [
                            {
                                'source': {
                                    'id': 23,
                                    'location': {
                                        'latitude': 10.0,
                                        'longitude': 10.0,
                                    },
                                },
                                'destination': {
                                    'location': {
                                        'latitude': 10.001,
                                        'longitude': 10.001,
                                    },
                                },
                                'estimatedPreparationFinishedAt': (
                                    '2020-04-12T11:50:00+03:00'
                                ),
                                'estimatedDeliveredAt': (
                                    '2020-04-12T12:12:00+03:00'
                                ),
                                'status': 'taken',
                            },
                            {
                                'source': {
                                    'id': 23,
                                    'location': {
                                        'latitude': 10.0,
                                        'longitude': 10.0,
                                    },
                                },
                                'destination': {
                                    'location': {
                                        'latitude': 10.001,
                                        'longitude': 10.001,
                                    },
                                },
                                'estimatedPreparationFinishedAt': (
                                    '2020-04-12T11:50:00+03:00'
                                ),
                                'estimatedDeliveredAt': (
                                    '2020-04-12T12:00:00+03:00'
                                ),
                                'status': 'taken',
                            },
                        ],
                    },
                ],
                'meta': {'count': 1},
            }

    return Mocks()


def _result_key(result):
    return result['calculator_name']


def _calc_result_key(result):
    return result['place_id'] + result.get('delivery_zone_id', 9999)


def _error_key(error):
    return error['place_id'] + error.get('delivery_zone_id', 9999)


def _sort_response(response):
    response['errors'].sort(key=_error_key)
    for item in response['results']:
        item['results'].sort(key=_calc_result_key)
    response['results'].sort(key=_result_key)


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
@pytest.mark.config(EDA_SURGE_CALCULATOR_CANDIDATES_AS_PRIMARY_SOURCE=True)
@pytest.mark.config(
    EDA_SURGE_CACHE_COURIERS_DESTINATIONS={
        'fetch_chunk_size': 1,
        'failed_requests_limit': 2,
    },
)
async def test_calc_surge(
        taxi_eda_surge_calculator, candidates, load_json, eda_courier_activity,
):
    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1, 2]}

    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    expected_response = load_json('expected.json')
    response = response.json()
    print(response)
    _sort_response(response)
    _sort_response(expected_response)
    assert response == expected_response


# Проверяем работу кеша при передаче одинаковых
# ресторанов с одинаковыми координатами.
# Ловим race_condition
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_multiple_cache_check.json',
)
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
@pytest.mark.config(EDA_SURGE_CALCULATOR_CANDIDATES_AS_PRIMARY_SOURCE=True)
@pytest.mark.config(
    EDA_SURGE_CACHE_COURIERS_DESTINATIONS={
        'fetch_chunk_size': 1,
        'failed_requests_limit': 2,
    },
    EDA_SURGE_CALCULATOR_MAIN={
        'split_request_percentage': 0,
        'only_couriers_with_active_shift': True,
    },
)
async def test_multiple_calc_surge(
        taxi_eda_surge_calculator,
        load_json,
        eda_courier_activity,
        experiments3,
        mockserver,
):
    @mockserver.json_handler('/candidates/list-profiles')
    def candidates_handler(request):
        return CANDIDATES_RESPONSE

    experiments3.add_config(
        consumers=['eda-surge-calculator/place'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'settings': {
                'limit': 100,
                'max_distance': 1000,
                'damper_x': 2,
                'damper_y': 1.75,
                'time_quants': 3,
                'cond_free_threshold': 1200,
                'cond_busy_threshold': 300,
                'c1': [-1.9936, -1.5553, -1.1169],
                'c2': [1.4147, 1.4413, 1.468],
                'additional_time_percents': [0, 10, 15, 60],
                'delivery_fee': [100, 120, 160, 200],
            },
            'pipelines': ['calc_surge'],
        },
        name='eats_surge_places_settings_by_place',
    )

    await taxi_eda_surge_calculator.invalidate_caches()

    places = [i for i in range(1, 16)]

    data = {'place_ids': places}

    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    expected_response = load_json('expected.json')
    response = response.json()
    _sort_response(response)
    _sort_response(expected_response)

    assert response['errors'] == []
    place_response = expected_response['results'][0]['results'][0]['result']

    for i in range(0, 15):
        current_place = response['results'][0]['results'][i]['result']
        assert place_response == current_place

    assert candidates_handler.times_called == 1


@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_three_places.json',
)
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
@pytest.mark.config(EATS_SURGE_FEATURE_FLAGS=TEST_FEATURE_FLAGS)
@pytest.mark.pipeline('resource_cache')
@pytest.mark.parametrize(
    ['main_place', 'expexted_values'],
    [
        (1, {'1': [22, 108], '2': [22, 108], '3': [22, 108]}),
        (
            2,
            {
                '1': ['No candidates'],
                '2': ['No candidates'],
                '3': ['No candidates'],
            },
        ),
    ],
)
async def test_lru_resource_cache(
        taxi_eda_surge_calculator,
        load_json,
        candidates,
        testpoint,
        main_place,
        expexted_values,
):
    testpoint_values = dict()

    @testpoint('cached-resource-candidates')
    def _testpoint_lru_candidates(testpoint_data):
        testpoint_values.update(testpoint_data)

    await taxi_eda_surge_calculator.invalidate_caches()

    data = {
        'place_ids': [main_place],
        'request_id': '113',
        'geohash': 'abc113',
    }
    response1 = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )

    await _testpoint_lru_candidates.wait_call()
    data = {'place_ids': [1, 2, 3], 'request_id': '113', 'geohash': 'abc113'}
    response2 = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert testpoint_values == expexted_values
