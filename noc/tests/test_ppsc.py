from itertools import product
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from bgp_state import BGPStateException
from click.testing import CliRunner
from ppsc import (APP_ERROR, CHECK_ERROR, CHECK_SYSTEMS, FILE_SUFFIX_BASELINE,
                  FILE_SUFFIX_CURRENT, ppsc)

EXIT_OK = 0
DEFAULT_SAVE_PATH = "/tmp/ppsc_state"
CUSTOM_DIR = "/tmp/ppsc_tmp"


def create_empty_result_file(path):
    path = Path(path)
    path.write_text("{}")
    return True


def create_error_raising_func(error, err_msg):
    def error_raising_func(path):
        create_empty_result_file(path)
        raise error(err_msg)

    return error_raising_func


@pytest.fixture
def clean_files():
    for combo in product(CHECK_SYSTEMS,
                         [FILE_SUFFIX_BASELINE, FILE_SUFFIX_CURRENT]):
        system, state = combo
        try:
            Path(f"{DEFAULT_SAVE_PATH}_{system}_{state}").unlink()
        except FileNotFoundError:
            # missing_ok=True available since 3.8
            pass
    p = Path(CUSTOM_DIR)
    if p.exists():
        for _file in p.iterdir():
            _file.unlink()
        p.rmdir()


def test_pre_check_all_ok(clean_files):
    empty_result_mock = MagicMock(side_effect=create_empty_result_file)
    mock_map = {
        "bgp": empty_result_mock,
        "ipvs": empty_result_mock,
        "ipaddr": empty_result_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    runner = CliRunner()
    result = runner.invoke(ppsc)
    assert result.exit_code == EXIT_OK
    assert result.output == "Pre-check OK\n"
    assert Path(f"{DEFAULT_SAVE_PATH}_bgp_{FILE_SUFFIX_BASELINE}").exists()
    assert Path(f"{DEFAULT_SAVE_PATH}_ipvs_{FILE_SUFFIX_BASELINE}").exists()
    assert Path(f"{DEFAULT_SAVE_PATH}_ipaddr_{FILE_SUFFIX_BASELINE}").exists()


def test_pre_checks_no_bgp(clean_files):
    err_msg = "No BGP sessions in Established state found!"
    #bgp_mock = MagicMock(side_effect=BGPStateException(err_msg))
    bgp_mock = MagicMock(
        side_effect=create_error_raising_func(BGPStateException, err_msg))
    empty_result_mock = MagicMock(side_effect=create_empty_result_file)
    mock_map = {
        "bgp": bgp_mock,
        "ipvs": empty_result_mock,
        "ipaddr": empty_result_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    runner = CliRunner()
    result = runner.invoke(ppsc)
    assert result.exit_code == CHECK_ERROR
    assert result.output == err_msg + "\n"
    assert Path(f"{DEFAULT_SAVE_PATH}_bgp_{FILE_SUFFIX_BASELINE}").exists()
    assert Path(f"{DEFAULT_SAVE_PATH}_ipvs_{FILE_SUFFIX_BASELINE}").exists()
    assert Path(f"{DEFAULT_SAVE_PATH}_ipaddr_{FILE_SUFFIX_BASELINE}").exists()


def test_post_check_no_diff(clean_files):
    none_mock = MagicMock(return_value=None)
    mock_map = {"bgp": none_mock, "ipvs": none_mock, "ipaddr": none_mock}
    zero_diff_mock = MagicMock(return_value=(0, ""))
    diff_map = {
        "bgp": zero_diff_mock,
        "ipvs": zero_diff_mock,
        "ipaddr": zero_diff_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.DIFFS_MAP", new=diff_map)
    patcher3 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    patcher3.start()
    for system in CHECK_SYSTEMS:
        create_empty_result_file(
            f"{DEFAULT_SAVE_PATH}_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(ppsc, ["--diff"])
    assert result.exit_code == EXIT_OK
    assert result.output == "Post-check OK\n"


def test_post_check_no_diff_but_warns(clean_files):
    none_mock = MagicMock(return_value=None)
    mock_map = {"bgp": none_mock, "ipvs": none_mock, "ipaddr": none_mock}
    zero_diff_mock = MagicMock(return_value=(0, ""))
    bgp_diff = "b_core_4 has more prefixes:\n+\t2001:db8:cc::4/128"
    bgp_diff_mock = MagicMock(return_value=(0, bgp_diff))
    diff_map = {
        "bgp": bgp_diff_mock,
        "ipvs": zero_diff_mock,
        "ipaddr": zero_diff_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.DIFFS_MAP", new=diff_map)
    patcher3 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    patcher3.start()
    for system in CHECK_SYSTEMS:
        create_empty_result_file(
            f"{DEFAULT_SAVE_PATH}_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(ppsc, ["--diff"])
    assert result.exit_code == EXIT_OK
    assert result.output == f"{bgp_diff}\nPost-check OK\n"


def test_post_check_one_system_diff(clean_files):
    none_mock = MagicMock(return_value=None)
    mock_map = {"bgp": none_mock, "ipvs": none_mock, "ipaddr": none_mock}
    zero_diff_mock = MagicMock(return_value=(0, ""))
    bgp_diff = "b_core_2 has less prefixes:\n-\t2001:db8:cc::d4d/128"
    bgp_diff_mock = MagicMock(return_value=(1, bgp_diff))
    diff_map = {
        "bgp": bgp_diff_mock,
        "ipvs": zero_diff_mock,
        "ipaddr": zero_diff_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.DIFFS_MAP", new=diff_map)
    patcher3 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    patcher3.start()
    for system in CHECK_SYSTEMS:
        create_empty_result_file(
            f"{DEFAULT_SAVE_PATH}_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(ppsc, ["--diff"])
    assert result.exit_code == CHECK_ERROR
    assert result.output == bgp_diff + "\n"


def test_post_check_two_systems_diff(clean_files):
    none_mock = MagicMock(return_value=None)
    mock_map = {"bgp": none_mock, "ipvs": none_mock, "ipaddr": none_mock}
    zero_diff_mock = MagicMock(return_value=(0, ""))
    bgp_diff = "b_core_2 has less prefixes:\n-\t2001:db8:cc::d4d/128"
    bgp_diff_mock = MagicMock(return_value=(0, bgp_diff))
    ipvs_diff = "TCP  198.51.100.200:80 OLD/NEW: 60 / 50"
    ipvs_diff_mock = MagicMock(return_value=(1, ipvs_diff))
    diff_map = {
        "bgp": bgp_diff_mock,
        "ipvs": ipvs_diff_mock,
        "ipaddr": zero_diff_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.DIFFS_MAP", new=diff_map)
    patcher3 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    patcher3.start()
    for system in CHECK_SYSTEMS:
        create_empty_result_file(
            f"{DEFAULT_SAVE_PATH}_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(ppsc, ["--diff"])
    assert result.exit_code == CHECK_ERROR
    assert result.output == f"{bgp_diff}\n{ipvs_diff}\n"


def test_post_check_j_warn(clean_files):
    none_mock = MagicMock(return_value=None)
    mock_map = {"bgp": none_mock, "ipvs": none_mock, "ipaddr": none_mock}
    zero_diff_mock = MagicMock(return_value=(0, ""))
    diff_map = {
        "bgp": zero_diff_mock,
        "ipvs": zero_diff_mock,
        "ipaddr": zero_diff_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.DIFFS_MAP", new=diff_map)
    j_msg = "WARN: svc_announced (announces disabled?)"
    patcher3 = patch("ppsc.query_juggler", return_value=(0, j_msg))
    patcher1.start()
    patcher2.start()
    patcher3.start()
    for system in CHECK_SYSTEMS:
        create_empty_result_file(
            f"{DEFAULT_SAVE_PATH}_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(ppsc, ["--diff"])
    assert result.exit_code == EXIT_OK
    assert result.output == j_msg + "\nPost-check OK\n"


def test_post_check_j_crit():
    j_msg = "CRIT: check_tun (/usr/sbin/check-tun pid not found)"
    with patch("ppsc.query_juggler", return_value=(1, j_msg)):
        runner = CliRunner()
        result = runner.invoke(ppsc, ["--diff"])
    assert result.exit_code == CHECK_ERROR
    assert result.output == j_msg + "\n"


def test_pre_check_j_crit():
    j_msg = "CRIT: check_tun (/usr/sbin/check-tun pid not found)"
    with patch("ppsc.query_juggler", return_value=(1, j_msg)):
        runner = CliRunner()
        result = runner.invoke(ppsc)
    assert result.exit_code == CHECK_ERROR
    assert result.output == j_msg + "\n"


def test_custom_save_path(clean_files):
    none_mock = MagicMock(return_value=None)
    bgp_mock = MagicMock(return_value=None)
    mock_map = {"bgp": bgp_mock, "ipvs": none_mock, "ipaddr": none_mock}
    p = Path(CUSTOM_DIR)
    with patch("ppsc.CHECKS_MAP", new=mock_map):
        runner = CliRunner()
        result = runner.invoke(
            ppsc, ["--save-path", p, "--filename-prefix", "save_there"])
    assert result.exit_code == EXIT_OK
    assert result.output == "Pre-check OK\n"
    bgp_mock.assert_called_with(
        f"{CUSTOM_DIR}/save_there_bgp_{FILE_SUFFIX_BASELINE}")


def test_custom_dir_only(clean_files):
    none_mock = MagicMock(return_value=None)
    bgp_mock = MagicMock(return_value=None)
    mock_map = {"bgp": bgp_mock, "ipvs": none_mock, "ipaddr": none_mock}
    p = Path(CUSTOM_DIR)
    with patch("ppsc.CHECKS_MAP", new=mock_map):
        runner = CliRunner()
        result = runner.invoke(ppsc, ["--save-path", p])
    assert result.exit_code == EXIT_OK
    assert result.output == "Pre-check OK\n"
    bgp_mock.assert_called_with(
        f"{CUSTOM_DIR}/ppsc_state_bgp_{FILE_SUFFIX_BASELINE}")


def test_custom_save_path_diff(clean_files):
    none_mock = MagicMock(return_value=None)
    bgp_mock = MagicMock(return_value=None)
    mock_map = {"bgp": bgp_mock, "ipvs": none_mock, "ipaddr": none_mock}
    zero_diff_mock = MagicMock(return_value=(0, ""))
    bgp_diff_mock = MagicMock(return_value=(0, ""))
    diff_map = {
        "bgp": bgp_diff_mock,
        "ipvs": zero_diff_mock,
        "ipaddr": zero_diff_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.DIFFS_MAP", new=diff_map)
    patcher3 = patch("ppsc.query_juggler", return_value=(0, ""))
    p = Path(CUSTOM_DIR)
    p.mkdir()
    patcher1.start()
    patcher2.start()
    patcher3.start()
    for system in CHECK_SYSTEMS:
        create_empty_result_file(
            f"{CUSTOM_DIR}/save_there_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(
        ppsc, ["--save-path", p, "--filename-prefix", "save_there", "--diff"])
    assert result.exit_code == EXIT_OK
    assert result.output == "Post-check OK\n"
    bgp_mock.assert_called_with(
        f"{CUSTOM_DIR}/save_there_bgp_{FILE_SUFFIX_CURRENT}")
    bgp_diff_mock.assert_called_with(
        f"{CUSTOM_DIR}/save_there_bgp_{FILE_SUFFIX_BASELINE}",
        f"{CUSTOM_DIR}/save_there_bgp_{FILE_SUFFIX_CURRENT}")


def test_pre_checks_skip_bgp(clean_files):
    none_mock = MagicMock(return_value=None)
    bgp_mock = MagicMock(return_value=None)
    mock_map = {"bgp": bgp_mock, "ipvs": none_mock, "ipaddr": none_mock}
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    runner = CliRunner()
    result = runner.invoke(ppsc, ["--check", "ipvs", "--check", "ipaddr"])
    assert result.exit_code == EXIT_OK
    bgp_mock.assert_not_called()


def test_post_check_skip_bgp_ipvs_diff_nok(clean_files):
    none_mock = MagicMock(return_value=None)
    bgp_mock = MagicMock(return_value=None)
    mock_map = {"bgp": bgp_mock, "ipvs": none_mock, "ipaddr": none_mock}
    zero_diff_mock = MagicMock(return_value=(0, ""))
    bgp_diff_mock = MagicMock(return_value=(0, ""))
    ipvs_diff = "TCP  198.51.100.200:80 OLD/NEW: 60 / 50"
    ipvs_diff_mock = MagicMock(return_value=(1, ipvs_diff))
    diff_map = {
        "bgp": bgp_diff_mock,
        "ipvs": ipvs_diff_mock,
        "ipaddr": zero_diff_mock
    }
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.DIFFS_MAP", new=diff_map)
    patcher3 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    patcher3.start()
    for system in ["ipvs", "ipaddr"]:
        create_empty_result_file(
            f"{DEFAULT_SAVE_PATH}_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(ppsc,
                           ["--diff", "--check", "ipvs", "--check", "ipaddr"])
    assert result.exit_code == CHECK_ERROR
    assert result.output == ipvs_diff + "\n"
    bgp_mock.assert_not_called()
    bgp_diff_mock.assert_not_called()


def test_pre_check_baseline_exists(clean_files):
    none_mock = MagicMock(return_value=None)
    mock_map = {"bgp": none_mock, "ipvs": none_mock, "ipaddr": none_mock}
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    for system in CHECK_SYSTEMS:
        create_empty_result_file(
            f"{DEFAULT_SAVE_PATH}_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(ppsc)
    assert result.exit_code == APP_ERROR
    assert "files already exists for: bgp, ipaddr, ipvs." in result.output


def test_pre_check_force_overwrite_baseline(clean_files):
    none_mock = MagicMock(return_value=None)
    mock_map = {"bgp": none_mock, "ipvs": none_mock, "ipaddr": none_mock}
    patcher1 = patch("ppsc.CHECKS_MAP", new=mock_map)
    patcher2 = patch("ppsc.query_juggler", return_value=(0, ""))
    patcher1.start()
    patcher2.start()
    for system in ["ipvs", "ipaddr"]:
        create_empty_result_file(
            f"{DEFAULT_SAVE_PATH}_{system}_{FILE_SUFFIX_BASELINE}")
    runner = CliRunner()
    result = runner.invoke(ppsc, ["--force"])
    assert result.exit_code == EXIT_OK
