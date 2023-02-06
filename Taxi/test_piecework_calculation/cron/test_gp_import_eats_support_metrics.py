import datetime

import pytest

from piecework_calculation.internal import gp

NOW = datetime.datetime(year=2022, month=2, day=10)

NOW_FOR_EMPTY = datetime.datetime(year=2021, month=12, day=31)


def result_sort(elem):
    return elem['operator_login'], elem['utc_event_dt']


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(PIECEWORK_CALCULATION_EATS_METRICS_IMPORT_DAYS=30)
async def test_import_two_rules(cron_context):
    expected_result = [
        {
            'operator_login': 'support',
            'quality_sum': 145.0,
            'quality_cnt': 2,
            'csat_sum': 9.8,
            'csat_cnt': 2,
            'claim_cnt': 0,
            'utc_event_dt': '02.02.2022',
        },
        {
            'operator_login': 'supersupport',
            'quality_sum': 80.0,
            'quality_cnt': 1,
            'csat_sum': 9.0,
            'csat_cnt': 2,
            'claim_cnt': 2,
            'utc_event_dt': '03.02.2022',
        },
        {
            'operator_login': 'support',
            'quality_sum': 90.0,
            'quality_cnt': 1,
            'csat_sum': 0.0,
            'csat_cnt': 0,
            'claim_cnt': 5,
            'utc_event_dt': '11.01.2022',
        },
        {
            'operator_login': 'bad_support',
            'quality_sum': 0.0,
            'quality_cnt': 0,
            'csat_sum': 5.0,
            'csat_cnt': 2,
            'claim_cnt': 0,
            'utc_event_dt': '04.02.2022',
        },
        {
            'operator_login': 'nice_support',
            'quality_sum': 99.0,
            'quality_cnt': 1,
            'csat_sum': 9.0,
            'csat_cnt': 2,
            'claim_cnt': 1,
            'utc_event_dt': '05.02.2022',
        },
        {
            'operator_login': 'nice_support',
            'quality_sum': 0.0,
            'quality_cnt': 0,
            'csat_sum': 5.0,
            'csat_cnt': 1,
            'claim_cnt': 0,
            'utc_event_dt': '06.02.2022',
        },
        {
            'operator_login': 'nice_support',
            'quality_sum': 270.9,
            'quality_cnt': 3,
            'csat_sum': 23.5,
            'csat_cnt': 5,
            'claim_cnt': 1,
            'utc_event_dt': '10.02.2022',
        },
        {
            'operator_login': 'nice_support',
            'quality_sum': 0.0,
            'quality_cnt': 0,
            'csat_sum': 12.0,
            'csat_cnt': 3,
            'claim_cnt': 0,
            'utc_event_dt': '07.02.2022',
        },
    ]

    await gp.import_gp_eats_support_metrics(cron_context)

    async with cron_context.pg.slave_pool.acquire() as conn:
        result = await conn.fetch(
            """
            SELECT
                operator_login,
                csat_sum,
                csat_cnt,
                quality_sum,
                quality_cnt,
                claim_cnt,
                TO_CHAR(utc_event_dt, 'DD.MM.YYYY') as utc_event_dt
            FROM piecework.eats_support_metrics
        """,
        )

    result = list(map(dict, result))

    assert sorted(result, key=result_sort) == sorted(
        expected_result, key=result_sort,
    )


@pytest.mark.now(NOW_FOR_EMPTY.isoformat())
@pytest.mark.config(PIECEWORK_CALCULATION_EATS_METRICS_IMPORT_DAYS=10)
async def test_empty_data_for_period(cron_context):
    await gp.import_gp_eats_support_metrics(cron_context)
    async with cron_context.pg.slave_pool.acquire() as conn:
        result = await conn.fetch(
            """
            SELECT *
            FROM piecework.eats_support_metrics
        """,
        )

    assert not result
