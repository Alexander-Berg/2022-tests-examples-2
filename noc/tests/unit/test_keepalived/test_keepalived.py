from datetime import datetime
from unittest.mock import Mock, call, mock_open, patch

import pytest

from balancer_agent.operations.systems.base import CommandExecutionError
from balancer_agent.operations.systems.keepalived import (
    FailedToReStartKeepalivedError,
    FailedToStartKeepalivedError,
    FailedToStopKeepalivedError,
    Keepalived,
    KeepalivedTest,
)

DATE_NOW = datetime.now().strftime("%Y%m%d")


class MockDatetime:
    def now(self):
        return self

    def strftime(self, *args):
        return DATE_NOW


TEST_SERVICE = "test"
TEST_CONFIG_ID = 123

EXCEPTION_MOCK_CONTENT = "Failure"


@pytest.mark.parametrize(
    "expected",
    [True, False],
)
@patch("balancer_agent.operations.systems.keepalived.CommandExecutor")
def test_check_process_exists(mocked_command_executor, expected):
    keepalived = KeepalivedTest()

    if not expected:
        mocked_command_executor.return_value.cmd_result.stdout = keepalived.NO_PROCESS_FOUND_OUTPUT

    result = keepalived.check_process_exists()
    mocked_command_executor.return_value.run_cmd.assert_called_with(keepalived.CHECK_PROCESS_BY_PID_CMD)

    if not expected:
        assert not result
    else:
        assert result


@pytest.mark.parametrize(
    "process_exists",
    [True, False],
)
@patch("balancer_agent.operations.systems.keepalived.CommandExecutor")
def test_start_keepalived(mocked_command_executor, process_exists):
    keepalived = KeepalivedTest()

    if not process_exists:
        mocked_command_executor.return_value.cmd_result.stdout = keepalived.NO_PROCESS_FOUND_OUTPUT
        with pytest.raises(FailedToStartKeepalivedError):
            keepalived.start()
    else:
        keepalived.start()

    assert mocked_command_executor.return_value.run_cmd.call_args_list[0][0][0] == keepalived.START_KEEPALIVED_CMD


@pytest.mark.parametrize(
    "process_exists_before_stop,process_exists_after_stop,executor_error",
    [
        # Keepalived process doesn't exist - nothing to stop
        (False, None, False),
        # Keepalived process successfully stopped
        (True, False, False),
        # Keepalived process has not stopped
        (True, True, False),
        # Keepalived process stop command failed, process has not stopped
        (True, True, True),
    ],
)
@patch("balancer_agent.operations.systems.keepalived.logger")
@patch("balancer_agent.operations.systems.keepalived.CommandExecutor")
def test_stop_keepalived(
    mocked_command_executor, logger, process_exists_before_stop, process_exists_after_stop, executor_error
):
    keepalived = KeepalivedTest()
    keepalived.check_process_exists = Mock(side_effect=[process_exists_before_stop, process_exists_after_stop])

    if not process_exists_before_stop:
        keepalived.stop()
        logger.info.assert_called_once_with("Stopping kepalived: Keepalived process does not exists. No need to stop")
    elif not process_exists_after_stop and not executor_error:
        keepalived.stop()
        assert (
            logger.info.call_args_list[0][0][0] == "Stopping kepalived: Keepalived process exists. Attempting to stop"
        )
        assert logger.info.call_args_list[1][0][0] == "Stopping kepalived: Keepalived has stopped"
        assert mocked_command_executor.return_value.run_cmd.call_args_list[0][0][0] == keepalived.STOP_KEEPALIVED_CMD
    elif executor_error and process_exists_after_stop:
        mocked_command_executor.return_value.run_cmd.return_value.validate_return_code_0 = Mock(
            side_effect=CommandExecutionError()
        )
        with pytest.raises(FailedToStopKeepalivedError):
            keepalived.stop()
        logger.info.assert_called_once_with("Stopping kepalived: Keepalived process exists. Attempting to stop")
        logger.warning.assert_called_once()
        logger.exception.assert_called_once_with("Stopping keepalived: Could not stop keepalived")
    elif process_exists_after_stop:
        with pytest.raises(FailedToStopKeepalivedError):
            keepalived.stop()
            logger.info.assert_called_once_with("Stopping kepalived: Keepalived process exists. Attempting to stop")
            logger.exception.assert_called_once_with("Stopping keepalived: Could not stop keepalived")


@pytest.mark.parametrize(
    "process_restarted,command_excution_error",
    [
        (True, False),
        (False, False),
        (False, True),
    ],
)
@patch("balancer_agent.operations.systems.keepalived.CommandExecutor")
def test_restart_keepalived(mocked_command_executor, process_restarted, command_excution_error):
    keepalived = Keepalived()

    if not process_restarted:
        mocked_command_executor.return_value.cmd_result.stdout = keepalived.NO_PROCESS_FOUND_OUTPUT
        with pytest.raises(FailedToReStartKeepalivedError):
            keepalived.restart()
    elif not command_excution_error:
        keepalived.restart()
    else:
        mocked_command_executor.return_value.run_cmd.return_value.validate_return_code_0 = Mock(
            side_effect=CommandExecutionError()
        )
        with pytest.raises(CommandExecutionError):
            keepalived.restart()

    assert mocked_command_executor.return_value.run_cmd.call_args_list[0][0][0] == keepalived.RESTART_KEEPALIVED_CMD


@pytest.mark.parametrize(
    "save_to_history",
    [True, False],
)
@patch("balancer_agent.operations.systems.keepalived.CommandExecutor")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest.erase_config")
@patch("balancer_agent.operations.systems.keepalived.Path")
@patch("balancer_agent.operations.systems.keepalived.datetime", new_callable=MockDatetime)
def test_restore_keepalived_config_success(
    mocked_datetime, mocked_path, mocked_erase_config, mocked_command_executor, save_to_history
):
    keepalived = KeepalivedTest()
    keepalived.restore_config(TEST_SERVICE, TEST_CONFIG_ID, save_to_history=save_to_history)

    if save_to_history:
        assert all(
            [
                str(arg) in mocked_path.call_args_list[0][0][0]
                for arg in [keepalived.config_manager.FAILED_TEST_DIR, TEST_SERVICE, DATE_NOW]
            ]
        )

        assert all(
            [
                str(arg) in mocked_command_executor.return_value.run_cmd.call_args_list[0][0][0]
                for arg in [
                    keepalived.config_manager.KEEPALIVED_CONFIGURATION_PATH,
                    keepalived.config_manager.FAILED_TEST_DIR,
                    TEST_SERVICE,
                    DATE_NOW,
                ]
            ]
        )
    else:
        assert not mocked_path.called

    mocked_erase_config.assert_called_once()


@patch("balancer_agent.operations.systems.keepalived.CommandExecutor")
@patch("balancer_agent.operations.systems.keepalived.Path")
@patch("balancer_agent.operations.systems.keepalived.datetime", new_callable=MockDatetime)
def test_restore_keepalived_config_failure(mocked_datetime, mocked_path, mocked_command_executor):
    mocked_command_executor.return_value.run_cmd.return_value.validate_return_code_0 = Mock(
        side_effect=CommandExecutionError()
    )
    keepalived = KeepalivedTest()

    with pytest.raises(CommandExecutionError):
        keepalived.restore_config(TEST_SERVICE, TEST_CONFIG_ID)


@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest.start")
@patch(
    "balancer_agent.operations.systems.keepalived.KeepalivedSingleServiceConfigurationManager.move_config_to_workdir"
)
@patch("balancer_agent.operations.systems.keepalived.KeepalivedSingleServiceConfigurationManager.save_config")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest.stop")
def test_agent_apply_config(mock_stop, mock__save_config, mock__move_config_to_workdir, mock_start):
    manager = Mock()
    manager.attach_mock(mock_stop, "mock_stop")
    manager.attach_mock(mock__save_config, "mock__save_config")
    manager.attach_mock(mock__move_config_to_workdir, "mock__move_config_to_workdir")
    manager.attach_mock(mock_start, "mock_start")

    keepalived = KeepalivedTest()
    keepalived.apply_config(Mock, Mock)

    expected_calls = [
        call.mock_stop(),
        call.mock__save_config(Mock),
        call.mock__move_config_to_workdir(),
        call.mock_start(),
    ]

    assert manager.mock_calls == expected_calls


@patch("balancer_agent.operations.systems.keepalived.open", new_callable=mock_open)
@patch("balancer_agent.operations.systems.keepalived.logger")
def test_save_config_success(mocked_logger, mocked_open):
    keepalived = KeepalivedTest()
    keepalived.config_manager.save_config([])
    mocked_open.assert_called_once_with(keepalived.config_manager.DEFAULT_CONFIGURATION_UPLOAD_PATH, "w")
    mocked_open.return_value.write.assert_called_once_with("")
    mocked_logger.info.assert_called_once_with("Upload keepalived config succeed")


@patch("balancer_agent.operations.systems.keepalived.open", side_effect=Exception(EXCEPTION_MOCK_CONTENT))
@patch("balancer_agent.operations.systems.keepalived.logger")
def test_save_config_failure(mocked_logger, mocked_open):
    keepalived = KeepalivedTest()

    with pytest.raises(Exception):
        keepalived.config_manager.save_config("")

    mocked_logger.exception.assert_called_once_with(f"Upload keepalived config failed due to {EXCEPTION_MOCK_CONTENT}")


@patch("balancer_agent.operations.systems.keepalived.open", new_callable=mock_open)
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest.start")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest.stop")
def test_erase_config(mocked_stop, mocked_start, mocked_open):
    keepalived = KeepalivedTest()
    keepalived.erase_config()

    mocked_open.assert_called_once_with(keepalived.config_manager.KEEPALIVED_CONFIGURATION_PATH, "w")
    mocked_open.return_value.close.assert_called_once()
    mocked_stop.assert_called_once()
    mocked_start.assert_called_once()
