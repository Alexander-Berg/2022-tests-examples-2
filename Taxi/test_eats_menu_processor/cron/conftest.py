# pylint: disable=redefined-outer-name
import pytest

from eats_menu_processor.generated.cron import (
    cron_context as cron_context_module,
)  # noqa: E501 pylint: disable=line-too-long


@pytest.fixture
async def cron_context(generated_secdist, pgsql, monkeypatch):
    ctx = cron_context_module.create_context()
    monkeypatch.setattr(cron_context_module, 'create_context', lambda: ctx)
    await ctx.on_startup(None)
    yield ctx
    await ctx.on_shutdown(None)
