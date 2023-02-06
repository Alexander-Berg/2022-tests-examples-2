import datetime

import psycopg2.tz
import pytest


# Configs:

CFG_FRAUD_EVENT_TYPES_DFT = ['fake_gps_protector', 'root_protector']
CFG_YT_TABLE_DFT = '//home/testsuite/fraud_signals'
CFG_YT_LIMIT_DFT = 4000


def cfg_make_fraud_check_settings(yt_limit=CFG_YT_LIMIT_DFT):
    cfg_fraud_check_settings = {
        'fraud_event_types': CFG_FRAUD_EVENT_TYPES_DFT,
        'fraud_event_lifetime_s': 259200,
        'fraud_event_interval_s': 1800,
        'fraud_signals_yt': {
            'table': CFG_YT_TABLE_DFT,
            'initial_cursor': '0',
            'limit': yt_limit,
            'fetch_period_ms': 900000,
        },
    }

    return cfg_fraud_check_settings


CFG_FRAUD_CHECK_SETTINGS_DFT = cfg_make_fraud_check_settings()
CFG_FRAUD_CHECK_SETTINGS_TINY_LIMIT = cfg_make_fraud_check_settings(yt_limit=4)


# DB helpers:

SELECT_SHIFT_FRAUD_EVENT_CACHE_FIRST = """
    SELECT time, driver_uuid, event_type
    FROM eats_logistics_performer_payouts.shift_fraud_event_cache
    LIMIT 1
"""

SELECT_SHIFT_FRAUD_EVENT_CACHE_COUNT = """
    SELECT COUNT(*) AS cache_size
    FROM eats_logistics_performer_payouts.shift_fraud_event_cache
"""

PG_TZ_MSK = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
PG_SHIFT_FRAUD_EVENT_CACHE_FIRST = {
    'time': datetime.datetime(2020, 6, 30, 10, 55, tzinfo=PG_TZ_MSK),
    'driver_uuid': '00D5',
    'event_type': 'root_protector',
}


@pytest.mark.now('2020-06-30T08:35:00+0000')
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_FRAUD_CHECK_SETTINGS_V4=CFG_FRAUD_CHECK_SETTINGS_DFT,  # noqa: E501 pylint: disable=line-too-long
)
@pytest.mark.yt(static_table_data=['yt_fraud_signals_1_1.yaml'])
async def test_shift_fraud_fetch_first_entry(
        pgsql, taxi_eats_logistics_performer_payouts, yt_apply,
):
    await taxi_eats_logistics_performer_payouts.run_periodic_task(
        'shift-fraud-events-fetch-periodic',
    )

    pg_cursor = pgsql['eats_logistics_performer_payouts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    pg_cursor.execute(SELECT_SHIFT_FRAUD_EVENT_CACHE_COUNT)
    pg_entry_num = pg_cursor.fetchone()

    assert pg_entry_num is not None
    assert pg_entry_num['cache_size'] == 1

    entry_first = PG_SHIFT_FRAUD_EVENT_CACHE_FIRST
    pg_cursor.execute(SELECT_SHIFT_FRAUD_EVENT_CACHE_FIRST)
    pg_entry_first = pg_cursor.fetchone()

    assert pg_entry_first is not None
    assert pg_entry_first['time'] == entry_first['time']
    assert pg_entry_first['driver_uuid'] == entry_first['driver_uuid']
    assert pg_entry_first['event_type'] == entry_first['event_type']


@pytest.mark.parametrize(
    'cfg_fraud_check',
    [
        pytest.param(CFG_FRAUD_CHECK_SETTINGS_DFT, id='large'),
        pytest.param(CFG_FRAUD_CHECK_SETTINGS_TINY_LIMIT, id='tiny'),
    ],
)
@pytest.mark.now('2020-06-30T08:35:00+0000')
@pytest.mark.yt(static_table_data=['yt_fraud_signals_7_11.yaml'])
async def test_shift_fraud_fetch_limit(
        cfg_fraud_check,
        pgsql,
        taxi_config,
        taxi_eats_logistics_performer_payouts,
        yt_apply,
):
    # Set config:
    taxi_config.set_values(
        {
            'EATS_LOGISTICS_PERFORMER_PAYOUTS_FRAUD_CHECK_SETTINGS_V4': (
                cfg_fraud_check
            ),
        },
    )

    # Perform test:
    await taxi_eats_logistics_performer_payouts.run_periodic_task(
        'shift-fraud-events-fetch-periodic',
    )
    pg_cursor = pgsql['eats_logistics_performer_payouts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    pg_cursor.execute(SELECT_SHIFT_FRAUD_EVENT_CACHE_COUNT)
    pg_fraud_enent_cache_count = pg_cursor.fetchone()
    assert pg_fraud_enent_cache_count is not None
    assert pg_fraud_enent_cache_count['cache_size'] == 7
