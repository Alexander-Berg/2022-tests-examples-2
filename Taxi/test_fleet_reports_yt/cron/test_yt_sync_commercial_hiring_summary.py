import datetime

import pytest

from fleet_reports_yt.generated.cron import run_cron

DB_FINAL_RESULT = [
    {
        'acquisition_source': 'Агенты',
        'acquisition_type': 'partner',
        'car_profile_brand_name': 'VW',
        'car_profile_model_name': 'Polo',
        'car_profile_id': '123',
        'car_number': 'A123BC76',
        'cnt_orders': 17,
        'paid_date_from': datetime.date.fromisoformat('2020-01-04'),
        'paid_date_to': datetime.date.fromisoformat('2021-01-04'),
        'driver_profile_id': '123',
        'driver_type': 'owner',
        'full_name': 'Один Два Три',
        'commercial_hiring_commission': 1000.0,
        'park_commission': 1500.0,
        'park_profit': 500.0,
        'rent': 1000.0,
        'park_id': 'pid1',
        'report_date': datetime.datetime.fromisoformat(
            '2022-02-12T09:00:00+00:00',
        ),
    },
    {
        'acquisition_source': 'Агенты',
        'acquisition_type': 'partner',
        'car_profile_brand_name': 'VW',
        'car_profile_model_name': 'Polo',
        'car_profile_id': '123',
        'car_number': 'A456BC76',
        'cnt_orders': 7,
        'paid_date_from': datetime.date.fromisoformat('2020-01-04'),
        'paid_date_to': datetime.date.fromisoformat('2021-01-04'),
        'driver_profile_id': '456',
        'driver_type': 'owner',
        'full_name': 'Четыре Пять Шеть',
        'commercial_hiring_commission': 1000.0,
        'park_commission': 1500.0,
        'park_profit': 500.0,
        'rent': 1000.0,
        'park_id': 'pid1',
        'report_date': datetime.datetime.fromisoformat(
            '2022-02-12T09:00:00+00:00',
        ),
    },
]


@pytest.mark.yt(
    schemas=['yt_data_scheme.yaml'], static_table_data=['yt_data.yaml'],
)
@pytest.mark.pgsql('fleet_reports')
@pytest.mark.now('2022-02-12T12:00:00')
async def test_run_cron(yt_apply, cron_context):
    # Second run should not change DB or fail
    for _ in range(2):
        await run_cron.main(
            [
                'fleet_reports_yt.crontasks.yt_sync_commercial_hiring_summary',
                '-t',
                '0',
            ],
        )
        rows = await cron_context.pg.main_master.fetch(
            """SELECT * FROM yt.commercial_hiring_summary_report
             ORDER BY park_id ASC, driver_profile_id ASC;""",
        )
        parsed = [dict(x) for x in rows]
        assert [DB_FINAL_RESULT[0]] == parsed


@pytest.mark.yt(
    schemas=['yt_data_scheme.yaml'], static_table_data=['yt_data.yaml'],
)
@pytest.mark.pgsql('fleet_reports', files=('report_exist.sql',))
@pytest.mark.now('2022-02-12T12:00:00')
async def test_delete_driver(yt_apply, cron_context):
    # Second run should not change DB or fail
    for _ in range(2):
        await run_cron.main(
            [
                'fleet_reports_yt.crontasks.yt_sync_commercial_hiring_summary',
                '-t',
                '0',
            ],
        )
        rows = await cron_context.pg.main_master.fetch(
            """SELECT * FROM yt.commercial_hiring_summary_report
             ORDER BY park_id ASC, driver_profile_id ASC;""",
        )
        parsed = [dict(x) for x in rows]
        assert [DB_FINAL_RESULT[0]] == parsed


@pytest.mark.yt(
    schemas=['yt_data_scheme.yaml'], static_table_data=['yt_data.yaml'],
)
@pytest.mark.pgsql('fleet_reports', files=('no_new_report.sql',))
@pytest.mark.now('2022-02-15T12:00:00')
async def test_no_report(yt_apply, cron_context):
    # Second run should not change DB or fail
    for _ in range(2):
        await run_cron.main(
            [
                'fleet_reports_yt.crontasks.yt_sync_commercial_hiring_summary',
                '-t',
                '0',
            ],
        )
        rows = await cron_context.pg.main_master.fetch(
            """SELECT * FROM yt.commercial_hiring_summary_report
             ORDER BY park_id ASC, driver_profile_id ASC;""",
        )
        parsed = [dict(x) for x in rows]
        assert DB_FINAL_RESULT == parsed
