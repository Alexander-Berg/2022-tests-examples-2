import json
import re
from copy import deepcopy
from http import HTTPStatus
from unittest.mock import Mock, PropertyMock, patch

import pytest
import requests_mock

from balancer_agent.core.exceptions import RestoreConfigError, TaskDeployError
from balancer_agent.core.status_codes import ServiceErrorCodes, SuccessOperationCodes, UnsuccessfulOperationCodes
from balancer_agent.operations.balancer_configs.config_containers import (
    BalancerConfigState,
    VSDistinguisher,
    VSDistinguisherFWM,
)
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.systems.keepalived import FailedToStopKeepalivedError
from balancer_agent.operations.tasks.handlers.ipvs_test_tasks import TestTasksHandler
from balancer_agent.operations.tasks.handlers.waiter import Waiter

from .static.tasks_from_api import TASK_DYNAMIC_WEIGHT, TASK_FWMARK, TASK_L4

from typing import Dict, List

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

AGENT_API_HOSTS = "https://host.*"

VS_DISTINGUISHER_1069929 = VSDistinguisher(ip="2a02:6b8:0:3400::50", port=80, protocol="TCP")
VS_DISTINGUISHER_1069928 = VSDistinguisher(ip="2a02:6b8:0:3400::50", port=443, protocol="TCP")

MOCK_SERVICES_IN_IPVS_FOR_TASK_L4 = {
    VS_DISTINGUISHER_1069929: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
    VS_DISTINGUISHER_1069928: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
}

MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS = [
    {"id": 1069929, "rss": [{"id": 1554, "status": "SUCCESS"}, {"id": 1555, "status": "SUCCESS"}], "status": "UP"},
    {"id": 1069928, "rss": [{"id": 1554, "status": "SUCCESS"}, {"id": 1555, "status": "SUCCESS"}], "status": "UP"},
]

MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_MISSING_VS = {
    VS_DISTINGUISHER_1069929: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
    VS_DISTINGUISHER_1069928: [],
}


MOCK_SERVICES_IN_IPVS_FOR_TASK_MISSING_VS_L4_VS_DEPLOY_STATUS = [
    {"id": 1069929, "rss": [{"id": 1554, "status": "SUCCESS"}, {"id": 1555, "status": "SUCCESS"}], "status": "UP"},
    {"id": 1069928, "rss": [], "status": "DOWN"},
]

MOCK_SERVICES_IN_IPVS_FOR_TASK_MISSING_VS_L4_VS_DEPLOY_STATUS2 = [
    {"id": 1069929, "rss": [{"id": 1554, "status": "SUCCESS"}], "status": "UP"},
    {"id": 1069928, "rss": [], "status": "DOWN"},
]


MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_MISSING_ALL_VS: Dict = {VS_DISTINGUISHER_1069929: [], VS_DISTINGUISHER_1069928: []}


MOCK_SERVICES_IN_IPVS_FOR_TASK_MISSING_ALL_VS_L4_VS_DEPLOY_STATUS = [
    {"id": 1069929, "rss": [], "status": "DOWN"},
    {"id": 1069928, "rss": [], "status": "DOWN"},
]


MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_RS_ZERO_WEIGHT = {
    VS_DISTINGUISHER_1069929: [{"address": "2a02:6b8:0:1482::115", "weight": 0}],
    VS_DISTINGUISHER_1069928: [{"address": "2a02:6b8:0:1482::115", "weight": 0}],
}


TASK_L4_RS_ZERO_WEIGHT_VS_DEPLOY_STATUS = [
    {"id": 1069929, "status": "DOWN", "rss": [{"id": 1554, "status": "SUCCESS"}]},
    {"id": 1069928, "status": "DOWN", "rss": [{"id": 1554, "status": "SUCCESS"}]},
]

TASK_L4_HIGH_QUORUM: Dict = deepcopy(TASK_L4)
for vs in TASK_L4_HIGH_QUORUM["data"]["vss"]:
    vs["config"]["quorum"] = 1000

TASK_L4_HIGH_QUORUM_VS_DEPLOY_STATUS = [
    {"id": 1069929, "status": "DOWN", "rss": [{"id": 1554, "status": "SUCCESS"}, {"id": 1555, "status": "SUCCESS"}]},
    {"id": 1069928, "status": "DOWN", "rss": [{"id": 1554, "status": "SUCCESS"}, {"id": 1555, "status": "SUCCESS"}]},
]

TASK_L4_HIGH_QUORUM_ON_ONE_VS: Dict = deepcopy(TASK_L4)
TASK_L4_HIGH_QUORUM_ON_ONE_VS["data"]["vss"][0]["config"]["quorum"] = 1000

TASK_L4_HIGH_QUORUM_ON_ONE_VS_DEPLOY_STATUS = [
    {"id": 1069929, "status": "DOWN", "rss": [{"id": 1554, "status": "SUCCESS"}, {"id": 1555, "status": "SUCCESS"}]},
    {"id": 1069928, "status": "UP", "rss": [{"id": 1554, "status": "SUCCESS"}, {"id": 1555, "status": "SUCCESS"}]},
]

VS_DISTINGUISHER_FWM_1069929 = VSDistinguisherFWM(af=10, fwmark=52407)
VS_DISTINGUISHER_FWM_1069928 = VSDistinguisherFWM(af=2, fwmark=52407)

MOCK_SERVICES_IN_IPVS_FOR_TASK_FWM = {
    VS_DISTINGUISHER_FWM_1069929: [{"address": "2a02:6b8:c02:7f4:0:1429:f3fd:d8d0", "weight": 1}],
    VS_DISTINGUISHER_FWM_1069928: [{"address": "2a02:6b8:c02:7f4:0:1429:f3fd:d8d0", "weight": 1}],
}

MOCK_SERVICES_IN_IPVS_FOR_TASK_FWM_VS_DEPLOY_STATUS = [
    {"id": 1069929, "rss": [{"id": 11554, "status": "SUCCESS"}], "status": "UP"},
    {"id": 1069928, "rss": [{"id": 21554, "status": "SUCCESS"}], "status": "UP"},
]


MOCK_BINDTO_IP = "2a02:6b8:0:e00::13:b0aa"


VS_DISTINGUISHER_DYNAMIC_WEIGHT_2520354 = VSDistinguisher(ip="2a02:6b8:0:3400::3:16", port=443, protocol="TCP")

MOCK_SERVICES_IN_IPVS_FOR_TASK_DYNAMIC_WEIGHT = {
    VS_DISTINGUISHER_DYNAMIC_WEIGHT_2520354: [{"address": "2a02:6b8:c01:710:8000:611:0:11", "weight": 10}]
}

MOCK_SERVICES_IN_IPVS_FOR_TASK_DYNAMIC_WEIGHT_VS_DEPLOY_STATUS = [
    {"id": 2520354, "rss": [{"id": 3082264, "status": "SUCCESS"}], "status": "UP"}
]

IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_FAILURE_TEST: List[Dict] = [
    {},
    {},
    {},
    {},
]

IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_FAILURE_TEST2 = [
    {},
    {},
    {
        VS_DISTINGUISHER_1069929: [
            {"address": "2a02:6b8:0:1482::115", "weight": 1},
        ],
    },
    {
        VS_DISTINGUISHER_1069929: [
            {"address": "2a02:6b8:0:1482::115", "weight": 1},
        ],
    },
    {
        VS_DISTINGUISHER_1069929: [
            {"address": "2a02:6b8:0:1482::115", "weight": 1},
        ],
    },
]


IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_SUCCESS_TEST = [
    {},
    {
        VS_DISTINGUISHER_1069929: [
            {"address": "2a02:6b8:0:1482::115", "weight": 1},
        ],
    },
    {
        VS_DISTINGUISHER_1069929: [
            {"address": "2a02:6b8:0:1482::115", "weight": 1},
        ]
    },
    {
        VS_DISTINGUISHER_1069929: [
            {"address": "2a02:6b8:0:1482::115", "weight": 1},
            {"address": "2a02:6b8:b010:31::233", "weight": 1},
        ],
        VS_DISTINGUISHER_1069928: [
            {"address": "2a02:6b8:0:1482::115", "weight": 1},
            {"address": "2a02:6b8:b010:31::233", "weight": 1},
        ],
    },
]


@pytest.mark.parametrize(
    "l3_response,ipvs_output,overall_deploy_status,vss_deploy_status,status_code,expected,error_flag,reported_code",
    [
        # No tasks
        ([], None, None, None, HTTPStatus.OK, None, False, None),
        # Valid task L4
        (
            [TASK_L4],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4,
            BalancerConfigState.SUCCESS_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            False,
            SuccessOperationCodes.BASE.value,
        ),
        # Missing VS in IPVS
        (
            [TASK_L4],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_MISSING_VS,
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_MISSING_VS_L4_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            True,
            UnsuccessfulOperationCodes.BASE.value,
        ),
        # No VS in IPVS
        (
            [TASK_L4],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_MISSING_ALL_VS,
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_MISSING_ALL_VS_L4_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            True,
            UnsuccessfulOperationCodes.BASE.value,
        ),
        # Zero RS weight in IPVS
        (
            [TASK_L4],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_RS_ZERO_WEIGHT,
            BalancerConfigState.FAILURE_STATUS,
            TASK_L4_RS_ZERO_WEIGHT_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            True,
            UnsuccessfulOperationCodes.BASE.value,
        ),
        # Unachievable quorum
        (
            [TASK_L4_HIGH_QUORUM],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4,
            BalancerConfigState.FAILURE_STATUS,
            TASK_L4_HIGH_QUORUM_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            True,
            UnsuccessfulOperationCodes.BASE.value,
        ),
        # Unachievable quorum on one VS
        (
            [TASK_L4_HIGH_QUORUM_ON_ONE_VS],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4,
            BalancerConfigState.FAILURE_STATUS,
            TASK_L4_HIGH_QUORUM_ON_ONE_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            True,
            UnsuccessfulOperationCodes.BASE.value,
        ),
        # Valid task FWMARK
        (
            [TASK_FWMARK],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_FWM,
            BalancerConfigState.SUCCESS_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_FWM_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            False,
            SuccessOperationCodes.BASE.value,
        ),
        # Valid task Dynamic weight
        (
            [TASK_DYNAMIC_WEIGHT],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_DYNAMIC_WEIGHT,
            BalancerConfigState.SUCCESS_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_DYNAMIC_WEIGHT_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            False,
            SuccessOperationCodes.BASE.value,
        ),
    ],
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetBase.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("requests.put")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=True)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=False)
@requests_mock.mock(kw="requests_mocker")
def test_handle_task(
    mocked_agent_mode1,
    mocked_agent_mode2,
    mocked_requests_put,
    mocked_keepalived,
    l3_response,
    ipvs_output,
    overall_deploy_status,
    vss_deploy_status,
    status_code,
    expected,
    error_flag,
    reported_code,
    **kwargs,
):
    mocked_requests_put().status_code = HTTPStatus.NO_CONTENT
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=json.dumps(l3_response), status_code=status_code)

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

        handler = TestTasksHandler(runtime_settings.runtime)
        handler.collect_tasks()

        if error_flag:
            with pytest.raises(TaskDeployError):
                assert handler.handle_task() == expected
        else:
            assert handler.handle_task() == expected
            if l3_response:
                mocked_keepalived.return_value.apply_config.assert_called_once()
                mocked_keepalived.return_value.erase_config.assert_called_once()

                mocked_ipvs_reset.assert_called_once()

    if ipvs_output:
        # starting from 1, due to a mocking call 'mocked_requests_put().status_code = HTTPStatus.NO_CONTENT' above
        for args, kwargs in mocked_requests_put.call_args_list[1:]:
            url = args[0]
            assert any([("/tasks/" + str(task["id"]) + "/deployment-status" in url) for task in l3_response])
            report_data = json.loads(kwargs["data"])
            assert report_data["overall_deployment_status"] == overall_deploy_status
            if error_flag:
                assert report_data["error"]["message"]
            else:
                assert not report_data["error"]["message"]

            assert report_data["error"]["code"] == reported_code
            assert report_data["ts"]
            assert report_data["vss"] == vss_deploy_status
            assert handler.headers == kwargs["headers"]


@pytest.mark.parametrize(
    "l3_response,ipvs_output,overall_deploy_status,vss_deploy_status,"
    "status_code,expected,error_flag,error_message,reported_code,attempts",
    [
        # Failure case - weight grows once but stop growing after that and retry limit ends
        (
            [TASK_L4],
            IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_FAILURE_TEST2,
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_MISSING_VS_L4_VS_DEPLOY_STATUS2,
            HTTPStatus.OK,
            None,
            True,
            True,
            UnsuccessfulOperationCodes.BASE.value,
            len(IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_FAILURE_TEST2),
        ),
        # Failure case - weight grows once but stop growing after that and dynamic timeout triggers
        (
            [TASK_L4],
            IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_FAILURE_TEST2
            + [
                {
                    VS_DISTINGUISHER_1069929: [
                        {"address": "2a02:6b8:0:1482::115", "weight": 1},
                    ],
                },
                {
                    VS_DISTINGUISHER_1069929: [
                        {"address": "2a02:6b8:0:1482::115", "weight": 1},
                    ],
                },
            ],
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_MISSING_VS_L4_VS_DEPLOY_STATUS2,
            HTTPStatus.OK,
            None,
            False,
            True,
            UnsuccessfulOperationCodes.BASE.value,
            len(IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_FAILURE_TEST2) + 2,
        ),
        # Failure case - weight doesn't grow between retries and dynamic timeout triggers
        (
            [TASK_L4],
            IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_FAILURE_TEST,
            BalancerConfigState.FAILURE_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_MISSING_ALL_VS_L4_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            False,
            True,
            UnsuccessfulOperationCodes.BASE.value,
            len(IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_FAILURE_TEST),
        ),
        # Success case - weight grows and reaches quorum up
        (
            [TASK_L4],
            IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_SUCCESS_TEST,
            BalancerConfigState.SUCCESS_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            None,
            False,
            False,
            SuccessOperationCodes.BASE.value,
            len(IPVS_OUTPUT_FOR_DYNAMIC_WAIT_KEEPALIVED_TIMEOUT_SUCCESS_TEST),
        ),
    ],
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetBase.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("requests.put")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=True)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=False)
@requests_mock.mock(kw="requests_mocker")
def test_handle_task_dynamic_wait_timeout(
    mock1,
    mock2,
    mocked_requests_put,
    mocked_keepalived,
    l3_response,
    ipvs_output,
    overall_deploy_status,
    vss_deploy_status,
    status_code,
    expected,
    error_flag,
    error_message,
    reported_code,
    attempts,
    **kwargs,
):
    mocked_requests_put().status_code = HTTPStatus.NO_CONTENT
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=json.dumps(l3_response), status_code=status_code)

    # To avoid waiting retries on request failure
    TestTasksHandler.send_task_status_to_l3.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1
    # There are three decorators wrapping wait_keepalived.
    # To access inner decorator (retry) parameters we need to do this
    Waiter.__call__.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = attempts
    Waiter.__call__.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "wait_fixed"
    ] = 0.000001

    with patch("balancer_agent.operations.systems.ipvs.IPVS.get_services", Mock(side_effect=ipvs_output)), patch(
        "balancer_agent.operations.systems.ipvs.IPVS.reset"
    ) as mocked_ipvs_reset:

        handler = TestTasksHandler(runtime_settings.runtime)
        handler.collect_tasks()

        if error_flag:
            with pytest.raises(TaskDeployError):
                assert handler.handle_task() == expected
        else:
            assert handler.handle_task() == expected
            if l3_response:
                mocked_keepalived.return_value.apply_config.assert_called_once()
                mocked_keepalived.return_value.erase_config.assert_called_once()

                mocked_ipvs_reset.assert_called_once()

    if ipvs_output:
        # starting from 1, due to a mocking call 'mocked_requests_put().status_code = HTTPStatus.NO_CONTENT' above
        for args, kwargs in mocked_requests_put.call_args_list[1:]:
            url = args[0]

            assert any([("/tasks/" + str(task["id"]) + "/deployment-status" in url) for task in l3_response])
            report_data = json.loads(kwargs["data"])
            assert report_data["overall_deployment_status"] == overall_deploy_status
            if error_message:
                assert report_data["error"]["message"]
            else:
                assert not report_data["error"]["message"]

            assert report_data["error"]["code"] == reported_code
            assert report_data["ts"]
            assert report_data["vss"] == vss_deploy_status
            assert handler.headers == kwargs["headers"]


@pytest.mark.parametrize(
    "l3_response,ipvs_output,overall_deploy_status,vss_deploy_status,status_code,reported_code,side_effect",
    [
        # Keepalived exception raised
        (
            [TASK_L4],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4,
            BalancerConfigState.FAILURE_STATUS,
            [],
            HTTPStatus.OK,
            FailedToStopKeepalivedError.code.value,
            FailedToStopKeepalivedError("Could not stop keepalived"),
        ),
        # Unknown exception raised
        (
            [TASK_L4],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4,
            BalancerConfigState.FAILURE_STATUS,
            [],
            HTTPStatus.OK,
            ServiceErrorCodes.UNKNOWN.value,
            Exception("Something is wrong"),
        ),
    ],
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetBase.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("requests.put")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=True)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=False)
@requests_mock.mock(kw="requests_mocker")
def test_handle_task_exception(
    mock1,
    mock2,
    mocked_requests_put,
    mocked_keepalived,
    l3_response,
    ipvs_output,
    overall_deploy_status,
    vss_deploy_status,
    status_code,
    reported_code,
    side_effect,
    **kwargs,
):
    mocked_requests_put().status_code = HTTPStatus.NO_CONTENT
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=json.dumps(l3_response), status_code=status_code)

    mocked_keepalived.return_value.apply_config = Mock(side_effect=side_effect)

    handler = TestTasksHandler(runtime_settings.runtime)
    handler.collect_tasks()

    with pytest.raises(TaskDeployError):
        assert not handler.handle_task()

    for args, kwargs in mocked_requests_put.call_args_list[1:]:
        url = args[0]
        assert any([("/tasks/" + str(task["id"]) + "/deployment-status" in url) for task in l3_response])
        report_data = json.loads(kwargs["data"])
        assert report_data["overall_deployment_status"] == overall_deploy_status
        assert report_data["error"]["message"]
        assert report_data["error"]["code"] == reported_code
        assert report_data["ts"]
        assert report_data["vss"] == vss_deploy_status
        assert handler.headers == kwargs["headers"]


@pytest.mark.parametrize(
    "l3_response,ipvs_output,overall_deploy_status,vss_deploy_status,status_code,reported_code,side_effect",
    [
        # Exception happened afteere successful deploy
        (
            [TASK_L4],
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4,
            BalancerConfigState.SUCCESS_STATUS,
            MOCK_SERVICES_IN_IPVS_FOR_TASK_L4_VS_DEPLOY_STATUS,
            HTTPStatus.OK,
            SuccessOperationCodes.BASE.value,
            Exception("Something is wrong"),
        )
    ],
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.VSDatasetBase.bindto",
    PropertyMock(return_value=MOCK_BINDTO_IP),
)
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("requests.put")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=True)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=False)
@requests_mock.mock(kw="requests_mocker")
def test_handle_task_after_deploy_exception(
    mock1,
    mock2,
    mocked_requests_put,
    mocked_keepalived,
    l3_response,
    ipvs_output,
    overall_deploy_status,
    vss_deploy_status,
    status_code,
    reported_code,
    side_effect,
    **kwargs,
):
    mocked_requests_put().status_code = HTTPStatus.NO_CONTENT
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=json.dumps(l3_response), status_code=status_code)

    mocked_keepalived.return_value.erase_config = Mock(side_effect=side_effect)
    # To avoid waiting retries on request failure
    TestTasksHandler.send_task_status_to_l3.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1
    # There are three decorators wrapping wait_keepalived.
    # To access inner decorator (retry) parameters we need to do this
    Waiter.__call__.__closure__[0].cell_contents.__closure__[1].cell_contents.__closure__[1].cell_contents[
        "stop_max_attempt_number"
    ] = 1

    with patch("balancer_agent.operations.systems.ipvs.IPVS.get_services", return_value=ipvs_output):
        handler = TestTasksHandler(runtime_settings.runtime)
        handler.collect_tasks()

        with pytest.raises(TaskDeployError):
            handler.handle_task()
            mocked_keepalived.return_value.apply_config.assert_called_once()
            mocked_keepalived.return_value.erase_config.assert_called_once()

    if ipvs_output:
        # starting from 1, due to a mocking call 'mocked_requests_put().status_code = HTTPStatus.NO_CONTENT' above
        for args, kwargs in mocked_requests_put.call_args_list[1:]:
            url = args[0]
            assert any([("/tasks/" + str(task["id"]) + "/deployment-status" in url) for task in l3_response])
            report_data = json.loads(kwargs["data"])
            assert report_data["overall_deployment_status"] == overall_deploy_status
            assert not report_data["error"]["message"]
            assert report_data["error"]["code"] == reported_code
            assert report_data["ts"]
            assert report_data["vss"] == vss_deploy_status
            assert handler.headers == kwargs["headers"]


@pytest.mark.parametrize(
    "l3_response,status_code,apply_config_side_effect,restore_config_side_effect",
    [
        # Keepalived exception raised
        ([TASK_L4], HTTPStatus.OK, FailedToStopKeepalivedError("Could not stop keepalived"), None),
        # Unknown exception raised
        ([TASK_L4], HTTPStatus.OK, Exception("Something is wrong"), Exception("Something is wrong")),
    ],
)
@patch("balancer_agent.operations.balancer_configs.config_containers.VSDatasetBase.bindto", MOCK_BINDTO_IP)
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("balancer_agent.operations.systems.ipvs.IPVS.reset")
@patch("requests.put")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=True)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=False)
@requests_mock.mock(kw="requests_mocker")
def test_restore_config(
    mock1,
    mock2,
    mocked_requests_put,
    mocked_ipvs_reset,
    mocked_keepalived,
    l3_response,
    status_code,
    apply_config_side_effect,
    restore_config_side_effect,
    **kwargs,
):
    """
    Checking restore config call succeed after handle_task failure
    """
    mocked_requests_put().status_code = HTTPStatus.NO_CONTENT
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=json.dumps(l3_response), status_code=status_code)

    mocked_keepalived.return_value.apply_config = Mock(side_effect=apply_config_side_effect)
    mocked_keepalived.return_value.restore_config = Mock(side_effect=restore_config_side_effect)

    handler = TestTasksHandler(runtime_settings.runtime)
    handler.collect_tasks()

    with pytest.raises(TaskDeployError):
        assert not handler.handle_task()

    if not restore_config_side_effect:
        handler.restore_config()
        mocked_ipvs_reset.assert_called_once()
    else:
        with pytest.raises(RestoreConfigError):
            handler.restore_config()

        mocked_ipvs_reset.assert_not_called()

    mocked_keepalived.return_value.restore_config.assert_called_once()
