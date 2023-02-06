import asyncio
import logging
import typing

from taxi.maintenance import run

from sox_test_service.generated.cron import cron_context as context_module


logger = logging.getLogger(__name__)


async def do_stuff(
        task_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        *,
        log_extra: typing.Optional[dict] = None,
):
    context = typing.cast(context_module.Context, task_context.data)
    logger.info('%s: starting task %s', context.unit_name, task_context.id)
