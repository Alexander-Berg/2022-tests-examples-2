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
                },
                {
                    # skipped too_far
                    'position': [10.020, 10.020],
                    'id': 'dbid0_uuid1',
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
                    # inside id-108
                    'position': [10.005, 10.001],
                    'id': 'dbid0_uuid2',
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


@pytest.mark.config(
    EDA_SURGE_REQUEST_CANDIDATES=True, EDA_SUPPLY_DETAILED_LOGS_PLACES=[1],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_get_extended_supply(
        taxi_eda_surge_calculator, candidates, load_json,
):
    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1], 'radius': 2100}
    response = await taxi_eda_surge_calculator.post(
        'v1/extended-supply', data=json.dumps(data),
    )
    assert response.status_code == 200
    response = response.json()

    expected_response = load_json('expected.json')

    assert response == expected_response
