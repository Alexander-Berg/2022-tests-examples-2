import pytest

from taxi_loyalty_py3.helpers import settings
from taxi_loyalty_py3.logic import yt_to_pg_driver_info_sync as logic


@pytest.mark.parametrize(
    'should_start',
    [
        pytest.param(False, marks=[pytest.mark.now('2020-01-01 00:00:00+02')]),
        pytest.param(False, marks=[pytest.mark.now('2020-01-01 00:00:00+00')]),
        pytest.param(False, marks=[pytest.mark.now('2020-01-01 00:00:00-02')]),
        pytest.param(False, marks=[pytest.mark.now('2020-01-31 20:00:00+03')]),
        pytest.param(False, marks=[pytest.mark.now('2020-01-31 20:59:59+03')]),
        pytest.param(True, marks=[pytest.mark.now('2020-01-31 21:00:00+03')]),
        pytest.param(True, marks=[pytest.mark.now('2020-01-31 22:00:00+03')]),
        pytest.param(True, marks=[pytest.mark.now('2020-01-31 22:59:59+03')]),
        pytest.param(False, marks=[pytest.mark.now('2020-01-31 23:00:00+03')]),
        pytest.param(False, marks=[pytest.mark.now('2020-01-31 23:59:59+03')]),
        pytest.param(False, marks=[pytest.mark.now('2020-02-01 00:00:00+03')]),
    ],
)
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS={
        '__default__': {},
        'last_order_update': {
            'enabled': True,
            'hours_to_next_month_start': 3,
            'hours_to_next_month_end': 1,
        },
    },
)
def test_end_of_month_approaching(cron_context, should_start):

    job_settings = settings.YtSyncSettings(cron_context, 'last_order_update')

    use_case = logic.YtToPgDriverInfoSync(cron_context, job_settings)

    assert use_case.should_start() == should_start
