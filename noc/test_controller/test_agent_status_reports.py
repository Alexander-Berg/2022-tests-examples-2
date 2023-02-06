import json
import re
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
import requests_mock
from requests.exceptions import ConnectionError

from balancer_agent.app import main
from balancer_agent.manager import Controller

AGENT_API_HOSTS = "https://host.*"
HOST_A = "host_a"
HOST_B = "host_b"
ACTIVE_STATE = "ACTIVE"
L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]
MOCK_COLLECTED_CONFIG = {
    "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
    "polling_interval": 0.01,
    "agent_mode": ACTIVE_STATE,
    "generator_version": 1,
}


class CollectorResponse:
    status_code = HTTPStatus.NO_CONTENT


class MocktTasksHandler:
    has_tasks_in_queue = False

    @staticmethod
    def collect_tasks():
        return True


@patch("balancer_agent.operations.systems.ipvs.IPVS")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("balancer_agent.app.WorkerThread.is_alive", side_effect=[True, True, Exception("Stop test")])
@patch("requests.post", return_value=CollectorResponse)
@patch("balancer_agent.operations.tasks.handlers.ipvs_test_tasks.TestTasksHandler.collect_tasks")
@patch("balancer_agent.agent.get_task_handler", return_value=MocktTasksHandler)
@patch("balancer_agent.operations.tasks.handlers.ipvs_test_tasks.TestTasksHandler.has_tasks_in_queue", False)
@patch("balancer_agent.agent.SettingsCollector._collect_settings_callback", lambda *args: MOCK_COLLECTED_CONFIG)
@patch("balancer_agent.operations.settings.TaskPollingIntervalCalculator.get_jitter", return_value=0)
@patch("balancer_agent.app.init_file_tracking_worker", Mock)
@patch("balancer_agent.app.init_agent", Mock)
@patch("balancer_agent.operations.settings.TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS", 0)
@requests_mock.mock(kw="requests_mocker")
def test_tasks_collection_tasks_not_collected(
    mocked_get_jitter,
    mocked_get_task_handler,
    mocked_collect_tasks,
    mock_requests_post,
    mock_worker_is_alive,
    mocked_keepalived,
    mocked_ipvs,
    **kwargs,
):
    """
    Check that the status has collected by every agent tracking cycle
    and status timestamp grows
    """
    requests_mocker = kwargs["requests_mocker"]
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=json.dumps([]), status_code=HTTPStatus.NO_CONTENT)

    with pytest.raises(Exception):
        main()

    first_report = json.loads(mock_requests_post.call_args_list[0][1]["data"])
    second_report = json.loads(mock_requests_post.call_args_list[1][1]["data"])

    assert first_report["counters"]["IDLE"] > 0
    assert second_report["counters"]["IDLE"] > 0
    assert first_report["counters"]["WAITING"] > 0
    assert second_report["counters"]["WAITING"] > 0
    # The changed_at timestamp is in seconds, but worker_tracking_seconds timer is 0.01 to speed up the tests
    # so it's expected to have the same time in seconds for both tracking cycles
    assert first_report["changed_at"] <= second_report["changed_at"]


@patch("balancer_agent.operations.systems.ipvs.IPVS")
@patch("balancer_agent.operations.systems.keepalived.KeepalivedTest")
@patch("balancer_agent.app.WorkerThread.is_alive", side_effect=[True, True, Exception("Stop test")])
@patch("requests.post", side_effect=ConnectionError)
@patch("balancer_agent.operations.tasks.handlers.ipvs_test_tasks.TestTasksHandler.collect_tasks")
@patch("balancer_agent.agent.get_task_handler", return_value=MocktTasksHandler)
@patch("balancer_agent.operations.tasks.handlers.ipvs_test_tasks.TestTasksHandler.has_tasks_in_queue", False)
@patch("balancer_agent.agent.SettingsCollector._collect_settings_callback", lambda *args: MOCK_COLLECTED_CONFIG)
@patch("balancer_agent.operations.settings.TaskPollingIntervalCalculator.get_jitter", return_value=0)
@patch("balancer_agent.operations.settings.TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS", 0)
@requests_mock.mock(kw="requests_mocker")
def test_manager_exception(
    mocked_get_jitter,
    mocked_get_task_handler,
    mocked_collect_tasks,
    mock_requests_post,
    mock_worker_is_alive,
    mocked_keepalived,
    mocked_ipvs,
    **kwargs,
):
    """
    Check unavailable L3 doesn't break agent lifecysle
    """
    Controller.send_report.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    requests_mocker = kwargs["requests_mocker"]
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=json.dumps([]), status_code=HTTPStatus.NO_CONTENT)

    with pytest.raises(Exception):
        main()

    # Check that exception was assigned and thrown
    assert mock_requests_post.side_effect == ConnectionError
    mock_requests_post.call_count > 1
