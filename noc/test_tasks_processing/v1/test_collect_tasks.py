import json
import re
from copy import deepcopy
from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests_mock

from balancer_agent.core.exceptions import PollingTasksError
from balancer_agent.core.status_codes import ServiceErrorCodes
from balancer_agent.definitions import TEST_MODE
from balancer_agent.operations.balancer_configs.config_containers import BalancerConfigState, VSDatasetBase
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.tasks.handlers.ipvs_test_tasks import TestTasksHandler

from .static.tasks_from_api import TASK_DYNAMIC_WEIGHT, TASK_FWMARK, TASK_L4

from typing import Dict

HOST_A = "host_a"
HOST_B = "host_b"
ACTIVE_STATE = "ACTIVE"
L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]

MOCK_COLLECTED_CONFIG = {
    "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
    "polling_interval": 300,
    "agent_mode": ACTIVE_STATE,
    "generator_version": 1,
}

AGENT_API_HOSTS = "https://host.*"

TASK_L4_INVALID = deepcopy(TASK_L4)
TASK_L4_INVALID["id"] = "1"

TASK_FWMARK_INVALID: Dict = deepcopy(TASK_FWMARK)
TASK_FWMARK_INVALID["data"]["vss"] = []


@pytest.mark.parametrize(
    "l3_response,error_flag,status_code,raises,expected",
    [
        (json.dumps([TASK_L4]), True, None, ValueError, PollingTasksError),
        (json.dumps({}), True, HTTPStatus.INTERNAL_SERVER_ERROR, None, PollingTasksError),
        (json.dumps({}), False, HTTPStatus.NOT_FOUND, None, False),
        ("not json", True, HTTPStatus.OK, None, PollingTasksError),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=True)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=False)
@requests_mock.mock(kw="requests_mocker")
def test_tasks_collection_tasks_not_collected(
    mock1, mock2, mocked_keepalived, mocked_ipvs, l3_response, error_flag, status_code, raises, expected, **kwargs
):
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    # To avoid waiting 7 retries on request failure
    TestTasksHandler.collect_tasks.__closure__[1].cell_contents.__closure__[0].cell_contents.__closure__[
        1
    ].cell_contents["stop_max_attempt_number"] = 1
    if error_flag and not status_code:
        requests_mocker.post(re.compile(AGENT_API_HOSTS), exc=raises)
        with pytest.raises(expected):
            TestTasksHandler(runtime_settings.runtime).collect_tasks()
    elif error_flag and status_code:
        requests_mocker.post(re.compile(AGENT_API_HOSTS), text=l3_response, status_code=status_code)
        with pytest.raises(expected):
            TestTasksHandler(runtime_settings.runtime).collect_tasks()
    else:
        requests_mocker.post(re.compile(AGENT_API_HOSTS), text=l3_response, status_code=status_code)
        assert TestTasksHandler(runtime_settings.runtime).collect_tasks() == expected


@pytest.mark.parametrize(
    "l3_response,status_code",
    [
        # Valid task L4
        (json.dumps([TASK_L4]), HTTPStatus.OK),
        # Valid task FWMARK
        (json.dumps([TASK_FWMARK]), HTTPStatus.OK),
        # Valid task FWMARK + L4 + DYNAMIC_WEIGHT
        (json.dumps([TASK_L4, TASK_FWMARK, TASK_DYNAMIC_WEIGHT]), HTTPStatus.OK),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@requests_mock.mock(kw="requests_mocker")
def test_tasks_collection_valid_tasks_collected(mocked_keepalived, mocked_ipvs, l3_response, status_code, **kwargs):
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    # To avoid waiting 7 retries on request failure
    TestTasksHandler.collect_tasks.__closure__[1].cell_contents.__closure__[0].cell_contents.__closure__[
        1
    ].cell_contents["stop_max_attempt_number"] = 1
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=l3_response, status_code=status_code)

    handler = TestTasksHandler(runtime_settings.runtime)
    handler.collect_tasks()
    assert handler.tasks_queue.amount == len(json.loads(l3_response))
    assert not handler.tasks_queue.invalid_tasks


@pytest.mark.parametrize(
    "valid_tasks,invalid_tasks",
    [
        # Invalid task
        (
            [],
            [TASK_L4_INVALID],
        ),
        # Invalid tasks
        (
            [],
            [TASK_L4_INVALID, TASK_FWMARK_INVALID],
        ),
        # Valid and invalid tasks
        (
            [TASK_L4, TASK_DYNAMIC_WEIGHT],
            [TASK_L4_INVALID, TASK_FWMARK_INVALID],
        ),
        # Empty tasks
        (
            [],
            [],
        ),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("balancer_agent.operations.tasks.handlers.ipvs_test_tasks.TestTasksHandler.send_invalid_task_status_to_l3")
@requests_mock.mock(kw="requests_mocker")
def test_tasks_collection_invalid_tasks_collected(
    mocked_send_invalid_task_status_to_l3, mocked_keepalived, mocked_ipvs, valid_tasks, invalid_tasks, **kwargs
):
    all_tasks = json.dumps(valid_tasks + invalid_tasks)
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    # To avoid waiting 7 retries on request failure
    TestTasksHandler.collect_tasks.__closure__[1].cell_contents.__closure__[0].cell_contents.__closure__[
        1
    ].cell_contents["stop_max_attempt_number"] = 1
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=all_tasks)
    handler = TestTasksHandler(runtime_settings.runtime)
    handler.collect_tasks()

    assert handler.tasks_queue.amount == len(valid_tasks)
    assert len(handler.tasks_queue.invalid_tasks) == len(invalid_tasks)


@pytest.mark.parametrize(
    "valid_tasks,invalid_tasks",
    [
        # Invalid task
        (
            [TASK_L4],
            [TASK_L4_INVALID],
        ),
        # Invalid tasks
        (
            [],
            [TASK_L4_INVALID, TASK_FWMARK_INVALID],
        ),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("requests.put")
@requests_mock.mock(kw="requests_mocker")
def test_invalid_task_status_report(
    mocked_requests_put, mocked_keepalived, mocked_ipvs, valid_tasks, invalid_tasks, **kwargs
):
    all_tasks = json.dumps(valid_tasks + invalid_tasks)
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    # To avoid waiting retries on request failure
    TestTasksHandler.send_invalid_task_status_to_l3.__closure__[1].cell_contents["stop_max_attempt_number"] = 1
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=all_tasks)
    handler = TestTasksHandler(runtime_settings.runtime)
    handler.collect_tasks()

    for args, kwargs in mocked_requests_put.call_args_list:
        url = args[0]
        assert any([("/tasks/" + str(task["id"]) + "/deployment-status" in url) for task in invalid_tasks])
        report_data = json.loads(kwargs["data"])
        assert report_data["overall_deployment_status"] == BalancerConfigState.FAILURE_STATUS
        assert report_data["error"]["message"]
        assert report_data["error"]["code"] == ServiceErrorCodes.TASK_VALIDATION_ERROR.value
        assert report_data["ts"]
        assert not report_data["vss"]

        headers = kwargs["headers"]
        assert handler.headers == headers

    assert mocked_requests_put.call_count == len(invalid_tasks)


@pytest.mark.parametrize(
    "valid_tasks,invalid_tasks",
    [
        # One valid and one invalid task
        (
            [TASK_L4],
            [TASK_L4_INVALID],
        ),
        # No valid tasks
        (
            [],
            [TASK_L4_INVALID, TASK_FWMARK_INVALID],
        ),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("requests.put")
@requests_mock.mock(kw="requests_mocker")
def test_cannot_send_invalid_task_status_report(
    mocked_requests_put, mocked_keepalived, mocked_ipvs, valid_tasks, invalid_tasks, **kwargs
):
    """
    Check that tasks handling doesn't stop if one task is invalid and its status cannot be delivered
    """
    mocked_requests_put().status_code = HTTPStatus.BAD_REQUEST
    all_tasks = json.dumps(invalid_tasks + valid_tasks)
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    TestTasksHandler.send_invalid_task_status_to_l3.__closure__[1].cell_contents["stop_max_attempt_number"] = 1
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=all_tasks)
    handler = TestTasksHandler(runtime_settings.runtime)

    assert handler.collect_tasks() == len(valid_tasks)
    assert handler.tasks_queue.amount == len(valid_tasks)
    assert len(handler.tasks_queue.invalid_tasks) == len(invalid_tasks)


@pytest.mark.parametrize(
    "valid_tasks, agent_mode",
    [
        ([TASK_L4, TASK_FWMARK, TASK_DYNAMIC_WEIGHT], TEST_MODE),
        ([TASK_L4, TASK_FWMARK, TASK_DYNAMIC_WEIGHT], None),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@requests_mock.mock(kw="requests_mocker")
def test_task_for_testing_changes_appropriate_config_fields(
    mocked_keepalived, mocked_ipvs, valid_tasks, agent_mode, **kwargs
):
    """
    Check that when the agent is in the test/not test mode,
    the announce setting and the dynamic_weight_coefficient
    are set appropriately.
    """
    with patch("balancer_agent.operations.balancer_configs.config_containers.AGENT_MODE", agent_mode):
        all_tasks = json.dumps(valid_tasks)
        requests_mocker = kwargs["requests_mocker"]
        runtime_settings = SettingsCollector()
        SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
        runtime_settings.collect_settings()
        requests_mocker.post(re.compile(AGENT_API_HOSTS), text=all_tasks)
        handler = TestTasksHandler(runtime_settings.runtime)
        handler.collect_tasks()

        task = handler.tasks_queue.get_next_task()

        if agent_mode == TEST_MODE:
            for vs in task.config.body.vss:
                assert not vs.announce
                assert vs.dynamic_weight_coefficient == VSDatasetBase.DYNAMIC_WEIGHT_TEST_RATIO
        else:
            for vs in task.config.body.vss:
                assert vs.announce
                assert vs.dynamic_weight_coefficient != VSDatasetBase.DYNAMIC_WEIGHT_TEST_RATIO
