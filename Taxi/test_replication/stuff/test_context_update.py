import typing

from replication import core_context
from replication.stuff import context_update

TMPL = 'postgres-test_sharded_pg_shard{}-queue_mongo-staging_test_sharded_pg'
SHARD0 = TMPL.format(0)
SHARD1 = TMPL.format(1)


async def test_do_stuff(replication_ctx):
    await _run_and_check(replication_ctx, expected_state=True, remove=False)
    await _run_and_check(replication_ctx, expected_state=False, remove=True)


async def _run_and_check(replication_ctx, expected_state, remove=False):
    replication_ctx = typing.cast(core_context.TasksCoreData, replication_ctx)
    states_wrapper = replication_ctx.rule_keeper.states_wrapper
    state_shard0 = states_wrapper.get_state(replication_id=SHARD0)
    state_shard1 = states_wrapper.get_state(replication_id=SHARD1)

    if remove:
        await state_shard0.remove()
        await state_shard1.remove()

    await context_update.update_context(replication_ctx)
    assert state_shard0.initialized is expected_state
    assert state_shard1.initialized is expected_state

    assert (
        states_wrapper.get_state(
            replication_id='mongo-test_rule-queue_mongo-staging_test_rule',
        ).initialized
        is False
    )
