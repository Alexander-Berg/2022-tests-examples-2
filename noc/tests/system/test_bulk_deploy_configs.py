import json
from copy import deepcopy
from http import HTTPStatus
from unittest.mock import Mock, PropertyMock, patch

import requests_mock

from balancer_agent.core.exceptions import TaskDeployError
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.systems.keepalived import Keepalived
from balancer_agent.operations.tasks.handlers.ipvs_prod_tasks import ProdTasksHandler
from balancer_agent.operations.tasks.handlers.ipvs_test_tasks import TestTasksHandler
from balancer_agent.operations.tasks.handlers.waiter import Waiter
from balancer_agent.operations.tasks.window import DEPLOYMENT_WINDOW

from .configs_from_api import ConfigGenerator, ConfigListGenerator

HOST_A = "host_a"
HOST_B = "host_b"
ACTIVE_STATE = "ACTIVE"
IDLE_STATE = "IDLE"
DRY_RUN_STATE = "DRY_RUN"

L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]

MOCK_INITIAL_CONFIG = {
    "controller": {
        "data_collector_url": "https://l3-test.tt.yandex-team.ru/api/v1/agent",
        "worker_tracking_seconds": 10,
    },
    "main": {
        "agent_mode": "prod",
        "balancing_type": "ipvs",
        "lb_name": "man1-testenv-lb0bb.yndx.net",
        "bulk_deploy": True,
    },
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
    "generator_version": 2,
    "config_tracking": "STRICT",
}

MOCK_COLLECTED_CONFIG_DRY_RUN = deepcopy(MOCK_COLLECTED_CONFIG)
# MOCK_COLLECTED_CONFIG_DRY_RUN["agent_mode"] = DRY_RUN_STATE
MOCK_COLLECTED_CONFIG_DRY_RUN["config_tracking"] = "STRICT"

AGENT_API_HOSTS = "https://host.*"

MOCK_BINDTO_IP = "2a02:6b8:0:e00::13:b0aa"


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def json(self):
        return json.loads(self.text)


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
@patch(
    "balancer_agent.operations.systems.keepalived.Keepalived.RESTART_KEEPALIVED_CMD",
    "sudo make -C /etc/keepalived restart;" "sleep 1;",
)
@patch("balancer_agent.operations.tasks.helpers.IS_PROD_AGENT", True)
def test_bulk_deploy_configs_in_cycle_success_deploys(a, metrics_reporter_mock, f, g, mocked_requests_post, h):
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG

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
        },
        amount=4,
    )

    DEPLOYMENT_WINDOW.ENABLED = True

    with patch(
        "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler._collect_locked_config"
    ) as mock_collect_locked_config, patch(
        "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler._collect_tasks"
    ) as mocked_collect_tasks:
        mock_collect_locked_config.side_effect = [
            MockResponse(json.dumps(cfg), status_code=HTTPStatus.OK) for cfg in configs_full_target_active
        ]

        mocked_collect_tasks.return_value = MockResponse(json.dumps(""), status_code=HTTPStatus.OK)
        # Always start with empty config
        keepalived = Keepalived()
        keepalived.RESTART_KEEPALIVED_CMD = "sudo make -C /etc/keepalived restart;" "sleep 1;"
        for cfg in configs_full_target_active:
            keepalived.erase_config(cfg["service"], with_history=True)
        handler = ProdTasksHandler(runtime_settings.runtime)
        handler.keepalived = keepalived

        # Case 1: no configs deployed, new config collection and deploy
        runtime_settings.collect_settings()

        configs_short = ConfigListGenerator.get(
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
        )

        configs_short_deployed = ConfigListGenerator.get(
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            deployed=True,
        )

        with patch("balancer_agent.operations.tasks.handlers.base_prod_tasks.requests.get") as mocked_requests:
            mocked_requests.side_effect = [
                MockResponse(json.dumps(configs_short)),
                MockResponse(json.dumps(configs_short_deployed[:1] + configs_short[1:])),
                MockResponse(json.dumps(configs_short_deployed[:3] + configs_short[3:])),
            ]
            assert DEPLOYMENT_WINDOW.current_limit() == 1
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is False

            assert handler.collect_tasks() == 1
            handler.handle_task()
            assert DEPLOYMENT_WINDOW.current_limit() == 2
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is False
            assert json.loads(mocked_requests_post.mock_calls[0][2]["data"]).get("id") == 1
            assert (
                mocked_requests_post.mock_calls[0][1][0]
                == "https://host_b/api/v1/agent/sas-1testenv-test-lb0aa.yndx.net/configs/1/deployment-status"
            )

            assert handler.collect_tasks() == 2

            handler.handle_task()
            handler.handle_task()
            assert DEPLOYMENT_WINDOW.current_limit() == 8
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is False
            mocked_requests_post.mock_calls[2][
                1
            ] == "https://host_b/api/v1/agent/sas-1testenv-test-lb0aa.yndx.net/configs/deployment-status?ids=2,3"
            assert json.loads(mocked_requests_post.mock_calls[2][2]["data"])["overall_deployment_status"] == "SUCCESS"
            assert json.loads(mocked_requests_post.mock_calls[2][2]["data"]).get("id") is None

            assert handler.collect_tasks() == 1
            handler.handle_task()
            assert DEPLOYMENT_WINDOW.current_limit() == 8
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is False

            assert (
                mocked_requests_post.mock_calls[4][1][0]
                == "https://host_b/api/v1/agent/sas-1testenv-test-lb0aa.yndx.net/configs/4/deployment-status"
            )
            assert json.loads(mocked_requests_post.mock_calls[4][2]["data"])["overall_deployment_status"] == "SUCCESS"


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
@patch(
    "balancer_agent.operations.systems.keepalived.Keepalived.RESTART_KEEPALIVED_CMD",
    "sudo make -C /etc/keepalived restart;" "sleep 1;",
)
@patch("balancer_agent.operations.tasks.helpers.IS_PROD_AGENT", True)
@requests_mock.mock(kw="requests_mocker")
def test_bulk_deploy_configs_in_cycle_failure_deploys(
    a, metrics_reporter_mock, f, g, mocked_requests_post, h, **kwargs
):
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG

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
        },
        amount=6,
    )

    # DEPLOYMENT_WINDOW is global - so to start from lower limit we need to set it manually
    DEPLOYMENT_WINDOW._current_limit = 1
    DEPLOYMENT_WINDOW.ENABLED = True
    DEPLOYMENT_WINDOW.UPPER_LIMIT = 2

    with patch(
        "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler._collect_locked_config"
    ) as mock_collect_locked_config, patch(
        "balancer_agent.operations.tasks.handlers.ipvs_prod_tasks.ProdTasksHandler._collect_tasks"
    ) as mocked_collect_tasks:
        mock_collect_locked_config.side_effect = [
            MockResponse(json.dumps(cfg), status_code=HTTPStatus.OK) for cfg in configs_full_target_active[:3]
        ] + [MockResponse(json.dumps(cfg), status_code=HTTPStatus.OK) for cfg in configs_full_target_active[1:]]

        mocked_collect_tasks.return_value = MockResponse(json.dumps(""), status_code=HTTPStatus.OK)
        # Always start with empty config
        keepalived = Keepalived()
        keepalived.RESTART_KEEPALIVED_CMD = "sudo make -C /etc/keepalived restart;" "sleep 1;"
        for cfg in configs_full_target_active:
            keepalived.erase_config(cfg["service"], with_history=True)
        handler = ProdTasksHandler(runtime_settings.runtime)
        handler.keepalived = keepalived

        runtime_settings.collect_settings()

        configs_short = ConfigListGenerator.get(
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
        )

        configs_short_deployed = ConfigListGenerator.get(
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            ConfigListGenerator.ACTIVE,
            deployed=True,
        )

        with patch("balancer_agent.operations.tasks.handlers.base_prod_tasks.requests.get") as mocked_requests:
            original_start = keepalived.start

            mocked_requests.side_effect = [
                MockResponse(json.dumps(configs_short)),
                MockResponse(json.dumps(configs_short_deployed[:1] + configs_short[1:])),
                MockResponse(json.dumps(configs_short_deployed[:1] + configs_short[1:])),
                MockResponse(json.dumps(configs_short_deployed[:2] + configs_short[2:])),
                MockResponse(json.dumps(configs_short_deployed[:3] + configs_short[3:])),
                MockResponse(json.dumps(configs_short_deployed[:4] + configs_short[4:])),
            ]

            assert handler.collect_tasks() == 1
            handler.handle_task()

            assert handler.collect_tasks() == 2
            assert DEPLOYMENT_WINDOW.current_limit() == 2
            handler.handle_task()
            # it's because DEPLOYMENT_WINDOW.UPPER_LIMIT is 2
            assert DEPLOYMENT_WINDOW.current_limit() == 2
            # Injecting keepalived error to trigger recovery process
            keepalived.start = Mock(
                side_effect=[
                    # This call will be during application of the config
                    Exception,
                    # This call will be on multi_erase in recovery process
                    True,
                ]
            )
            try:
                handler.handle_task()
            except TaskDeployError:
                assert keepalived.start.call_count == 1
                handler.restore_config()
            assert keepalived.start.call_count == 2
            assert DEPLOYMENT_WINDOW.current_limit() == 1
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is True
            assert DEPLOYMENT_WINDOW.recovery_count == 2

            # Recover regular keepalived.start
            keepalived.start = original_start

            assert handler.collect_tasks() == 1
            handler.handle_task()
            assert (
                mocked_requests_post.mock_calls[2][1][0]
                == "https://host_a/api/v1/agent/sas-1testenv-test-lb0aa.yndx.net/configs/2/deployment-status"
            )
            assert DEPLOYMENT_WINDOW.current_limit() == 1
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is True
            assert DEPLOYMENT_WINDOW.recovery_count == 1

            assert handler.collect_tasks() == 1
            handler.handle_task()

            assert DEPLOYMENT_WINDOW.current_limit() == 1
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is False
            assert DEPLOYMENT_WINDOW.recovery_count == 0
            assert (
                mocked_requests_post.mock_calls[4][1][0]
                == "https://host_a/api/v1/agent/sas-1testenv-test-lb0aa.yndx.net/configs/3/deployment-status"
            )
            assert json.loads(mocked_requests_post.mock_calls[4][2]["data"])["overall_deployment_status"] == "SUCCESS"

            assert handler.collect_tasks() == 1
            handler.handle_task()

            assert DEPLOYMENT_WINDOW.current_limit() == 2
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is False
            assert DEPLOYMENT_WINDOW.recovery_count == 0
            assert (
                mocked_requests_post.mock_calls[6][1][0]
                == "https://host_a/api/v1/agent/sas-1testenv-test-lb0aa.yndx.net/configs/4/deployment-status"
            )
            assert json.loads(mocked_requests_post.mock_calls[6][2]["data"])["overall_deployment_status"] == "SUCCESS"

            assert handler.collect_tasks() == 2
            handler.handle_task()
            handler.handle_task()
            assert DEPLOYMENT_WINDOW.current_limit() == 2
            assert DEPLOYMENT_WINDOW.in_recovery_mode() is False
            assert DEPLOYMENT_WINDOW.recovery_count == 0
            assert (
                mocked_requests_post.mock_calls[8][1][0]
                == "https://host_a/api/v1/agent/sas-1testenv-test-lb0aa.yndx.net/configs/deployment-status?ids=5,6"
            )
            assert json.loads(mocked_requests_post.mock_calls[8][2]["data"])["overall_deployment_status"] == "SUCCESS"
