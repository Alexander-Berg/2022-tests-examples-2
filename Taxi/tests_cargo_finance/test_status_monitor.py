import pytest


def make_expected_stats(
        claims_debt_count=0,
        taxiparks_debt_count=0,
        error_count=0,
        disabled_stats_count=0,
):
    return {
        'flow_stats': {
            'claims': {
                'debt_count': claims_debt_count,
                'processing_count': 1,
                'total_count': 2,
            },
            'taxiparks': {
                'debt_count': taxiparks_debt_count,
                'processing_count': 1,
                'total_count': 3,
            },
        },
        'errors': {
            'error_count': error_count,
            'disabled_stats_count': disabled_stats_count,
            'claims': {'hanged_count': 0},
            'taxiparks': {'hanged_count': 1},
        },
        'timing': {'flow_stats': 0},
    }


@pytest.mark.pgsql('cargo_finance', files=['insert_payments.sql'])
@pytest.mark.config(
    CARGO_FINANCE_MAIN_BOARD_ENABLED=True,
    CARGO_FINANCE_MAIN_BOARD_SETTINGS={
        'worker_settings': {'sleep_time_seconds': 45},
        'graphs_settings': {
            'statistics_ttl_seconds:': 60,
            'settings_by_graph': {
                'hanged_payments': {'hanged_duration_seconds': 300},
            },
        },
    },
)
async def test_worker_processing_events_stats(run_status_monitor_worker):
    stats = await run_status_monitor_worker()
    assert stats == make_expected_stats(claims_debt_count=1)
