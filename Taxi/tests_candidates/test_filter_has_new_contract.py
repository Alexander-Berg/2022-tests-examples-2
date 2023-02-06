import pytest


_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_filter_has_new_contract(
        taxi_candidates, driver_positions, chain_busy_drivers,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid1_uuid2', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
        ],
    )
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 10,
                'left_distance': 100,
                'destination': [55, 35],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'tl': [36.464186, 56.286216],
        'br': [39.438735, 54.985976],
        'point': [37.630971, 55.743789],
        'logistic': {'check_new_contract': True},
    }
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200, response.text
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['id'] == 'dbid0_uuid1'

    del request_body['logistic']
    request_body['order'] = {'request': {'check_new_logistic_contract': True}}
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200, response.text
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 1
    assert candidates[0]['id'] == 'dbid0_uuid1'


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    EXTRA_EXAMS_BY_ZONE={},
    CORP_RESALE_LOGISTICS_TO_TAXI_BY_COUNTRIES={
        '__default__': {'is_enabled': False},
        'rus': {'is_enabled': True},
    },
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'logistic_econom': {
            'client': 'delivery_client_b2b_logistics_payment',
            'partner': 'delivery_park_b2b_logistics_payment',
        },
        'logistic_vip': {
            'client': 'delivery_client_b2b_logistics_payment',
            'partner': 'delivery_park_b2b_logistics_payment',
        },
    },
)
async def test_disable_by_country(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.309, 55.566]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.310, 55.567]},
        ],
    )
    body = {
        'allowed_classes': ['econom', 'vip'],
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.311, 55.568],
        'order': {'request': {'check_new_logistic_contract': True}},
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200, response.text
    assert 'candidates' in response.json()
    candidates = response.json()['candidates']
    assert len(candidates) == 2
