# pylint: disable=redefined-outer-name
from TPL_PY_PACKAGE.generated.TPL_UNIT_NAME import run_monrun


async def test_example():
    msg = await run_monrun.run(
        ['TPL_PY_PACKAGE.monrun_checks.TPL_UNIT_NAME_example', 'type_one'],
    )
    assert msg == '0; Check type: type_one'

    msg = await run_monrun.run(
        ['TPL_PY_PACKAGE.monrun_checks.TPL_UNIT_NAME_example', 'type_two'],
    )
    assert msg == '0; Check type: type_two'
