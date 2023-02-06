import pytest

from eats_performer_hiring_metrics.common import db
from eats_performer_hiring_metrics.generated.cron import (
    cron_context as context_module,
)


async def test_webim_sync_cursor_flow(
        cron_context: context_module.Context,
) -> None:
    assert (await db.get_webim_sync_cursor(cron_context.pg)) is None
    with pytest.raises(db.DBWebimCursorNotExists):
        await db.update_webim_sync_cursor(cron_context.pg, '1')
    await db.insert_webim_sync_cursor(cron_context.pg, '2')
    assert (await db.get_webim_sync_cursor(cron_context.pg)) == '2'
    await db.update_webim_sync_cursor(cron_context.pg, '3')
    assert (await db.get_webim_sync_cursor(cron_context.pg)) == '3'
