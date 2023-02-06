from testsuite.utils import ordered_object


ENDPOINT = 'v1/parks/orders/metrics-aggregation'


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
        ],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'hourly'},
    )

    expected_response = {
        'metrics_aggregation': [
            {'name': 'successful', 'value': 1},
            {'name': 'successful_cash', 'value': 2},
            {'name': 'driver_cancelled', 'value': 3},
            {'name': 'successful_econom', 'value': 4},
            {'name': 'successful_cashless', 'value': 5},
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_aggregation'],
    )


async def test_two_hourly_rows(taxi_driver_orders_metrics):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-17T03:00:00+03',
        'to': '2020-03-17T05:00:00+03',
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
        'metrics_aggregation': [
            {'name': 'successful', 'value': 2},
            {'name': 'successful_cash', 'value': 4},
            {'name': 'driver_cancelled', 'value': 6},
            {'name': 'successful_econom', 'value': 8},
            {'name': 'successful_cashless', 'value': 10},
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
        ],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'daily'},
    )

    expected_response = {
        'metrics_aggregation': [
            {'name': 'successful', 'value': 1},
            {'name': 'successful_cash', 'value': 2},
            {'name': 'driver_cancelled', 'value': 3},
            {'name': 'successful_econom', 'value': 4},
            {'name': 'successful_cashless', 'value': 5},
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_aggregation'],
    )


async def test_two_daily_rows(
        taxi_driver_orders_metrics, mock_fleet_parks_list,
):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-18T00:00:00+03',
        'to': '2020-03-20T00:00:00+03',
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
        'metrics_aggregation': [
            {'name': 'successful', 'value': 2},
            {'name': 'successful_cash', 'value': 4},
            {'name': 'driver_cancelled', 'value': 6},
            {'name': 'successful_econom', 'value': 8},
            {'name': 'successful_cashless', 'value': 10},
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_aggregation'],
    )


async def test_all_rows(taxi_driver_orders_metrics, mock_fleet_parks_list):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-17T00:00:00+03',
        'to': '2020-03-20T00:00:00+03',
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
        'metrics_aggregation': [
            {'name': 'successful', 'value': 4},
            {'name': 'successful_cash', 'value': 8},
            {'name': 'driver_cancelled', 'value': 12},
            {'name': 'successful_econom', 'value': 16},
            {'name': 'successful_cashless', 'value': 20},
        ],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_aggregation'],
    )


async def test_unknown_hourly_metrics(taxi_driver_orders_metrics):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-21T10:00:00+03',
        'to': '2020-03-21T12:00:00+03',
        'metrics': ['unknown'],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'hourly'},
    )

    expected_response = {
        'metrics_aggregation': [{'name': 'unknown', 'value': 0}],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_aggregation'],
    )


async def test_unknown_daily_metrics(
        taxi_driver_orders_metrics, mock_fleet_parks_list,
):
    payload = {
        'park_id': 'park_id_1',
        'from': '2020-03-21T00:00:00+03',
        'to': '2020-03-25T00:00:00+03',
        'metrics': ['unknown'],
    }

    response = await taxi_driver_orders_metrics.post(
        ENDPOINT, json=payload, params={'type': 'daily'},
    )

    expected_response = {
        'metrics_aggregation': [{'name': 'unknown', 'value': 0}],
    }

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['metrics_aggregation'],
    )
