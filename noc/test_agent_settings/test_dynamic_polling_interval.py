import math
from time import sleep
from unittest.mock import patch

import pytest

from balancer_agent.operations.settings import TaskPollingIntervalCalculator

INTERVAL_0 = 0.01
INTERVAL_1 = 4
INTERVAL_2 = 7
INTERVAL_3 = 9

ZERO_TASKS = 0
ONE_TASK = 1
TWO_TASKS = 2
MANY_TASKS = 100


GET_NEW_TASKS_HAVE_CHANGES_IN_SETTINGS = [
    (ZERO_TASKS, INTERVAL_1, INTERVAL_1),
    (ONE_TASK, INTERVAL_2, INTERVAL_1),
    (ONE_TASK, INTERVAL_1, INTERVAL_2),
    (ONE_TASK, INTERVAL_1, INTERVAL_1),
    # interval has not changed and no tasks arrived so interval*=1/2
    (ZERO_TASKS, INTERVAL_3, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS),
    (ZERO_TASKS, INTERVAL_1, INTERVAL_3),
]


GET_NEW_TASKS_NO_CHANGES_IN_SETTINGS = [
    (ZERO_TASKS, INTERVAL_1, INTERVAL_1),
    (ONE_TASK, INTERVAL_1, INTERVAL_1),
    (ONE_TASK, INTERVAL_1, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS),
    (ONE_TASK, INTERVAL_1, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS),
    (ZERO_TASKS, INTERVAL_1, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS),
    (ZERO_TASKS, INTERVAL_1, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS * math.e),
    (ZERO_TASKS, INTERVAL_1, INTERVAL_1),
    (TWO_TASKS, INTERVAL_1, INTERVAL_1),
    (ZERO_TASKS, INTERVAL_1, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS),
    (ZERO_TASKS, INTERVAL_1, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS * math.e),
    (MANY_TASKS, INTERVAL_3, INTERVAL_1),
    (MANY_TASKS, INTERVAL_3, INTERVAL_3),
    (ZERO_TASKS, INTERVAL_3, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS),
    (ZERO_TASKS, INTERVAL_3, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS * math.e),
    (ZERO_TASKS, INTERVAL_3, TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS * math.e * math.e),
    (ZERO_TASKS, INTERVAL_3, INTERVAL_3),
]


@TaskPollingIntervalCalculator.tasks_by_time
def mock_tasks_handler(amount_of_tasks):
    return amount_of_tasks


@TaskPollingIntervalCalculator.tasks_by_time
def mock_tasks_handler_error(amount_of_tasks):
    raise Exception("Test TaskPollingIntervalCalculator")


def mock_action_polling(amount_of_tasks):
    sleep(TaskPollingIntervalCalculator.get_updated_interval() / 10000)
    mock_tasks_handler(amount_of_tasks)


def mock_action_polling_error(amount_of_tasks):
    sleep(abs(TaskPollingIntervalCalculator.get_updated_interval()) / 10000)
    mock_tasks_handler_error(amount_of_tasks)


def mock_action_polling_no_task_handling(amount_of_tasks):
    sleep(TaskPollingIntervalCalculator.get_updated_interval() / 10000)


def mock_get_settings(reference_polling_interval):
    TaskPollingIntervalCalculator.set_reference_interval(reference_polling_interval)


@patch("balancer_agent.operations.settings.TaskPollingIntervalCalculator.get_jitter", return_value=0)
def test_dynamic_polling_interval_no_tasks_no_changes_in_settings(mocked_get_jitter):
    TaskPollingIntervalCalculator.start_counter(INTERVAL_1)

    for i in range(10):
        mock_action_polling(ZERO_TASKS)
        assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_1
        mock_get_settings(INTERVAL_1)
        assert TaskPollingIntervalCalculator.calculated_interval == TaskPollingIntervalCalculator.reference_interval


@patch("balancer_agent.operations.settings.TaskPollingIntervalCalculator.get_jitter", return_value=0)
def test_dynamic_polling_interval_below_minimal(mocked_get_jitter):
    TaskPollingIntervalCalculator.start_counter(INTERVAL_1)
    mock_action_polling(ZERO_TASKS)
    mock_get_settings(INTERVAL_0)

    for i in range(10):
        mock_action_polling(ZERO_TASKS)
        mock_get_settings(INTERVAL_0)
        assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_1


@pytest.mark.parametrize(
    "params",
    [
        GET_NEW_TASKS_HAVE_CHANGES_IN_SETTINGS,
        GET_NEW_TASKS_NO_CHANGES_IN_SETTINGS,
    ],
)
@patch("balancer_agent.operations.settings.TaskPollingIntervalCalculator.get_jitter", return_value=0)
def test_dynamic_polling_interval(mocked_get_jitter, params):
    TaskPollingIntervalCalculator.start_counter(INTERVAL_1)

    for amount_of_tasks, reference_interval, expected_interval in params:

        mock_action_polling(amount_of_tasks)
        mock_get_settings(reference_interval)

        assert TaskPollingIntervalCalculator.calculated_interval.timer == expected_interval


@patch("balancer_agent.operations.settings.TaskPollingIntervalCalculator.get_jitter", return_value=0)
def test_dynamic_polling_interval_calling_get_updated_interval_without_tasks_by_time(mocked_get_jitter):
    TaskPollingIntervalCalculator.start_counter(INTERVAL_1)
    mock_action_polling_no_task_handling(ZERO_TASKS)
    mock_get_settings(INTERVAL_1)

    mock_action_polling_no_task_handling(ZERO_TASKS)
    mock_get_settings(INTERVAL_2)
    mock_action_polling_no_task_handling(ZERO_TASKS)
    assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_2
    mock_action_polling_no_task_handling(ZERO_TASKS)
    assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_2
    mock_action_polling_no_task_handling(ZERO_TASKS)
    assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_2

    mock_get_settings(INTERVAL_1)
    mock_action_polling_no_task_handling(ZERO_TASKS)
    assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_1
    mock_action_polling_no_task_handling(ZERO_TASKS)
    assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_1
    mock_action_polling_no_task_handling(ZERO_TASKS)
    assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_1

    mock_get_settings(INTERVAL_1)
    mock_action_polling(ONE_TASK)
    assert TaskPollingIntervalCalculator.calculated_interval.timer == INTERVAL_1
    mock_action_polling(ZERO_TASKS)
    assert (
        TaskPollingIntervalCalculator.calculated_interval.timer
        == TaskPollingIntervalCalculator.MINIMAL_POLLING_INTERVAL_SECONDS
    )
