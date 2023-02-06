import os
import subprocess
from datetime import datetime

import pytest
from keepalived_configs_for_testing import EMPTY_KEEPALIVED_CONFIG, VALID_KEEPALIVED_CONFIG

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
FAILED_TEST_DIR = "/home/ttmgmt/service-configs-failed"


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
