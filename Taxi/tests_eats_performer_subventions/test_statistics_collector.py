import pytest


@pytest.mark.pgsql(
    'eats_performer_subventions', files=['subvention_goals.sql'],
)
async def test_statistics_collector_metrics(
        taxi_eats_performer_subventions,
        taxi_eats_performer_subventions_monitor,
):
    await taxi_eats_performer_subventions.run_task('statistics-collector-task')

    metrics = await taxi_eats_performer_subventions_monitor.get_metric(
        'statistics-collector',
    )

    assert metrics['goals_by_statuses_count'] == {
        'dxgy': {
            'in_progress': 3,
            'cancelled': 0,
            'paid': 0,
            'finished': 1,
            'failed': 1,
        },
        'daily_goal': {
            'in_progress': 2,
            'cancelled': 0,
            'paid': 0,
            'finished': 0,
            'failed': 1,
        },
        'retention': {
            'in_progress': 0,
            'cancelled': 0,
            'paid': 0,
            'finished': 0,
            'failed': 0,
        },
    }

    assert metrics['not_synced_goals_count'] == {
        'dxgy': 3,
        'daily_goal': 2,
        'retention': 0,
    }
    assert metrics['not_paid_goals_count'] == {
        'dxgy': 1,
        'daily_goal': 0,
        'retention': 0,
    }
