from taxi.maintenance import run
from taxi.maintenance import task

from replication import core_context
from replication import create_context


async def test_basic_cron_run(replication_ctx, loop, mock):
    @mock
    async def do_stuff(context, loop, log_extra=None):
        assert isinstance(context.data, core_context.TasksCoreData)

    await run.run_task(
        task.BaseTask('', '', do_stuff, 0),
        create_context.create_context,
        force_start=True,
        rand_delay=0,
        without_lock=True,
        quiet=False,
        loop=loop,
    )
    assert len(do_stuff.calls) == 1
