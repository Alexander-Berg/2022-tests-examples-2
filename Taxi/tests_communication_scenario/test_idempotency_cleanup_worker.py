import pytest


def get_tokens(pgsql):
    cursor = pgsql['communication_scenario'].cursor()
    cursor.execute('SELECT token FROM idempotency_tokens')
    return list(cursor)


@pytest.mark.pgsql('communication_scenario', files=['idempotency_expired.sql'])
async def test_idempotency_cleanup(taxi_communication_scenario, pgsql):
    assert get_tokens(pgsql)
    await taxi_communication_scenario.run_task(
        'distlock/idempotency-cleanup-worker',
    )
    assert not get_tokens(pgsql)
