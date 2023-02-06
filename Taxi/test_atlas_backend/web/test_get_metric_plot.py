import http
from typing import AsyncGenerator
from typing import List

from clickhouse_driver import errors as clickhouse_errors
import pytest


@pytest.mark.config(
    ATLAS_GRANULARITY_MAPPING={
        'plot': {
            '1': 600,
            '10': 60,
            '11': 300,
            '2': 3600,
            '20': 1,
            '21': 5,
            '3': 10800,
            '4': 21600,
            '5': 86400,
            '6': 604800,
            '7': None,
        },
    },
)
@pytest.mark.parametrize(
    'car_class,query_pattern,wow,actual_result,'
    'time_delta_offsets,coefficients,expected_result',
    [
        (
            'any',
            '1',
            '0',
            [
                (1608012180, 4),
                (1608012120, 138),
                (1608012000, 140),
                (1608012060, 158),
            ],
            [0],
            [1.0, 1.25],
            [
                [
                    [1608012000, 140.0],
                    [1608012060, 158.0],
                    [1608012120, 138.0],
                    [1608012180, 4.0],
                ],
            ],
        ),
        (
            ['econom', 'uberx'],
            'if(car_class_refined == \'\', car_class, car_class_refined) IN (\'econom\', \'uberx\')',  # noqa: E501
            '2',
            [
                (1608012180, 2),
                (1608012120, 101),
                (1608012000, 194),
                (1608012060, 213),
            ],
            [0, 1209600],
            [1.0, 1.25],
            [
                [
                    [1608012000, 194.0],
                    [1608012060, 213.0],
                    [1608012120, 101.0],
                    [1608012180, 2.0],
                ],
                [
                    [1608012000, 242.5],
                    [1608012060, 266.25],
                    [1608012120, 126.25],
                    [1608012180, 2.5],
                ],
            ],
        ),
        (
            'business',
            'if(car_class_refined == \'\', car_class, car_class_refined) IN (\'business\')',  # noqa: E501
            'days-3',
            [
                (1608012180, 7),
                (1608012120, 206),
                (1608012000, 156),
                (1608012060, 181),
            ],
            [0, 259200],
            [1.0, 1.25],
            [
                [
                    [1608012000, 156.0],
                    [1608012060, 181.0],
                    [1608012120, 206.0],
                    [1608012180, 7.0],
                ],
                [
                    [1608012000, 195.0],
                    [1608012060, 226.25],
                    [1608012120, 257.5],
                    [1608012180, 8.75],
                ],
            ],
        ),
    ],
)
async def test_get_metric_plot(
        car_class,
        query_pattern,
        wow,
        actual_result,
        time_delta_offsets,
        coefficients,
        expected_result,
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
):
    columns = ('atlas_ts', 'UInt64'), ('value', 'UInt64')

    async def _generate_time_series(
            time_delta_offsets_: List[int], coefficients_: List[float],
    ) -> AsyncGenerator:
        async def _result(time_delta_offset_: int, coefficient_: float):
            yield columns
            for i in range(4):
                yield actual_result[i][0] - time_delta_offset_, actual_result[
                    i
                ][1] * coefficient_

        for time_delta_offset, coefficient in zip(
                time_delta_offsets_, coefficients_,
        ):
            yield _result(time_delta_offset, coefficient)

    time_series_generator = _generate_time_series(
        time_delta_offsets, coefficients,
    )

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        return await time_series_generator.__anext__()

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': car_class,
            'city': 'Казань',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'requests_share_found',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': wow,
            'polygons': None,
            'corp_type': 'all',
            'payment_type': None,
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    assert data == expected_result


@pytest.mark.config(ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}})
@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('omnipotent_user', 200),
        ('metrics_view_protected_group_user', 200),
        ('super_user', 200),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_view_group_auth(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        username,
        expected_status,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (('atlas_ts', 'UInt64'), ('value', 'UInt64')),
                (1608012180, 4),
                (1608012120, 138),
                (1608012000, 140),
                (1608012060, 158),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': 'any',
            'city': 'Казань',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'z_edit_protected_metric',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
            'corp_type': 'all',
            'payment_type': None,
        },
    )
    assert result.status == expected_status


@pytest.mark.config(
    ATLAS_GRANULARITY_MAPPING={
        'plot': {
            '1': 600,
            '10': 60,
            '11': 300,
            '2': 3600,
            '20': 1,
            '21': 5,
            '3': 10800,
            '4': 21600,
            '5': 86400,
            '6': 604800,
            '7': None,
        },
    },
)
@pytest.mark.parametrize(
    'city,geonodes,geopreset,query_pattern,username,expected_status,expected_message',  # noqa: E501
    (
        pytest.param(
            None,
            None,
            None,
            None,
            'test_user1',
            http.HTTPStatus.BAD_REQUEST,
            {
                'message': (
                    'Exactly one geo filter '
                    '(city, geonodes, geopreset) should be used'
                ),
            },
        ),
        pytest.param(
            'Казань',
            [{'name': 'br_kazan', 'type': 'agglomeration'}],
            None,
            None,
            'test_user1',
            http.HTTPStatus.BAD_REQUEST,
            {
                'message': (
                    'Exactly one geo filter '
                    '(city, geonodes, geopreset) should be used'
                ),
            },
        ),
        pytest.param(
            None,
            [{'name': 'br_kazan', 'type': 'agglomeration'}],
            None,
            None,
            'random_user',
            http.HTTPStatus.FORBIDDEN,
            {
                'message': (
                    'User random_user is not allowed'
                    ' to see [\'kazan\'] tariff zones'
                ),
            },
        ),
        pytest.param(
            None,
            [
                {'name': 'br_moscow', 'type': 'agglomeration'},
                {'name': 'br_leningradskaja_obl', 'type': 'geo_node'},
            ],
            None,
            None,
            'test_user1',
            http.HTTPStatus.FORBIDDEN,
            {
                'message': (
                    'User test_user1 is not allowed'
                    ' to see [\'moscow\'] tariff zones'
                ),
            },
        ),
        pytest.param(
            None,
            [{'name': 'br_leningradskaja_obl', 'type': 'geo_node'}],
            None,
            'AND nearest_zone IN (\'kolpino\', \'spb\')',
            'test_user1',
            http.HTTPStatus.OK,
            {},
        ),
        pytest.param(
            None,
            [{'name': 'fi_russia_macro', 'type': 'geo_node'}],
            None,
            'AND nearest_zone IN (\'kolpino\', \'spb\')',
            'test_user1',
            http.HTTPStatus.OK,
            {},
        ),
        pytest.param(
            None,
            None,
            1,
            'AND nearest_zone IN (\'kolpino\', \'spb\')',
            'test_user1',
            http.HTTPStatus.OK,
            {},
        ),
        pytest.param(
            None,
            None,
            1,
            None,
            'test_user2',
            http.HTTPStatus.FORBIDDEN,
            {'message': 'User test_user2 is not allowed to use preset: id=1 '},
        ),
        pytest.param(
            None,
            None,
            10,
            None,
            'test_user1',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'NotFound::PresetNotExists',
                'message': 'There is no preset with id=10',
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend',
    files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
)
async def test_get_metric_plot_geo(
        city,
        geonodes,
        geopreset,
        query_pattern,
        username,
        expected_status,
        expected_message,
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
):
    ch_data_mock = [
        [1608012000, None],
        [1608012060, None],
        [1608012120, None],
        [1608012180, 4.0],
    ]

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(query, *args, **kwargs):
        async def _result():
            assert query_pattern in query
            data = [
                (('atlas_ts', 'UInt64'), ('value', 'UInt64')),
            ] + ch_data_mock
            for item in data:
                yield item

        return _result()

    params = {
        'car_class': 'any',
        'date_from': 1608012000,
        'date_to': 1608012180,
        'granularity': '10',
        'metric': 'requests_share_found',
        'offset_time': False,
        'quadkeys': None,
        'utcoffset': 3,
        'wow': '0',
        'polygons': None,
        'corp_type': 'all',
        'payment_type': None,
    }
    if city:
        params['city'] = city
    if geonodes:
        params['geonodes'] = geonodes
    if geopreset:
        params['geo_preset_id'] = geopreset

    result = await web_app_client.post('/api/metrics/plot', json=params)
    assert result.status == expected_status, await result.text()
    data = await result.json()
    if not expected_message:
        expected_message = [ch_data_mock]
    assert data == expected_message


@pytest.mark.config(
    ATLAS_GRANULARITY_MAPPING={
        'plot': {
            '1': 600,
            '10': 60,
            '11': 300,
            '2': 3600,
            '20': 1,
            '21': 5,
            '3': 10800,
            '4': 21600,
            '5': 86400,
            '6': 604800,
            '7': None,
        },
    },
)
async def test_get_metric_plot_aggregated(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data_detailed = [
                (('atlas_ts', 'UInt64'), ('value', 'Int64')),
                (1608012180, 4),
                (1608012120, 138),
                (1608012000, 140),
                (1608012060, 158),
            ]
            data_aggregated = [
                (('atlas_ts', 'UInt64'), ('value', 'Int64')),
                (1608012180, -4),
                (1608012120, -138),
                (1608012000, -140),
                (1608012060, -158),
            ]
            if 'atlas.orders_aggregated' in args[0]:
                for item in data_aggregated:
                    yield item
            else:
                for item in data_detailed:
                    yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': 'any',
            'city': 'Казань',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'z_trips_with_aggregated_version',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'tags': 'thermobag',  # отсутствует в агрегате
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected_detailed = [
        [
            [1608012000, 140.0],
            [1608012060, 158.0],
            [1608012120, 138.0],
            [1608012180, 4.0],
        ],
    ]
    assert data == expected_detailed

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': 'any',
            'city': 'Казань',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'z_trips_with_aggregated_version',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected_aggregated = [
        [
            [1608012000, -140.0],
            [1608012060, -158.0],
            [1608012120, -138.0],
            [1608012180, -4.0],
        ],
    ]
    assert data == expected_aggregated

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': 'any',
            'city': 'Казань',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'z_trips_with_aggregated_version',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'use_aggregates_speedup': False,  # Отключает агрегаты
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    assert data == expected_detailed


@pytest.mark.config(ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}})
@pytest.mark.parametrize(
    'car_class, expected_status',
    [
        ('any', 200),
        ('econom', 200),
        (['business', 'econom'], 200),
        (['any', 'econom'], 400),
        (['econom', 'vip', 'any'], 400),
        (['any'], 200),
    ],
)
async def test_multi_car_class(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        car_class,
        expected_status,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (('atlas_ts', 'UInt64'), ('value', 'UInt64')),
                (1608012180, 4),
                (1608012120, 138),
                (1608012000, 140),
                (1608012060, 158),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': car_class,
            'city': 'Казань',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'requests_share_found',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
            'corp_type': 'all',
            'payment_type': None,
        },
    )
    assert result.status == expected_status


@pytest.mark.config(ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}})
@pytest.mark.pgsql('taxi_db_postgres_atlas_backend', files=['pg_source.sql'])
async def test_get_metric_with_source(
        web_app_client, patch, atlas_blackbox_mock,
):
    @patch('yt.clickhouse.execute')
    def _execute(*args, **kwargs):
        return [
            {'atlas_ts': 1608012000, 'value': '66078.34831914098'},
            {'atlas_ts': 1608012120, 'value': '60208.49186579521'},
            {'atlas_ts': 1608012060, 'value': '58215.69288958551'},
            {'atlas_ts': 1608012180, 'value': '1581.7299999999998'},
        ]

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': ['any'],
            'city': 'Москва',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'simple_metric_with_source',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
            'corp_type': 'all',
            'payment_type': None,
        },
    )
    assert result.status == 200, await result.text()


@pytest.mark.config(ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}})
async def test_get_metric_with_unknown_source(
        web_app_client, atlas_blackbox_mock,
):

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': ['any'],
            'city': 'Москва',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'simple_metric_with_source',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
            'corp_type': 'all',
            'payment_type': None,
        },
    )
    assert result.status == 404, await result.text()


@pytest.mark.pgsql('taxi_db_postgres_atlas_backend', files=['pg_source.sql'])
@pytest.mark.config(ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}})
async def test_get_metric_with_ch_source(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
) -> None:
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute(*args, **kwargs):
        async def _result():
            data = [
                (('atlas_ts', 'UInt64'), ('value', 'UInt64')),
                (1608012000, 66078.34831914098),
                (1608012120, 60208.49186579521),
                (1608012060, 58215.69288958551),
                (1608012180, 1581.7299999999998),
            ]
            for row in data:
                yield row

        return _result()

    result = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': ['any'],
            'city': 'Москва',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'simple_metric_static_source',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
            'corp_type': 'all',
            'payment_type': None,
        },
    )
    assert result.status == 200, await result.text()


@pytest.mark.config(ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}})
async def test_get_metric_plot_with_exceeded_timeout(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TOO_SLOW,
        )

    response = await web_app_client.post(
        '/api/metrics/plot',
        json={
            'car_class': 'any',
            'city': 'Казань',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'z_edit_protected_metric',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
            'corp_type': 'all',
            'payment_type': None,
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }
