import pytest

from eats_place_groups_replica.generated.cron import run_cron


@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_ABANDONED_TASKS={
        'enabled': True,
        'deadline': 300,
    },
)
@pytest.mark.pgsql('eats_place_groups_replica', files=['tasks.sql'])
async def test_set_status_failed(pgsql):

    await run_cron.main(
        [
            'eats_place_groups_replica.crontasks.finish_abandoned_tasks',
            '-t',
            '0',
        ],
    )

    with pgsql['eats_place_groups_replica'].dict_cursor() as cursor:
        cursor.execute(
            'SELECT status FROM integration_tasks WHERE id = \'task_id__1\'',
        )
        data = next(cursor)[0]
        assert data == 'failed'
        cursor.execute(
            'SELECT status FROM integration_tasks WHERE id = \'task_id__2\'',
        )
        data = next(cursor)[0]
        assert data == 'created'
