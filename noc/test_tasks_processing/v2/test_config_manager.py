import json
import re
from copy import deepcopy
from datetime import datetime
from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests_mock

from balancer_agent.operations.balancer_configs.config_containers import BalancerConfigL3States
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.systems.config_manager import ConfigID as CurrentConfigs
from balancer_agent.operations.tasks.handlers.ipvs_prod_tasks import ProdTasksHandler

from .static.configs_from_api import ConfigListGenerator

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


active_config_from_api = ConfigListGenerator.get(ConfigListGenerator.ACTIVE)

active_locked_config_from_api = deepcopy(active_config_from_api)
active_locked_config_from_api[0]["locked"] = datetime.now().timestamp()

removed_config_from_api = ConfigListGenerator.get(ConfigListGenerator.REMOVED)

unprocessable_config_from_api = ConfigListGenerator.get(ConfigListGenerator.ACTIVE)
unprocessable_config_from_api[0]["state"] = BalancerConfigL3States.FAILED.name

deployed_config_from_api = deepcopy(active_config_from_api)
deployed_config_from_api[0]["state"] = BalancerConfigL3States.DEPLOYED.name


@pytest.mark.parametrize(
    "configs_short,configs_on_balancer,expected",
    [
        # Collected a new unlocked config - need to deploy
        (active_config_from_api, [], [config["id"] for config in active_config_from_api]),
        # Collected existing locked config - need redeploy
        (
            active_locked_config_from_api,
            [CurrentConfigs("dummy_service", config["id"]) for config in active_locked_config_from_api],
            [config["id"] for config in active_locked_config_from_api],
        ),
        # Collected existing unlocked config with state UNKNOWN - need to redeploy
        (
            active_config_from_api,
            [CurrentConfigs("dummy_service", config["id"]) for config in active_config_from_api],
            [config["id"] for config in active_config_from_api],
        ),
        # Collected existing unlocked config with state DEPLOYED - no need to redeploy
        (
            deployed_config_from_api,
            [CurrentConfigs("dummy_service", config["id"]) for config in deployed_config_from_api],
            [],
        ),
        # Collected removed config - always need to redeploy
        (
            removed_config_from_api,
            [CurrentConfigs("dummy_service", config["id"]) for config in removed_config_from_api],
            [config["id"] for config in removed_config_from_api],
        ),
        # Collected removed config - no need to redeploy
        (
            unprocessable_config_from_api,
            [CurrentConfigs("dummy_service", config["id"]) for config in unprocessable_config_from_api],
            [],
        ),
    ],
)
@patch("balancer_agent.operations.systems.config_manager.ConfigManager.need_redeploy_corrupted", return_value=False)
@patch("balancer_agent.operations.systems.config_manager.ConfigManager._clear_dir_no_fail")
@requests_mock.mock(kw="requests_mocker")
def test_find_configs_to_handle(
    mock_need_redeploy_corrupted, mock_clear_dir_no_fail, configs_short, configs_on_balancer, expected, **kwargs
):
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()

    requests_mocker.get(
        re.compile("https://host.*/configs$"),
        text=json.dumps(configs_short),
        status_code=HTTPStatus.OK,
    )
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=HTTPStatus.OK)

    # To avoid waiting 7 retries on request failure
    ProdTasksHandler.collect_tasks.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[
        0
    ].cell_contents.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    tasks_handler = ProdTasksHandler(runtime_settings.runtime)

    configs = tasks_handler.get_configs()
    tasks_handler.keepalived.config_manager.get_current_configs = lambda *args: configs_on_balancer
    found_configs = tasks_handler.keepalived.find_unsynchronized_configs(configs.configs)

    assert [config.id for config in found_configs] == expected
