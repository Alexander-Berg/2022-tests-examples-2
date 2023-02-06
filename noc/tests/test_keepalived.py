from unittest.mock import Mock, patch

from keepalived import CHECK_WAIT_TIME, KEEPALIVED_PATH, check_pid_with_retries, exit_if_bad_result, find_pid_in_file
from tt_main.constants import CRIT_STATUS, HEAT_WARN_STATUS

CHECK_NAME = "keepalived"


def test_pidfile_pid_not_found(tmp_path):
    p = tmp_path / "pidfile"
    p.write_text("15")
    result, message = find_pid_in_file(p, [16, 300, 54])
    assert not result
    assert "PID not found" in message


def test_pidfile_pid_nodata(tmp_path):
    p = tmp_path / "pidfile"
    p.write_text(" ")
    status, message = find_pid_in_file(p, [16, 300, 54])
    assert not status
    assert "PID not found" in message


def test_pidfile_pid_no_file(tmp_path):
    status, message = find_pid_in_file("/tmp/non_existent_file", [16, 300, 54])
    assert not status
    assert "not exists" in message


def test_pidfile_pid_found(tmp_path):
    p = tmp_path / "pidfile"
    p.write_text("300")
    result, _ = find_pid_in_file(p, [16, 300, 54])
    assert result


def test_exit_if_bad_result_not_status():
    print_mock = Mock()
    err_message = "problem"
    with patch("keepalived.output.print_json_format", new=print_mock):
        exit_if_bad_result(False, err_message, KEEPALIVED_PATH, CHECK_NAME, True)
    print_mock.assert_called_with(
        CHECK_NAME, f"search PID return error: {err_message}", CRIT_STATUS, tags=[HEAT_WARN_STATUS], sync_to_heat=True
    )


def test_exit_if_bad_result_not_pids():
    print_mock = Mock()
    with patch("keepalived.output.print_json_format", new=print_mock):
        exit_if_bad_result(True, [], KEEPALIVED_PATH, CHECK_NAME, True)
    print_mock.assert_called_with(
        CHECK_NAME, f"{KEEPALIVED_PATH} PID not found", CRIT_STATUS, tags=[HEAT_WARN_STATUS], sync_to_heat=True
    )


def test_exit_if_bad_result_no_fail():
    print_mock = Mock()
    with patch("keepalived.output.print_json_format", new=print_mock):
        exit_if_bad_result(True, [1], KEEPALIVED_PATH, CHECK_NAME, True)
    print_mock.assert_not_called()


@patch("keepalived.output.print_json_format", return_value=True)
@patch("keepalived.time.sleep", return_value=True)
@patch("keepalived.find_pid_in_file", return_value=(True, None))
@patch("keepalived.system.search_pids_by_cmdline", return_value=(True, [1]))
def test_check_pid_with_retries_ok(search_pids_mock, find_pid_mock, sleep_mock, *_):
    check_pid_with_retries(CHECK_NAME, True, retry=True)
    search_pids_mock.assert_called_once()
    find_pid_mock.assert_called_once()
    sleep_mock.assert_not_called()


@patch("tt_main.utils.time.sleep", return_value=True)
@patch("keepalived.output.print_json_format", return_value=True)
@patch("keepalived.time.sleep", return_value=True)
@patch("keepalived.find_pid_in_file", return_value=(True, None))
@patch("keepalived.system.search_pids_by_cmdline", side_effect=[(True, []), (True, [1])])
def test_check_pid_with_retries_search_pid_retry(search_pids_mock, find_pid_mock, sleep_mock, _, retry_sleep_mock):
    check_pid_with_retries(CHECK_NAME, True, retry=True)
    assert search_pids_mock.call_count == 2
    find_pid_mock.assert_called_once()
    sleep_mock.assert_not_called()
    retry_sleep_mock.assert_called_once()


@patch("keepalived.output.print_json_format", return_value=True)
@patch("keepalived.time.sleep", return_value=True)
@patch("keepalived.find_pid_in_file", side_effect=[(False, "problem"), (True, None)])
@patch("keepalived.system.search_pids_by_cmdline", return_value=(True, [1]))
def test_check_pid_with_retries_find_pid_in_file_retry(
    search_pids_mock,
    find_pid_mock,
    sleep_mock,
    *_,
):
    check_pid_with_retries(CHECK_NAME, True, retry=True)
    assert search_pids_mock.call_count == 2
    assert find_pid_mock.call_count == 2
    sleep_mock.assert_called_with(CHECK_WAIT_TIME)


@patch("keepalived.output.print_json_format", return_value=True)
@patch("keepalived.time.sleep", return_value=True)
@patch("keepalived.find_pid_in_file", side_effect=[(False, "problem"), (True, None)])
@patch("keepalived.system.search_pids_by_cmdline", side_effect=[(True, []), (True, [1]), (True, [1])])
def test_check_pid_with_retries_complex_problem(search_pids_mock, find_pid_mock, sleep_mock, *_):
    check_pid_with_retries(CHECK_NAME, True, retry=True)
    assert search_pids_mock.call_count == 3
    assert find_pid_mock.call_count == 2
    sleep_mock.assert_called_with(CHECK_WAIT_TIME)


@patch("keepalived.output.print_json_format", return_value=True)
@patch("keepalived.time.sleep", return_value=True)
@patch("keepalived.find_pid_in_file", return_value=(False, "problem"))
@patch("keepalived.system.search_pids_by_cmdline", return_value=(True, [1]))
def test_check_pid_with_retries_fail(search_pids_mock, find_pid_mock, sleep_mock, print_json_mock):
    check_pid_with_retries(CHECK_NAME, True, retry=True)
    assert search_pids_mock.call_count == 2
    assert find_pid_mock.call_count == 2
    sleep_mock.assert_called_with(CHECK_WAIT_TIME)
    print_json_mock.assert_called_with(CHECK_NAME, "problem", CRIT_STATUS, tags=[HEAT_WARN_STATUS], sync_to_heat=True)
