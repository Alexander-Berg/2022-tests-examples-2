from testsuite.utils import ordered_object


ENDPOINT = 'v1/parks/drivers/orders/metrics-aggregation-bulk'


async def test_empty_metrics(taxi_driver_orders_metrics):
    payload = {
        'park_id': 'park_id_1',
        'driver_ids': ['driver_id_?', 'driver_id_??'],
        'from': '2020-03-17T03:00:00+03',
        'to': '2020-03-17T04:00:00+03',
        'metrics': ['successful', 'successful_cash'],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'hourly'},
    )

    expected_response = {
        'drivers_metrics_aggregation': [
            {
                'driver_id': 'driver_id_?',
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                ],
            },
            {
                'driver_id': 'driver_id_??',
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'successful_cash', 'value': 0},
                ],
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(),
        expected_response,
        ['drivers_metrics_aggregation', 'drivers_metrics_aggregation.metrics'],
    )


async def test_hourly_one_rows(taxi_driver_orders_metrics):
    payload = {
        'park_id': 'park_id_1',
        'driver_ids': ['driver_id_1', 'driver_id_2'],
        'from': '2020-03-17T03:00:00+03',
        'to': '2020-03-17T04:00:00+03',
        'metrics': ['successful', 'successful_cash'],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'hourly'},
    )

    expected_response = {
        'drivers_metrics_aggregation': [
            {
                'driver_id': 'driver_id_1',
                'metrics': [
                    {'name': 'successful', 'value': 1},
                    {'name': 'successful_cash', 'value': 2},
                ],
            },
            {
                'driver_id': 'driver_id_2',
                'metrics': [
                    {'name': 'successful', 'value': 2},
                    {'name': 'successful_cash', 'value': 1},
                ],
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(),
        expected_response,
        ['drivers_metrics_aggregation', 'drivers_metrics_aggregation.metrics'],
    )


async def test_hourly_two_rows(taxi_driver_orders_metrics):
    payload = {
        'park_id': 'park_id_1',
        'driver_ids': ['driver_id_1', 'driver_id_2'],
        'from': '2020-03-17T03:00:00+03',
        'to': '2020-03-17T05:00:00+03',
        'metrics': ['successful', 'successful_cash', 'driver_cancelled'],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'hourly'},
    )

    expected_response = {
        'drivers_metrics_aggregation': [
            {
                'driver_id': 'driver_id_1',
                'metrics': [
                    {'name': 'successful', 'value': 2},
                    {'name': 'successful_cash', 'value': 4},
                    {'name': 'driver_cancelled', 'value': 6},
                ],
            },
            {
                'driver_id': 'driver_id_2',
                'metrics': [
                    {'name': 'successful', 'value': 2},
                    {'name': 'successful_cash', 'value': 1},
                    {'name': 'driver_cancelled', 'value': 0},
                ],
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(),
        expected_response,
        ['drivers_metrics_aggregation', 'drivers_metrics_aggregation.metrics'],
    )


async def test_daily_one_rows(
        taxi_driver_orders_metrics, mock_fleet_parks_list,
):
    payload = {
        'park_id': 'park_id_1',
        'driver_ids': ['driver_id_1', 'driver_id_2'],
        'from': '2020-03-18T00:00:00+03',
        'to': '2020-03-19T00:00:00+03',
        'metrics': ['successful', 'driver_cancelled'],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'daily'},
    )

    expected_response = {
        'drivers_metrics_aggregation': [
            {
                'driver_id': 'driver_id_1',
                'metrics': [
                    {'name': 'successful', 'value': 1},
                    {'name': 'driver_cancelled', 'value': 3},
                ],
            },
            {
                'driver_id': 'driver_id_2',
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'driver_cancelled', 'value': 0},
                ],
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(),
        expected_response,
        ['drivers_metrics_aggregation', 'drivers_metrics_aggregation.metrics'],
    )


async def test_all_rows(taxi_driver_orders_metrics, mock_fleet_parks_list):
    payload = {
        'park_id': 'park_id_1',
        'driver_ids': ['driver_id_1', 'driver_id_2', 'driver_id_?'],
        'from': '2020-03-17T00:00:00+03',
        'to': '2020-03-21T00:00:00+03',
        'metrics': ['successful', 'unknown'],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'daily'},
    )

    expected_response = {
        'drivers_metrics_aggregation': [
            {
                'driver_id': 'driver_id_1',
                'metrics': [
                    {'name': 'successful', 'value': 3},
                    {'name': 'unknown', 'value': 0},
                ],
            },
            {
                'driver_id': 'driver_id_2',
                'metrics': [
                    {'name': 'successful', 'value': 8},
                    {'name': 'unknown', 'value': 0},
                ],
            },
            {
                'driver_id': 'driver_id_?',
                'metrics': [
                    {'name': 'successful', 'value': 0},
                    {'name': 'unknown', 'value': 0},
                ],
            },
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(),
        expected_response,
        ['drivers_metrics_aggregation', 'drivers_metrics_aggregation.metrics'],
    )
