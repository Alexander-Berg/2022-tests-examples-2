import pytest

from crons.generated.cron import run_monrun


async def call_check():
    return await run_monrun.run(
        ['crons.monrun_checks.commands_too_long_in_queue'],
    )


@pytest.mark.now('2020-05-25T11:00:00Z')
async def test_ok():
    msg = await call_check()
    assert msg == '0; Check done'


@pytest.mark.now('2020-05-25T12:00:00Z')
@pytest.mark.config(
    CRON_COMMANDS_SETTINGS={
        '__default__': {'sleep_for': 300},  # 5 minutes
        'in_config': {'sleep_for': 600},  # 10 minutes
    },
)
async def test_warn():
    msg = await call_check()
    assert (
        msg == '1; 2 commands are too long in queue for tasks: in_config, some'
    )
