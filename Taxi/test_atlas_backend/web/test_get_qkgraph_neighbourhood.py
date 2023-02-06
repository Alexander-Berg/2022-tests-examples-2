from clickhouse_driver import errors as clickhouse_errors


async def test_qk_graph_neighbourhood(
        clickhouse_client_mock, atlas_blackbox_mock, patch, web_app_client,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data_ = [
                (
                    ('qk_from', 'String'),
                    ('avg_dist', 'Float64'),
                    ('cnt', 'Uint32'),
                ),
                ('1203101011220112', 8538.585, 2),
                ('1203101010333221', 8696.5648, 75),
                ('1203101012111301', 5183.658916083921, 286),
            ]
            for item in data_:
                yield item

        return _result()

    response = await web_app_client.post(
        '/api/qk_graph/neighbourhood',
        json={
            'lat': 55.754695207989954,
            'lon': 37.65033558011056,
            'type': 'distance',
            'max_value': 10000,
        },
    )
    assert response.status == 200

    data = await response.json()
    by_quadkey = {item['quadkey']: item['values'] for item in data}
    assert by_quadkey == {
        '1203101011220112': [8538.585, 2],
        '1203101010333221': [8696.5648, 75],
        '1203101012111301': [5183.658916083921, 286],
    }


async def test_qk_graph_neighbourhood_with_exceeded_timeout(
        clickhouse_client_mock, atlas_blackbox_mock, patch, web_app_client,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/api/qk_graph/neighbourhood',
        json={
            'lat': 55.754695207989954,
            'lon': 37.65033558011056,
            'type': 'distance',
            'max_value': 10000,
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TimeoutExceeded',
        'message': 'Timeout exceeded',
    }
