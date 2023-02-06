# pylint: disable=redefined-outer-name, unused-variable
import json

import pytest


@pytest.fixture
def eda_candidates(mockserver):
    @mockserver.json_handler('/eda-candidates/search')
    def search_handler(request):
        return {
            'candidates': [
                {'id': '11', 'position': [10.002, 10.002]},
                # unexpected courier, should not be counted
                {'id': '666', 'position': [10.002, 10.002]},
                # courier with region_id=2, should not be counted
                {'id': '33', 'position': [10.002, 10.002]},
            ],
        }


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
async def test_calc_extended_surge(
        taxi_eda_surge_calculator, eda_candidates, load_json, mockserver,
):
    seen_request = []

    @mockserver.json_handler('/candidates/list-profiles')
    def search_handler(request):

        assert request.json['zone_id'] == 'spb'
        seen_request.append(
            (tuple(request.json['tl']), tuple(request.json['br'])),
        )
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

    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    response = response.json()

    expected_response = load_json('expected.json')

    assert response == expected_response

    assert len(seen_request) == 4


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
@pytest.mark.config(
    EDA_SURGE_CALCULATOR_MAIN={
        'split_request_percentage': 0,
        'only_couriers_with_active_shift': True,
    },
)
async def test_calc_extended_surge_not_split(
        taxi_eda_surge_calculator, eda_candidates, load_json, mockserver,
):
    seen_request = []

    @mockserver.json_handler('/candidates/list-profiles')
    def search_handler(request):

        assert request.json['zone_id'] == 'spb'
        seen_request.append(
            (tuple(request.json['tl']), tuple(request.json['br'])),
        )
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

    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    response = response.json()

    expected_response = load_json('expected.json')

    assert response == expected_response
    assert len(seen_request) == 1
