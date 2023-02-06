import pytest


@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_use_graph(
        taxi_candidates, driver_positions, dispatch_settings_mocks,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625344, 55.755430]},
        ],
    )

    dispatch_settings_mocks.set_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'PEDESTRIAN_DISABLED': True,
                            'MAX_ROBOT_TIME': 400,
                            'PAID_SUPPLY_MAX_ROUTE_TIME': 1000,
                        },
                    },
                ],
            },
        ],
    )

    body = {
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert not candidates

    body = {
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'order': {
            'fixed_price': {
                'paid_supply_price': 12,
                'paid_supply_info': {'time': 1000, 'distance': 2000},
            },
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 2

    body = {
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'order': {
            'fixed_price': {
                'paid_supply_info': {'time': 1000, 'distance': 2000},
            },
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert not candidates

    body = {
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'extra_data': {'multiclass': {'paid_supply_classes': ['econom']}},
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert not candidates

    body = {
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'order': {
            'fixed_price': {
                'paid_supply_info': {'time': 1000, 'distance': 2000},
            },
        },
        'extra_data': {'multiclass': {'paid_supply_classes': ['econom']}},
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['uuid'] == 'uuid0'

    body = {
        'allowed_classes': ['econom', 'uberblack'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'order': {
            'fixed_price': {
                'paid_supply_price': 12,
                'paid_supply_info': {'time': 1000, 'distance': 2000},
            },
        },
        'extra_data': {'multiclass': {'paid_supply_classes': ['econom']}},
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['uuid'] == 'uuid0'
