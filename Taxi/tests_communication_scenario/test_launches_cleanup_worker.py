import pytest


def get_launches(pgsql):
    cursor = pgsql['communication_scenario'].cursor()
    cursor.execute('SELECT launch_id FROM launches')
    return list(cursor)


@pytest.mark.pgsql(
    'communication_scenario', files=['test_launches_cleanup.sql'],
)
@pytest.mark.config(
    COMMUNICATION_SCENARIO_LAUNCHES_CLEANUP_WORKER={
        'delete_interval_ms': 0,
        'launch_ttl_minutes': 0,
        'delete_limit': 123,
    },
)
async def test_launches_cleanup(taxi_communication_scenario, pgsql):
    assert get_launches(pgsql)
    await taxi_communication_scenario.run_task(
        'distlock/launches-cleanup-worker',
    )
    assert not get_launches(pgsql)
