# pylint: disable=C0103, W0603
import datetime

import pytest

from atlas_etl.generated.cron import run_cron


NOW = datetime.datetime(2021, 3, 15, 4, 16, 13)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'atlas.orders_aggregated_cmt_small': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_orders_aggregated_cmt_small(
        clickhouse_client_mock, load, load_py_json, db, patch,
):
    calls_count = 0

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        nonlocal calls_count
        calls_count += 1

    await run_cron.main(
        ['atlas_etl.crontasks.orders_aggregated_cmt_small', '-t', '0'],
    )

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'atlas.orders_aggregated_cmt_small'},
    )
    # 2 chunks by 5 queries per chunk
    assert calls_count == 15
    assert str(etl_info['last_upload_date']) == '2021-03-15 04:16:00'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'atlas.orders_aggregated_cmt_big': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_orders_aggregated_cmt_big(
        clickhouse_client_mock, load, load_py_json, db, patch,
):
    calls_count = 0

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        nonlocal calls_count
        calls_count += 1

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'atlas.orders_aggregated_cmt_big'},
    )
    assert etl_info is None  # Record is not exist yet

    await run_cron.main(
        ['atlas_etl.crontasks.orders_aggregated_cmt_big', '-t', '0'],
    )

    # 15 chunks(30 hours with 2 hours chunks) by 5 queries per chunk
    assert calls_count == 75

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'atlas.orders_aggregated_cmt_big'},
    )
    assert str(etl_info['last_upload_date']) == '2021-03-14 22:55:00'
