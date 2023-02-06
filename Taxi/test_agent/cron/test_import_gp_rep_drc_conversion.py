import contextlib
import datetime

import pytest

from agent.generated.cron import run_cron


@pytest.mark.now('2022-01-10T12:00:00+0000')
async def test_import_rep_drc(cron_context):
    async with contextlib.AsyncExitStack() as stack:
        pool = await stack.enter_async_context(
            cron_context.greenplum.get_pool(),
        )
        greenplum_conn = await stack.enter_async_context(pool.acquire())
        await greenplum_conn.execute(
            f"""
                CREATE SCHEMA IF NOT EXISTS taxi_udm_piecework;""",
        )
        create_query = f"""
                CREATE TABLE  IF NOT EXISTS
                taxi_udm_piecework.rep_operator_hiring_conversion_daily_snp(
                user_login TEXT,
                utc_business_dttm TIMESTAMP,
                call_cnt INTEGER,
                lead_cnt INTEGER,
                activated_lead_cnt INTEGER
                );
                """
        await greenplum_conn.execute(create_query)

        data = [
            ['webalex', datetime.datetime(2022, 1, 1, 12), 100, 50, 40],
            ['webalex', datetime.datetime(2022, 1, 2, 12), 90, 40, 30],
            ['webalex', datetime.datetime(2022, 1, 3, 12), 0, 0, 0],
            ['webalex', datetime.datetime(2022, 1, 4, 12), 200, 100, 50],
            ['webalex', datetime.datetime(2022, 1, 5, 12), 1000, 500, 400],
        ]

        await greenplum_conn.copy_records_to_table(
            table_name='rep_operator_hiring_conversion_daily_snp',
            schema_name='taxi_udm_piecework',
            records=data,
            columns=[
                'user_login',
                'utc_business_dttm',
                'call_cnt',
                'lead_cnt',
                'activated_lead_cnt',
            ],
        )

        await run_cron.main(
            ['agent.crontasks.import_gp_rep_drc_conversion', '-t', '0'],
        )

        query = 'SELECT * FROM agent.gp_rep_drc_conversion ORDER BY dt'
        async with cron_context.pg.slave_pool.acquire() as conn:
            assert (
                [
                    {
                        'login': row['login'],
                        'dt': row['dt'].strftime('%Y-%m-%d'),
                        'call_cnt': row['call_cnt'],
                        'lead_cnt': row['lead_cnt'],
                        'activated_lead_cnt': row['activated_lead_cnt'],
                    }
                    for row in await conn.fetch(query)
                ]
                == [
                    {
                        'login': 'webalex',
                        'dt': '2022-01-01',
                        'call_cnt': 100,
                        'lead_cnt': 50,
                        'activated_lead_cnt': 40,
                    },
                    {
                        'login': 'webalex',
                        'dt': '2022-01-02',
                        'call_cnt': 90,
                        'lead_cnt': 40,
                        'activated_lead_cnt': 30,
                    },
                    {
                        'login': 'webalex',
                        'dt': '2022-01-03',
                        'call_cnt': 0,
                        'lead_cnt': 0,
                        'activated_lead_cnt': 0,
                    },
                    {
                        'login': 'webalex',
                        'dt': '2022-01-04',
                        'call_cnt': 200,
                        'lead_cnt': 100,
                        'activated_lead_cnt': 50,
                    },
                    {
                        'login': 'webalex',
                        'dt': '2022-01-05',
                        'call_cnt': 1000,
                        'lead_cnt': 500,
                        'activated_lead_cnt': 400,
                    },
                ]
            )
