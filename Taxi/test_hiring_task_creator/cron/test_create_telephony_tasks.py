# pylint: disable=redefined-outer-name
import freezegun
import pytest

from hiring_task_creator.generated.cron import run_cron


@freezegun.freeze_time('2020-10-01 09:21:34+0300', tz_offset=3)
@pytest.mark.usefixtures('geobase')
@pytest.mark.usefixtures('hiring_sf_loader')
@pytest.mark.usefixtures('hiring_telephony_oktell_callback')
async def test_create_telephony_tasks():
    await run_cron.main(
        ['hiring_task_creator.crontasks.create_telephony_tasks', '-t', '0'],
    )


@freezegun.freeze_time('2020-10-01 09:21:34+0300', tz_offset=3)
@pytest.mark.usefixtures('geobase', 'hiring_sf_loader')
async def test_none_task_fix(hiring_telephony_oktell_callback):
    with pytest.raises(RuntimeError):
        await run_cron.main(
            [
                'hiring_task_creator.crontasks.create_telephony_tasks',
                '-t',
                '0',
            ],
        )

    assert hiring_telephony_oktell_callback.has_calls
