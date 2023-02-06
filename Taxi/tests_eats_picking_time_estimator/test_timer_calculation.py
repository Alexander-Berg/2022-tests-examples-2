import pytest


def _build_config(
        load_json,
        timer_type,
        countable_time,
        weighted_time,
        min_value=None,
        max_value=None,
):
    config = load_json('config.json')
    timer = config['configs'][0]['default_value']['timers'][0]
    timer['type'] = timer_type
    timer['coefficients']['countable_item_picking_time'] = countable_time
    timer['coefficients']['weighted_item_picking_time'] = weighted_time
    timer['coefficients']['min_value'] = min_value
    timer['coefficients']['max_value'] = max_value
    return config


@pytest.mark.parametrize(
    'countable_item_picking_size, weighted_item_picking_size, '
    'countable_item_picking_time, weighted_item_picking_time, expected',
    [
        (1, 1, 1, 1, 2),
        (1, 1, 2, 3, 5),
        (2, 3, 4, 5, 23),
        (0, 1, 2, 3, 3),
        (1, 0, 2, 3, 2),
    ],
)
async def test_timer_calculation_only_exp3_simple_formula(
        taxi_eats_picking_time_estimator,
        load_json,
        load_order,
        experiments3,
        countable_item_picking_size,
        weighted_item_picking_size,
        countable_item_picking_time,
        weighted_item_picking_time,
        expected,
):
    timer_type = 'test-timer'
    order = load_order('test_order.json')

    items = order['items']
    weighted_item = items.pop(0)
    countable_item = items.pop(0)
    items.extend([weighted_item] * weighted_item_picking_size)
    items.extend([countable_item] * countable_item_picking_size)

    experiments3.add_experiments_json(
        _build_config(
            load_json,
            timer_type,
            countable_time=countable_item_picking_time,
            weighted_time=weighted_item_picking_time,
        ),
    )
    await taxi_eats_picking_time_estimator.invalidate_caches()

    response = await taxi_eats_picking_time_estimator.post(
        '/api/v1/timer/calculate-duration',
        json={'timer_type': timer_type, 'order': order},
    )
    assert response.status == 200
    assert response.json()['eta_seconds'] == expected


async def test_timer_calculation_kwargs(
        taxi_eats_picking_time_estimator, load_json, load_order, experiments3,
):
    timer_type = 'test-timer'
    order = load_order('test_order.json')
    del order['picker_id']
    del order['flow_type']

    experiments3.add_experiments_json(
        _build_config(
            load_json, timer_type, countable_time=60, weighted_time=60,
        ),
    )
    await taxi_eats_picking_time_estimator.invalidate_caches()

    response = await taxi_eats_picking_time_estimator.post(
        '/api/v1/timer/calculate-duration',
        json={'timer_type': timer_type, 'order': order},
    )
    assert response.status == 200


async def test_only_config_no_timer_404(
        taxi_eats_picking_time_estimator, load_json, load_order, experiments3,
):
    experiments3.add_experiments_json(
        _build_config(load_json, 'timer_picking', 1, 0),
    )
    await taxi_eats_picking_time_estimator.invalidate_caches()

    order = load_order('test_order.json')
    response = await taxi_eats_picking_time_estimator.post(
        '/api/v1/timer/calculate-duration',
        json={'timer_type': 'test-timer', 'order': order},
    )
    assert response.status == 404
    assert response.json()['code'] == 'TIMER_TYPE_NOT_FOUND'


async def test_no_config_404(
        taxi_eats_picking_time_estimator, load_json, load_order, experiments3,
):
    await taxi_eats_picking_time_estimator.invalidate_caches()

    order = load_order('test_order.json')
    response = await taxi_eats_picking_time_estimator.post(
        '/api/v1/timer/calculate-duration',
        json={'timer_type': 'test-timer', 'order': order},
    )
    assert response.status == 404
    assert response.json()['code'] == 'CONFIG_FETCH_FAILURE'


@pytest.mark.parametrize(
    'countable_item_picking_time, weighted_item_picking_time, expected',
    [(10, 20, 15), (1, 2, 10)],
)
async def test_response_clamp(
        taxi_eats_picking_time_estimator,
        load_json,
        load_order,
        experiments3,
        countable_item_picking_time,
        weighted_item_picking_time,
        expected,
):

    order = load_order('test_order.json')

    experiments3.add_experiments_json(
        _build_config(
            load_json,
            'test-timer',
            countable_time=countable_item_picking_time,
            weighted_time=weighted_item_picking_time,
            min_value=10,
            max_value=15,
        ),
    )
    await taxi_eats_picking_time_estimator.invalidate_caches()

    response = await taxi_eats_picking_time_estimator.post(
        '/api/v1/timer/calculate-duration',
        json={'timer_type': 'test-timer', 'order': order},
    )
    assert response.json()['eta_seconds'] == expected


@pytest.mark.parametrize(
    'test, countable_item_picking_time, weighted_item_picking_time, expected',
    [
        ('test_order.json', 10, 20, 15),
        ('test_order_with_picked_item.json', 10, 20, 15),
    ],
)
async def test_estimate_with_picked_items(
        taxi_eats_picking_time_estimator,
        test,
        load_json,
        load_order,
        experiments3,
        countable_item_picking_time,
        weighted_item_picking_time,
        expected,
):

    order = load_order(test)

    experiments3.add_experiments_json(
        _build_config(
            load_json,
            'test-timer',
            countable_time=countable_item_picking_time,
            weighted_time=weighted_item_picking_time,
            min_value=10,
            max_value=15,
        ),
    )
    await taxi_eats_picking_time_estimator.invalidate_caches()

    response = await taxi_eats_picking_time_estimator.post(
        '/api/v1/timer/calculate-duration',
        json={'timer_type': 'test-timer', 'order': order},
    )
    assert response.json()['eta_seconds'] == expected
