import pytest


PARKS_AGGREGATION_URL = 'v1/parks/orders/metrics-aggregation'
PARKS_BY_INTERVALS_URL = 'v1/parks/orders/metrics-by-intervals'

DRIVERS_AGGREGATION_URL = 'v1/parks/drivers/orders/metrics-aggregation'
DRIVERS_BY_INTERVALS_URL = 'v1/parks/drivers/orders/metrics-by-intervals'


@pytest.mark.parametrize(
    'begin, end, url, message',
    [
        (
            '2021-03-21T10:30:00+05',
            '2020-03-21T11:30:00+05',
            PARKS_AGGREGATION_URL,
            '\'from\' time must be aligned on a hour boundary',
        ),
        (
            '2021-03-21T10:00:00-05',
            '2020-03-21T10:30:00-05',
            PARKS_AGGREGATION_URL,
            '\'to\' time must be aligned on a hour boundary',
        ),
        (
            '2021-03-21T11:00:00+05',
            '2020-03-21T10:00:00+05',
            PARKS_AGGREGATION_URL,
            '\'from\' time must be less than \'to\' time',
        ),
        (
            '2021-03-21T10:30:00-05',
            '2020-03-21T10:00:00-05',
            PARKS_BY_INTERVALS_URL,
            '\'from\' time must be aligned on a hour boundary',
        ),
        (
            '2021-03-21T10:00:00+05',
            '2020-03-21T10:30:00+05',
            PARKS_BY_INTERVALS_URL,
            '\'to\' time must be aligned on a hour boundary',
        ),
        (
            '2021-03-21T11:00:00-05',
            '2020-03-21T10:00:00-05',
            PARKS_BY_INTERVALS_URL,
            '\'from\' time must be less than \'to\' time',
        ),
    ],
)
async def test_parks_hour_range_validate(
        taxi_driver_orders_metrics, begin, end, url, message,
):
    payload = {
        'park_id': 'park_id_1',
        'from': begin,
        'to': end,
        'metrics': ['metric_name'],
    }

    response = await taxi_driver_orders_metrics.post(
        url, json=payload, params={'type': 'hourly'},
    )

    expected_response = {'code': '400', 'message': message}

    assert response.status_code == 400, response.text
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'begin, end, url, message',
    [
        (
            '2020-03-21T10:30:00+05',
            '2020-03-21T11:30:00+05',
            DRIVERS_AGGREGATION_URL,
            '\'from\' time must be aligned on a hour boundary',
        ),
        (
            '2020-03-21T10:00:00-05',
            '2020-03-21T10:30:00-05',
            DRIVERS_AGGREGATION_URL,
            '\'to\' time must be aligned on a hour boundary',
        ),
        (
            '2020-03-21T11:00:00+05',
            '2020-03-21T10:00:00+05',
            DRIVERS_AGGREGATION_URL,
            '\'from\' time must be less than \'to\' time',
        ),
        (
            '2020-03-21T10:30:00-05',
            '2020-03-21T10:00:00-05',
            DRIVERS_BY_INTERVALS_URL,
            '\'from\' time must be aligned on a hour boundary',
        ),
        (
            '2020-03-21T10:00:00+05',
            '2020-03-21T10:30:00+05',
            DRIVERS_BY_INTERVALS_URL,
            '\'to\' time must be aligned on a hour boundary',
        ),
        (
            '2020-03-21T11:00:00-05',
            '2020-03-21T10:00:00-05',
            DRIVERS_BY_INTERVALS_URL,
            '\'from\' time must be less than \'to\' time',
        ),
    ],
)
async def test_drivers_hour_range_validate(
        taxi_driver_orders_metrics, begin, end, url, message,
):
    payload = {
        'park_id': 'park_id_1',
        'driver_id': 'driver_id_1',
        'from': begin,
        'to': end,
        'metrics': ['metric_name'],
    }

    response = await taxi_driver_orders_metrics.post(
        url, json=payload, params={'type': 'hourly'},
    )

    expected_response = {'code': '400', 'message': message}

    assert response.status_code == 400, response.text
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'begin, end, url, message',
    [
        (
            '2020-03-21T00:00:00+00',
            '2020-03-21T11:30:00+03',
            PARKS_AGGREGATION_URL,
            '\'from\' time must be aligned on a day boundary',
        ),
        (
            '2020-03-21T00:00:00+03',
            '2020-03-21T00:00:00+00',
            PARKS_AGGREGATION_URL,
            '\'to\' time must be aligned on a day boundary',
        ),
        (
            '2020-03-21T00:00:00+03',
            '2020-03-21T00:00:00+03',
            PARKS_AGGREGATION_URL,
            '\'from\' time must be less than \'to\' time',
        ),
        (
            '2020-03-21T00:00:00+00',
            '2020-03-21T10:00:00+03',
            PARKS_BY_INTERVALS_URL,
            '\'from\' time must be aligned on a day boundary',
        ),
        (
            '2020-03-21T00:00:00+03',
            '2020-03-21T00:00:00+00',
            PARKS_BY_INTERVALS_URL,
            '\'to\' time must be aligned on a day boundary',
        ),
        (
            '2020-03-21T00:00:00+03',
            '2020-03-21T00:00:00+03',
            PARKS_BY_INTERVALS_URL,
            '\'from\' time must be less than \'to\' time',
        ),
    ],
)
async def test_parks_day_range_validate(
        taxi_driver_orders_metrics,
        mock_fleet_parks_list,
        begin,
        end,
        url,
        message,
):
    payload = {
        'park_id': 'park_id_1',
        'from': begin,
        'to': end,
        'metrics': ['metric_name'],
    }

    response = await taxi_driver_orders_metrics.post(
        url, json=payload, params={'type': 'daily'},
    )

    expected_response = {'code': '400', 'message': message}

    assert response.status_code == 400, response.text
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'begin, end, url, message',
    [
        (
            '2020-03-21T00:00:00+00',
            '2020-03-21T11:30:00+03',
            DRIVERS_AGGREGATION_URL,
            '\'from\' time must be aligned on a day boundary',
        ),
        (
            '2020-03-21T00:00:00+03',
            '2020-03-21T00:00:00+00',
            DRIVERS_AGGREGATION_URL,
            '\'to\' time must be aligned on a day boundary',
        ),
        (
            '2020-03-21T00:00:00+03',
            '2020-03-21T00:00:00+03',
            DRIVERS_AGGREGATION_URL,
            '\'from\' time must be less than \'to\' time',
        ),
        (
            '2020-03-21T00:00:00+00',
            '2020-03-21T10:00:00+03',
            DRIVERS_BY_INTERVALS_URL,
            '\'from\' time must be aligned on a day boundary',
        ),
        (
            '2020-03-21T00:00:00+03',
            '2020-03-21T00:00:00+00',
            DRIVERS_BY_INTERVALS_URL,
            '\'to\' time must be aligned on a day boundary',
        ),
        (
            '2020-03-21T00:00:00+03',
            '2020-03-21T00:00:00+03',
            DRIVERS_BY_INTERVALS_URL,
            '\'from\' time must be less than \'to\' time',
        ),
    ],
)
async def test_drives_day_range_validate(
        taxi_driver_orders_metrics,
        mock_fleet_parks_list,
        begin,
        end,
        url,
        message,
):
    payload = {
        'park_id': 'park_id_1',
        'driver_id': 'driver_id_1',
        'from': begin,
        'to': end,
        'metrics': ['metric_name'],
    }

    response = await taxi_driver_orders_metrics.post(
        url, json=payload, params={'type': 'daily'},
    )

    expected_response = {'code': '400', 'message': message}

    assert response.status_code == 400, response.text
    assert response.json() == expected_response
