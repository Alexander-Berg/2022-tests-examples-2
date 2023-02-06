from collections import namedtuple
from unittest.mock import patch

from cpu_stat import check_cpu_utilization
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS

scputimes = namedtuple(
    "scputimes",
    "user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice")


def test_cpu_util_ok():
    with patch("psutil.cpu_times_percent",
               side_effect=[
                   16 * [
                       scputimes(0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                 0.0)
                   ],
                   scputimes(0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0)
               ]):
        res = check_cpu_utilization()
    assert res[0] == OK_STATUS
    assert res[1] == "OK"


def test_high_avg_si():
    avg_data = scputimes(0.0, 0.0, 0.0, 54.0, 0.0, 0.0, 46.0, 0.0, 0.0, 0.0)
    with patch("psutil.cpu_times_percent",
               side_effect=[
                   16 * [
                       scputimes(0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                 0.0)
                   ], avg_data
               ]):
        res = check_cpu_utilization()
    assert res[0] == WARN_STATUS
    assert "high average softirq" in res[1]


def test_one_core_heavy_is_ok():
    cores_data = 16 * [
        scputimes(0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    ]
    cores_data[5] = scputimes(0.0, 0.0, 0.0, 5.0, 95.0, 0.0, 0.0, 0.0, 0.0,
                              0.0)
    avg_data = scputimes(0.0, 0.0, 0.0, 95.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0)
    with patch("psutil.cpu_times_percent", side_effect=[cores_data, avg_data]):
        res = check_cpu_utilization()
    assert res[0] == OK_STATUS
    assert res[1] == "OK"


def test_four_cores_heavy_is_not_ok():
    cores_data = 16 * [
        scputimes(0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    ]
    cores_data[3] = scputimes(0.0, 0.0, 0.0, 5.0, 95.0, 0.0, 0.0, 0.0, 0.0,
                              0.0)
    cores_data[6] = scputimes(0.0, 0.0, 0.0, 5.0, 95.0, 0.0, 0.0, 0.0, 0.0,
                              0.0)
    cores_data[12] = scputimes(93.0, 0.0, 0.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0)
    cores_data[14] = scputimes(93.0, 0.0, 0.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0)
    avg_data = scputimes(0.0, 0.0, 0.0, 95.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0)
    with patch("psutil.cpu_times_percent", side_effect=[cores_data, avg_data]):
        res = check_cpu_utilization()
    assert res[0] == CRIT_STATUS
    assert "4 cores" in res[1]


def test_one_core_high_si_is_crit():
    cores_data = 16 * [
        scputimes(0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    ]
    cores_data[4] = scputimes(10.0, 0.0, 0.0, 5.0, 0.0, 0.0, 85.0, 0.0, 0.0,
                              0.0)
    avg_data = scputimes(0.0, 0.0, 0.0, 70.0, 0.0, 0.0, 15.0, 0.0, 0.0, 0.0)
    with patch("psutil.cpu_times_percent", side_effect=[cores_data, avg_data]):
        res = check_cpu_utilization()
    assert res[0] == CRIT_STATUS
    assert "softirq" in res[1]


def test_some_cores_high_si_is_crit():
    cores_data = 16 * [
        scputimes(0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    ]
    cores_data[4] = scputimes(10.0, 0.0, 0.0, 5.0, 0.0, 0.0, 85.0, 0.0, 0.0,
                              0.0)
    cores_data[0] = scputimes(8.0, 0.0, 0.0, 7.0, 0.0, 0.0, 85.0, 0.0, 0.0,
                              0.0)
    cores_data[14] = scputimes(0.0, 0.0, 0.0, 5.0, 10.0, 0.0, 85.0, 0.0, 0.0,
                               0.0)
    avg_data = scputimes(0.0, 0.0, 0.0, 70.0, 0.0, 0.0, 15.0, 0.0, 0.0, 0.0)
    with patch("psutil.cpu_times_percent", side_effect=[cores_data, avg_data]):
        res = check_cpu_utilization()
    assert res[0] == CRIT_STATUS
    assert "3 cores softirq" in res[1]
