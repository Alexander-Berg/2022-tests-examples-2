from unittest.mock import patch

import pytest
from hw_watcher_status import (get_hw_status, is_modules_valid,
                               parse_enabled_modules)
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS


def test_disk_ok():
    with patch('hw_watcher_status.make_cmd_call',
               return_value=['OK; Last check: Fri Sep  4 20:39:08 2020']):
        assert get_hw_status("disk")[1] == "OK"


def test_malformed_output_status():
    with patch('hw_watcher_status.make_cmd_call',
               return_value=['BAD; some error happened']):
        assert "malformed output" in get_hw_status("cpu")[1]


def test_malformed_output_length():
    with patch('hw_watcher_status.make_cmd_call',
               return_value=['BAD hw_watcher message']):
        assert "malformed output" in get_hw_status("cpu")[1]


def test_mem_erorrs():
    with patch('hw_watcher_status.make_cmd_call',
               return_value=['FAILED; uncorrectable errors DIMM1; more text']):
        result = get_hw_status("mem")
        assert "uncorrectable errors" in result[1]
        assert result[0] == WARN_STATUS


def test_no_config_file():
    with pytest.raises(IOError):
        parse_enabled_modules('/tmp/no_such_file')


def test_parse_enabled_modules(tmpdir):
    content = """[global]
mail_to = traffic-cc@yandex-team.ru
enable_module = mem, ecc, disk, cpu, bmc
reaction = bot-needcall"""

    p = tmpdir.join("hw_watcher.conf")
    p.write(content)
    result = parse_enabled_modules(str(p))
    assert len(result) == 5
    assert "disk" in result


def test_parse_no_modules_string(tmpdir):
    content = """[global]
mail_to = traffic-cc@yandex-team.ru
reaction = bot-needcall"""

    p = tmpdir.join("hw_watcher.conf")
    p.write(content)
    result = parse_enabled_modules(str(p))
    assert len(result) == 0


def test_parse_empty_modules_string(tmpdir):
    content = """[global]
mail_to = traffic-cc@yandex-team.ru
enable_module =
reaction = bot-needcall"""

    p = tmpdir.join("hw_watcher.conf")
    p.write(content)
    result = parse_enabled_modules(str(p))
    assert len(result) == 0


def test_incorrect_modules_string():
    assert is_modules_valid({"m;m", "!"}) is False


def test_correct_modules_string():
    assert is_modules_valid({"mem", "disk"}) is True


def test_empty_modules_string():
    assert is_modules_valid(set()) is False
