# pylint: disable=C0103, W0603
import math

from clickhouse_driver import errors as clickhouse_errors
import pytest

from atlas_backend.internal.metrics.query_proc import parameter_types


async def _result_gen(coeffs):
    values = [18846, 2279, 69465]
    ch_template = [
        (('city', 'String'), ('value', 'Float64')),
        'Санкт-Петербург',
        'Нижний Новгород',
        'Москва',
    ]

    async def _result(_coef):
        yield ch_template[0]
        for i in range(1, 4):
            row = (ch_template[i], values[i - 1] * _coef)
            yield row

    for coef in coeffs:
        yield _result(coef)


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param(
            'cities', ['Санкт-Петербург', 'Нижний Новгород', 'Москва'],
        ),
        pytest.param(
            'geonodes',
            [
                {'name': 'br_moscow', 'type': 'agglomeration'},
                {'name': 'br_saintpetersburg', 'type': 'agglomeration'},
                {'name': 'br_nizhny_novgorod', 'type': 'agglomeration'},
            ],
        ),
    ],
)
async def test_get_metric_leaderboard(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        key,
        value,
):
    result_gen = _result_gen([1, 0.9])

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        return await result_gen.__anext__()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            key: value,
            'car_class': 'any',
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['requests_share_burnt'],
            'wow': '1',
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected = {
        'cols': ['requests_share_burnt', 'city'],
        'rows': [
            {
                'city': 'Санкт-Петербург',
                'requests_share_burnt': pytest.approx(18846.0),
                'requests_share_burnt_old': pytest.approx(16961.4),
            },
            {
                'city': 'Нижний Новгород',
                'requests_share_burnt': pytest.approx(2279.0),
                'requests_share_burnt_old': pytest.approx(2051.1),
            },
            {
                'city': 'Москва',
                'requests_share_burnt': pytest.approx(69465.0),
                'requests_share_burnt_old': pytest.approx(62518.5),
            },
        ],
    }
    assert data == expected


calls_count = 0


async def test_get_metric_leaderboard_complicated(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    result_gen = _result_gen([0.6, 0.5, 1.2, 1.3])
    global calls_count
    calls_count = 0

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        global calls_count
        if calls_count == 0:
            query = args[0] if args else kwargs['query']
            assert (
                query
                == """SELECT
    city as city,
    SUM(cnt) as value
FROM
    (
--REGISTER_PARAM MultiSelector city
--REGISTER_PARAM MultiSelector car_class
--REGISTER_PARAM DateRange ts
--REGISTER_PARAM MultiSelector quadkey
--REGISTER_PARAM ContainsSelector tags
--REGISTER_PARAM Selector corp_contract_id
--REGISTER_PARAM CorpType corp_type
--REGISTER_PARAM MultiSelector tariff_zones
--REGISTER_PARAM PaymentType payment_type
--REGISTER_PARAM Selector couriers_source
--REGISTER_PARAM MultiSelector grocery_ids
--REGISTER_PARAM GeoNode geonodes

SELECT
    dttm_utc_1_min,
    city,
    source_quadkey as quadkey,
    nearest_zone,
    CASE
  WHEN corp_contract_id in (
      '544807/20', '554742/20', '761898/20'
  ) THEN 'food'
  WHEN corp_client_id is not null THEN 'corp'
  WHEN payment_method_id LIKE 'business%' THEN 'corp'
  ELSE 'not_corp'
END as corp_order_type,
    1 as cnt
FROM
    atlas.ods_order FINAL
WHERE
    1 = 1
    AND dttm_utc_1_min BETWEEN 1609231800 AND 1609232400
    AND city IN ('Санкт-Петербург', 'Нижний Новгород', 'Москва')
    AND quadkey IN ('12031010130002300')
    AND if(car_class_refined == '', car_class, car_class_refined) IN ('econom')
    AND (has(user_tags, 'super_tag') or has(cand_perf_tags, 'super_tag'))
    AND (corp_contract_id = 'ololo' OR corp_client_id = 'ololo')
    AND corp_order_type IN ('food', 'corp')
    AND nearest_zone IN ('ololo_tz1', 'trololo_tz2')
    AND couriers_source = '123'
    AND orders_place_id IN (1, 2)
    AND payment_method_id NOT LIKE 'business%' AND payment_type = 'coop_account'
    AND user_fraud = 0
    AND 1)
GROUP BY
    city"""  # noqa: E501,W291
            )

        calls_count += 1
        return await result_gen.__anext__()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'cities': ['Санкт-Петербург', 'Нижний Новгород', 'Москва'],
            'car_class': 'econom',
            'quadkeys': [
                '120310101300023000',
                '120310101300023001',
                '120310101300023002',
                '120310101300023003',
            ],
            'corp_contract_id': 'ololo',
            'couriers_source': '123',
            'corp_type': 'only_corp',
            'date_from': 1609231800,
            'date_to': 1609232400,
            'grocery_ids': [1, 2],
            'metrics': ['requests_share_found', 'z_edit_protected_metric'],
            'payment_type': 'coop_account',
            'tags': 'super_tag',
            'tariff_zones': ['ololo_tz1', 'trololo_tz2'],
            'wow': '1',
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected = {
        'cols': ['requests_share_found', 'z_edit_protected_metric', 'city'],
        'rows': [
            {
                'city': 'Санкт-Петербург',
                'requests_share_found': pytest.approx(11307.6),
                'requests_share_found_old': pytest.approx(9423.0),
                'z_edit_protected_metric': pytest.approx(22615.2),
                'z_edit_protected_metric_old': pytest.approx(24499.8),
            },
            {
                'city': 'Нижний Новгород',
                'requests_share_found': pytest.approx(1367.4),
                'requests_share_found_old': pytest.approx(1139.5),
                'z_edit_protected_metric': pytest.approx(2734.8),
                'z_edit_protected_metric_old': pytest.approx(2962.7),
            },
            {
                'city': 'Москва',
                'requests_share_found': pytest.approx(41679.0),
                'requests_share_found_old': pytest.approx(34732.5),
                'z_edit_protected_metric': pytest.approx(83358.0),
                'z_edit_protected_metric_old': pytest.approx(90304.5),
            },
        ],
    }

    assert data == expected


async def test_get_metric_leaderboard_empty(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            ch_data = [(('city', 'String'), ('value', 'Int64'))]
            for item in ch_data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'cities': ['Санкт-Петербург', 'Нижний Новгород'],
            'car_class': 'any',
            'corp_type': 'all',
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['requests_share_burnt'],
            'wow': '1',
        },
    )

    assert result.status == 200, await result.text()
    data = await result.json()
    expected = {'cols': ['requests_share_burnt', 'city'], 'rows': []}
    assert data == expected


@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('omnipotent_user', 200),
        ('metrics_view_protected_group_user', 403),
        ('super_user', 200),
        ('main_user', 200),
        ('nonexisted_user', 403),
        ('city_user', 403),
    ],
)
async def test_get_metric_leaderboard_all_cities(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        username,
        expected_status,
):
    global calls_count
    calls_count = 0

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            global calls_count
            if calls_count == 0:
                query = args[0] if args else kwargs['query']
                assert (
                    query
                    == """SELECT
    city,
    SUM(requests_share_burnt) / SUM(requests_volume) as value
FROM
    (
--REGISTER_PARAM MultiSelector city
--REGISTER_PARAM MultiSelector car_class
--REGISTER_PARAM DateRange ts
--REGISTER_PARAM MultiSelector quadkey
--REGISTER_PARAM TimeBucketGrid time_grid
--REGISTER_PARAM GeoNode geonodes

SELECT
    ts_1_min,
    city,
    quadkey as quadkey,
    requests_volume, requests_share_burnt*requests_volume AS requests_share_burnt
FROM
    atlas_orders.orders
WHERE
    1 = 1
    AND ts_1_min BETWEEN 1609231800 AND 1609232400
    AND 1
    AND 1
    AND 1
    AND requests_share_burnt >= 0.0
    AND requests_volume >= 0.0
    AND _table BETWEEN 'orders_20201229' AND 'orders_20201229'
   AND 1)
GROUP BY
    city"""  # noqa: E501,W291
                )
            calls_count += 1
            ch_data = [(('city', 'String'), ('value', 'Int64'))]
            for item in ch_data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'cities': [],
            'car_class': 'any',
            'corp_type': 'all',
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['requests_share_burnt'],
            'wow': '1',
        },
    )

    assert result.status == expected_status
    if result.status == 200:
        data = await result.json()
        expected = {'cols': ['requests_share_burnt', 'city'], 'rows': []}
        assert data == expected


async def test_get_metric_leaderboard_nan_inf(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    async def _bad_result_gen():
        async def _result1():
            ch_data = [
                (('city', 'String'), ('value', 'Float64')),
                ('Санкт-Петербург', 42),
                ('Москва', math.inf),
            ]
            for item in ch_data:
                yield item

        async def _result1_old():
            ch_data = [
                (('city', 'String'), ('value', 'Float64')),
                ('Москва', 12),
                ('Нижний Новгород', -math.inf),
                ('Владивосток', math.nan),
            ]
            for item in ch_data:
                yield item

        yield _result1()
        yield _result1_old()

    result_gen = _bad_result_gen()

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        return await result_gen.__anext__()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'cities': [
                'Санкт-Петербург',
                'Нижний Новгород',
                'Москва',
                'Владивосток',
            ],
            'car_class': 'any',
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['requests_share_burnt'],
            'wow': '1',
        },
    )

    assert result.status == 200, await result.text()
    data = await result.json()
    expected = {
        'cols': ['requests_share_burnt', 'city'],
        'rows': [
            {
                'city': 'Санкт-Петербург',
                'requests_share_burnt': pytest.approx(42.0),
                'requests_share_burnt_old': None,
            },
            {
                'city': 'Москва',
                'requests_share_burnt': None,
                'requests_share_burnt_old': pytest.approx(12.0),
            },
            {
                'city': 'Нижний Новгород',
                'requests_share_burnt': None,
                'requests_share_burnt_old': None,
            },
            {
                'city': 'Владивосток',
                'requests_share_burnt': None,
                'requests_share_burnt_old': None,
            },
        ],
    }
    assert data == expected


async def test_get_metric_leaderboard_aggregated(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data_detailed = [
                (('city', 'String'), ('value', 'Float64')),
                ('Москва', 12),
                ('Нижний Новгород', 13),
                ('Владивосток', 16),
            ]
            data_aggregated = [
                (('city', 'String'), ('value', 'Float64')),
                ('Москва', -12),
                ('Нижний Новгород', -13),
                ('Владивосток', -16),
            ]
            if 'atlas.orders_aggregated' in args[0]:
                for item in data_aggregated:
                    yield item
            else:
                for item in data_detailed:
                    yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'car_class': 'any',
            'cities': ['Москва', 'Нижний Новгород', 'Владивосток'],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'metrics': ['z_trips_with_aggregated_version'],
            'wow': '0',
            'tags': 'thermobag',  # отсутствует в агрегате
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected_detailed = {
        'cols': ['z_trips_with_aggregated_version', 'city'],
        'rows': [
            {'city': 'Москва', 'z_trips_with_aggregated_version': 12.0},
            {
                'city': 'Нижний Новгород',
                'z_trips_with_aggregated_version': 13.0,
            },
            {'city': 'Владивосток', 'z_trips_with_aggregated_version': 16.0},
        ],
    }
    assert data == expected_detailed

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'car_class': 'any',
            'cities': ['Москва', 'Нижний Новгород', 'Владивосток'],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'metrics': ['z_trips_with_aggregated_version'],
            'wow': '0',
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    expected_aggregated = {
        'cols': ['z_trips_with_aggregated_version', 'city'],
        'rows': [
            {'city': 'Москва', 'z_trips_with_aggregated_version': -12.0},
            {
                'city': 'Нижний Новгород',
                'z_trips_with_aggregated_version': -13.0,
            },
            {'city': 'Владивосток', 'z_trips_with_aggregated_version': -16.0},
        ],
    }
    assert data == expected_aggregated

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'car_class': 'any',
            'cities': ['Москва', 'Нижний Новгород', 'Владивосток'],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'metrics': ['z_trips_with_aggregated_version'],
            'wow': '0',
            'use_aggregates_speedup': False,  # Отключает агрегаты
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    assert data == expected_detailed


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_get_metric_leaderboard_intersected_geozones(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'geonodes': [
                {'name': 'br_saintpetersburg', 'type': 'agglomeration'},
                {'name': 'br_russia', 'type': 'country'},
            ],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'grocery_ids': [1, 2],
            'metrics': ['requests_share_found', 'z_edit_protected_metric'],
            'wow': '1',
        },
    )
    assert result.status == 400, await result.text()


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_get_metric_leaderboard_geozones(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        query = args[0] if args else kwargs['query']
        assert 'WHEN tariff_zones IN (\'moscow\')' in query
        assert 'WHEN tariff_zones IN (\'spb\', \'kolpino\')' in query

        async def _result():
            data_detailed = [
                (('city', 'String'), ('value', 'Float64')),
                ('Москва', 12),
                ('Ленинградская область', 13),
                (None, 25),  # with totals case
            ]
            for item in data_detailed:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'geonodes': [
                {'name': 'br_leningradskaja_obl', 'type': 'node'},
                {'name': 'br_moscow', 'type': 'agglomeration'},
            ],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['z_trips_with_aggregated_version'],
            'car_class': 'any',
            'wow': '0',
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    assert data == {
        'cols': ['z_trips_with_aggregated_version', 'city'],
        'rows': [
            {'city': 'Москва', 'z_trips_with_aggregated_version': 12.0},
            {
                'city': 'Ленинградская область',
                'z_trips_with_aggregated_version': 13.0,
            },
            {'city': '', 'z_trips_with_aggregated_version': 25.0},
        ],
    }


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_get_metric_leaderboard_geozones_nonbasic_hierarchy(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        query = args[0] if args else kwargs['query']
        assert 'nearest_zone IN (\'kolpino\', \'spb\')' in query

        async def _result():
            data_detailed = [
                (('city', 'String'), ('value', 'Float64')),
                ('Россия', 12),
                (None, 12),  # with totals case
            ]
            for item in data_detailed:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'geonodes': [{'name': 'fi_russia', 'type': 'node'}],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['z_trips_with_aggregated_version'],
            'car_class': 'any',
            'wow': '0',
        },
    )
    assert result.status == 200, await result.text()
    data = await result.json()
    assert data == {
        'cols': ['z_trips_with_aggregated_version', 'city'],
        'rows': [
            {'city': 'Россия', 'z_trips_with_aggregated_version': 12.0},
            {'city': '', 'z_trips_with_aggregated_version': 12.0},
        ],
    }


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_get_metric_leaderboard_not_filtered_zones(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        query = args[0] if args else kwargs['query']
        assert 'WHEN tariff_zones IN (\'moscow\')' in query
        assert 'WHEN tariff_zones IN (\'spb\', \'kolpino\')' in query

        async def _result():
            data_detailed = [
                (('city', 'String'), ('value', 'Float64')),
                ('Москва', 12),
                ('Ленинградская область', 13),
                (
                    parameter_types.DEFAULT_CITY,
                    5,
                ),  # not filtered geozones case
                (None, 30),  # with totals case
            ]
            for item in data_detailed:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'geonodes': [
                {'name': 'br_leningradskaja_obl', 'type': 'node'},
                {'name': 'br_moscow', 'type': 'agglomeration'},
            ],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['z_trips_with_aggregated_version'],
            'car_class': 'any',
            'wow': '0',
        },
    )
    assert result.status == 400, await result.text()
    data = await result.json()
    assert data == {
        'message': 'Geozones were not properly filtered',
        'code': 'BadRequest::NotFilteredGeoZones',
    }


@pytest.mark.parametrize(
    'username',
    [
        pytest.param(
            'test_user1',
            marks=[
                pytest.mark.pgsql(
                    'taxi_db_postgres_atlas_backend',
                    files=['pg_hierarchy.sql'],
                ),
            ],
        ),
    ],
)
async def test_get_metric_leaderboard_permission(
        clickhouse_client_mock,
        web_app_client,
        patch,
        atlas_blackbox_mock,
        username,
):
    result = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'geonodes': [
                {'name': 'br_leningradskaja_obl', 'type': 'node'},
                {'name': 'br_moscow', 'type': 'agglomeration'},
            ],
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['z_trips_with_aggregated_version'],
            'car_class': 'any',
            'wow': '0',
        },
    )

    assert result.status == 403, await result.text()
    data = await result.json()
    assert (
        data['message']
        == 'User test_user1 is not allowed to see [\'moscow\'] tariff zones'
    )


@pytest.mark.pgsql('taxi_db_postgres_atlas_backend', files=['pg_source.sql'])
async def test_get_metric_with_source(
        web_app_client, patch, atlas_blackbox_mock,
):
    @patch('yt.clickhouse.execute')
    def _execute(*args, **kwargs):
        return [
            {'city': 'Готэм-Сити', 'value': 9434.6185},
            {'city': 'Спрингфилд', 'value': -329.65},
            {'city': 'Гравити Фолз', 'value': 10.38},
            {'city': 'Шир', 'value': 80.33200000000001},
        ]

    result = await web_app_client.post(
        '/api/metrics/leaderboard/',
        json={
            'car_class': ['any'],
            'cities': [],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'metrics': ['simple_metric_with_source'],
            'use_aggregates_speedup': True,
            'wow': '0',
        },
    )
    assert result.status == 200, await result.text()


async def test_get_metric_with_unknown_source(
        web_app_client, atlas_blackbox_mock,
):

    result = await web_app_client.post(
        '/api/metrics/leaderboard/',
        json={
            'car_class': ['any'],
            'cities': [],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'metrics': ['simple_metric_with_source'],
            'use_aggregates_speedup': True,
            'wow': '0',
        },
    )
    assert result.status == 404, await result.text()


@pytest.mark.pgsql('taxi_db_postgres_atlas_backend', files=['pg_source.sql'])
async def test_get_metric_with_ch_source(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
) -> None:
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute(*args, **kwargs):
        async def _result():
            data = [
                (('city', 'String'), ('value', 'Float64')),
                ('Готэм-Сити', 9434.6185),
                ('Спрингфилд', -329.65),
                ('Гравити Фолз', 10.38),
                ('Шир', 80.33200000000001),
            ]
            for row in data:
                yield row

        return _result()

    result = await web_app_client.post(
        '/api/metrics/leaderboard/',
        json={
            'car_class': ['any'],
            'cities': [],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'metrics': ['simple_metric_static_source'],
            'use_aggregates_speedup': True,
            'wow': '0',
        },
    )
    assert result.status == 200, await result.text()


async def test_get_metric_leaderboard_with_exceeded_timeout(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/api/metrics/leaderboard',
        json={
            'cities': ['Санкт-Петербург', 'Нижний Новгород'],
            'car_class': 'any',
            'corp_type': 'all',
            'date_from': 1609231800,
            'date_to': 1609232400,
            'metrics': ['requests_share_burnt'],
            'wow': '1',
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }
