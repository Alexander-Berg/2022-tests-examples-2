# pylint: disable=redefined-outer-name

import pytest

from support_info import cron_run


@pytest.mark.config(
    SUPPORT_PROMOCODE_MONITORING_SETTINGS={
        'reserve_daily_limit': 20000,
        'reserve_series_limit': 10000000,
        'reserve_days_series_finish': 10,
    },
)
@pytest.mark.now('2018-12-28T12:34:56')
async def test_promocodes_monitor(db, simple_secdist):
    with pytest.raises(RuntimeError) as exc:
        await cron_run.main(
            ['support_info.crontasks.promocodes_monitor', '-t', '0', '-d'],
        )
    assert exc.value.args[0] == [
        'daily limit 1/15000',
        'regret series limit 1/10000000',
        'regret series finish 2017-05-07 12:34:56',
    ]
