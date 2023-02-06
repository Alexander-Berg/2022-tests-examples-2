# pylint: disable=redefined-outer-name, unused-variable
import json

import pytest


@pytest.fixture
def candidates(mockserver):
    @mockserver.json_handler('/candidates/list-profiles')
    def search_handler(request):
        return {
            'drivers': [
                {
                    'position': [10.001, 10.001],
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
            ],
        }


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
            if courier_activity_context.get_count() <= 2:
                return mockserver.make_response('bad request', status=400)

            if courier_activity_context.get_count() == 3:
                return {
                    'payload': [
                        {
                            'courierId': 33,
                            'regionId': 1,
                            'activeDeliveries': [],
                        },
                    ],
                    'meta': {'count': 1},
                }

            return {
                'payload': [
                    {'courierId': 11, 'regionId': 1, 'activeDeliveries': []},
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


OLD_CACHE_EXPECTED_RESPONSE = {
    'results': [
        {
            'calculator_name': 'calc_surge',
            'results': [
                {
                    'place_id': 1,
                    'result': {
                        'load_level': 72.72727272727273,
                        'additional_time_percents': 60,
                        'busy': 0,
                        'delivery_fee': 200,
                        'surge_level': 3,
                        'free': 1,
                    },
                },
            ],
        },
    ],
    'errors': [],
}

NEW_CACHE_EXPECTED_RESPONSE = {
    'results': [
        {
            'calculator_name': 'calc_surge',
            'results': [
                {
                    'place_id': 1,
                    'result': {
                        'load_level': 72.72727272727273,
                        'additional_time_percents': 60,
                        'busy': 0,
                        'delivery_fee': 200,
                        'surge_level': 3,
                        'free': 1,
                    },
                },
            ],
        },
    ],
    'errors': [],
}


@pytest.mark.parametrize(
    ['failed_requests_limit', 'expected_response'],
    [('0', OLD_CACHE_EXPECTED_RESPONSE), ('5', NEW_CACHE_EXPECTED_RESPONSE)],
)
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    EDA_SURGE_REQUEST_CANDIDATES=True, EDA_SUPPLY_DETAILED_LOGS_PLACES=[1],
)
@pytest.mark.now('2020-04-12T12:00:00+03:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calc_surge2(
        taxi_eda_surge_calculator,
        eda_courier_activity,
        candidates,
        expected_response,
        taxi_config,
        failed_requests_limit,
):
    taxi_config.set_values(
        {
            'EDA_SURGE_CACHE_COURIERS_DESTINATIONS': {
                'fetch_chunk_size': 1,
                'failed_requests_limit': int(failed_requests_limit),
            },
        },
    )

    await taxi_eda_surge_calculator.invalidate_caches()

    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200

    response = response.json()
    _sort_response(response)
    _sort_response(expected_response)

    assert response == expected_response


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_region_id_cache(taxi_eda_surge_calculator, testpoint):
    @testpoint('cached-region-ids')
    def _testpoint_region_id(data):
        assert sorted(data['regions']) == [1, 2]

    await taxi_eda_surge_calculator.invalidate_caches()

    assert _testpoint_region_id.times_called == 1
