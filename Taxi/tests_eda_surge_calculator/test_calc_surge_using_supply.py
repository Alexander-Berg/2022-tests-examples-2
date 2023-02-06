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


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    EDA_SURGE_REQUEST_CANDIDATES=True, EDA_SUPPLY_DETAILED_LOGS_PLACES=[1],
)
@pytest.mark.now('2020-04-12T12:00:00+03:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calc_surge1(taxi_eda_surge_calculator, candidates):
    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    expected_response = {
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
    response = response.json()
    _sort_response(response)
    _sort_response(expected_response)

    print(response)
    assert response == expected_response


@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
@pytest.mark.now('2020-04-12T12:00:00+03:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_candidates_error(
        taxi_eda_surge_calculator, candidates, mockserver,
):
    # we should interpret 404 error as empty response
    @mockserver.handler('/candidates/list-profiles')
    def search_handler(request):
        return mockserver.make_response(json={'code': 'Not found'}, status=404)

    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    expected_response = {
        'results': [
            {
                'calculator_name': 'calc_surge',
                'results': [
                    {
                        'place_id': 1,
                        'result': {
                            'load_level': 114.28571428571428,
                            'additional_time_percents': 60,
                            'busy': 0,
                            'delivery_fee': 200,
                            'surge_level': 3,
                            'free': 0,
                        },
                    },
                ],
            },
        ],
        'errors': [],
    }
    response = response.json()
    _sort_response(response)
    _sort_response(expected_response)
    assert response == expected_response
