from clickhouse_driver import errors as clickhouse_errors
import pytest


async def test_get_metric_map(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (
                    ('quadkey', 'String'),
                    ('value_0', 'UInt64'),
                    ('value_1', 'UInt64'),
                ),
                ('12031010130002300', 22, 11),
                (None, 12, None),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/map',
        json={
            'city': 'Москва',
            'car_class': ['any', 'econom'],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'granularity': '1',
            'metrics': ['requests_share_found', 'requests_share_found'],
            'quadkeys': [
                '120310101300023000',
                '120310101300023001',
                '120310101300023002',
                '120310101300023003',
            ],
            'utcoffset': 3,
            'corp_type': 'all',
            'cell_size': 17,
            'payment_type': None,
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected = [
        {'quadkey': '12031010130002300', 'values': [22.0, 11.0]},
        {'quadkey': None, 'values': [12.0, None]},
    ]
    assert data == expected


@pytest.mark.config(
    ATLAS_BACKEND_CHYT_CLIENT_QOS={
        '__default__': {
            'attempts': 1,
            'retry-delay-ms': 300,
            'timeout-ms': 60000,
        },
    },
)
async def test_get_metric_map_chyt(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('yt.clickhouse.execute')
    def _execute(*args, **kwargs):
        return [
            {'value_0': 120, 'quadkey': '12031010121111'},
            {'value_0': 140, 'quadkey': '12031010121112'},
        ]

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (('quadkey', 'String'), ('value_1', 'UInt64')),
                ('12031010121111', 22),
                ('12031010121112', 12),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/map',
        json={
            'city': 'Москва',
            'car_class': ['any', 'any'],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'granularity': '2',
            'metrics': ['chyt_sum_fact_km', 'requests_share_found'],
            'utcoffset': 3,
            'quadkeys': ['12031010121111', '12031010121112'],
            'corp_type': 'all',
            'cell_size': 14,
            'payment_type': None,
        },
    )
    data = await result.json()
    assert result.status == 200, await result.text()
    expected = [
        {'quadkey': '12031010121111', 'values': [120, 22]},
        {'quadkey': '12031010121112', 'values': [140, 12]},
    ]
    assert data == expected


@pytest.mark.parametrize(
    'geonodes,query_pattern',
    (
        pytest.param(
            [{'name': 'br_moscow', 'type': 'agglomeration'}],
            'nearest_zone IN (\'moscow\')',
        ),
        pytest.param(
            [{'name': 'fi_russia_macro', 'type': 'geo_node'}],
            'nearest_zone IN (\'kolpino\', \'spb\')',
        ),
    ),
)
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_get_metric_map_geonodes(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        geonodes,
        query_pattern,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        query = args[0] if args else kwargs['query']
        assert query_pattern in query

        async def _result():
            data = [
                (
                    ('quadkey', 'String'),
                    ('value_0', 'UInt64'),
                    ('value_1', 'UInt64'),
                ),
                ('12031010130002300', 22, 11),
                (None, 12, None),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/map',
        json={
            'geonodes': geonodes,
            'car_class': ['any', 'econom'],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'granularity': '1',
            'metrics': ['requests_share_found', 'requests_share_found'],
            'quadkeys': [
                '120310101300023000',
                '120310101300023001',
                '120310101300023002',
                '120310101300023003',
            ],
            'utcoffset': 3,
            'corp_type': 'all',
            'cell_size': 17,
            'payment_type': None,
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected = [
        {'quadkey': '12031010130002300', 'values': [22.0, 11.0]},
        {'quadkey': None, 'values': [12.0, None]},
    ]
    assert data == expected


@pytest.mark.pgsql('taxi_db_postgres_atlas_backend', files=['pg_source.sql'])
async def test_get_metric_with_source(
        web_app_client, patch, atlas_blackbox_mock,
):
    @patch('yt.clickhouse.execute')
    def _execute(*args, **kwargs):
        return [
            {'quadkey': '120310101300020', 'value_0': '66078.34831914098'},
            {'quadkey': '120310101300021', 'value_0': '60208.49186579521'},
            {'quadkey': '120310101300022', 'value_0': '58215.69288958551'},
            {'quadkey': '120310101300023', 'value_0': '1581.7299999999998'},
        ]

    result = await web_app_client.post(
        '/api/metrics/map',
        json={
            'car_class': ['any'],
            'city': 'Москва',
            'date_from': 1640354400,
            'date_to': 1640354580,
            'granularity': '2',
            'metrics': ['simple_metric_with_source'],
            'quadkeys': [
                '120310101300020',
                '120310101300021',
                '120310101300022',
                '120310101300023',
            ],
            'utcoffset': 3,
            'cell_size': 15,
            'payment_type': None,
        },
    )
    assert result.status == 200, await result.text()


async def test_get_metric_with_unknown_source(
        web_app_client, atlas_blackbox_mock,
):

    result = await web_app_client.post(
        '/api/metrics/map',
        json={
            'car_class': ['any'],
            'city': 'Москва',
            'date_from': 1640354400,
            'date_to': 1640354580,
            'granularity': '2',
            'metrics': ['simple_metric_with_source'],
            'quadkeys': [
                '120310101300020',
                '120310101300021',
                '120310101300022',
                '120310101300023',
            ],
            'utcoffset': 3,
            'cell_size': 15,
            'payment_type': None,
        },
    )
    assert result.status == 404, await result.text()


@pytest.mark.pgsql('taxi_db_postgres_atlas_backend', files=['pg_source.sql'])
async def test_get_metric_with_ch_source(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute(*args, **kwargs):
        async def _result():
            data = [
                (('quadkey', 'String'), ('value_0', 'UInt64')),
                ('120310101300020', 66078.34831914098),
                ('120310101300021', 60208.49186579521),
                ('120310101300022', 58215.69288958551),
                ('120310101300023', 1581.7299999999998),
            ]
            for row in data:
                yield row

        return _result()

    result = await web_app_client.post(
        '/api/metrics/map',
        json={
            'car_class': ['any'],
            'city': 'Москва',
            'date_from': 1640354400,
            'date_to': 1640354580,
            'granularity': '2',
            'metrics': ['simple_metric_static_source'],
            'quadkeys': [
                '120310101300020',
                '120310101300021',
                '120310101300022',
                '120310101300023',
            ],
            'utcoffset': 3,
            'cell_size': 15,
            'payment_type': None,
        },
    )
    assert result.status == 200, await result.text()


async def test_get_metric_map_with_exceeded_timeout(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/api/metrics/map',
        json={
            'city': 'Москва',
            'car_class': ['any', 'econom'],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'granularity': '1',
            'metrics': ['requests_share_found', 'requests_share_found'],
            'quadkeys': [
                '120310101300023000',
                '120310101300023001',
                '120310101300023002',
                '120310101300023003',
            ],
            'utcoffset': 3,
            'corp_type': 'all',
            'cell_size': 17,
            'payment_type': None,
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }


@pytest.mark.parametrize(
    'geo_preset_id,query_pattern',
    (
        pytest.param(1, 'nearest_zone IN (\'kolpino\', \'spb\')'),
        pytest.param(4, 'nearest_zone IN (\'kolpino\', \'moscow\', \'spb\')'),
    ),
)
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend',
    files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
)
async def test_get_metric_map_geopreset(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        geo_preset_id,
        query_pattern,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        query = args[0] if args else kwargs['query']
        assert query_pattern in query

        async def _result():
            data = [
                (
                    ('quadkey', 'String'),
                    ('value_0', 'UInt64'),
                    ('value_1', 'UInt64'),
                ),
                ('12031010130002300', 22, 11),
                (None, 12, None),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/map',
        json={
            'geo_preset_id': geo_preset_id,
            'car_class': ['any', 'econom'],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'granularity': '1',
            'metrics': ['requests_share_found', 'requests_share_found'],
            'quadkeys': [
                '120310101300023000',
                '120310101300023001',
                '120310101300023002',
                '120310101300023003',
            ],
            'utcoffset': 3,
            'corp_type': 'all',
            'cell_size': 17,
            'payment_type': None,
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected = [
        {'quadkey': '12031010130002300', 'values': [22.0, 11.0]},
        {'quadkey': None, 'values': [12.0, None]},
    ]
    assert data == expected
