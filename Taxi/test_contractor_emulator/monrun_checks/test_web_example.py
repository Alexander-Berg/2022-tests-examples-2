# pylint: disable=redefined-outer-name
from contractor_emulator.generated.web import run_monrun


async def test_example():
    msg = await run_monrun.run(
        ['contractor_emulator.monrun_checks.web_example', 'type_one'],
    )
    assert msg == '0; Check type: type_one'

    msg = await run_monrun.run(
        ['contractor_emulator.monrun_checks.web_example', 'type_two'],
    )
    assert msg == '0; Check type: type_two'
