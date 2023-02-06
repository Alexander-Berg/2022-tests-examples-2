import datetime

import pytest

from replication.foundation import sequences_schedule

_PG_TASK_ID = (
    'postgres-basic_source_postgres_shard0-'
    'queue_mongo-staging_basic_source_postgres'
)
_MONGO_SNAPSHOT_TASK_ID = (
    'mongo-basic_source_mongo_snapshot-'
    'queue_mongo-staging_basic_source_mongo_snapshot'
)
_MONGO_SNAPSHOT_TASK_ID2 = (
    'queue_mongo-staging_basic_source_mongo_snapshot-'
    'yt-basic_source_mongo_snapshot-arni'
)


@pytest.mark.parametrize(
    'replication_id,expected_filter_result',
    [
        ('queue_mongo-staging_test_rule-yt-test_rule_struct-arni', True),
        pytest.param(
            'queue_mongo-staging_test_rule-yt-test_rule_struct-hahn',
            True,
            marks=pytest.mark.now('2020-03-17T09:00:01.000Z'),
        ),
        # test cron
        pytest.param(
            'mongo-test_rule-queue_mongo-staging_test_rule',
            True,
            marks=pytest.mark.now('2020-03-17T09:00:05.000Z'),
        ),
        pytest.param(
            'mongo-test_rule-queue_mongo-staging_test_rule',
            False,  # too early
            marks=pytest.mark.now('2020-03-17T09:02:00.000Z'),
        ),
        pytest.param(
            'mongo-test_rule-queue_mongo-staging_test_rule',
            True,
            marks=pytest.mark.now('2020-03-17T09:03:00.000Z'),
        ),
        pytest.param(
            'mongo-test_rule-queue_mongo-staging_test_rule',
            True,  # outdated last sync
            marks=pytest.mark.now('2020-03-17T09:04:20.000Z'),
        ),
        # test period
        pytest.param(
            _PG_TASK_ID,
            True,
            marks=pytest.mark.now('2020-03-17T09:00:00.000Z'),
        ),
        pytest.param(
            _PG_TASK_ID,
            False,
            marks=pytest.mark.now('2020-03-17T09:03:00.000Z'),
        ),
        pytest.param(
            _PG_TASK_ID,
            False,
            marks=pytest.mark.now('2020-03-17T09:05:00.000Z'),
        ),
        pytest.param(
            _PG_TASK_ID,
            True,
            marks=pytest.mark.now('2020-03-17T09:10:10.000Z'),
        ),
        pytest.param(
            _PG_TASK_ID,
            True,  # outdated last sync
            marks=pytest.mark.now('2020-03-17T09:12:10.000Z'),
        ),
        # snapshots
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID,
            False,  # the period has not come
            marks=pytest.mark.now('2020-03-17T08:59:00.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID,
            False,
            marks=pytest.mark.now('2020-03-17T09:12:10.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID,
            True,
            marks=pytest.mark.now('2020-03-17T09:20:01.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID2,
            True,  # last_synced < queue_ready_ts=2020-03-17 09:00
            marks=pytest.mark.now('2020-03-17T08:59:00.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID2,
            True,  # last_synced < queue_ready_ts=2020-03-17 09:00
            marks=pytest.mark.now('2020-03-17T09:12:10.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID2,
            False,  # wait for source->queue_mongo upload
            marks=pytest.mark.now('2020-03-17T09:20:01.000Z'),
        ),
    ],
)
async def test_filter_tasks(
        replication_ctx, replication_id, expected_filter_result,
):
    filter_result = await _filter_tasks(replication_ctx, replication_id)
    assert (
        filter_result is expected_filter_result
    ), f'utcnow={datetime.datetime.utcnow()}'


@pytest.mark.parametrize(
    'replication_id,expected_filter_result',
    [
        # snapshots
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID,
            False,  # the period has not come
            marks=pytest.mark.now('2020-03-17T09:00:00.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID,
            False,
            marks=pytest.mark.now('2020-03-17T09:12:10.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID,
            False,  # current key lock acquired
            marks=pytest.mark.now('2020-03-17T09:20:01.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID2,
            False,  # the period has not come
            marks=pytest.mark.now('2020-03-17T09:00:00.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID2,
            False,
            marks=pytest.mark.now('2020-03-17T09:12:10.000Z'),
        ),
        pytest.param(
            _MONGO_SNAPSHOT_TASK_ID2,
            False,  # mongo->queue_mongo key lock acquired
            marks=pytest.mark.now('2020-03-17T09:20:01.000Z'),
        ),
    ],
)
async def test_filter_tasks_with_locks(
        replication_ctx, replication_id, expected_filter_result,
):
    filter_result = await _filter_tasks(
        replication_ctx,
        replication_id,
        acquired_keys=(_MONGO_SNAPSHOT_TASK_ID,),
    )
    assert filter_result is expected_filter_result


async def _filter_tasks(replication_ctx, replication_id, acquired_keys=()):
    class DummyCronClient:
        @staticmethod
        async def is_acquired(key) -> bool:
            return key in acquired_keys

    states_wrapper = replication_ctx.rule_keeper.states_wrapper
    states = [
        state
        for _, state in states_wrapper.state_items(
            replication_ids=[replication_id],
        )
    ]
    assert len(states) == 1, replication_id
    return await sequences_schedule.is_state_ready(
        replication_ctx.rule_keeper,
        replication_ctx.config,
        cron_client=DummyCronClient(),
        state=states[0],
    )
