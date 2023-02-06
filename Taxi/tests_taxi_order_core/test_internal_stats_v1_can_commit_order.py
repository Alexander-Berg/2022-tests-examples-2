import pytest

# Пожалуйста, обновляйте эти числа, если меняете данные в базе для этого теста
# 1 Москва карго (1 младше 5 минут, 1 старше)
# 1 Краснодар карго
# Суммарно карго = 2

# 1 СПБ такси
# 3 Краснодар такси
# 2 Москва такси (2 по времени входят в 5 минут, еще 1 не входит)
# Суммарно такси = 6

# Суммарно все = 8


@pytest.mark.parametrize(
    'request_data, can_commit',
    [
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'taxi'},
            True,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': False,
                        'global_limit': 1,
                        'per_service': {
                            '__default__': {
                                'total': 1,
                                'per_city': {'__default__': 1},
                            },
                        },
                    },
                ),
            ],
            id='disabled_config',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'taxi'},
            False,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 1,
                                'per_city': {'__default__': 1},
                            },
                        },
                    },
                ),
            ],
            id='limited_total_and_per_city_default',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'taxi'},
            False,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 10,
                                'per_city': {'__default__': 2},
                            },
                        },
                    },
                ),
            ],
            id='limited_per_city_default',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'taxi'},
            False,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 2,
                                'per_city': {'__default__': 10},
                            },
                        },
                    },
                ),
            ],
            id='limited_total_default',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'taxi'},
            True,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 7,
                                'per_city': {'__default__': 3},
                            },
                        },
                    },
                ),
            ],
            id='not_limited_default',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'NEW', 'order_type': 'taxi'},
            True,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 7,
                                'per_city': {'__default__': 3},
                            },
                        },
                    },
                ),
            ],
            id='not_limited_some_random_city',
        ),
        pytest.param(
            {
                'order_id': 'order-id',
                'city': 'Краснодар',
                'order_type': 'taxi',
            },
            True,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 1,
                                'per_city': {'__default__': 1},
                            },
                            'taxi': {
                                'total': 7,
                                'per_city': {
                                    '__default__': 1,
                                    'Краснодар': 4,
                                    'Москва': 1,
                                },
                            },
                        },
                    },
                ),
            ],
            id='krasnodar_not_limited',
        ),
        pytest.param(
            {
                'order_id': 'order-id',
                'city': 'Краснодар',
                'order_type': 'taxi',
            },
            False,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 100,
                                'per_city': {'__default__': 100},
                            },
                            'taxi': {
                                'total': 10,
                                'per_city': {
                                    '__default__': 10,
                                    'Краснодар': 1,
                                    'Москва': 10,
                                },
                            },
                        },
                    },
                ),
            ],
            id='krasnodar_limited_per_city',
        ),
        pytest.param(
            {
                'order_id': 'order-id',
                'city': 'Краснодар',
                'order_type': 'taxi',
            },
            False,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 100,
                                'per_city': {'__default__': 100},
                            },
                            'taxi': {
                                'total': 5,
                                'per_city': {
                                    '__default__': 10,
                                    'Краснодар': 10,
                                    'Москва': 10,
                                },
                            },
                        },
                    },
                ),
            ],
            id='krasnodar_limited_total',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'taxi'},
            True,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 1,
                                'per_city': {'__default__': 1},
                            },
                            'taxi': {
                                'total': 7,
                                'per_city': {
                                    '__default__': 1,
                                    'Краснодар': 1,
                                    'Москва': 3,
                                },
                            },
                        },
                    },
                ),
            ],
            id='moscow_not_limited',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'cargo'},
            True,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 1,
                                'per_city': {'__default__': 1},
                            },
                            'taxi': {
                                'total': 1,
                                'per_city': {
                                    '__default__': 1,
                                    'Краснодар': 1,
                                    'Москва': 1,
                                },
                            },
                            'cargo': {
                                'total': 3,
                                'per_city': {
                                    '__default__': 1,
                                    'Краснодар': 1,
                                    'Москва': 2,
                                },
                            },
                        },
                    },
                ),
            ],
            id='cargo_moscow_not_limited',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'cargo'},
            False,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 9,
                        'per_service': {
                            '__default__': {
                                'total': 1,
                                'per_city': {'__default__': 1},
                            },
                            'taxi': {
                                'total': 1,
                                'per_city': {
                                    '__default__': 1,
                                    'Краснодар': 1,
                                    'Москва': 1,
                                },
                            },
                            'cargo': {
                                'total': 2,
                                'per_city': {
                                    '__default__': 1,
                                    'Краснодар': 1,
                                    'Москва': 2,
                                },
                            },
                        },
                    },
                ),
            ],
            id='cargo_moscow_limited',
        ),
        pytest.param(
            {'order_id': 'order-id', 'city': 'Москва', 'order_type': 'taxi'},
            False,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_PENDING_ORDERS_LIMITS={
                        'enabled': True,
                        'global_limit': 8,
                        'per_service': {
                            '__default__': {
                                'total': 100,
                                'per_city': {'__default__': 100},
                            },
                        },
                    },
                ),
            ],
            id='limited_globally',
        ),
    ],
)
@pytest.mark.config(
    ORDER_CORE_ORDER_LIMITS_CACHE_SETTINGS={
        'enabled': True,
        'mongo-max-time-ms': 10000,
    },
)
async def test_stats(taxi_order_core, testpoint, request_data, can_commit):
    @testpoint('too-old-limits-cache')
    def too_old_cache_data(data):
        return {}

    response = await taxi_order_core.get(
        '/internal/stats/v1/can-commit-order', params=request_data,
    )
    assert response.status_code == 200
    assert response.json() == {'can_commit': can_commit}
    assert not too_old_cache_data.has_calls


@pytest.mark.config(
    ORDER_CORE_ORDER_LIMITS_CACHE_SETTINGS={
        'enabled': True,
        'mongo-max-time-ms': 10000,
    },
    ORDER_CORE_PENDING_ORDERS_LIMITS={
        'enabled': True,
        'global_limit': 1,
        'per_service': {
            '__default__': {'total': 1, 'per_city': {'__default__': 1}},
        },
        'max_cache_age_seconds': 60,
    },
)
async def test_stats_too_old_cache(
        taxi_order_core, testpoint, taxi_config, mocked_time,
):
    @testpoint('too-old-limits-cache')
    def too_old_cache_data(data):
        return {}

    response = await taxi_order_core.get(
        '/internal/stats/v1/can-commit-order',
        params={
            'order_id': 'order-id',
            'city': 'Москва',
            'order_type': 'taxi',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'can_commit': False}
    assert not too_old_cache_data.has_calls

    taxi_config.set(
        ORDER_CORE_ORDER_LIMITS_CACHE_SETTINGS={
            'enabled': False,
            'mongo-max-time-ms': 10000,
        },
    )
    mocked_time.sleep(100)

    response = await taxi_order_core.get(
        '/internal/stats/v1/can-commit-order',
        params={
            'order_id': 'order-id',
            'city': 'Москва',
            'order_type': 'taxi',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'can_commit': True}
    assert too_old_cache_data.has_calls
