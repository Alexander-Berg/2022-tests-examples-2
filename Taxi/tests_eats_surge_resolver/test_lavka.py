import json

import pytest


@pytest.mark.experiments3(filename='surge_exp_delivery.json')
async def test_cache_is_used(
        taxi_eats_surge_resolver, mockserver, grocery_surge, grocery_depots,
):
    surge_level = 1
    place_id = 150
    expected_place_ids = [place_id]

    grocery_depots.add_depot(depot_test_id=place_id, auto_add_zone=False)
    grocery_depots.add_depot(depot_test_id=111, auto_add_zone=False)
    await taxi_eats_surge_resolver.invalidate_caches()

    @mockserver.json_handler('/eda-surge-calculator/v1/calc-surge-grocery')
    def _mock_calc_surge(request):
        results = []
        for place_id in expected_place_ids:
            results.append(
                {
                    'place_id': place_id,
                    'result': {
                        'load_level': surge_level,
                        'delivery_zone_id': 55,
                    },
                },
            )
        return {
            'errors': [],
            'results': [
                {
                    'calculator_name': 'calc_surge_grocery_v1',
                    'results': results,
                },
            ],
        }

    request = {
        'jsonrpc': '2.0',
        'method': 'surge.FindByPlaceIds',
        'id': 1,
        'params': {'placeIds': [place_id], 'ts': '2020-02-20T10:05:41+00:00'},
    }

    print(json.dumps(request))

    response = await taxi_eats_surge_resolver.post(
        'api/v1/surge-level', json=request,
    )
    assert response.status_code == 200

    response = response.json()

    print(response)

    assert response == {
        'id': 1,
        'jsonrpc': '2.0',
        'result': [{'placeId': 150}],
    }
