import os

import pytest

import sandbox.tests.common.network as tests_network


@pytest.fixture(scope="session")
def tests_env(config_path):
    env = {
        "SANDBOX_CONFIG": config_path,
    }
    if "SANDBOX_WEB_CONFIG" not in os.environ:
        # update config only if it is not updated in tests_dir fixture
        os.environ.update(env)
    return env


@pytest.fixture(scope="session")
def taskbox(taskbox_binary, run_daemon, tests_env):
    run_daemon([taskbox_binary], env=tests_env)


@pytest.fixture(scope="session")
def serviceapi(host, serviceapi_port, serviceapi_binary, run_daemon, tests_env):
    run_daemon([serviceapi_binary], env=tests_env)
    tests_network.wait_until_port_is_ready(host, serviceapi_port, timeout=5)
