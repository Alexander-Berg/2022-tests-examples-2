# pylint: disable=redefined-outer-name
from hiring_task_creator.generated.cron import run_monrun


async def test_example():
    msg = await run_monrun.run(
        ['hiring_task_creator.monrun_checks.cron_example', 'type_one'],
    )
    assert msg == '0; Check type: type_one'

    msg = await run_monrun.run(
        ['hiring_task_creator.monrun_checks.cron_example', 'type_two'],
    )
    assert msg == '0; Check type: type_two'
