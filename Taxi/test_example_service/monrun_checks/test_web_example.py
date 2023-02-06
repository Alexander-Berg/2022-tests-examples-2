# pylint: disable=redefined-outer-name
from example_service.generated.web import run_monrun


async def test_example():
    msg = await run_monrun.run(
        ['web-check', 'example_service.monrun_checks.web_example'],
        is_check_name_passed_as_first_argument=True,
    )
    assert msg == '0; Check done'
