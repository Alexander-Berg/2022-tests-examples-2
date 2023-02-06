import json
import re
from copy import deepcopy
from http import HTTPStatus
from importlib import import_module
from unittest.mock import Mock, PropertyMock, patch

import pytest
import requests_mock

from balancer_agent import definitions as defs
from balancer_agent.core.config import BalancingType
from balancer_agent.operations.balancer_configs.config_containers import VS_STATUS_BY_ID_EMTPY
from balancer_agent.operations.helpers.dry_run import OnDryRun
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.systems.keepalived import ConfigurationProductionManager
from balancer_agent.operations.tasks.handlers.waiter import Waiter

from .configs_from_api import ConfigGenerator, ConfigListGenerator

HOST_A = "host_a"
HOST_B = "host_b"
ACTIVE_STATE = "ACTIVE"
IDLE_STATE = "IDLE"
DRY_RUN_STATE = "DRY_RUN"

L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]

# MOCK_INITIAL_CONFIG = {
#     "controller": {
#         "data_collector_url": "https://l3-test.tt.yandex-team.ru/api/v1/agent",
#         "worker_tracking_seconds": 10,
#     },
#     "main": {"agent_mode": "prod", "balancing_type": "ipvs", "lb_name": "man1-testenv-lb0bb.yndx.net"},
#     "stage": "development",
#     "startup": {
#         "initial_state": IDLE_STATE,
#         "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
#         "settings_polling_interval": 6000,
#         "signal_failure_interval": 10000,
#         "tasks_polling_interval": 1000,
#     },
# }

MOCK_COLLECTED_CONFIG = {
    "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
    "polling_interval": 300,
    "agent_mode": ACTIVE_STATE,
    "generator_version": 2,
    "config_tracking": "STRICT",
}

MOCK_COLLECTED_CONFIG_DRY_RUN = deepcopy(MOCK_COLLECTED_CONFIG)
MOCK_COLLECTED_CONFIG_DRY_RUN["agent_mode"] = DRY_RUN_STATE
MOCK_COLLECTED_CONFIG_DRY_RUN["config_tracking"] = "STRICT"

AGENT_API_HOSTS = "https://host.*"

MOCK_BINDTO_IP = "2a02:6b8:0:e00::13:b0aa"


class MockResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code

    def json(self):
        return json.loads(self.text)


@pytest.mark.ipvs
@patch(
    "balancer_agent.operations.systems.keepalived.Keepalived.RESTART_KEEPALIVED_CMD",
    "sudo make -C /etc/keepalived restart;" "sleep 1;",
)
def test_ipvs_deploy_configs_in_cycle():
    assert defs.BALANCING_TYPE == BalancingType.IPVS

    from balancer_agent.operations.systems.keepalived import Keepalived
    from balancer_agent.operations.tasks.handlers.ipvs_prod_tasks import ProdTasksHandler
    from balancer_agent.operations.tasks.handlers.ipvs_test_tasks import TestTasksHandler

    # To avoid waiting 7 retries on request failure
    ProdTasksHandler.collect_tasks.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[
        0
    ].cell_contents.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    # To avoid waiting retries on request failure
    TestTasksHandler.send_task_status_to_l3.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1

    # Always start with empty config
    keepalived = Keepalived()
    assert keepalived.RESTART_KEEPALIVED_CMD == "sudo make -C /etc/keepalived restart;" "sleep 1;"

    deploy_configs_in_cycle("balancer_agent.operations.tasks.handlers.ipvs_prod_tasks", keepalived)


@pytest.mark.yanet
def test_yanet_deploy_configs_in_cycle():
    assert defs.BALANCING_TYPE == BalancingType.YANET

    from balancer_agent.operations.systems.keepalived import MonaliveProd
    from balancer_agent.operations.tasks.handlers.yanet_prod_tasks import ProdTasksHandler
    from balancer_agent.operations.tasks.handlers.yanet_test_tasks import TestTasksHandler

    # To avoid waiting 7 retries on request failure
    ProdTasksHandler.collect_tasks.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[
        0
    ].cell_contents.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    # To avoid waiting retries on request failure
    TestTasksHandler.send_task_status_to_l3.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1

    # Always start with empty config
    monalive_manager = MonaliveProd()
    deploy_configs_in_cycle("balancer_agent.operations.tasks.handlers.yanet_prod_tasks", monalive_manager)


@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetBase.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.AGENT_MODE",
    new_callable=PropertyMock(return_value="prod"),
)
@patch("requests.post")
@patch("balancer_agent.operations.systems.iptables.IpTables")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=False)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=True)
@patch("balancer_agent.core.metrics.METRICS_REPORTER", return_value=PropertyMock)
@patch("balancer_agent.operations.tasks.helpers.IS_PROD_AGENT", True)
@requests_mock.mock(kw="requests_mocker")
def deploy_configs_in_cycle(
    prod_handler_module_name: str,
    config_manager: ConfigurationProductionManager,
    metrics_reporter_mock: Mock,
    is_prod_agent_mock: Mock,
    is_test_agent_mock: Mock,
    ip_tables_mock: Mock,
    mocked_requests_post: Mock,
    agent_mode_mock: Mock,
    **kwargs,
):
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG

    mocked_requests_post.return_value.status_code = HTTPStatus.NO_CONTENT

    # There are three decorators wrapping wait_keepalived.
    # To access inner decorator (retry) parameters we need to do this
    Waiter.__call__.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1

    configs_full_target_active = ConfigGenerator.get(
        {
            "config_target": "ACTIVE",
            "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
        }
    )[0]

    with patch(f"{prod_handler_module_name}.ProdTasksHandler._collect_tasks") as mocked_collect_tasks:
        mocked_collect_tasks.return_value = MockResponse(json.dumps(""), status_code=HTTPStatus.OK)

        with patch(f"{prod_handler_module_name}.ProdTasksHandler._collect_locked_config") as mock_collect_locked_config:
            mock_collect_locked_config.return_value = MockResponse(
                json.dumps(configs_full_target_active), status_code=HTTPStatus.OK
            )

            config_manager.erase_config(configs_full_target_active["service"], with_history=True)

            prod_handler_module = import_module(prod_handler_module_name)
            handler = prod_handler_module.ProdTasksHandler(runtime_settings.runtime)

            # Case 1: no configs deployed, new config collection and deploy
            runtime_settings.collect_settings()
            configs_short = ConfigListGenerator.get(ConfigListGenerator.ACTIVE)

            requests_mocker.get(
                re.compile(AGENT_API_HOSTS),
                text=json.dumps(configs_short),
                status_code=HTTPStatus.OK,
            )

            assert handler.collect_tasks() == 1
            handler.handle_task()
            assert json.loads(mocked_requests_post.call_args[1]["data"])["overall_deployment_status"] == "SUCCESS"

            # Case 2: Collected the same configs as before - redeploy not needed
            configs_short = ConfigListGenerator.get(ConfigListGenerator.ACTIVE)
            configs_short[0]["state"] = "DEPLOYED"

            requests_mocker.get(
                re.compile(AGENT_API_HOSTS),
                text=json.dumps(configs_short),
                status_code=HTTPStatus.OK,
            )

            assert handler.collect_tasks() == 0

            # Case 3: Collected the same config but with locked state - redeploy collected config
            configs_short = ConfigListGenerator.get(ConfigListGenerator.ACTIVE, locked=True)

            requests_mocker.get(
                re.compile(AGENT_API_HOSTS),
                text=json.dumps(configs_short),
                status_code=HTTPStatus.OK,
            )

            assert handler.collect_tasks() == 1
            handler.handle_task()
            assert json.loads(mocked_requests_post.call_args[1]["data"])["overall_deployment_status"] == "SUCCESS"

        configs_full_target_removed = ConfigGenerator.get(
            {
                "config_target": "REMOVED",
                "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
            }
        )[0]

        with patch(f"{prod_handler_module_name}.ProdTasksHandler._collect_locked_config") as mock_collect_locked_config:
            mock_collect_locked_config.return_value = MockResponse(
                json.dumps(configs_full_target_removed), status_code=HTTPStatus.OK
            )

            # Case 4: Delete config
            configs_short = ConfigListGenerator.get(ConfigListGenerator.REMOVED, locked=False)

            requests_mocker.get(
                re.compile(AGENT_API_HOSTS),
                text=json.dumps(configs_short),
                status_code=HTTPStatus.OK,
            )

            assert handler.collect_tasks() == 1
            handler.handle_task()
            assert json.loads(mocked_requests_post.call_args[1]["data"])["overall_deployment_status"] == "SUCCESS"

            # Case 5: Collected the same configs as before, but deleted config appeared again - will be deleted again
            # this test case is repeated in case 6
            # assert handler.collect_tasks() == 1

            # Case 6: Collected the same config but with locked state - re-delete collected config
            configs_short = ConfigListGenerator.get(ConfigListGenerator.REMOVED, locked=True)

            requests_mocker.get(
                re.compile(AGENT_API_HOSTS),
                text=json.dumps(configs_short),
                status_code=HTTPStatus.OK,
            )

            assert handler.collect_tasks() == 1
            handler.handle_task()
            assert json.loads(mocked_requests_post.call_args[1]["data"])["overall_deployment_status"] == "SUCCESS"

            config_manager.erase_config(configs_full_target_removed["service"], with_history=True)


@pytest.mark.ipvs
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetBase.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.AGENT_MODE",
    new_callable=PropertyMock(return_value="prod"),
)
@patch("requests.post")
@patch("balancer_agent.operations.systems.iptables.IpTablesCache.ips_without_rules")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=False)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.BalancerConfigState.all_deployed",
    new_callable=PropertyMock,
)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=True)
@patch("balancer_agent.core.metrics.METRICS_REPORTER", return_value=PropertyMock)
@patch(
    "balancer_agent.operations.systems.keepalived.Keepalived.RESTART_KEEPALIVED_CMD",
    "sudo make -C /etc/keepalived restart;" "sleep 1;",
)
@patch("balancer_agent.operations.systems.keepalived.KeepalivedBase.check_process_exists")
@patch(
    "balancer_agent.operations.systems.config_manager.ConfigManager.KEEPALIVED_WILDCARD_CONFIG_PATH",
    new_callable=PropertyMock,
)
@patch("balancer_agent.operations.tasks.helpers.IS_PROD_AGENT", True)
@patch(
    "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler.headers",
    PropertyMock(return_value={"Content-Type": "application/json; charset=UTF-8"}),
)
@requests_mock.mock(kw="requests_mocker")
def test_dry_run_deployment(
    mock_ka_path,
    mock_check_process_exists,
    metric_reporter_mock,
    mock_is_prod_agent,
    mock_all_deployed,
    mock_is_test_agent,
    mock_ips_without_rules,
    mocked_requests_post,
    i,
    **kwargs,
):
    from balancer_agent.operations.systems.keepalived import Keepalived
    from balancer_agent.operations.tasks.handlers.ipvs_prod_tasks import ProdTasksHandler
    from balancer_agent.operations.tasks.handlers.ipvs_test_tasks import TestTasksHandler

    assert OnDryRun.enabled is False
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG_DRY_RUN

    # To avoid waiting 7 retries on request failure
    ProdTasksHandler.collect_tasks.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[
        0
    ].cell_contents.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    mocked_requests_post.return_value.status_code = HTTPStatus.NO_CONTENT

    # To avoid waiting retries on request failure
    TestTasksHandler.send_task_status_to_l3.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1
    # There are three decorators wrapping wait_keepalived.
    # To access inner decorator (retry) parameters we need to do this
    Waiter.__call__.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1

    configs_full_target_active = ConfigGenerator.get(
        {
            "config_target": "ACTIVE",
            "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
        }
    )[0]

    with patch(
        "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler._collect_locked_config"
    ) as mock_collect_locked_config, patch(
        "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler._collect_tasks"
    ) as mocked_collect_tasks:
        mock_collect_locked_config.return_value = MockResponse(
            json.dumps(configs_full_target_active), status_code=HTTPStatus.OK
        )
        mocked_collect_tasks.return_value = MockResponse(json.dumps(""), status_code=HTTPStatus.OK)
        # Always start with empty config
        keepalived = Keepalived()
        keepalived.RESTART_KEEPALIVED_CMD = "sudo make -C /etc/keepalived restart;" "sleep 1;"
        # keepalived.erase_config(configs_full_target_active["service"], with_history=True)
        call_times_before_decorated = mock_ka_path.call_count
        handler = ProdTasksHandler(runtime_settings.runtime)
        handler.keepalived = keepalived

        # Case 1: no configs deployed, new config collection and deploy
        runtime_settings.collect_settings()
        configs_short = ConfigListGenerator.get(ConfigListGenerator.ACTIVE)

        requests_mocker.get(
            re.compile(AGENT_API_HOSTS),
            text=json.dumps(configs_short),
            status_code=HTTPStatus.OK,
        )

        assert handler.collect_tasks() == 1
        handler.handle_task()
        # expect call count not increased in dry-run
        assert mock_ka_path.call_count == call_times_before_decorated
        assert json.loads(mocked_requests_post.call_args[1]["data"])["overall_deployment_status"] == "SUCCESS"

        # Case 2: Collected the same configs as before - redeploy not needed
        configs_short = ConfigListGenerator.get(ConfigListGenerator.ACTIVE)
        configs_short[0]["state"] = "DEPLOYED"

        requests_mocker.get(
            re.compile(AGENT_API_HOSTS),
            text=json.dumps(configs_short),
            status_code=HTTPStatus.OK,
        )

        assert handler.collect_tasks() == 0

        # Case 3: Collected the same config but with locked state - redeploy collected config
        configs_short = ConfigListGenerator.get(ConfigListGenerator.ACTIVE, locked=True)

        requests_mocker.get(
            re.compile(AGENT_API_HOSTS),
            text=json.dumps(configs_short),
            status_code=HTTPStatus.OK,
        )

        assert handler.collect_tasks() == 1
        handler.handle_task()
        assert json.loads(mocked_requests_post.call_args[1]["data"])["overall_deployment_status"] == "SUCCESS"
        assert json.loads(mocked_requests_post.call_args[1]["data"])["vs_status"] == VS_STATUS_BY_ID_EMTPY

        configs_full_target_removed = ConfigGenerator.get(
            {
                "config_target": "REMOVED",
                "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
            }
        )[0]

    with patch(
        "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler._collect_locked_config"
    ) as mock_collect_locked_config, patch(
        "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler._collect_tasks"
    ) as mocked_collect_tasks:
        mock_collect_locked_config.return_value = MockResponse(
            json.dumps(configs_full_target_removed), status_code=HTTPStatus.OK
        )
        mocked_collect_tasks.return_value = MockResponse(json.dumps(""), status_code=HTTPStatus.OK)

        # Case 4: Delete config
        configs_short = ConfigListGenerator.get(ConfigListGenerator.REMOVED, locked=False)

        requests_mocker.get(
            re.compile(AGENT_API_HOSTS),
            text=json.dumps(configs_short),
            status_code=HTTPStatus.OK,
        )

        assert handler.collect_tasks() == 1
        handler.handle_task()
        assert json.loads(mocked_requests_post.call_args[1]["data"])["overall_deployment_status"] == "SUCCESS"
        assert json.loads(mocked_requests_post.call_args[1]["data"])["vs_status"] == VS_STATUS_BY_ID_EMTPY
        # Case 5: Collected the same configs as before, but deleted config appeared again - will be deleted again
        # this test case is repeaded in case 6
        # assert handler.collect_tasks() == 1

        # Case 6: Collected the same config but with locked state - re-delete collected config
        configs_short = ConfigListGenerator.get(ConfigListGenerator.REMOVED, locked=True)

        requests_mocker.get(
            re.compile(AGENT_API_HOSTS),
            text=json.dumps(configs_short),
            status_code=HTTPStatus.OK,
        )

        assert handler.collect_tasks() == 1
        handler.handle_task()
        assert json.loads(mocked_requests_post.call_args[1]["data"])["overall_deployment_status"] == "SUCCESS"
        assert json.loads(mocked_requests_post.call_args[1]["data"])["vs_status"] == VS_STATUS_BY_ID_EMTPY

        keepalived.erase_config(configs_full_target_removed["service"], with_history=True)
        # BalancerConfigState.all_deployed should not be accessed in dry_run
        mock_all_deployed.assert_not_called()
        # IpTablesCache.ips_without_rules should not be accessed in dry_run
        mock_ips_without_rules.assert_not_called()
        # KeepalivedBase .start .stop .track_liveness use .check_process_exists checking that it's accessed in dry run
        mock_check_process_exists.assert_not_called()
        assert OnDryRun.enabled is True

        SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
        SettingsCollector().collect_settings()
        assert OnDryRun.enabled is False
