import datetime

import pytest

from eats_place_groups_replica.generated.cron import run_cron

CRON_SETTINGS = [
    'eats_place_groups_replica.crontasks.delete_rest_task',
    '-t',
    '0',
]
_NOW = datetime.datetime(2021, 1, 1, 6, 0, 1, tzinfo=datetime.timezone.utc)


@pytest.mark.pgsql('eats_place_groups_replica', files=['info.sql'])
async def test_should_not_start_if_disabled(
        pgsql, cron_context, cron_runner, stq,
):
    assert _get_count(pgsql) == 2
    await run_cron.main(CRON_SETTINGS)
    assert _get_count(pgsql) == 2


@pytest.mark.config(EATS_PLACE_GROUPS_REPLICA_DELETE_REST_TASK_ENABLE=True)
@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_RESTAURANT_SETTINGS={'diff_days': 100},
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('eats_place_groups_replica', files=['info.sql'])
async def test_delete_rest_task(
        cron_context, stq, cron_runner, pgsql, load_json,
):
    assert _get_count(pgsql) == 2
    await run_cron.main(CRON_SETTINGS)
    assert _get_count(pgsql) == 1


def _get_count(pgsql):
    with pgsql['eats_place_groups_replica'].dict_cursor() as cursor:
        cursor.execute(f'select count(*) from integration_tasks')
        count = cursor.fetchone()
    return count[0]
