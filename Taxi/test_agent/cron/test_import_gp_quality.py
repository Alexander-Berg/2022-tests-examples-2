import contextlib
import datetime

from agent.generated.cron import run_cron


EXPECTED_START = [
    {
        'ticket_code': 'AUDKON-1',
        'operator_login': 'webalex',
        'commutation_queue_code': 'test',
        'ticket_type_code': 'test',
        'score_total': 0,
        'dialog_url': 'test_url',
        'auditor_comment': 'test',
    },
    {
        'ticket_code': 'AUDKON-3906747',
        'operator_login': 'webalex',
        'commutation_queue_code': 'test',
        'ticket_type_code': 'test',
        'score_total': 0,
        'dialog_url': 'test_url',
        'auditor_comment': 'test',
    },
]


EXPECTED_END = [
    {
        'ticket_code': 'AUDKON-3906746',
        'operator_login': 'webalex',
        'commutation_queue_code': 'ru_taxi_disp_comfort_on_4',
        'ticket_type_code': 'prosluskaIOcenka',
        'score_total': 100,
        'dialog_url': 'fpS84CdzexW0ByDwZN5dyjte4dM%3D',
        'auditor_comment': None,
    },
    {
        'ticket_code': 'AUDKON-3906747',
        'operator_login': 'webalex',
        'commutation_queue_code': 'ru_taxi_disp_comfort_on_4',
        'ticket_type_code': 'prosluskaIOcenka',
        'score_total': 100,
        'dialog_url': 'fpS84CdzexW0ByDwZN5dyjte4dM%3D',
        'auditor_comment': None,
    },
    {
        'ticket_code': 'AUDKON-3906748',
        'operator_login': 'webalex',
        'commutation_queue_code': 'ru_taxi_disp_comfort_on_4',
        'ticket_type_code': 'prosluskaIOcenka',
        'score_total': 100,
        'dialog_url': 'fpS84CdzexW0ByDwZN5dyjte4dM%3D',
        'auditor_comment': None,
    },
]


async def get_quality(cron_context):
    query = 'SELECT * FROM agent.gp_details_quality ORDER BY ticket_code'
    async with cron_context.pg.slave_pool.acquire() as conn:
        return [
            {
                'ticket_code': row['ticket_code'],
                'operator_login': row['operator_login'],
                'commutation_queue_code': row['commutation_queue_code'],
                'ticket_type_code': row['ticket_type_code'],
                'score_total': row['score_total'],
                'dialog_url': row['dialog_url'],
                'auditor_comment': row['auditor_comment'],
            }
            for row in await conn.fetch(query)
        ]


async def test_import_gp_quality(cron_context):
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
                taxi_cdm_piecework.dm_quality_ticket_act(
                utc_updated_dttm TIMESTAMP,
                utc_resolved_dttm TIMESTAMP,
                utc_dialog_dttm TIMESTAMP,
                ticket_code TEXT,
                line_code TEXT,
                operator_login TEXT,
                ticket_type_code TEXT,
                score_total FLOAT,
                dialog_url TEXT,
                auditor_comment TEXT,
                for_operator_flg BOOLEAN
                );
                """
        await greenplum_conn.execute(create_query)

        data = [
            [
                datetime.datetime.now(),
                datetime.datetime.now(),
                datetime.datetime.now(),
                'AUDKON-3906746',
                'ru_taxi_disp_comfort_on_4',
                'webalex',
                'prosluskaIOcenka',
                100,
                'fpS84CdzexW0ByDwZN5dyjte4dM%3D',
                None,
                True,
            ],
            [
                datetime.datetime.now(),
                datetime.datetime.now(),
                datetime.datetime.now(),
                'AUDKON-3906747',
                'ru_taxi_disp_comfort_on_4',
                'webalex',
                'prosluskaIOcenka',
                100,
                'fpS84CdzexW0ByDwZN5dyjte4dM%3D',
                None,
                True,
            ],
            [
                datetime.datetime.now(),
                datetime.datetime.now(),
                datetime.datetime.now(),
                'AUDKON-3906748',
                'ru_taxi_disp_comfort_on_4',
                'webalex',
                'prosluskaIOcenka',
                100,
                'fpS84CdzexW0ByDwZN5dyjte4dM%3D',
                None,
                True,
            ],
            [
                datetime.datetime.now(),
                datetime.datetime.now(),
                datetime.datetime.now(),
                'AUDKON-390653',
                'ru_taxi_disp_comfort_on_4',
                None,
                'prosluskaIOcenka',
                100,
                'fpS84CdzexW0ByDwZN5dyjte4dM%3D',
                None,
                True,
            ],
            [
                datetime.datetime.now(),
                datetime.datetime.now(),
                datetime.datetime.now(),
                'AUDKON-391555',
                'ru_taxi_disp_comfort_on_4',
                'webalex',
                'prosluskaIOcenka',
                None,
                'fpS84CdzexW0ByDwZN5dyjte4dM%3D',
                None,
                True,
            ],
            [
                datetime.datetime.now(),
                datetime.datetime.now(),
                datetime.datetime.now(),
                'AUDKON-39155511',
                'ru_taxi_disp_comfort_on_4',
                'webalex',
                'prosluskaIOcenka',
                None,
                'fpS84CdzexW0ByDwZN5dyjte4dM%3D12',
                None,
                False,
            ],
        ]

        await greenplum_conn.copy_records_to_table(
            table_name='dm_quality_ticket_act',
            schema_name='taxi_cdm_piecework',
            records=data,
            columns=[
                'utc_updated_dttm',
                'utc_resolved_dttm',
                'utc_dialog_dttm',
                'ticket_code',
                'line_code',
                'operator_login',
                'ticket_type_code',
                'score_total',
                'dialog_url',
                'auditor_comment',
                'for_operator_flg',
            ],
        )

        assert await get_quality(cron_context=cron_context) == EXPECTED_START

        await run_cron.main(['agent.crontasks.import_gp_quality', '-t', '0'])

        assert await get_quality(cron_context=cron_context) == EXPECTED_END
