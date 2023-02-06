from testsuite.utils import ordered_object


ENDPOINT = 'v1/parks/orders/metrics-by-intervals'


async def test_one_hourly_row(taxi_driver_orders_metrics):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-17T03:00:00+03',
        'to': '2020-03-17T04:00:00+03',
        'metrics': [
            'successful',
            'successful_cash',
            'driver_cancelled',
            'successful_econom',
            'successful_cashless',
            'successful_active_drivers',
        ],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'hourly'},
    )

    expected_response = {
        'metrics_by_intervals': [
            {
                'metrics': [
                    {'name': 'successful', 'value': 1},
                    {'name': 'successful_cash', 'value': 2},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 4},
                    {'name': 'successful_cashless', 'value': 5},
                    {'name': 'successful_active_drivers', 'value': 111},
                ],
                'from': '2020-03-17T00:00:00+00:00',
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_by_intervals.metrics'],
    )


async def test_two_hourly_row(taxi_driver_orders_metrics):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-17T03:00:00+03',
        'to': '2020-03-17T06:00:00+03',
        'metrics': [
            'successful',
            'successful_cash',
            'driver_cancelled',
            'successful_econom',
            'successful_cashless',
            'successful_active_drivers',
        ],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'hourly'},
    )

    expected_response = {
        'metrics_by_intervals': [
            {
                'metrics': [
                    {'name': 'successful', 'value': 1},
                    {'name': 'successful_cash', 'value': 2},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 4},
                    {'name': 'successful_cashless', 'value': 5},
                    {'name': 'successful_active_drivers', 'value': 111},
                ],
                'from': '2020-03-17T00:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                    {'name': 'successful_econom', 'value': 0},
                    {'name': 'successful_cashless', 'value': 0},
                    {'name': 'successful_active_drivers', 'value': 0},
                ],
                'from': '2020-03-17T01:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 5},
                    {'name': 'successful_cash', 'value': 4},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 2},
                    {'name': 'successful_cashless', 'value': 1},
                    {'name': 'successful_active_drivers', 'value': 222},
                ],
                'from': '2020-03-17T02:00:00+00:00',
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_aggregation'],
    )


async def test_five_intervals(taxi_driver_orders_metrics):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-17T02:00:00+03',
        'to': '2020-03-17T07:00:00+03',
        'metrics': [
            'successful',
            'successful_cash',
            'driver_cancelled',
            'successful_econom',
            'successful_cashless',
        ],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'hourly'},
    )

    expected_response = {
        'metrics_by_intervals': [
            {
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                    {'name': 'successful_econom', 'value': 0},
                    {'name': 'successful_cashless', 'value': 0},
                ],
                'from': '2020-03-16T23:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 1},
                    {'name': 'successful_cash', 'value': 2},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 4},
                    {'name': 'successful_cashless', 'value': 5},
                ],
                'from': '2020-03-17T00:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                    {'name': 'successful_econom', 'value': 0},
                    {'name': 'successful_cashless', 'value': 0},
                ],
                'from': '2020-03-17T01:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 5},
                    {'name': 'successful_cash', 'value': 4},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 2},
                    {'name': 'successful_cashless', 'value': 1},
                ],
                'from': '2020-03-17T02:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                    {'name': 'successful_econom', 'value': 0},
                    {'name': 'successful_cashless', 'value': 0},
                ],
                'from': '2020-03-17T03:00:00+00:00',
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_aggregation'],
    )


async def test_one_daily_row(
        taxi_driver_orders_metrics, mock_fleet_parks_list,
):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-18T00:00:00+03',
        'to': '2020-03-19T00:00:00+03',
        'metrics': [
            'successful',
            'successful_cash',
            'driver_cancelled',
            'successful_econom',
            'successful_cashless',
            'successful_active_drivers',
        ],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'daily'},
    )

    expected_response = {
        'metrics_by_intervals': [
            {
                'metrics': [
                    {'name': 'successful', 'value': 10},
                    {'name': 'successful_cash', 'value': 2},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 4},
                    {'name': 'successful_cashless', 'value': 5},
                    {'name': 'successful_active_drivers', 'value': 333},
                ],
                'from': '2020-03-17T21:00:00+00:00',
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_by_intervals.metrics'],
    )


async def test_two_daily_rows(
        taxi_driver_orders_metrics, mock_fleet_parks_list,
):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-18T00:00:00+03',
        'to': '2020-03-21T00:00:00+03',
        'metrics': [
            'successful',
            'successful_cash',
            'driver_cancelled',
            'successful_econom',
            'successful_cashless',
            'successful_active_drivers',
        ],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'daily'},
    )

    expected_response = {
        'metrics_by_intervals': [
            {
                'metrics': [
                    {'name': 'successful', 'value': 10},
                    {'name': 'successful_cash', 'value': 2},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 4},
                    {'name': 'successful_cashless', 'value': 5},
                    {'name': 'successful_active_drivers', 'value': 333},
                ],
                'from': '2020-03-17T21:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                    {'name': 'successful_econom', 'value': 0},
                    {'name': 'successful_cashless', 'value': 0},
                    {'name': 'successful_active_drivers', 'value': 0},
                ],
                'from': '2020-03-18T21:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 5},
                    {'name': 'successful_cash', 'value': 4},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 2},
                    {'name': 'successful_cashless', 'value': 1},
                    {'name': 'successful_active_drivers', 'value': 444},
                ],
                'from': '2020-03-19T21:00:00+00:00',
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_by_intervals.metrics'],
    )


async def test_all_rows(taxi_driver_orders_metrics, mock_fleet_parks_list):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-16T00:00:00+03',
        'to': '2020-03-22T00:00:00+03',
        'metrics': [
            'successful',
            'successful_cash',
            'driver_cancelled',
            'successful_econom',
            'successful_cashless',
        ],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'daily'},
    )

    expected_response = {
        'metrics_by_intervals': [
            {
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                    {'name': 'successful_econom', 'value': 0},
                    {'name': 'successful_cashless', 'value': 0},
                ],
                'from': '2020-03-15T21:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 6},
                    {'name': 'successful_cash', 'value': 6},
                    {'name': 'driver_cancelled', 'value': 6},
                    {'name': 'successful_econom', 'value': 6},
                    {'name': 'successful_cashless', 'value': 6},
                ],
                'from': '2020-03-16T21:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 10},
                    {'name': 'successful_cash', 'value': 2},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 4},
                    {'name': 'successful_cashless', 'value': 5},
                ],
                'from': '2020-03-17T21:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                    {'name': 'successful_econom', 'value': 0},
                    {'name': 'successful_cashless', 'value': 0},
                ],
                'from': '2020-03-18T21:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 5},
                    {'name': 'successful_cash', 'value': 4},
                    {'name': 'driver_cancelled', 'value': 3},
                    {'name': 'successful_econom', 'value': 2},
                    {'name': 'successful_cashless', 'value': 1},
                ],
                'from': '2020-03-19T21:00:00+00:00',
            },
            {
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                    {'name': 'successful_econom', 'value': 0},
                    {'name': 'successful_cashless', 'value': 0},
                ],
                'from': '2020-03-20T21:00:00+00:00',
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_by_intervals.metrics'],
    )
