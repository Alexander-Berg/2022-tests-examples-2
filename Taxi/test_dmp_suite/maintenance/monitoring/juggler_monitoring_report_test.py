import datetime
import unittest
from dmp_suite.juggler import EventStatus
from dmp_suite.maintenance.monitoring.juggler_monitoring_report import LagInfo


def test_lag_info_format_lag():
    formatter = LagInfo.format_lag
    m, h, d = 60, 3600, 24*3600
    assert formatter(12) == '12s'
    assert formatter(14*d + 6 * h + 35) == '14d06h'
    assert formatter(2 * h) == '2h00m'
    assert formatter(2 * d + 1 * h + 40 * m) == '2d01h'
    assert formatter(0) == '0s'
    assert formatter(-1 * h) == '-1h00m'


class TestLagInfoStatus(unittest.TestCase):
    def setUp(self):
        self.now = datetime.datetime(2019, 7, 31, 17)
        self.default_params = dict(dt=self.now, domain='', name='', param_name='')

    def test_status_ok(self):
        ok = dict(crit_lag=10, warn_lag=7, last_up=self.now - datetime.timedelta(seconds=7), **self.default_params)
        li = LagInfo(**ok)
        assert li.status == EventStatus.OK
        assert li.lag_current == 7

    def test_status_warn(self):
        ok = dict(crit_lag=10, warn_lag=7, last_up=self.now - datetime.timedelta(seconds=8), **self.default_params)
        li = LagInfo(**ok)
        assert li.status == EventStatus.WARN
        assert li.lag_current == 8

    def test_status_crit(self):
        ok = dict(crit_lag=10, warn_lag=None, last_up=self.now - datetime.timedelta(seconds=11), **self.default_params)
        li = LagInfo(**ok)
        assert li.status == EventStatus.CRIT
        assert li.lag_current == 11
