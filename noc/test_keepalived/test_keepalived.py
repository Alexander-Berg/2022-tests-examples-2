import difflib
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from keepalived_configs_for_testing import EMPTY_KEEPALIVED_CONFIG, VALID_KEEPALIVED_CONFIG, VALID_KEEPALIVED_CONFIGS
from mock.mock import Mock

from balancer_agent.operations.systems.base import CommandExecutionError
from balancer_agent.operations.systems.keepalived import (
    KeepalivedSingleServiceConfigurationManager,
    KeepalivedTest,
    MonaliveTest,
)

DATE_NOW = datetime.now().strftime("%Y%m%d")


class MockDatetime:
    def now(self):
        return self

    def strftime(self, *args):
        return DATE_NOW


EMPTY_SIZE = 0

TEST_SERVICE = "test"
TEST_CONFIG_ID = 123

STOP_KEEPALIVED_CMD = "sudo make -C /etc/keepalived stop"
START_KEEPALIVED_CMD = "sudo make -C /etc/keepalived start"
KEEPALIVED_CONFIGURATION_PATH = "/etc/keepalived/keepalived.conf"
FAILED_TEST_DIR = "/home/ttmgmt/keepalived_failed_test_configs"


def executor(cmd):
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)


class KeepalivedState:
    def __init__(self, config=None):
        self.config = config

    def set_running_state(self):
        executor(STOP_KEEPALIVED_CMD)
        with open(KEEPALIVED_CONFIGURATION_PATH, "w") as f:
            f.write(self.config)
        executor(START_KEEPALIVED_CMD)

        return self

    def set_stopped_state(self):
        executor(STOP_KEEPALIVED_CMD)
        if self.config is not None:
            with open(KEEPALIVED_CONFIGURATION_PATH, "w") as f:
                f.write(self.config)
        else:
            try:
                os.remove(KEEPALIVED_CONFIGURATION_PATH)
            except FileNotFoundError:
                pass

        return self


@pytest.fixture
def keepalived_initial_state_running_with_config():
    return KeepalivedState(VALID_KEEPALIVED_CONFIG).set_running_state()


@pytest.fixture
def keepalived_initial_state_running_with_empty_config():
    return KeepalivedState(EMPTY_KEEPALIVED_CONFIG).set_running_state()


@pytest.fixture
def keepalived_initial_state_stopped_with_config():
    return KeepalivedState(VALID_KEEPALIVED_CONFIG).set_stopped_state()


@pytest.fixture
def keepalived_initial_state_stopped_with_empty_config():
    return KeepalivedState(EMPTY_KEEPALIVED_CONFIG).set_stopped_state()


@pytest.fixture
def keepalived_initial_state_stopped_with_no_config():
    return KeepalivedState().set_stopped_state()


@pytest.mark.ipvs
@pytest.mark.parametrize(
    "process_exists, keepalived_state_setter",
    [
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_config")),
    ],
)
def test_check_process_exists(process_exists, keepalived_state_setter):
    keepalived = KeepalivedTest()

    if not process_exists:
        assert not keepalived.check_process_exists()
    else:
        assert keepalived.check_process_exists()


@pytest.mark.ipvs
@pytest.mark.parametrize(
    "keepalived_state_setter",
    [
        pytest.lazy_fixture("keepalived_initial_state_running_with_config"),
        pytest.lazy_fixture("keepalived_initial_state_stopped_with_config"),
    ],
)
def test_start(keepalived_state_setter):
    keepalived = KeepalivedTest()
    keepalived.start()

    assert keepalived.check_process_exists()


@pytest.mark.ipvs
@pytest.mark.parametrize(
    "keepalived_state_setter",
    [
        pytest.lazy_fixture("keepalived_initial_state_running_with_config"),
        pytest.lazy_fixture("keepalived_initial_state_stopped_with_config"),
    ],
)
def test_stop(keepalived_state_setter):
    keepalived = KeepalivedTest()
    keepalived.stop()

    assert not keepalived.check_process_exists()


@pytest.mark.ipvs
@pytest.mark.parametrize(
    "process_exists, keepalived_state_setter",
    [
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_empty_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_empty_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_no_config")),
    ],
)
def test_erase_config_in_ipvs_env(process_exists, keepalived_state_setter):
    keepalived = KeepalivedTest()
    keepalived.erase_config()
    assert Path(KEEPALIVED_CONFIGURATION_PATH).stat().st_size == EMPTY_SIZE

    assert keepalived.check_process_exists()


@pytest.mark.yanet
@pytest.mark.parametrize(
    "keepalived_state_setter",
    [
        (pytest.lazy_fixture("keepalived_initial_state_running_with_config"),),
        (pytest.lazy_fixture("keepalived_initial_state_running_with_empty_config"),),
        (pytest.lazy_fixture("keepalived_initial_state_stopped_with_config"),),
        (pytest.lazy_fixture("keepalived_initial_state_stopped_with_empty_config"),),
        (pytest.lazy_fixture("keepalived_initial_state_stopped_with_no_config"),),
    ],
)
def test_erase_config_in_yanet_env(keepalived_state_setter):
    monalive = MonaliveTest()
    monalive.erase_config()
    assert Path(KEEPALIVED_CONFIGURATION_PATH).stat().st_size == EMPTY_SIZE

    # todo: check
    assert monalive.check_process_exists()


@pytest.mark.ipvs
@pytest.mark.parametrize(
    "process_exists, keepalived_state_setter",
    [
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_empty_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_empty_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_no_config")),
    ],
)
def test_apply_config_in_ipvs_env(process_exists, keepalived_state_setter):
    keepalived = KeepalivedTest()

    for config, expected in [(VALID_KEEPALIVED_CONFIGS, VALID_KEEPALIVED_CONFIG), ([], EMPTY_KEEPALIVED_CONFIG)]:
        keepalived.apply_config(config, Mock())

        with open(KEEPALIVED_CONFIGURATION_PATH) as applied_config:
            found_diff = "".join(difflib.unified_diff(applied_config.read(), expected))
            assert not found_diff
        assert keepalived.check_process_exists()


@pytest.mark.yanet
@pytest.mark.parametrize(
    "keepalived_state_setter",
    [
        (pytest.lazy_fixture("keepalived_initial_state_running_with_config"),),
        (pytest.lazy_fixture("keepalived_initial_state_running_with_empty_config"),),
        (pytest.lazy_fixture("keepalived_initial_state_stopped_with_config"),),
        (pytest.lazy_fixture("keepalived_initial_state_stopped_with_empty_config"),),
        (pytest.lazy_fixture("keepalived_initial_state_stopped_with_no_config"),),
    ],
)
def test_apply_config_in_yanet_env(keepalived_state_setter):
    monalive = MonaliveTest()

    for config, expected in [(VALID_KEEPALIVED_CONFIGS, VALID_KEEPALIVED_CONFIG), ([], EMPTY_KEEPALIVED_CONFIG)]:
        monalive.apply_config(config, Mock())

        with open(KEEPALIVED_CONFIGURATION_PATH) as applied_config:
            found_diff = "".join(difflib.unified_diff(applied_config.read(), expected))
            assert not found_diff, found_diff
        # todo: check
        assert monalive.check_process_exists()


@pytest.mark.ipvs
@pytest.mark.parametrize(
    "process_exists, keepalived_state_setter",
    [
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_no_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_empty_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_empty_config")),
    ],
)
@patch("balancer_agent.operations.systems.keepalived.datetime", new_callable=MockDatetime)
def test_restore_config(mocked_datetime, process_exists, keepalived_state_setter):
    rollback_history_path = os.path.join(
        KeepalivedSingleServiceConfigurationManager.FAILED_TEST_DIR, TEST_SERVICE, DATE_NOW, str(TEST_CONFIG_ID)
    )
    shutil.rmtree(os.path.join(KeepalivedSingleServiceConfigurationManager.FAILED_TEST_DIR), ignore_errors=True)
    keepalived = KeepalivedTest()

    if keepalived_state_setter.config is not None:
        keepalived.restore_config(TEST_SERVICE, TEST_CONFIG_ID, save_to_history=True)

        with open(rollback_history_path) as stored_config:
            assert stored_config.read() == keepalived_state_setter.config
        assert keepalived.check_process_exists()
        assert Path(KEEPALIVED_CONFIGURATION_PATH).stat().st_size == EMPTY_SIZE
    else:
        with pytest.raises(CommandExecutionError):
            keepalived.restore_config(TEST_SERVICE, TEST_CONFIG_ID, save_to_history=True)
        assert not keepalived.check_process_exists()


@pytest.mark.yanet
@pytest.mark.parametrize(
    "process_exists, keepalived_state_setter",
    [
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_no_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_empty_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_empty_config")),
    ],
)
@patch("balancer_agent.operations.systems.keepalived.datetime", new_callable=MockDatetime)
def test_restore_config(mocked_datetime, process_exists, keepalived_state_setter):
    rollback_history_path = os.path.join(
        KeepalivedSingleServiceConfigurationManager.FAILED_TEST_DIR, TEST_SERVICE, DATE_NOW, str(TEST_CONFIG_ID)
    )
    shutil.rmtree(os.path.join(KeepalivedSingleServiceConfigurationManager.FAILED_TEST_DIR), ignore_errors=True)
    config_manager = MonaliveTest()

    if keepalived_state_setter.config is not None:
        config_manager.restore_config(TEST_SERVICE, TEST_CONFIG_ID, save_to_history=True)

        with open(rollback_history_path) as stored_config:
            assert stored_config.read() == keepalived_state_setter.config
        assert config_manager.check_process_exists()
        assert Path(KEEPALIVED_CONFIGURATION_PATH).stat().st_size == EMPTY_SIZE
    else:
        with pytest.raises(CommandExecutionError):
            config_manager.restore_config(TEST_SERVICE, TEST_CONFIG_ID, save_to_history=True)
        assert not config_manager.check_process_exists()
