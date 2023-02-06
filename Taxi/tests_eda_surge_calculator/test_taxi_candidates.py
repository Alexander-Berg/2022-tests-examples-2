# pylint: disable=redefined-outer-name, unused-variable
import json

import pytest


EDA_SURGE_CALCULATOR_CANDIDATES_EXTRA = {
    'allowed_classes': ['courier', 'express'],
    'virtual_tariffs': [
        {
            'class': 'courier',
            'special_requirements': [{'id': 'thermobag_confirmed'}],
        },
        {
            'class': 'express',
            'special_requirements': [{'id': 'thermobag_confirmed'}],
        },
    ],
    'filtration': 'searchable',
    'only_free': True,
    'data_keys': ['status', 'chain_info'],
}


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
@pytest.mark.config(EDA_SURGE_CALCULATOR_MAIN={'split_request_percentage': 0})
@pytest.mark.dispatch_settings(
    settings=[
        {
            'zone_name': 'spb',
            'tariff_name': 'courier',
            'parameters': [
                {
                    'values': {
                        'MAX_ROBOT_DISTANCE': 1000,
                        'SUPPLY_ROUTE_DISTANCE_COEFF': 2,
                    },
                },
            ],
        },
    ],
)
async def test_taxi_candidates(
        taxi_eda_surge_calculator, load_json, mockserver, experiments3,
):
    experiments3.add_config(
        consumers=['eda-surge-calculator/zone'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=EDA_SURGE_CALCULATOR_CANDIDATES_EXTRA,
        name='eda_surge_calculator_candidates_extra',
    )

    @mockserver.json_handler('/candidates/list-profiles')
    def mock_list_profiles(request):
        assert request.json == dict(
            {
                'br': [10.027449952008094, 9.976120623622515],
                'data_keys': ['status', 'chain_info'],
                'tl': [9.978653563616906, 10.024489727939985],
                'zone_id': 'spb',
            },
            **EDA_SURGE_CALCULATOR_CANDIDATES_EXTRA,
        )
        return {
            'drivers': [
                {
                    'position': [10.002, 10.002],
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
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
                    'position': [10.000, 10.000],
                    'id': 'dbid1_uuid1',
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'status': {
                        'status': 'busy',
                        'orders': [],
                        'driver': 'verybusy',
                        'taximeter': 'busy',
                    },
                },
                {
                    'position': [10.020, 10.020],
                    'id': 'dbid2_uuid2',
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                },
                {
                    'position': [10.005, 10.001],
                    'id': 'dbid3_uuid3',
                    'dbid': 'dbid3',
                    'uuid': 'uuid3',
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                },
            ],
        }

    await taxi_eda_surge_calculator.invalidate_caches()
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps({'place_ids': [1]}),
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected.json')
    assert mock_list_profiles.times_called == 1


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache_2.json')
@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
@pytest.mark.config(EDA_SURGE_CALCULATOR_MAIN={'split_request_percentage': 0})
@pytest.mark.config(
    EDA_SURGE_CACHE_CANDIDATES={
        'enabled': True,
        'updates_enabled': True,
        'queue_rps': 30,
        'queue_size': 100,
        'timeout_ms': 1000,
    },
)
@pytest.mark.dispatch_settings(
    settings=[
        {
            'zone_name': 'spb',
            'tariff_name': 'courier',
            'parameters': [
                {
                    'values': {
                        'MAX_ROBOT_DISTANCE': 2000,
                        'SUPPLY_ROUTE_DISTANCE_COEFF': 1,
                    },
                },
            ],
        },
        {
            'zone_name': '__default__',
            'tariff_name': 'courier',
            'parameters': [
                {
                    'values': {
                        'MAX_ROBOT_DISTANCE': 2000,
                        'SUPPLY_ROUTE_DISTANCE_COEFF': 1.5,
                    },
                },
            ],
        },
    ],
)
async def test_taxi_candidates_cache(
        taxi_eda_surge_calculator, load_json, mockserver, experiments3,
):
    experiments3.add_config(
        consumers=['eda-surge-calculator/zone'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=EDA_SURGE_CALCULATOR_CANDIDATES_EXTRA,
        name='eda_surge_calculator_candidates_extra',
    )

    @mockserver.json_handler('/candidates/list-profiles')
    def mock_list_profiles(request):
        return {
            'drivers': [
                {
                    'position': [9.999, 9.999],
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
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
                    'position': [10.002, 10.002],
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                },
                {
                    'position': [10.000, 10.000],
                    'id': 'dbid1_uuid1',
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'status': {
                        'status': 'busy',
                        'orders': [],
                        'driver': 'verybusy',
                        'taximeter': 'busy',
                    },
                },
                {
                    'position': [10.013, 10.012],
                    'id': 'dbid2_uuid2',
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                },
                {
                    'position': [11.005, 11.001],
                    'id': 'dbid3_uuid3',
                    'dbid': 'dbid3',
                    'uuid': 'uuid3',
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                },
            ],
        }

    await taxi_eda_surge_calculator.invalidate_caches()
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps({'place_ids': [1, 2, 3]}),
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_2.json')
    assert mock_list_profiles.times_called == 2
