import pytest

from fleet_reports_yt.generated.cron import run_monrun

FLEET_REPORTS_YT_MONRUN_YQL_STATUS = {
    'error_updated_at_delta': 10,
    'old_end_updated_at_delta': 12,
    'old_start_updated_at_delta': 36,
    'created_at_delta': 72,
    'alert_count_error': 1,
    'alert_count_active': 1,
    'alert_count_old_active': 1,
}


def _make_operation(status) -> str:
    return f"""
        INSERT INTO yt.operations
            (
                operation_id,
                operation_status,
                type,
                status,
                cluster,
                created_at,
                updated_at
            )
        VALUES
            (
                'operation_id_0',
                'COMPLETED',
                'report_summary',
                '{status}',
                'hahn',
                '2020-05-18T00:00:00+00:00',
                '2020-05-18T00:00:00+00:00'
            )
        """


@pytest.mark.pgsql(
    'fleet_reports', queries=[_make_operation('uploaded_to_db')],
)
@pytest.mark.now('2020-05-18T00:05:00+00:00')
@pytest.mark.config(
    FLEET_REPORTS_YT_MONRUN_YQL_STATUS=FLEET_REPORTS_YT_MONRUN_YQL_STATUS,
)
async def test_ok():
    msg = await run_monrun.run(
        ['fleet_reports_yt.monrun_checks.cron_yql_status'],
    )
    assert msg == '0; OK'


@pytest.mark.pgsql(
    'fleet_reports',
    queries=[_make_operation('yql_error'), _make_operation('uploaded_to_db')],
)
@pytest.mark.now('2020-05-18T00:05:00+00:00')
@pytest.mark.config(
    FLEET_REPORTS_YT_MONRUN_YQL_STATUS=FLEET_REPORTS_YT_MONRUN_YQL_STATUS,
)
async def test_error():
    msg = await run_monrun.run(
        ['fleet_reports_yt.monrun_checks.cron_yql_status'],
    )
    assert msg == '2; YQL count_error = 1'


@pytest.mark.pgsql(
    'fleet_reports',
    queries=[
        _make_operation('yql_running'),
        _make_operation('uploaded_to_db'),
    ],
)
@pytest.mark.now('2020-05-18T00:05:00+00:00')
@pytest.mark.config(
    FLEET_REPORTS_YT_MONRUN_YQL_STATUS=FLEET_REPORTS_YT_MONRUN_YQL_STATUS,
)
async def test_active():
    msg = await run_monrun.run(
        ['fleet_reports_yt.monrun_checks.cron_yql_status'],
    )
    assert msg == '1; YQL count_active = 1'


@pytest.mark.now('2020-05-18T16:00:00+00:00')
@pytest.mark.config(
    FLEET_REPORTS_YT_MONRUN_YQL_STATUS=FLEET_REPORTS_YT_MONRUN_YQL_STATUS,
)
async def test_all():
    msg = await run_monrun.run(
        ['fleet_reports_yt.monrun_checks.cron_yql_status'],
    )
    assert msg == '1; YQL count_all = 0'
