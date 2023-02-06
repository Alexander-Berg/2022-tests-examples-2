import json
import re
from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests_mock

from balancer_agent.core.exceptions import PollingTasksError, TasksCollectionProcessingError
from balancer_agent.operations.balancer_configs.config_containers import BalancerConfigL3Targets
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.tasks.handlers.ipvs_prod_tasks import ProdTasksHandler

from .static.configs_from_api import (
    CONFIG_GENERATOR_SETTINGS,
    CONFIG_GENERATOR_SETTINGS_ONE_VS_GROUP_ONE_VS,
    ConfigGenerator,
    ConfigListGenerator,
)

HOST_A = "host_a"
HOST_B = "host_b"
ACTIVE_STATE = "ACTIVE"
L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]

MOCK_COLLECTED_CONFIG = {
    "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
    "polling_interval": 300,
    "agent_mode": ACTIVE_STATE,
    "generator_version": 2,
}

AGENT_API_HOSTS = "https://host.*"


@pytest.mark.parametrize(
    "l3_response,error_flag,status_code,http_raises,expected",
    [
        # Collected one config success case
        (
            json.dumps(
                ConfigListGenerator.get(
                    ConfigListGenerator.ACTIVE,
                )
            ),
            False,
            HTTPStatus.OK,
            ValueError,
            PollingTasksError,
        ),
        # Collected multiple configs success case
        (
            json.dumps(ConfigListGenerator.get(ConfigListGenerator.ACTIVE, ConfigListGenerator.REMOVED)),
            False,
            HTTPStatus.OK,
            None,
            None,
        ),
        # Backend error while collecting configs
        (json.dumps([]), True, HTTPStatus.INTERNAL_SERVER_ERROR, None, PollingTasksError),
        # Not found code while collecting configs
        (json.dumps([]), False, HTTPStatus.NOT_FOUND, None, False),
        # Empty config list collected
        (json.dumps([]), False, HTTPStatus.OK, None, False),
        # Invalid task format
        ("not json", True, HTTPStatus.OK, None, PollingTasksError),
        # Invalid task format
        (json.dumps({"revision": 1, "configs": []}), True, HTTPStatus.OK, None, PollingTasksError),
    ],
)
@patch("balancer_agent.operations.systems.keepalived.Keepalived")
@requests_mock.mock(kw="requests_mocker")
def test_configs_list_collection(
    mocked_keepalived, l3_response, error_flag, status_code, http_raises, expected, **kwargs
):
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.get(re.compile(AGENT_API_HOSTS), text=l3_response, status_code=status_code)

    if error_flag and not status_code:
        requests_mocker.get(re.compile(AGENT_API_HOSTS), exc=http_raises)
        with pytest.raises(expected):
            ProdTasksHandler(runtime_settings.runtime).get_configs()
    elif error_flag and status_code:
        requests_mocker.get(re.compile(AGENT_API_HOSTS), text=l3_response, status_code=status_code)
        with pytest.raises(expected):
            ProdTasksHandler(runtime_settings.runtime).get_configs()
    else:
        requests_mocker.get(re.compile(AGENT_API_HOSTS), text=l3_response, status_code=status_code)

        configs = ProdTasksHandler(runtime_settings.runtime).get_configs()

        if not json.loads(l3_response) or status_code == HTTPStatus.NOT_FOUND:
            assert not configs
        else:
            assert configs.configs[0].revision is not None

            for config in configs.configs:
                assert isinstance(config.id, int)
                assert config.target in BalancerConfigL3Targets.__members__.keys()


@pytest.mark.parametrize(
    "l3_response,error_flag,status_code,http_raises,expected",
    [
        # Collected one config success case
        (json.dumps(ConfigGenerator.get(CONFIG_GENERATOR_SETTINGS)), False, HTTPStatus.OK, None, 1),
        # Collected one config success case
        (json.dumps({"invalid_format": True}), False, HTTPStatus.OK, None, 0),
        # Collected multiple configs success case
        (
            json.dumps(ConfigGenerator.get(CONFIG_GENERATOR_SETTINGS_ONE_VS_GROUP_ONE_VS)),
            False,
            HTTPStatus.OK,
            None,
            1,
        ),
        # Backend error while collecting configs
        (json.dumps({}), True, HTTPStatus.INTERNAL_SERVER_ERROR, None, PollingTasksError),
        # Not found code while collecting configs
        (json.dumps({}), False, HTTPStatus.NOT_FOUND, None, None),
    ],
)
@patch("balancer_agent.operations.systems.keepalived.Keepalived")
@requests_mock.mock(kw="requests_mocker")
def test_lock_config(mocked_keepalived, l3_response, error_flag, status_code, http_raises, expected, **kwargs):
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.get(
        re.compile(AGENT_API_HOSTS),
        text=json.dumps(
            ConfigListGenerator.get(
                ConfigListGenerator.ACTIVE,
            )
        ),
        status_code=status_code,
    )
    # To avoid waiting 7 retries on request failure
    ProdTasksHandler.collect_tasks.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[
        0
    ].cell_contents.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    if error_flag and not status_code:
        requests_mocker.post(re.compile(AGENT_API_HOSTS), exc=http_raises)
        with pytest.raises(expected):
            ProdTasksHandler(runtime_settings.runtime).collect_tasks()
    elif error_flag and status_code:
        requests_mocker.post(re.compile(AGENT_API_HOSTS), text=l3_response, status_code=status_code)
        with pytest.raises(expected):
            ProdTasksHandler(runtime_settings.runtime).collect_tasks()
    else:
        requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
        requests_mocker.get(
            re.compile("https://host.*/configs$"),
            text=json.dumps(
                ConfigListGenerator.get(
                    ConfigListGenerator.ACTIVE,
                )
            ),
            status_code=status_code,
        )
        requests_mocker.get(re.compile("https://host.*/configs/.*"), text=l3_response, status_code=status_code)

        with patch(
            "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler.send_invalid_task_status_to_l3"
        ) as mocked_send_invalid_task_status_to_l3:

            if expected is not None:
                handler = ProdTasksHandler(runtime_settings.runtime)
                handler.keepalived.find_unsynchronized_configs = lambda configs: configs
                assert expected == handler.collect_tasks()

            if expected == 0:
                assert len(mocked_send_invalid_task_status_to_l3.call_args_list[0]) == 2
            else:
                mocked_send_invalid_task_status_to_l3.assert_not_called()


@pytest.mark.parametrize(
    "l3_response,error_flag,status_code,tasks_not_in_sync_count",
    [
        # Collected config is not in sync with deployed configs
        (json.dumps(ConfigGenerator.get(CONFIG_GENERATOR_SETTINGS)), False, HTTPStatus.OK, 1),
        # Collected config is in sync with deployed configs
        (json.dumps(ConfigGenerator.get(CONFIG_GENERATOR_SETTINGS)), False, HTTPStatus.OK, 0),
        # Error during comparing collected and applied configs
        (json.dumps(ConfigGenerator.get(CONFIG_GENERATOR_SETTINGS)), True, HTTPStatus.OK, None),
    ],
)
@requests_mock.mock(kw="requests_mocker")
def test_lock_config_different_keepalived_outputs(
    l3_response, error_flag, status_code, tasks_not_in_sync_count, **kwargs
):
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.get(
        re.compile("https://host.*/configs$"),
        text=json.dumps(
            ConfigListGenerator.get(
                ConfigListGenerator.ACTIVE,
            )
        ),
        status_code=status_code,
    )
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
    requests_mocker.get(re.compile("https://host.*/configs/.*"), text=l3_response, status_code=status_code)

    # To avoid waiting 7 retries on request failure
    ProdTasksHandler.collect_tasks.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[
        0
    ].cell_contents.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    tasks_handler = ProdTasksHandler(runtime_settings.runtime)

    if not error_flag:
        configs = tasks_handler.get_configs()
        tasks_handler.keepalived.find_unsynchronized_configs = (
            lambda *args, configs=configs.configs if tasks_not_in_sync_count else []: configs
        )

        assert tasks_not_in_sync_count == tasks_handler.collect_tasks()
    else:

        def exceptor():
            raise Exception("Test case")

        tasks_handler.keepalived.find_unsynchronized_configs = lambda *args: exceptor()
        with pytest.raises(TasksCollectionProcessingError):
            tasks_handler.collect_tasks()
            assert True
