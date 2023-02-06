# pylint: disable=redefined-outer-name,unused-variable,no-method-argument
import datetime
import typing

import pytest

from driver_referrals.generated.cron import run_cron


async def test_map_reduce_no_task(cron_context):
    await run_cron.main(['driver_referrals.jobs.map_reduce', '-t', '0', '-d'])

    async with cron_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM synced_orders')

    assert not rows


@pytest.fixture
def mock_yt(
        patch,
) -> typing.Callable[
    [typing.Dict[str, typing.List[typing.List[typing.Any]]]], None,
]:
    def get_mocked_query_result(result: typing.List[typing.List[typing.Any]]):
        class _MockYqlRequestOperation:
            def run(self):
                pass

            def subscribe(self, *args, **kwargs):
                pass

            def get_results(*args, **kwargs):
                return [_MockYqlTable()]

        class _MockYqlTable:
            label = None
            is_truncated = False

            def fetch_full_data(self):
                return True

            rows = result

        return _MockYqlRequestOperation()

    def mock_yt_helper(
            result: typing.Dict[str, typing.List[typing.List[typing.Any]]],
    ) -> None:
        @patch('yql.api.v1.client.YqlClient.query')
        def patch_yql_query(query: str, *args, **kwargs):
            for search_string, query_result in result.items():
                if search_string in query:
                    return get_mocked_query_result(query_result)
            raise Exception(
                'Query does not match any search strings', query, list(result),
            )

    return mock_yt_helper


@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO tasks (id, task_date) """
        """VALUES ('task_id', '2019-04-20')""",
    ],
    files=['pg_driver_referrals.sql'],
)
@pytest.mark.now('2019-04-20 08:00:00')
@pytest.mark.parametrize(
    'expected_external_daily_stats',
    [
        [],
        pytest.param(
            [
                {
                    'park_id': 'park_id_eats_1',
                    'driver_id': 'driver_id_eats_1',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 3,
                    'rides_accounted': 3,
                },
                {
                    'park_id': 'park_id_lavka_1',
                    'driver_id': 'driver_id_lavka_1',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 5,
                    'rides_accounted': 5,
                },
            ],
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ENABLED_EXTERNAL_ORDER_STATS=['eda', 'lavka'],
            ),
            id='testing external order stats providers',
        ),
    ],
)
async def test_map_reduce(
        cron_context, patch, mock_yt, expected_external_daily_stats,
):
    @patch(
        'driver_referrals.generated.cron.yt_wrapper'
        '.plugin.AsyncYTClient.create',
    )
    async def create_table(*args, **kwargs):
        pass

    @patch(
        'driver_referrals.generated.cron.yt_wrapper'
        '.plugin.AsyncYTClient.write_table',
    )
    async def write_table(*args, **kwargs):
        # FIXME: add check drivers to fetch
        pass

    mock_yt(
        {
            'orders_monthly': [
                [
                    'order1',
                    'park1',
                    'driver1',
                    float(datetime.datetime(1970, 1, 18, 11, 40).timestamp()),
                    'moscow',
                    'econom',
                    'Москва',
                    'taxi',
                ],
                [
                    'order2',
                    'park1',
                    'driver1',
                    float(
                        datetime.datetime(1970, 1, 18, 11, 40, 1).timestamp(),
                    ),
                    'tver',
                    'comfort',
                    'Москва',
                    'taxi',
                ],
                [
                    'order3',
                    'park1',
                    'driver1',
                    float(
                        datetime.datetime(1970, 1, 18, 11, 40, 2).timestamp(),
                    ),
                    'moscow',
                    'econom',
                    'Калуга',
                    'taxi',
                ],
                [
                    'order4',
                    'park1',
                    'driver4',
                    float(
                        datetime.datetime(1970, 1, 18, 11, 40, 3).timestamp(),
                    ),
                    'moscow',
                    'econom',
                    'Москва',
                    'taxi',
                ],
            ],
            'bigfood/order/2019-01-01': [
                ['driver_id_eats_1', 'park_id_eats_1', 3],
            ],
            'dm_lavka_order/2019': [
                ['driver_id_lavka_1', 'park_id_lavka_1', 5],
            ],
        },
    )

    await run_cron.main(['driver_referrals.jobs.map_reduce', '-t', '0', '-d'])

    async with cron_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM synced_orders')
        tasks = await conn.fetch('SELECT * FROM tasks')
        external_daily_stats = await conn.fetch(
            """
            SELECT park_id, driver_id, date,
                   rides_total, rides_accounted
            FROM external_daily_stats
            ORDER BY park_id, driver_id
            """,
        )

    rows = [dict(row) for row in rows]

    assert rows == [
        {
            'order_id': 'order1',
            'park_id': 'park1',
            'driver_id': 'driver1',
            'nearest_zone': None,
            'nearest_zones': ['moscow'],
            'created_at': datetime.datetime(1970, 1, 18, 11, 40),
            'tariff_class': 'econom',
            'orders_provider': 'taxi',
            'synced_at': datetime.datetime(2019, 4, 20, 8),
        },
        {
            'order_id': 'order2',
            'park_id': 'park1',
            'driver_id': 'driver1',
            'nearest_zone': None,
            'nearest_zones': ['tver'],
            'created_at': datetime.datetime(1970, 1, 18, 11, 40, 1),
            'tariff_class': 'comfort',
            'orders_provider': 'taxi',
            'synced_at': datetime.datetime(2019, 4, 20, 8),
        },
        {
            'order_id': 'order3',
            'park_id': 'park1',
            'driver_id': 'driver1',
            'nearest_zone': None,
            'nearest_zones': ['moscow'],
            'created_at': datetime.datetime(1970, 1, 18, 11, 40, 2),
            'tariff_class': 'econom',
            'orders_provider': 'taxi',
            'synced_at': datetime.datetime(2019, 4, 20, 8),
        },
        {
            'order_id': 'order4',
            'park_id': 'park1',
            'driver_id': 'driver4',
            'nearest_zone': None,
            'nearest_zones': ['moscow'],
            'created_at': datetime.datetime(1970, 1, 18, 11, 40, 3),
            'tariff_class': 'econom',
            'orders_provider': 'taxi',
            'synced_at': datetime.datetime(2019, 4, 20, 8),
        },
    ]

    assert len(tasks) == 1
    assert tasks[0]['map_reduce_done']

    assert [
        dict(s) for s in external_daily_stats
    ] == expected_external_daily_stats
