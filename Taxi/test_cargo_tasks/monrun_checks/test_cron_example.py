# pylint: disable=redefined-outer-name
from cargo_tasks.generated.cron import run_monrun


async def test_example():
    msg = await run_monrun.run(
        ['cargo_tasks.monrun_checks.cron_example', 'type_one'],
    )
    assert msg == '0; Check type: type_one'

    msg = await run_monrun.run(
        ['cargo_tasks.monrun_checks.cron_example', 'type_two'],
    )
    assert msg == '0; Check type: type_two'
