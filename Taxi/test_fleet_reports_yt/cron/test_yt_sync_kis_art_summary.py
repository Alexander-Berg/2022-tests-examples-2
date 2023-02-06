import datetime

import pytest

from fleet_reports_yt.generated.cron import run_cron

DB_FINAL_RESULT = [
    {
        'active_drivers_count': 11,
        'drivers_with_permanent_id_count': 5,
        'drivers_with_requested_id_count': 2,
        'drivers_with_temporary_id_count': 2,
        'drivers_with_failed_id_count': 0,
        'drivers_without_id_count': 1,
        'park_id': 'pid1',
        'report_date': datetime.date(2021, 8, 3),
    },
    {
        'active_drivers_count': 15,
        'drivers_with_permanent_id_count': 5,
        'drivers_with_requested_id_count': 5,
        'drivers_with_temporary_id_count': 5,
        'drivers_with_failed_id_count': 0,
        'drivers_without_id_count': 0,
        'park_id': 'pid2',
        'report_date': datetime.date(2021, 8, 3),
    },
    {
        'active_drivers_count': 100,
        'drivers_with_permanent_id_count': 55,
        'drivers_with_requested_id_count': 10,
        'drivers_with_temporary_id_count': 5,
        'drivers_with_failed_id_count': 0,
        'drivers_without_id_count': 20,
        'park_id': 'pid3',
        'report_date': datetime.date(2021, 8, 3),
    },
    {
        'active_drivers_count': 15,
        'drivers_with_permanent_id_count': 5,
        'drivers_with_requested_id_count': 5,
        'drivers_with_temporary_id_count': 5,
        'drivers_with_failed_id_count': 0,
        'drivers_without_id_count': 0,
        'park_id': 'pid2',
        'report_date': datetime.date(2021, 8, 4),
    },
    {
        'active_drivers_count': 150,
        'drivers_with_permanent_id_count': 55,
        'drivers_with_requested_id_count': 10,
        'drivers_with_temporary_id_count': 5,
        'drivers_with_failed_id_count': 0,
        'drivers_without_id_count': 20,
        'park_id': 'pid3',
        'report_date': datetime.date(2021, 8, 4),
    },
    {
        'active_drivers_count': 10,
        'drivers_with_permanent_id_count': 5,
        'drivers_with_requested_id_count': 2,
        'drivers_with_temporary_id_count': 2,
        'drivers_with_failed_id_count': 12,
        'drivers_without_id_count': 1,
        'park_id': 'pid4',
        'report_date': datetime.date(2021, 8, 4),
    },
    {
        'active_drivers_count': 10,
        'drivers_with_permanent_id_count': 5,
        'drivers_with_requested_id_count': 0,
        'drivers_with_temporary_id_count': 4,
        'drivers_with_failed_id_count': 10,
        'drivers_without_id_count': 1,
        'park_id': 'pid1',
        'report_date': datetime.date(2021, 8, 5),
    },
    {
        'active_drivers_count': 15,
        'drivers_with_permanent_id_count': 10,
        'drivers_with_requested_id_count': 0,
        'drivers_with_temporary_id_count': 5,
        'drivers_with_failed_id_count': 0,
        'drivers_without_id_count': 0,
        'park_id': 'pid2',
        'report_date': datetime.date(2021, 8, 5),
    },
    {
        'active_drivers_count': 100,
        'drivers_with_permanent_id_count': 55,
        'drivers_with_requested_id_count': 10,
        'drivers_with_temporary_id_count': 15,
        'drivers_with_failed_id_count': 0,
        'drivers_without_id_count': 10,
        'park_id': 'pid3',
        'report_date': datetime.date(2021, 8, 5),
    },
]


@pytest.mark.yt(
    schemas=['yt_data_scheme.yaml'], static_table_data=['yt_data.yaml'],
)
@pytest.mark.pgsql('fleet_reports')
async def test_run_cron(yt_apply, cron_context):
    # Second run should not change DB or fail
    for _ in range(2):
        await run_cron.main(
            ['fleet_reports_yt.crontasks.yt_sync_kis_art_summary', '-t', '0'],
        )
        rows = await cron_context.pg.main_master.fetch(
            """SELECT * FROM yt.kis_art_summary_report
             ORDER BY report_date ASC, park_id ASC;""",
        )
        parsed = [dict(x) for x in rows]
        for row in parsed:
            del row['id']
        assert DB_FINAL_RESULT == parsed
