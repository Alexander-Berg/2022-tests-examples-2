# pylint: disable=redefined-outer-name
from eats_contact_center_monitoring.generated.cron import run_monrun


async def test_example():
    msg = await run_monrun.run(
        [
            'eats_contact_center_monitoring.monrun_checks.cron_example',
            'type_one',
        ],
    )
    assert msg == '0; Check type: type_one'

    msg = await run_monrun.run(
        [
            'eats_contact_center_monitoring.monrun_checks.cron_example',
            'type_two',
        ],
    )
    assert msg == '0; Check type: type_two'
