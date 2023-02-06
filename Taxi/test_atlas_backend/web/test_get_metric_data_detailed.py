from clickhouse_driver import errors as clickhouse_errors


async def test_get_metric_data_detailed(
        clickhouse_client_mock, web_app_client, patch,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (
                    ('dttm', 'UInt32'),
                    ('car_class', 'String'),
                    ('source_geoareas', 'Array(String)'),
                    ('cnt', 'UInt64'),
                ),
                (1603974600, 'econom', ['kazan', 'kazan_activation'], 3),
                (
                    1603974600,
                    'comfortplus',
                    ['kazan', 'tatarstan_activation'],
                    3,
                ),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/v1/data-access/detailed',
        json={
            'metric_id': 'z_detailed_data_airports',
            'parameters': {
                'ts': {'from': 1603974600, 'to': 1603975800},
                'source_geoareas': ['kazan', 'spb'],
            },
        },
    )
    assert result.status == 200
    data = await result.json()
    expected = {
        'meta': {
            'columns_description': [
                {'name': 'dttm', 'type_name': 'UInt32'},
                {'name': 'car_class', 'type_name': 'String'},
                {'name': 'source_geoareas', 'type_name': 'Array(String)'},
                {'name': 'cnt', 'type_name': 'UInt64'},
            ],
            'data_increment_mark': '2020-11-12T10:52:45+03:00',
        },
        'data': [
            {
                'dttm': 1603974600,
                'car_class': 'econom',
                'source_geoareas': ['kazan', 'kazan_activation'],
                'cnt': 3,
            },
            {
                'dttm': 1603974600,
                'car_class': 'comfortplus',
                'source_geoareas': ['kazan', 'tatarstan_activation'],
                'cnt': 3,
            },
        ],
    }

    assert data == expected


async def test_get_metric_data_detailed_with_exceeded_timeout(
        clickhouse_client_mock, web_app_client, patch,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/v1/data-access/detailed',
        json={
            'metric_id': 'z_detailed_data_airports',
            'parameters': {
                'ts': {'from': 1603974600, 'to': 1603975800},
                'source_geoareas': ['kazan', 'spb'],
            },
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TimeoutExceeded',
        'message': 'Timeout exceeded',
    }
