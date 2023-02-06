# pylint: disable=redefined-outer-name
import contextlib
import datetime

import pytest

from agent.generated.cron import run_cron


@pytest.mark.now('2022-06-15T00:00:00+0000')
async def test_import_international_taxi(cron_context):
    async with contextlib.AsyncExitStack() as stack:

        async with contextlib.AsyncExitStack() as stack:
            pool = await stack.enter_async_context(
                cron_context.greenplum.get_pool(),
            )
        greenplum_conn = await stack.enter_async_context(pool.acquire())
        await greenplum_conn.execute(
            f"""
                CREATE SCHEMA IF NOT EXISTS taxi_cdm_piecework;""",
        )
        create_query = f"""
                        CREATE TABLE  IF NOT EXISTS
                        taxi_cdm_piecework.rep_operator_activity_halfhourly(
                        _etl_processed_dttm timestamp,
                        staff_login text,
                        action_cnt integer,
                        action_dur_sec_sum integer,
                        action_name varchar,
                        utc_report_dttm timestamp,
                        operator_shift_flg bool
                        );
                        """
        await greenplum_conn.execute(create_query)

        data = [
            [
                datetime.datetime(2022, 6, 15, 0, 0),
                'login_1',
                20,
                600,
                'close',
                datetime.datetime(2022, 6, 15, 0, 0),
                True,
            ],
            [
                datetime.datetime(2022, 6, 15, 0, 0),
                'login_1',
                30,
                900,
                'comment',
                datetime.datetime(2022, 6, 15, 1, 0),
                True,
            ],
            [
                datetime.datetime(2022, 6, 15, 0, 0),
                'login_1',
                40,
                1200,
                'communicate',
                datetime.datetime(2022, 6, 12, 12, 30),
                False,
            ],
            [
                datetime.datetime(2022, 6, 15, 0, 0),
                'login_1',
                0,
                0,
                'comment',
                datetime.datetime(2022, 6, 15, 0, 0),
                True,
            ],
            [
                datetime.datetime(2022, 6, 15, 0, 0),
                'login_2',
                None,
                None,
                None,
                None,
                True,
            ],
            [
                datetime.datetime(2022, 6, 15, 0, 0),
                'login_3',
                20,
                600,
                'dismiss',
                datetime.datetime(2022, 6, 15, 2, 0),
                True,
            ],
        ]

        expected_data = [
            {
                'login': 'login_1',
                'action_cnt': 50,
                'last_update': datetime.datetime(2022, 6, 15, 0, 0),
                'date': datetime.date(2022, 6, 15),
                'work_action_cnt': 50,
                'work_hours': 1.0,
                'sum_time_sec': 1500,
            },
            {
                'login': 'login_1',
                'action_cnt': 40,
                'last_update': datetime.datetime(2022, 6, 15, 0, 0),
                'date': datetime.date(2022, 6, 12),
                'work_action_cnt': 0,
                'work_hours': 0.0,
                'sum_time_sec': 1200,
            },
            {
                'login': 'login_3',
                'action_cnt': 20,
                'last_update': datetime.datetime(2022, 6, 15, 0, 0),
                'date': datetime.date(2022, 6, 15),
                'work_action_cnt': 20,
                'work_hours': 0.5,
                'sum_time_sec': 600,
            },
        ]

        await greenplum_conn.copy_records_to_table(
            table_name='rep_operator_activity_halfhourly',
            schema_name='taxi_cdm_piecework',
            records=data,
            columns=[
                '_etl_processed_dttm',
                'staff_login',
                'action_cnt',
                'action_dur_sec_sum',
                'action_name',
                'utc_report_dttm',
                'operator_shift_flg',
            ],
        )

    async with cron_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.international_taxi_support_metrics'
        result = await conn.fetch(query)
        assert result[0]['login'] == 'login_3'
    await run_cron.main(
        ['agent.crontasks.import_international_taxi', '-t', '0'],
    )

    async with cron_context.pg.slave_pool.acquire() as conn:

        query = 'SELECT * FROM agent.international_taxi_support_metrics'
        result = await conn.fetch(query)

        for row in result:
            assert dict(row) in expected_data

    async with cron_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.international_taxi_support_metrics'
        result = await conn.fetch(query)
        assert len(result) == 3
