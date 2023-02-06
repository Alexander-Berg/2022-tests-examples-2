import pytest

from fleet_fines.generated.cron import cron_context as context_module


@pytest.mark.config(
    FLEET_FINES_FUSE={
        'yamoney': {'is_enabled': True, 'delay_minutes': 60, 'threshold': 2},
    },
)
async def test_fuse(cron_context: context_module.Context):
    assert not await cron_context.pg_access.fuse.yamoney_is_off()
    await cron_context.pg_access.fuse.set_yamoney()
    assert not await cron_context.pg_access.fuse.yamoney_is_off()
    await cron_context.pg_access.fuse.set_yamoney()
    assert await cron_context.pg_access.fuse.yamoney_is_off()
