# pylint: disable=redefined-outer-name
from example_service.generated.cron import run_monrun


async def test_example():
    msg = await run_monrun.run(
        ['check-1', 'example_service.monrun_checks.cron_example', 'type_one'],
        is_check_name_passed_as_first_argument=True,
    )
    assert msg == '0; Check type: type_one'

    msg = await run_monrun.run(
        ['check-2', 'example_service.monrun_checks.cron_example', 'type_two'],
        is_check_name_passed_as_first_argument=True,
    )
    assert msg == '0; Check type: type_two'
