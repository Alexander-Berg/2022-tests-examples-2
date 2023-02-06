import pytest

from fleet_reports_yt.generated.cron import run_cron

FETCH_DATA = """SELECT * FROM yt.report_summary_parks
            ORDER BY date_month ASC, park_id ASC"""


@pytest.mark.yt(
    schemas=['yt_data_scheme.yaml'], static_table_data=['yt_data.yaml'],
)
@pytest.mark.config(FLEET_REPORTS_YT_JOBS={'report_summary_v2': True})
@pytest.mark.pgsql('fleet_reports', files=('fleet_reports.sql',))
async def test_run_cron(yt_apply, patch, cron_context):
    @patch('fleet_reports_yt.logic.jobs.report_summary.drivers.run')
    async def _run(*args, **kwargs):
        pass

    await run_cron.main(['fleet_reports_yt.crontasks.yt_load', '-t', '0'])
    rows = await cron_context.pg.main_master.fetch(FETCH_DATA)
    parsed = [dict(x) for x in rows]
    assert parsed[0]['avg_cars_work_time_seconds'] == 760
    assert parsed[0]['price_hiring_returned_inc_vat'] is None
