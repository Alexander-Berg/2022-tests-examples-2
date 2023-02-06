import json
import re
from http import HTTPStatus
from unittest.mock import Mock, PropertyMock, patch

import pytest
import requests_mock

from balancer_agent.core.exceptions import RestoreConfigError, TaskDeployError
from balancer_agent.core.status_codes import ServiceErrorCodes, SuccessOperationCodes, UnsuccessfulOperationCodes
from balancer_agent.operations.balancer_configs.config_containers import (
    VS_STATUS_BY_ID_EMTPY,
    BalancerConfigState,
    VirtualServerState,
    VSDistinguisher,
)
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.systems.keepalived import FailedToStopKeepalivedError
from balancer_agent.operations.tasks.handlers.ipvs_prod_tasks import ProdTasksHandler
from balancer_agent.operations.tasks.handlers.ipvs_test_tasks import TestTasksHandler
from balancer_agent.operations.tasks.handlers.waiter import Waiter

from .static.configs_from_api import ConfigGenerator, ConfigListGenerator

from typing import Dict

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
    "generator_version": 2,
}

AGENT_API_HOSTS = "https://host.*"

VS_DISTINGUISHER_1069928 = VSDistinguisher(ip="2a02:6b8:0:3400::0", port=80, protocol="TCP")
VS_DISTINGUISHER_1069929 = VSDistinguisher(ip="2a02:6b8:0:3400::0", port=801, protocol="TCP")
VS_DISTINGUISHER_1069930 = VSDistinguisher(ip="2a02:6b8:0:3400::1", port=80, protocol="TCP")
VS_DISTINGUISHER_1069931 = VSDistinguisher(ip="2a02:6b8:0:3400::1", port=801, protocol="TCP")


MOCK_SERVICES_IN_IPVS_FOR_TASK_L4 = {
    VS_DISTINGUISHER_1069928: [],
    VS_DISTINGUISHER_1069929: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
    VS_DISTINGUISHER_1069930: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
    VS_DISTINGUISHER_1069931: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
}

MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_MISSING_VS = {
    VS_DISTINGUISHER_1069928: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
    VS_DISTINGUISHER_1069929: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
    VS_DISTINGUISHER_1069930: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
}

MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS = [
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::1-80-TCP",
        "id": 1069930,
        "ip": "2a02:6b8:0:3400::1",
        "port": 80,
        "protocol": "TCP",
        "rss": ["2a02:6b8:0:1482::115", "2a02:6b8:b010:31::233"],
        "status": VirtualServerState.DEPLOYED,
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::1-801-TCP",
        "id": 1069931,
        "ip": "2a02:6b8:0:3400::1",
        "port": 801,
        "protocol": "TCP",
        "rss": ["2a02:6b8:0:1482::115", "2a02:6b8:b010:31::233"],
        "status": VirtualServerState.DEPLOYED,
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::0-80-TCP",
        "id": 1069928,
        "ip": "2a02:6b8:0:3400::0",
        "port": 80,
        "protocol": "TCP",
        "rss": [],
        "status": VirtualServerState.DEPLOYED,
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::0-801-TCP",
        "id": 1069929,
        "ip": "2a02:6b8:0:3400::0",
        "port": 801,
        "protocol": "TCP",
        "rss": ["2a02:6b8:0:1482::115", "2a02:6b8:b010:31::233"],
        "status": VirtualServerState.DEPLOYED,
    },
]


MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_EXTERNAL = json.loads(
    json.dumps(
        {
            VirtualServerState.ANNOUNCED: [],
            VirtualServerState.DEPLOYED: [1069930, 1069931, 1069928, 1069929],
            VirtualServerState.FAILED: [],
        }
    )
)


MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_VS = [
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::1-80-TCP",
        "id": 1069930,
        "ip": "2a02:6b8:0:3400::1",
        "port": 80,
        "protocol": "TCP",
        "rss": ["2a02:6b8:0:1482::115", "2a02:6b8:b010:31::233"],
        "status": VirtualServerState.DEPLOYED,
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::1-801-TCP",
        "id": 1069931,
        "ip": "2a02:6b8:0:3400::1",
        "port": 801,
        "protocol": "TCP",
        "rss": [],
        "status": VirtualServerState.FAILED,
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::0-80-TCP",
        "id": 1069928,
        "ip": "2a02:6b8:0:3400::0",
        "port": 80,
        "protocol": "TCP",
        "rss": ["2a02:6b8:0:1482::115", "2a02:6b8:b010:31::233"],
        "status": VirtualServerState.DEPLOYED,
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::0-801-TCP",
        "id": 1069929,
        "ip": "2a02:6b8:0:3400::0",
        "port": 801,
        "protocol": "TCP",
        "rss": ["2a02:6b8:0:1482::115", "2a02:6b8:b010:31::233"],
        "status": VirtualServerState.DEPLOYED,
    },
]


MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_VS_EXTERNAL = json.loads(
    json.dumps(
        {
            VirtualServerState.ANNOUNCED: [],
            VirtualServerState.DEPLOYED: [1069930, 1069928, 1069929],
            VirtualServerState.FAILED: [1069931],
        }
    )
)

MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_MISSING_ALL_VS: Dict = {}


MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_ALL_VS = [
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::1-80-TCP",
        "id": 1069930,
        "ip": "2a02:6b8:0:3400::1",
        "port": 80,
        "protocol": "TCP",
        "rss": [],
        "status": "FAILED",
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::1-801-TCP",
        "id": 1069931,
        "ip": "2a02:6b8:0:3400::1",
        "port": 801,
        "protocol": "TCP",
        "rss": [],
        "status": "FAILED",
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::0-80-TCP",
        "id": 1069928,
        "ip": "2a02:6b8:0:3400::0",
        "port": 80,
        "protocol": "TCP",
        "rss": [],
        "status": "FAILED",
    },
    {
        "_announce_condition_reached_in_ipvs": False,
        "_announced_interface_found": False,
        "_distinguisher": "2a02:6b8:0:3400::0-801-TCP",
        "id": 1069929,
        "ip": "2a02:6b8:0:3400::0",
        "port": 801,
        "protocol": "TCP",
        "rss": [],
        "status": "FAILED",
    },
]


MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_ALL_VS_EXTERNAL = json.loads(
    json.dumps(
        {
            VirtualServerState.ANNOUNCED: [],
            VirtualServerState.DEPLOYED: [],
            VirtualServerState.FAILED: [1069930, 1069931, 1069928, 1069929],
        }
    )
)


MOCK_BINDTO_IP = "2a02:6b8:0:e00::13:b0aa"


@pytest.mark.parametrize(
    "l3_response,ipvs_output,overall_deployment_status,vss_deploy_status_internal,"
    "vss_deploy_status_external,status_code,expected,error_flag,error_code",
    [
        # TODO: 'no tasks' test doesn't make sense until task collection batch operation have supported
        # ([], None, None, None, HTTPStatus.OK, None, False, None),
        # Valid task L4. All VSS are deployed
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
                    }
                )
            ),
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4,
            BalancerConfigState.SUCCESS_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_EXTERNAL,
            HTTPStatus.OK,
            None,
            False,
            SuccessOperationCodes.BASE.value,
        ),
        # Missing VS in IPVS
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
                    }
                )
            ),
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_MISSING_VS,
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_VS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_VS_EXTERNAL,
            HTTPStatus.OK,
            None,
            True,
            UnsuccessfulOperationCodes.BASE.value,
        ),
        # No VS in IPVS
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
                    }
                )
            ),
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_MISSING_ALL_VS,
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_ALL_VS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_ALL_VS_EXTERNAL,
            HTTPStatus.OK,
            None,
            True,
            UnsuccessfulOperationCodes.BASE.value,
        ),
    ],
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetV2.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.AGENT_MODE",
    new_callable=PropertyMock(return_value="prod"),
)
@patch("balancer_agent.operations.systems.keepalived.Keepalived")
@patch("balancer_agent.operations.systems.iptables.IpTables")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=False)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=True)
@requests_mock.mock(kw="requests_mocker")
def test_handle_task(
    mock1,
    mock2,
    mocked_iptables,
    mocked_keepalived,
    mocked_agent_mode,
    l3_response,
    ipvs_output,
    overall_deployment_status,
    vss_deploy_status_internal,
    vss_deploy_status_external,
    status_code,
    expected,
    error_flag,
    error_code,
    **kwargs,
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
    mocked_requests_post = requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
    requests_mocker.get(re.compile("https://host.*/configs/.*"), text=l3_response, status_code=status_code)

    # To avoid waiting 7 retries on request failure
    ProdTasksHandler.collect_tasks.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[
        0
    ].cell_contents.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    # To avoid waiting retries on request failure
    TestTasksHandler.send_task_status_to_l3.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1
    # There are three decorators wrapping wait_keepalived.
    # To access inner decorator (retry) parameters we need to do this
    Waiter.__call__.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1

    with patch("balancer_agent.operations.systems.ipvs.IPVS.get_services", return_value=ipvs_output), patch(
        "balancer_agent.operations.systems.ipvs.IPVS.reset"
    ) as mocked_ipvs_reset:

        handler = ProdTasksHandler(runtime_settings.runtime)
        handler.keepalived.find_unsynchronized_configs = lambda configs: configs
        handler.collect_tasks()

        if error_flag:
            with pytest.raises(TaskDeployError):
                assert handler.handle_task() == expected
        else:
            assert handler.handle_task() == expected
            if l3_response:
                mocked_keepalived.return_value.apply_config.assert_called_once()
                mocked_keepalived.return_value.track_liveness.assert_called_once()
                mocked_iptables.return_value.restart.assert_called_once()
                # two calls - first - lock config, second - send deployment status
                assert mocked_requests_post.call_count == 2
                mocked_ipvs_reset.assert_not_called()

    assert handler.task.config.state.vss_status == vss_deploy_status_internal
    assert f"{json.loads(l3_response)['id']}/deployment-status" in mocked_requests_post.last_request.url

    report_body = mocked_requests_post.last_request.json()
    assert overall_deployment_status == report_body["overall_deployment_status"]
    assert error_code == report_body["error"]["code"]
    assert report_body["vs_status"] == vss_deploy_status_external


@pytest.mark.parametrize(
    "l3_response,overall_deployment_status,vss_deploy_status,status_code,error_code,side_effect",
    [
        # Keepalived exception raised
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
                    }
                )
            ),
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_ALL_VS,
            HTTPStatus.OK,
            FailedToStopKeepalivedError.code.value,
            FailedToStopKeepalivedError("Could not stop keepalived"),
        ),
        # Unknown exception raised
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
                    }
                )
            ),
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS_MISSING_ALL_VS,
            HTTPStatus.OK,
            ServiceErrorCodes.UNKNOWN.value,
            Exception("Something is wrong"),
        ),
    ],
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetV2.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch("balancer_agent.operations.systems.keepalived.Keepalived")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=False)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=True)
@requests_mock.mock(kw="requests_mocker")
def test_handle_task_exception(
    mock1,
    mock2,
    mocked_keepalived,
    l3_response,
    overall_deployment_status,
    vss_deploy_status,
    status_code,
    error_code,
    side_effect,
    **kwargs,
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
    mocked_requests_post = requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
    requests_mocker.get(re.compile("https://host.*/configs/.*"), text=l3_response, status_code=status_code)
    mocked_keepalived.return_value.apply_config = Mock(side_effect=side_effect)

    handler = ProdTasksHandler(runtime_settings.runtime)
    handler.keepalived.find_unsynchronized_configs = lambda configs: configs
    handler.collect_tasks()

    with pytest.raises(TaskDeployError):
        assert not handler.handle_task()

    assert handler.task.config.state.vss_status == vss_deploy_status

    assert f"{json.loads(l3_response)['id']}/deployment-status" in mocked_requests_post.last_request.path

    report_body = mocked_requests_post.last_request.json()
    assert overall_deployment_status == report_body["overall_deployment_status"]
    assert error_code == report_body["error"]["code"]
    assert report_body["vs_status"] == json.loads(json.dumps(VS_STATUS_BY_ID_EMTPY))


@pytest.mark.parametrize(
    "l3_response,status_code,apply_config_side_effect,erase_config_side_effect",
    [
        # Keepalived exception raised
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
                    }
                )
            ),
            HTTPStatus.OK,
            FailedToStopKeepalivedError("Could not stop keepalived"),
            None,
        ),
        # Unknown exception raised
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
                    }
                )
            ),
            HTTPStatus.OK,
            Exception("Something is wrong"),
            Exception("Something is wrong"),
        ),
    ],
)
@patch("balancer_agent.operations.balancer_configs.config_containers.VSDatasetV2.bindto", MOCK_BINDTO_IP)
@patch("balancer_agent.operations.systems.keepalived.Keepalived")
@patch("balancer_agent.operations.systems.ipvs.IPVS.reset")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=False)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=True)
@requests_mock.mock(kw="requests_mocker")
def test_restore_config(
    mock1,
    mock2,
    mocked_ipvs_reset,
    mocked_keepalived,
    l3_response,
    status_code,
    apply_config_side_effect,
    erase_config_side_effect,
    **kwargs,
):
    """
    Checking restore config call succeed after handle_task failure
    """
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

    mocked_keepalived.return_value.apply_config = Mock(side_effect=apply_config_side_effect)
    mocked_keepalived.return_value.multi_erase_config = Mock(side_effect=erase_config_side_effect)

    handler = ProdTasksHandler(runtime_settings.runtime)
    handler.keepalived.find_unsynchronized_configs = lambda configs: configs
    handler.collect_tasks()

    with pytest.raises(TaskDeployError):
        assert not handler.handle_task()

    if not erase_config_side_effect:
        handler.restore_config()
    else:
        with pytest.raises(RestoreConfigError):
            handler.restore_config()

    mocked_keepalived.return_value.multi_erase_config.assert_called_once()


@pytest.mark.parametrize(
    "l3_response,overall_deployment_status,status_code,expected,error_flag,error_code",
    [
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "REMOVED",
                        "vs_group_settings": {"num": 2, "min_up": (1, 1), "num_vss": (2, 2)},
                    }
                )
            ),
            BalancerConfigState.SUCCESS_STATUS,
            HTTPStatus.OK,
            None,
            False,
            SuccessOperationCodes.BASE.value,
        ),
    ],
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetV2.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.AGENT_MODE",
    new_callable=PropertyMock(return_value="prod"),
)
@patch("balancer_agent.operations.systems.keepalived.Keepalived")
@patch("balancer_agent.operations.systems.iptables.IpTables")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=False)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=True)
@requests_mock.mock(kw="requests_mocker")
def test_remove_config(
    mock1,
    mock2,
    mocked_iptables,
    mocked_keepalived,
    mocked_agent_mode,
    l3_response,
    overall_deployment_status,
    status_code,
    expected,
    error_flag,
    error_code,
    **kwargs,
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

    mocked_requests_post = requests_mocker.post(re.compile(AGENT_API_HOSTS), text=l3_response, status_code=status_code)

    # To avoid waiting retries on request failure
    TestTasksHandler.send_task_status_to_l3.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1
    # There are three decorators wrapping wait_keepalived.
    # To access inner decorator (retry) parameters we need to do this
    Waiter.__call__.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1

    handler = ProdTasksHandler(runtime_settings.runtime)
    handler.keepalived.find_unsynchronized_configs = lambda configs: configs
    handler.collect_tasks()

    if error_flag:
        with pytest.raises(TaskDeployError):
            assert handler.handle_task() == expected
    else:
        assert handler.handle_task() == expected
        if l3_response:
            mocked_keepalived.return_value.erase_config.assert_called_once()
            mocked_keepalived.return_value.track_liveness.assert_called_once()
            # two calls - first - collect tasks, second - send deployment status
            assert mocked_requests_post.call_count == 2

    assert f"{json.loads(l3_response)['id']}/deployment-status" in mocked_requests_post.last_request.url

    report_body = mocked_requests_post.last_request.json()
    assert overall_deployment_status == report_body["overall_deployment_status"]
    assert error_code == report_body["error"]["code"]
    assert report_body["vs_status"] == json.loads(json.dumps(VS_STATUS_BY_ID_EMTPY))
