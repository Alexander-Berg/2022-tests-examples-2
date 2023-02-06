# pylint: disable=unused-variable
import json

import pytest


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(EDA_SURGE_REQUEST_CANDIDATES=True)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_history_surge(taxi_eda_surge_calculator, mockserver, load_json):
    @mockserver.json_handler('/candidates/list-profiles')
    def profiles(request):
        return

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def surge_level(request):
        assert request.json['calculator_name'] == 'calc_name'
        return [
            {
                'calculatorName': 'calc_name',
                'nativeInfo': {
                    'deliveryFee': 399.0,
                    'loadLevel': 85,
                    'surgeLevel': 3,
                },
                'taxiInfo': {'surgeLevel': 2},
                'placeId': 1,
            },
        ]

    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    response = response.json()

    expected_response = load_json('expected.json')

    assert response == expected_response
