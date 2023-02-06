import pytest

TASK_TABLE_SYNC_START = 'task-table-sync-start'
SQL_SELECT_ALL_ROWS = """
SELECT * FROM
cashback_annihilator.balance_sync
"""


@pytest.mark.suspend_periodic_tasks(TASK_TABLE_SYNC_START)
@pytest.mark.config(CASHBACK_ANNIHILATOR_TABLE_SYNC_START_ENABLED=False)
async def test_periodic_sync_start_disabled(taxi_cashback_annihilator, pgsql):
    await taxi_cashback_annihilator.run_periodic_task(TASK_TABLE_SYNC_START)

    db = pgsql['cashback_annihilator']
    cursor = db.cursor()
    cursor.execute(SQL_SELECT_ALL_ROWS)

    rows = [row[0] for row in cursor]
    assert not rows


@pytest.mark.suspend_periodic_tasks(TASK_TABLE_SYNC_START)
@pytest.mark.config(
    CASHBACK_ANNIHILATOR_TABLE_SYNC_START_ENABLED=True,
    CASHBACK_ANNIHILATOR_TABLE_PATH='//home/table',
)
async def test_periodic_sync_start(
        taxi_cashback_annihilator, pgsql, yt_apply, yt_proxy,
):
    await taxi_cashback_annihilator.run_periodic_task(TASK_TABLE_SYNC_START)

    db = pgsql['cashback_annihilator']
    cursor = db.cursor()
    cursor.execute(SQL_SELECT_ALL_ROWS)

    rows = [row[0] for row in cursor]
    assert len(rows) == 1


@pytest.mark.suspend_periodic_tasks(TASK_TABLE_SYNC_START)
@pytest.mark.config(
    CASHBACK_ANNIHILATOR_TABLE_SYNC_START_ENABLED=True,
    CASHBACK_ANNIHILATOR_TABLE_PATH='//home/table',
)
async def test_periodic_sync_with_active_sync(
        taxi_cashback_annihilator, pgsql, yt_apply, yt_proxy,
):
    await taxi_cashback_annihilator.run_periodic_task(TASK_TABLE_SYNC_START)
    await taxi_cashback_annihilator.run_periodic_task(TASK_TABLE_SYNC_START)

    db = pgsql['cashback_annihilator']
    cursor = db.cursor()
    cursor.execute(SQL_SELECT_ALL_ROWS)

    rows = [row[0] for row in cursor]
    assert len(rows) == 1
