# pylint: disable=protected-access
from replication import core_context
from replication.foundation.invalid_docs import clean


async def test_auto_decrease_alerts(
        replication_ctx: core_context.TasksCoreData,
):
    invalid_docs_thresholds = (
        replication_ctx.pluggy_deps.invalid_docs_thresholds
    )
    await invalid_docs_thresholds.ensure_init()
    assert invalid_docs_thresholds.get_invalid_docs_alert('admin_draft') == 2
    assert (
        invalid_docs_thresholds.get_invalid_docs_can_continue('admin_draft')
        == 3
    )
    await clean.auto_decrease_alerts(
        replication_ctx.rule_keeper.invalid_docs_wrapper,
        replication_ctx.pluggy_deps.invalid_docs_thresholds,
    )
    await invalid_docs_thresholds.cache_holder.refresh_cache()
    assert invalid_docs_thresholds.get_invalid_docs_alert('admin_draft') == 2
    assert (
        invalid_docs_thresholds.get_invalid_docs_can_continue('admin_draft')
        == 3
    )

    await replication_ctx.db.replication_invalid_docs.remove({})
    await clean.auto_decrease_alerts(
        replication_ctx.rule_keeper.invalid_docs_wrapper,
        replication_ctx.pluggy_deps.invalid_docs_thresholds,
    )
    await invalid_docs_thresholds.cache_holder.refresh_cache()
    assert invalid_docs_thresholds.get_invalid_docs_alert('admin_draft') == 0
    assert (
        invalid_docs_thresholds.get_invalid_docs_can_continue('admin_draft')
        == 3
    )
