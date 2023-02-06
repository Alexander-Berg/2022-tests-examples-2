import datetime

import pytest

from eats_place_groups_replica.generated.cron import run_cron

CRON_SETTINGS = [
    'eats_place_groups_replica.crontasks.init_scheduler_rest',
    '-t',
    '0',
]
_NOW = datetime.datetime(2021, 1, 1, 6, 0, 1, tzinfo=datetime.timezone.utc)


async def test_should_not_start_if_disabled(cron_context, cron_runner, stq):
    await run_cron.main(CRON_SETTINGS)
    assert not stq.eats_place_groups_replica_create_task.has_calls


@pytest.mark.config(EATS_PLACE_GROUPS_REPLICA_INIT_SCHEDULER_ENABLE=True)
@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_RESTAURANT_SETTINGS={
        'parser_stop_list': {'place_group_id1': {'retry_time': 10}},
    },
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('eats_place_groups_replica', files=['info.sql'])
async def test_init_scheduler_rest(
        cron_context, stq, cron_runner, pgsql, load_json,
):
    with stq.flushing():
        await run_cron.main(CRON_SETTINGS)

        assert stq.eats_place_groups_replica_create_task.has_calls
        road_stq_data = load_json('road_stq_data.json')
        for i in range(0, 11):
            task = stq.eats_place_groups_replica_create_task.next_call()[
                'kwargs'
            ]['task']
            assert task['type'] == road_stq_data[i]['type']
            assert task['place_id'] == road_stq_data[i]['place_id']
        assert stq.is_empty
