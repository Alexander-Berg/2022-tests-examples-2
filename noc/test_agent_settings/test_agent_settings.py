import json
from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests_mock
from box import Box
from box.exceptions import BoxKeyError

from balancer_agent.core.exceptions import PollingSettingsError
from balancer_agent.operations.settings import SETTINGS_COLLECTION_ATTEMPTS, RuntimeSettings, SettingsCollector

HOST_A = "host_a"
HOST_B = "host_b"
ACTIVE_STATE = "ACTIVE"
IDLE_STATE = "IDLE"
L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]

MOCK_INITIAL_CONFIG = {
    "controller": {
        "data_collector_url": "https://l3-test.tt.yandex-team.ru/api/v1/agent",
        "worker_tracking_seconds": 10,
    },
    "main": {"agent_mode": "test", "balancing_type": "ipvs", "lb_name": "man1-testenv-lb0bb.yndx.net"},
    "stage": "development",
    "startup": {
        "initial_state": IDLE_STATE,
        "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
        "settings_polling_interval": 6000,
        "signal_failure_interval": 10000,
        "tasks_polling_interval": 1000,
    },
}

MOCK_COLLECTED_CONFIG = {
    "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
    "polling_interval": 300,
    "agent_mode": ACTIVE_STATE,
    "generator_version": 1,
}


@pytest.mark.parametrize("base_config", [Box(MOCK_INITIAL_CONFIG), Box({})])
def test_agent_settings_parse_fields(base_config):
    with patch("balancer_agent.operations.settings.definitions.BASE_CONFIG", base_config):
        if base_config:
            runtime_settings = RuntimeSettings()
            assert runtime_settings.is_active == (MOCK_INITIAL_CONFIG["startup"]["initial_state"] != IDLE_STATE)
            assert (
                round(runtime_settings.settings_polling_interval, 0)
                == MOCK_INITIAL_CONFIG["startup"]["settings_polling_interval"]
            )
            assert (
                round(runtime_settings.tasks_polling_interval, 0)
                == MOCK_INITIAL_CONFIG["startup"]["tasks_polling_interval"]
            )
            assert (
                round(runtime_settings.signal_failure_interval, 0)
                == MOCK_INITIAL_CONFIG["startup"]["signal_failure_interval"]
            )
        else:
            with pytest.raises(BoxKeyError):
                RuntimeSettings()


def test_l3_hosts_pool():
    with patch("balancer_agent.operations.settings.definitions.BASE_CONFIG", Box(MOCK_INITIAL_CONFIG)):
        runtime_settings = RuntimeSettings()
        next_host = HOST_A

        for i in range(10):
            host = runtime_settings.l3_host
            assert host.startswith(runtime_settings.HTTPS_PREFIX)
            assert host.endswith(runtime_settings.API_ADDRESS)
            assert next_host in host

            if HOST_A in host:
                next_host = HOST_B
            if HOST_B in host:
                next_host = HOST_A


@pytest.mark.parametrize(
    "l3_response,error_flag,status_code,expected",
    [
        (json.dumps(MOCK_COLLECTED_CONFIG), False, HTTPStatus.OK, None),
        (json.dumps(MOCK_COLLECTED_CONFIG), True, None, PollingSettingsError),
        (json.dumps(MOCK_COLLECTED_CONFIG), True, HTTPStatus.INTERNAL_SERVER_ERROR, PollingSettingsError),
        ("not json", True, 200, PollingSettingsError),
        ("[]", True, 200, PollingSettingsError),
    ],
)
@requests_mock.mock(kw="requests_mocker")
def test_settings_collection(l3_response, error_flag, status_code, expected, **kwargs):
    requests_mocker = kwargs["requests_mocker"]
    SettingsCollector._collect_settings_callback.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    with patch("balancer_agent.operations.settings.definitions.BASE_CONFIG", Box(MOCK_INITIAL_CONFIG)):
        if not error_flag:
            requests_mocker.get(
                "https://host_a/api/v1/agent" + SettingsCollector.COLLECT_SETTING_URI,
                text=l3_response,
                status_code=status_code,
            )
            startup_settings = RuntimeSettings()
            runtime_settings = SettingsCollector()
            runtime_settings.collect_settings()

            assert startup_settings.settings_polling_interval == runtime_settings.runtime.settings_polling_interval
            assert startup_settings.signal_failure_interval == runtime_settings.runtime.signal_failure_interval
            assert (
                round(runtime_settings.runtime.tasks_polling_interval, 0) == MOCK_COLLECTED_CONFIG["polling_interval"]
            )
            assert runtime_settings.runtime.initial_state == MOCK_COLLECTED_CONFIG["agent_mode"]
            assert HOST_A in runtime_settings.runtime.l3_host or HOST_A in runtime_settings.runtime.l3_host
            assert runtime_settings.runtime.is_active == (MOCK_COLLECTED_CONFIG["agent_mode"] == ACTIVE_STATE)
        elif status_code:
            requests_mocker.get(
                "https://host_a/api/v1/agent" + SettingsCollector.COLLECT_SETTING_URI,
                text=l3_response,
                status_code=status_code,
            )
            runtime_settings = SettingsCollector()
            with pytest.raises(expected):
                runtime_settings.collect_settings()
        else:
            requests_mocker.get("https://host_a/api/v1/agent" + SettingsCollector.COLLECT_SETTING_URI, exc=expected)
            runtime_settings = SettingsCollector()
            with pytest.raises(expected):
                runtime_settings.collect_settings()


@patch("balancer_agent.operations.settings.requests.get", side_effect=PollingSettingsError)
def test_settings_collection_retry(mocked_requests):
    SettingsCollector._collect_settings_callback.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = SETTINGS_COLLECTION_ATTEMPTS
    SettingsCollector._collect_settings_callback.__closure__[1].cell_contents["wait_random_min"] = 0
    SettingsCollector._collect_settings_callback.__closure__[1].cell_contents["wait_random_max"] = 1

    with patch("balancer_agent.operations.settings.definitions.BASE_CONFIG", Box(MOCK_INITIAL_CONFIG)):
        runtime_settings = SettingsCollector()

        with pytest.raises(PollingSettingsError):
            runtime_settings.collect_settings()
        assert mocked_requests.call_count == SETTINGS_COLLECTION_ATTEMPTS
