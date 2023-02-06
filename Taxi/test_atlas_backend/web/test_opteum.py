from clickhouse_driver import errors as clickhouse_errors
import pytest


@pytest.mark.config(
    ATLAS_OPTEUM={
        'metrics': {
            'cancelled_by_client': 'client_cancelled',
            'cancelled_by_driver': 'driver_cancelled',
            'successful_by_payment_0': 'successful_cash',
            'successful_orders': 'successful',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_opteum_parks(web_app_client, patch):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (
                    ('park_id', 'String'),
                    ('successful', 'UInt64'),
                    ('driver_cancelled', 'UInt64'),
                    ('successful_cash', 'UInt64'),
                    ('tz_offset', 'UInt64'),
                ),
                ('park_1', 1, 2, 3, 2),
                ('park_2', 1, 0, 0, 4),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/v1/parks/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': ['successful', 'driver_cancelled', 'successful_cash'],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert result.status == 200
    data = await result.json()
    expected = {
        'last_load_at': '2020-11-12T09:58:22+03:00',
        'parks': [
            {
                'park_id': 'park_1',
                'metrics': [
                    {'name': 'successful', 'value': 1},
                    {'name': 'driver_cancelled', 'value': 2},
                    {'name': 'successful_cash', 'value': 3},
                ],
                'tz': 2,
            },
            {
                'park_id': 'park_2',
                'metrics': [{'name': 'successful', 'value': 1}],
                'tz': 4,
            },
        ],
    }
    assert data == expected


@pytest.mark.config(
    ATLAS_OPTEUM={
        'metrics': {
            'cancelled_by_client': 'client_cancelled',
            'cancelled_by_driver': 'driver_cancelled',
            'successful_by_payment_0': 'successful_cash',
            'successful_orders': 'successful',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_opteum_parks_400(web_app_client):
    result = await web_app_client.post(
        '/v1/parks/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': ['not_existing_metric'],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert result.status == 400


@pytest.mark.config(
    ATLAS_OPTEUM={
        'metrics': {
            'cancelled_by_client': 'client_cancelled',
            'cancelled_by_driver': 'driver_cancelled',
            'successful_by_payment_0': 'successful_cash',
            'successful_orders': 'successful',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_opteum_parks_with_exceeded_timeout(web_app_client, patch):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/v1/parks/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': ['successful', 'driver_cancelled', 'successful_cash'],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }


@pytest.mark.config(
    ATLAS_OPTEUM={
        'metrics': {
            'cancelled_by_client': 'client_cancelled',
            'cancelled_by_driver': 'driver_cancelled',
            'successful_by_payment_0': 'successful_cash',
            'successful_orders': 'successful',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_opteum_drivers(web_app_client, patch):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (
                    ('park_id', 'String'),
                    ('driver_id', 'String'),
                    ('successful', 'UInt64'),
                    ('driver_cancelled', 'UInt64'),
                    ('successful_cash', 'UInt64'),
                    ('tz_offset', 'UInt64'),
                ),
                ('park_1', 'driver_1', 1, 2, 3, 2),
                ('park_1', 'driver_2', 1, 2, 3, 2),
                ('park_2', 'driver_3', 1, 0, 0, 4),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/v1/parks/drivers/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': ['successful', 'driver_cancelled', 'successful_cash'],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert result.status == 200
    data = await result.json()
    expected = {
        'drivers': [
            {
                'park_id': 'park_1',
                'driver_id': 'driver_1',
                'metrics': [
                    {'name': 'successful', 'value': 1},
                    {'name': 'driver_cancelled', 'value': 2},
                    {'name': 'successful_cash', 'value': 3},
                ],
                'tz': 2,
            },
            {
                'park_id': 'park_1',
                'driver_id': 'driver_2',
                'metrics': [
                    {'name': 'successful', 'value': 1},
                    {'name': 'driver_cancelled', 'value': 2},
                    {'name': 'successful_cash', 'value': 3},
                ],
                'tz': 2,
            },
            {
                'park_id': 'park_2',
                'driver_id': 'driver_3',
                'metrics': [{'name': 'successful', 'value': 1}],
                'tz': 4,
            },
        ],
        'last_load_at': '2020-11-12T09:58:22+03:00',
    }
    assert data == expected


@pytest.mark.config(
    ATLAS_OPTEUM={
        'metrics': {
            'cancelled_by_client': 'client_cancelled',
            'cancelled_by_driver': 'driver_cancelled',
            'successful_by_payment_0': 'successful_cash',
            'successful_orders': 'successful',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_opteum_drivers_400(web_app_client):
    result = await web_app_client.post(
        '/v1/parks/drivers/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': ['not_existing_metric'],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert result.status == 400


@pytest.mark.config(
    ATLAS_OPTEUM={
        'metrics': {
            'cancelled_by_client': 'client_cancelled',
            'cancelled_by_driver': 'driver_cancelled',
            'successful_by_payment_0': 'successful_cash',
            'successful_orders': 'successful',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_opteum_drivers_with_exceeded_timeout(web_app_client, patch):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/v1/parks/drivers/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': ['successful', 'driver_cancelled', 'successful_cash'],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }


@pytest.mark.config(
    ATLAS_OPTEUM_SAAS={
        'metrics': {
            'canceled_by_user': 'yango_cancelled_by_user',
            'completed_platform': 'yango_succesfull_platform',
            'completed_own': 'yango_successfull_own',
            'completed:vip': 'yango_successful_vip',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_opteum_saas(web_app_client, patch):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (
                    ('park_id', 'String'),
                    ('yango_cancelled_by_user', 'UInt64'),
                    ('yango_succesfull_platform', 'UInt64'),
                    ('yango_successfull_own', 'UInt64'),
                    ('yango_successful_vip', 'UInt64'),
                ),
                ('park_1', 1, 2, 3, 2),
                ('park_2', 1, 5, 3, 2),
                ('park_3', 1, 0, 0, 4),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/v1/parks/saas/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': [
                'yango_successful_vip',
                'yango_cancelled_by_user',
                'yango_succesfull_platform',
            ],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert result.status == 200
    data = await result.json()
    expected = {
        'parks': [
            {
                'park_id': 'park_1',
                'metrics': [
                    {'name': 'yango_successful_vip', 'value': 2},
                    {'name': 'yango_cancelled_by_user', 'value': 1},
                    {'name': 'yango_succesfull_platform', 'value': 2},
                ],
            },
            {
                'park_id': 'park_2',
                'metrics': [
                    {'name': 'yango_successful_vip', 'value': 2},
                    {'name': 'yango_cancelled_by_user', 'value': 1},
                    {'name': 'yango_succesfull_platform', 'value': 5},
                ],
            },
            {
                'park_id': 'park_3',
                'metrics': [
                    {'name': 'yango_successful_vip', 'value': 4},
                    {'name': 'yango_cancelled_by_user', 'value': 1},
                ],
            },
        ],
    }
    assert data == expected


@pytest.mark.config(
    ATLAS_OPTEUM_SAAS={
        'metrics': {
            'canceled_by_user': 'yango_cancelled_by_user',
            'completed_platform': 'yango_succesfull_platform',
            'completed_own': 'yango_successfull_own',
            'completed:vip': 'yango_successful_vip',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_saas_drivers_400(web_app_client):
    result = await web_app_client.post(
        '/v1/parks/saas/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': ['not_existing_metric'],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert result.status == 400

    result = await web_app_client.post(
        '/v1/parks/saas/orders/metrics',
        params={'aggregate_time_policy': 'local'},
        json={
            'metrics': ['yango_successful_vip'],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert result.status == 400


@pytest.mark.config(
    ATLAS_OPTEUM_SAAS={
        'metrics': {
            'canceled_by_user': 'yango_cancelled_by_user',
            'completed_platform': 'yango_succesfull_platform',
            'completed_own': 'yango_successfull_own',
            'completed:vip': 'yango_successful_vip',
        },
    },
)
@pytest.mark.usefixtures('clickhouse_client_mock')
async def test_opteum_saas_with_exceeded_timeout(web_app_client, patch):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/v1/parks/saas/orders/metrics',
        params={'aggregate_time_policy': 'utc'},
        json={
            'metrics': [
                'yango_successful_vip',
                'yango_cancelled_by_user',
                'yango_succesfull_platform',
            ],
            'from': '2021-03-12T05:00:00+00:00',
            'to': '2021-03-12T07:00:00+00:00',
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }
