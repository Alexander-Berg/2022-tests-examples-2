from replication.foundation.invalid_docs import queue_events
from replication.stuff import queue_monitoring


async def test_do_stuff(replication_ctx):
    await queue_monitoring.run_queue_monitoring(replication_ctx)
    events_storage = queue_events.get_queue_events_storage(
        replication_ctx.pluggy_deps.replication_settings,
    )
    recent = await events_storage.get_recent()
    assert recent == {'test_sharded_rule': 3}
