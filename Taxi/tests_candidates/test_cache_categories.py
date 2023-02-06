import pytest


DCA_USE_CATEGORIES = {
    'categories_cache_enabled': True,
    'use_parks_from_config': False,
    'http_client_timeout_ms': 1000,
    'http_client_retries': 3,
    'parks': [],
    'categories_comparator_enabled': True,
    'categories_comparator_period_ms': 10,
}

DRIVER_CATEGORIES_API_LIMITS = {
    '/v1/drivers/categories/bulk': {
        '__default__': {'max': 20000, 'min': 1},
        'cars': {'max': 20000, 'min': 1},
        'drivers': {'max': 20000, 'min': 1},
        'parks': {'max': 20000, 'min': 1},
    },
    '__default__': {'__default__': {'max': 20000, 'min': 1}},
}


@pytest.mark.parametrize('contractor_usage_percent', [0, 100])
@pytest.mark.parametrize('car_usage_percent', [0, 100])
@pytest.mark.parametrize('park_usage_percent', [0, 100])
@pytest.mark.parametrize(
    'allowed_classes,candidates_count',
    [(['econom'], 1), (['vip'], 1), (['comfortplus'], 0)],
)
@pytest.mark.config(
    DRIVER_CATEGORIES_API_USE_CATEGORIES_IN_CANDIDATES=DCA_USE_CATEGORIES,
    EXTRA_EXAMS_BY_ZONE={},
    DRIVER_CATEGORIES_API_LIMITS=DRIVER_CATEGORIES_API_LIMITS,
)
async def test_categories_cache(
        taxi_candidates,
        driver_positions,
        allowed_classes,
        candidates_count,
        taxi_config,
        experiments3,
        contractor_usage_percent,
        car_usage_percent,
        park_usage_percent,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='candidates_categories_cache_settings',
        consumers=['candidates/user'],
        default_value={
            'enable_lazy_park': park_usage_percent == 100,
            'enable_lazy_car': car_usage_percent == 100,
            'enable_lazy_contractor': contractor_usage_percent == 100,
        },
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/class'],
        'allowed_classes': allowed_classes,
        'zone_id': 'moscow',
        'point': [55, 35],
    }
    response = await taxi_candidates.post('search', json=body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == candidates_count
