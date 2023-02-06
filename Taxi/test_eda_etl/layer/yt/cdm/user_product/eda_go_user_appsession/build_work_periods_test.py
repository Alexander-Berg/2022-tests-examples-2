import pytest

from dmp_suite import datetime_utils as dtu
from dmp_suite.task import splitters

from eda_etl.layer.yt.cdm.user_product.eda_go_user_appsession.loader import build_work_periods


@pytest.mark.parametrize(
    't_now, t_ctl, periods',
    [
        pytest.param(
            dtu.parse_datetime('2021-11-03 06:00:00'),
            dtu.parse_datetime('2021-11-01 23:59:59.999999'),
            [
                dtu.Period('2021-10-31 00:00:00', '2021-11-02 23:59:59.999999'),
            ],
        ),
        pytest.param(
            dtu.parse_datetime('2021-11-08 06:00:00'),
            dtu.parse_datetime('2021-11-06 23:59:59.999999'),
            [
                dtu.Period('2021-10-25 00:00:00', '2021-10-31 23:59:59.999999'),
                dtu.Period('2021-11-05 00:00:00', '2021-11-07 23:59:59.999999'),
            ],
        ),
        pytest.param(
            dtu.parse_datetime('2021-11-08 06:00:00'),
            dtu.parse_datetime('2021-10-30 23:59:59.999999'),
            [
                dtu.Period('2021-10-18 00:00:00', '2021-11-07 23:59:59.999999'),
            ],
        ),
    ],
)
def test_build_work_periods(t_now, t_ctl, periods):
    def flat_map(f, items):
        return [r for i in items for r in f(i)]
    sp_days = splitters.SplitInDays()
    sp_months = splitters.SplitInMonths()
    assert flat_map(sp_days.split, periods) == build_work_periods(t_now, t_ctl, sp_days)
    assert flat_map(sp_months.split, periods) == build_work_periods(t_now, t_ctl, sp_months)
