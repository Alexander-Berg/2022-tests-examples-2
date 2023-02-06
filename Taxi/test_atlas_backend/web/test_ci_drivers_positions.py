from clickhouse_driver import errors as clickhouse_errors
import pytest


@pytest.mark.now('2021-04-10T11:30:40.123456+0300')
@pytest.mark.parametrize('username', ['super_user'])
async def test_get_avail_ci_names(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        username,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        query = args[0]
        assert (
            query
            == """SELECT DISTINCT ci_name
FROM    atlas.ci_driver_positions
WHERE   1 = 1
 and lat <= 55.12
 and lon >= 37.32
 and lat >= 55.01
 and lon <= 37.54
 and utc_timestamp_1_min >= toUnixTimestamp(\'2021-03-11 08:30:40\', \'UTC\')"""  # noqa: E501
        )

        async def _result():
            data = [(('ci_name', 'String'),), ('kd',), ('gt',)]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/map/ci-avail-drivers-positions',
        json={'tl': [55.12, 37.32], 'br': [55.01, 37.54]},
    )
    assert result.status == 200
    content = await result.json()
    assert content == ['kd', 'gt']


@pytest.mark.parametrize('username', ['super_user'])
async def test_get_ci_drivers_positions_hist(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        username,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        query = args[0]
        assert (
            query
            == """SELECT yandex_driver_ids_list,
ci_name,
utc_timestamp_1_min,
lat,
lon,
ci_driver_id
FROM    atlas.ci_driver_positions
WHERE   1 = 1
 and utc_timestamp_1_min >= 1615890823
 and utc_timestamp_1_min <= 1615892623
 and lat <= 55.12
 and lon >= 37.32
 and lat >= 55.01
 and lon <= 37.54
 and ci_name IN ('kd')"""
        )

        async def _result():
            data = [
                (
                    ('yandex_driver_ids_list', 'Array(String)'),
                    ('ci_name', 'String'),
                    ('utc_timestamp_1_min', 'UInt64'),
                    ('lat', 'Float64'),
                    ('lon', 'Float64'),
                    ('ci_driver_id', 'String'),
                ),
                (
                    ['400000179112_cb9da930f7cd42c680e4e5c35d56b123'],
                    'kd',
                    1615890900,
                    55.5397547,
                    37.5141573,
                    '6867941166fe567ea1a88502f028adad',
                ),
                (
                    ['400000031767_8572217f8cea31f35bc53e1530676345'],
                    'kd',
                    1615890900,
                    55.5401521,
                    37.4927518,
                    '9a06c2477e2f683ac93dbd8ef0911212',
                ),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/map/ci-drivers-positions-history',
        json={
            'tl': [55.12, 37.32],
            'br': [55.01, 37.54],
            'ci_names': ['kd'],
            'ts_from': 1615890823,
            'ts_to': 1615892623,
        },
    )
    assert result.status == 200
    content = await result.json()
    assert content == {
        'kd': {
            '1615890900': [
                {
                    'geopoint': [
                        pytest.approx(55.5397547),
                        pytest.approx(37.5141573),
                    ],
                    'ci_driver_id': '6867941166fe567ea1a88502f028adad',
                    'yandex_driver_ids_list': [
                        '400000179112_cb9da930f7cd42c680e4e5c35d56b123',
                    ],
                },
                {
                    'geopoint': [
                        pytest.approx(55.5401521),
                        pytest.approx(37.4927518),
                    ],
                    'ci_driver_id': '9a06c2477e2f683ac93dbd8ef0911212',
                    'yandex_driver_ids_list': [
                        '400000031767_8572217f8cea31f35bc53e1530676345',
                    ],
                },
            ],
        },
    }


@pytest.mark.parametrize('username', ['super_user'])
async def test_get_ci_drivers_positions_hist_with_exceeded_timeout(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        username,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/api/map/ci-drivers-positions-history',
        json={
            'tl': [55.12, 37.32],
            'br': [55.01, 37.54],
            'ci_names': ['kd'],
            'ts_from': 1615890823,
            'ts_to': 1615892623,
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }
