from copy import copy
from unittest.mock import patch

from memory import check_free_mem
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS

# Stripped version of what tt_main.system.parse_meminfo returns
MEMINFO_SAMPLE = {
    'MemTotal': '131903776 kB',
    'MemFree': '88580328 kB',
    'MemAvailable': '88397304 kB',
    'MemKernel': '39960436 kB'
}


def test_check_free_mem_ok():
    with patch("memory.parse_meminfo", return_value=(True, MEMINFO_SAMPLE)):
        status, message = check_free_mem()
    assert status == OK_STATUS


def test_check_free_mem_low():
    meminfo = copy(MEMINFO_SAMPLE)
    meminfo["MemAvailable"] = "200000 kB"
    with patch("memory.parse_meminfo", return_value=(True, meminfo)):
        status, message = check_free_mem()
    assert status == CRIT_STATUS
    assert message == "MemAvailable less than threshold"


def test_check_free_mem_parsing_error():
    with patch("memory.parse_meminfo", return_value=(False, "some error")):
        status, message = check_free_mem()
    assert status == CRIT_STATUS
    assert message == "error: some error"


def test_check_free_mem_no_key():
    meminfo = copy(MEMINFO_SAMPLE)
    del meminfo["MemAvailable"]
    with patch("memory.parse_meminfo", return_value=(True, meminfo)):
        status, message = check_free_mem()
    assert status == CRIT_STATUS
    assert message == "MemAvailable not found"


def test_multiple_issues():
    meminfo = copy(MEMINFO_SAMPLE)
    thresholds = {"MemAvailable": 500000, "MemFree": 500000}
    del meminfo["MemAvailable"]
    meminfo["MemFree"] = "200000 kB"
    with patch("memory.parse_meminfo", return_value=(True, meminfo)):
        status, message = check_free_mem(thresholds)
    assert status == CRIT_STATUS
    assert message == "MemAvailable not found; MemFree less than threshold"
