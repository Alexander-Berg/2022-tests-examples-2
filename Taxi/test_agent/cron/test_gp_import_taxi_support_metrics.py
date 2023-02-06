# pylint: disable=redefined-outer-name
import contextlib
import datetime

from agent.generated.cron import run_cron


async def test_import(cron_context):
    async with contextlib.AsyncExitStack() as stack:

        async with contextlib.AsyncExitStack() as stack:
            pool = await stack.enter_async_context(
                cron_context.greenplum.get_pool(),
            )
        greenplum_conn = await stack.enter_async_context(pool.acquire())
        await greenplum_conn.execute(
            f"""
                CREATE SCHEMA IF NOT EXISTS taxi_cdm_contactcenter;""",
        )
        create_query = f"""
                        CREATE TABLE  IF NOT EXISTS
                        taxi_cdm_contactcenter.dm_operator_quality_metric(
                        _etl_processed_dttm timestamp,
                        csat_avg float,
                        csat_cnt float,
                        csat_low_cnt float,
                        csat_not_excepted_sum float,
                        csat_not_excepted_cnt float,
                        operator_login text,
                        quality_cnt float,
                        quality_sum float,
                        utc_report_dt date
                        );
                        """
        await greenplum_conn.execute(create_query)

        data = [
            [
                datetime.datetime(2021, 12, 15),
                4.55,
                122,
                122,
                4.55,
                122,
                'login_1',
                2,
                50,
                datetime.datetime(2021, 12, 1).date(),
            ],
            [
                datetime.datetime(2021, 12, 15),
                None,
                None,
                None,
                None,
                None,
                'login_2',
                None,
                None,
                datetime.datetime(2021, 12, 2).date(),
            ],
            [
                datetime.datetime(2022, 2, 2),
                10,
                12,
                12,
                10,
                12,
                'login_3',
                13,
                14,
                datetime.datetime(2021, 1, 1).date(),
            ],
            [
                datetime.datetime(2022, 2, 3),
                20,
                22,
                22,
                20,
                22,
                'login_3',
                23,
                24,
                datetime.datetime(2021, 1, 1).date(),
            ],
        ]

        expected_data = {
            'login_1': {
                'csat_avg': 4.55,
                'csat_cnt': 122.0,
                'csat_low_cnt': 122.0,
                'csat_not_excepted_sum': 4.55,
                'csat_not_excepted_cnt': 122.0,
                'date': datetime.date(2021, 12, 1),
                'last_update': datetime.datetime(2021, 12, 15, 0, 0),
                'login': 'login_1',
                'quality_cnt': 2.0,
                'quality_avg': None,
                'quality_sum': 50.0,
            },
            'login_2': {
                'csat_avg': None,
                'csat_cnt': None,
                'csat_low_cnt': None,
                'csat_not_excepted_sum': None,
                'csat_not_excepted_cnt': None,
                'date': datetime.date(2021, 12, 2),
                'last_update': datetime.datetime(2021, 12, 15, 0, 0),
                'login': 'login_2',
                'quality_cnt': None,
                'quality_avg': None,
                'quality_sum': None,
            },
            'login_3': {
                'csat_avg': 20.0,
                'csat_cnt': 22.0,
                'csat_low_cnt': 22.0,
                'csat_not_excepted_sum': 20.0,
                'csat_not_excepted_cnt': 22.0,
                'date': datetime.date(2021, 1, 1),
                'last_update': datetime.datetime(2022, 2, 3, 0, 0),
                'login': 'login_3',
                'quality_cnt': 23.0,
                'quality_avg': 1000,
                'quality_sum': 24.0,
            },
        }

        await greenplum_conn.copy_records_to_table(
            table_name='dm_operator_quality_metric',
            schema_name='taxi_cdm_contactcenter',
            records=data,
            columns=[
                '_etl_processed_dttm',
                'csat_avg',
                'csat_cnt',
                'csat_low_cnt',
                'csat_not_excepted_sum',
                'csat_not_excepted_cnt',
                'operator_login',
                'quality_cnt',
                'quality_sum',
                'utc_report_dt',
            ],
        )

    async with cron_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.taxi_support_metrics'
        result = await conn.fetch(query)
        assert len(result) == 1
        assert result[0]['login'] == 'login_3'

    await run_cron.main(
        ['agent.crontasks.gp_import_taxi_support_metrics', '-t', '0'],
    )

    async with cron_context.pg.slave_pool.acquire() as conn:

        query = 'SELECT * FROM agent.taxi_support_metrics'

        result = await conn.fetch(query)
        assert len(data) == len(result) + 1  # 1 duplicate

        for row in result:
            login = row['login']
            row = dict(row)
            assert row == expected_data.get(login)
