import datetime

import pytest

from atlas_etl.generated.cron import run_cron


NOW = datetime.datetime(2021, 3, 15, 4, 16, 0)

DROP_PARTITION_TEMPLATE = (
    'ALTER TABLE {destination_table_path} on cluster '
    ' DROP PARTITION {part_name}'
)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.orders_aggregated_source': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_orders_aggregated_source(
        clickhouse_client_mock, load, load_py_json, db, patch,
):
    insert_query_template = load('orders_aggregated_insert.sql')

    async def _query_gen():
        start_dttm = datetime.datetime(2021, 3, 14, 0, 0, 0)
        table_name = 'orders_aggregated_source'

        for i in range(10):
            current_start_dttm = start_dttm + datetime.timedelta(hours=3) * i
            current_end_dttm = min(
                current_start_dttm + datetime.timedelta(hours=3), NOW,
            )

            if i % 8 == 0:
                yield DROP_PARTITION_TEMPLATE.format(
                    destination_table_path=f'atlas_distr_data.{table_name}',
                    part_name=current_start_dttm.strftime('%Y%m%d'),
                )

            yield insert_query_template.format(
                table_name=table_name,
                start_dttm=current_start_dttm,
                end_dttm=current_end_dttm,
                quadkey_column='source_quadkey',
            )

    query_gen = _query_gen()

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        query = args[0]
        expected_query = await query_gen.__anext__()
        assert query == expected_query

    await run_cron.main(
        ['atlas_etl.crontasks.orders_aggregated_source', '-t', '0'],
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.orders_aggregated_dropoff': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_orders_aggregated_dropoff(
        clickhouse_client_mock, load, load_py_json, db, patch,
):
    insert_query_template = load('orders_aggregated_insert.sql')

    async def _query_gen():
        table_name = 'orders_aggregated_dropoff'
        yield DROP_PARTITION_TEMPLATE.format(
            destination_table_path=f'atlas_distr_data.{table_name}',
            part_name='20210315',
        )
        yield insert_query_template.format(
            start_dttm=datetime.datetime(2021, 3, 15, 0, 0, 0),
            end_dttm=datetime.datetime(2021, 3, 15, 3, 0, 0),
            quadkey_column='dest_quadkey',
            table_name=table_name,
        )
        yield insert_query_template.format(
            start_dttm=datetime.datetime(2021, 3, 15, 3, 0, 0),
            end_dttm=NOW,
            quadkey_column='dest_quadkey',
            table_name=table_name,
        )

    query_gen = _query_gen()

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        query = args[0]
        expected_query = await query_gen.__anext__()
        assert query == expected_query

    await run_cron.main(
        ['atlas_etl.crontasks.orders_aggregated_dropoff', '-t', '0'],
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.orders_aggregated_dropoff': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_orders_aggregated_dropoff_custom_args(
        clickhouse_client_mock, load, load_py_json, db, patch,
):
    insert_query_template = load('orders_aggregated_insert.sql')

    async def _query_gen():
        table_name = 'orders_aggregated_dropoff'
        yield DROP_PARTITION_TEMPLATE.format(
            destination_table_path=f'atlas_distr_data.{table_name}',
            part_name='20210314',
        )
        yield insert_query_template.format(
            start_dttm=datetime.datetime(2021, 3, 14, 0, 0, 0),
            end_dttm=datetime.datetime(2021, 3, 14, 2, 30, 0),
            quadkey_column='dest_quadkey',
            table_name=table_name,
        )

    query_gen = _query_gen()

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        query = args[0]
        expected_query = await query_gen.__anext__()
        assert query == expected_query

    await run_cron.main(
        [
            'atlas_etl.crontasks.orders_aggregated_dropoff',
            '-t',
            '0',
            '--start_dttm',
            '2021-03-14 01:30:00',
            '--end_dttm',
            '2021-03-14 02:30:00',
        ],
    )

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'ods.orders_aggregated_dropoff'},
    )

    assert str(etl_info['last_upload_date']) == '2021-03-14 02:30:00'
