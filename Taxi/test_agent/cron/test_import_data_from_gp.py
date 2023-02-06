# pylint: disable=redefined-outer-name
import contextlib
import datetime

from agent.generated.cron import run_cron


async def test_import_gp(cron_context):
    async with contextlib.AsyncExitStack() as stack:
        pool = await stack.enter_async_context(
            cron_context.greenplum.get_pool(),
        )
        greenplum_conn = await stack.enter_async_context(pool.acquire())
        await greenplum_conn.execute(
            f"""
                CREATE SCHEMA IF NOT EXISTS taxi_rep_callcenter;""",
        )
        create_query = f"""
                CREATE TABLE  IF NOT EXISTS
                taxi_rep_callcenter.rep_operator_activity_daily(
                _etl_processed_dttm TIMESTAMP,
                staff_login VARCHAR,
                lcl_report_dt DATE,
                converted_disp_call_cnt float,
                completed_disp_call_cnt float,
                quality_coeff_consultation_sum_pcnt float,
                quality_coeff_order_placing_sum_pcnt float,
                quality_coeff_consultation_cnt float,
                quality_coeff_order_placing_cnt float,
                delay_cnt float,
                abcense_cnt float,
                claim_cnt integer,
                call_cnt integer,
                success_order_cnt integer,
                quality_coeff_order_placing_sum float,
                quality_coeff_consultation_sum float
                );
                """
        await greenplum_conn.execute(create_query)

        etl_time = datetime.datetime.now() + datetime.timedelta(days=1)
        lcl_report_dt = etl_time.date()

        data = [
            [
                etl_time,
                'webalex',
                lcl_report_dt,
                0.1,
                0.1,
                0.1,
                0.1,
                0,
                0,
                1,
                30,
                20,
                1,
                1,
            ],
            [
                etl_time,
                'liambaev',
                lcl_report_dt,
                0.1,
                0.1,
                0.1,
                0.1,
                0,
                0,
                1,
                30,
                20,
                1,
                1,
            ],
            [
                etl_time,
                'piskarev',
                lcl_report_dt,
                0.1,
                0.1,
                0.1,
                0.1,
                0,
                0,
                5,
                30,
                20,
                1,
                1,
            ],
        ]

        expected_data = {
            'webalex': {
                'login': 'webalex',
                'date': lcl_report_dt,
                'last_update': etl_time,
                'call_cnt': 30,
                'success_order_cnt': 20,
                'quality_coeff_consultation_sum_pcnt': 0.1,
                'quality_coeff_order_placing_sum_pcnt': 0.1,
                'quality_coeff_consultation_cnt': 0.1,
                'quality_coeff_order_placing_cnt': 0.1,
                'delay_cnt': 0,
                'abcense_cnt': 0,
                'claim_cnt': 1,
                'quality_coeff_order_placing_sum': 1,
                'quality_coeff_consultation_sum': 1,
            },
            'liambaev': {
                'login': 'liambaev',
                'date': lcl_report_dt,
                'last_update': etl_time,
                'call_cnt': 30,
                'success_order_cnt': 20,
                'quality_coeff_consultation_sum_pcnt': 0.1,
                'quality_coeff_order_placing_sum_pcnt': 0.1,
                'quality_coeff_consultation_cnt': 0.1,
                'quality_coeff_order_placing_cnt': 0.1,
                'delay_cnt': 0,
                'abcense_cnt': 0,
                'claim_cnt': 1,
                'quality_coeff_order_placing_sum': 1,
                'quality_coeff_consultation_sum': 1,
            },
            'piskarev': {
                'login': 'piskarev',
                'date': lcl_report_dt,
                'last_update': etl_time,
                'call_cnt': 30,
                'success_order_cnt': 20,
                'quality_coeff_consultation_sum_pcnt': 0.1,
                'quality_coeff_order_placing_sum_pcnt': 0.1,
                'quality_coeff_consultation_cnt': 0.1,
                'quality_coeff_order_placing_cnt': 0.1,
                'delay_cnt': 0,
                'abcense_cnt': 0,
                'claim_cnt': 5,
                'quality_coeff_order_placing_sum': 1,
                'quality_coeff_consultation_sum': 1,
            },
        }

        await greenplum_conn.copy_records_to_table(
            table_name='rep_operator_activity_daily',
            schema_name='taxi_rep_callcenter',
            records=data,
            columns=[
                '_etl_processed_dttm',
                'staff_login',
                'lcl_report_dt',
                'quality_coeff_consultation_sum_pcnt',
                'quality_coeff_order_placing_sum_pcnt',
                'quality_coeff_consultation_cnt',
                'quality_coeff_order_placing_cnt',
                'delay_cnt',
                'abcense_cnt',
                'claim_cnt',
                'call_cnt',
                'success_order_cnt',
                'quality_coeff_order_placing_sum',
                'quality_coeff_consultation_sum',
            ],
        )

    async with cron_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.gp_dsp_operator_activity_daily'
        result = await conn.fetch(query)
        assert len(result) == 1
        assert result[0]['login'] == 'andrey'

    await run_cron.main(['agent.crontasks.disp_import_greenplum', '-t', '0'])

    async with cron_context.pg.slave_pool.acquire() as conn:

        query = 'SELECT * FROM agent.gp_dsp_operator_activity_daily'

        result = await conn.fetch(query)
        assert len(result) == len(data)

        for row in result:
            login = row['login']
            row = dict(row)
            assert row == expected_data.get(login)
