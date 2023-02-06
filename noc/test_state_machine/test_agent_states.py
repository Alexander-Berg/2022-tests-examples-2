import time
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

import pytest

from balancer_agent.agent import Agent, AgentStates, Machine
from balancer_agent.core.exceptions import (
    InvalidState,
    InvalidStateTransitionError,
    PollingSettingsError,
    RestoreConfigError,
    RollbackConfigError,
    TaskDeployError,
    TasksCollectionError,
)


@patch("balancer_agent.agent.SettingsCollector")
@patch("balancer_agent.agent.Machine")
@patch("balancer_agent.agent.Agent.action_failure")
@patch("balancer_agent.agent.Agent.action_rollback")
@patch("balancer_agent.agent.Agent.action_restore")
@patch("balancer_agent.agent.Agent.action_handle_tasks")
@patch("balancer_agent.agent.Agent.action_polling")
@patch("balancer_agent.agent.Agent.action_get_settings")
def test_agent_life_cycle_order(
    mock_action_get_settings,
    mock_action_polling,
    mock_action_handle_tasks,
    mock_action_restore,
    mock_action_rollback,
    mock_action_failure,
    mock_machine,
    mock_settings_collector,
):
    manager = Mock()
    manager.attach_mock(mock_action_get_settings, "mock_action_get_settings")
    manager.attach_mock(mock_action_polling, "mock_action_polling")
    manager.attach_mock(mock_action_handle_tasks, "mock_action_handle_tasks")
    manager.attach_mock(mock_action_restore, "mock_action_restore")
    manager.attach_mock(mock_action_rollback, "mock_action_rollback")
    manager.attach_mock(mock_action_failure, "mock_action_failure")

    agent = Agent(queue=Mock, can_run=Mock)
    agent.life_cycle()

    expected_calls = [
        call.mock_action_get_settings(),
        call.mock_action_polling(),
        call.mock_action_handle_tasks(),
        call.mock_action_restore(),
        call.mock_action_rollback(),
        call.mock_action_failure(),
    ]

    assert manager.mock_calls == expected_calls


@pytest.mark.parametrize(
    "init_state,settings_collected,agent_active,target_state",
    [
        # Check action has executed and state changes when the initial state is IDLE
        (AgentStates.IDLE, True, True, AgentStates.WAITING),
        # Check action has executed and state changes when the initial state is IDLE
        (AgentStates.IDLE, True, False, AgentStates.IDLE),
        # Check state doesn't change when the initial state is not IDLE
        (AgentStates.WAITING, True, True, AgentStates.WAITING),
    ],
)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector", new_callable=MagicMock)
def test_action_get_settings_success_cases(
    mock_settings_collector, mock_event, init_state, settings_collected, agent_active, target_state
):
    collect_settings = mock_settings_collector.return_value.collect_settings
    collect_settings.return_value = settings_collected
    agent_is_active = PropertyMock(return_value=agent_active)
    type(mock_settings_collector.return_value.runtime).is_active = agent_is_active

    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine.set_state(init_state)
    agent.action_get_settings()

    assert agent.machine.state == target_state

    if init_state == AgentStates.IDLE:
        collect_settings.assert_called_once()
        agent_is_active.assert_called_once_with()
    else:
        collect_settings.assert_not_called()
        agent_is_active.assert_not_called()

    if not agent_active:
        mock_event.return_value.wait.assert_called_once_with(
            timeout=mock_settings_collector.return_value.runtime.settings_polling_interval
        )
    else:
        mock_event.return_value.wait.assert_not_called()


@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_get_settings_failure_cases(mock_settings_collector, mock_event):
    mock_settings_collector_instance = mock_settings_collector.return_value
    mock_settings_collector_instance.collect_settings.side_effect = PollingSettingsError

    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine.set_state(AgentStates.IDLE)
    agent.action_get_settings()

    assert agent.machine.state == AgentStates.IDLE


@pytest.mark.parametrize(
    "init_state,time_to_update_settings,has_tasks_in_queue,target_state",
    [
        # Agent has to re-collect settings due to timout
        (AgentStates.WAITING, True, None, AgentStates.IDLE),
        # No tasks collected
        (AgentStates.WAITING, False, False, AgentStates.WAITING),
        # Collected tasks to deploy
        (AgentStates.WAITING, False, True, AgentStates.ACTIVE),
        # State doen't match action
        (AgentStates.IDLE, True, None, AgentStates.IDLE),
    ],
)
@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector", new_callable=MagicMock)
def test_action_polling_success_cases(
    mock_settings_collector,
    mock_event,
    mock_get_task_handler,
    init_state,
    time_to_update_settings,
    has_tasks_in_queue,
    target_state,
):
    has_tasks_in_queue = PropertyMock(return_value=has_tasks_in_queue)
    type(mock_get_task_handler.return_value).has_tasks_in_queue = has_tasks_in_queue
    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine.set_state(init_state)
    agent._is_time_to_update_settings = lambda: time_to_update_settings
    agent.action_polling()

    assert agent.machine.state == target_state

    if not time_to_update_settings:
        mock_get_task_handler.return_value.collect_tasks.assert_called_once_with()
        has_tasks_in_queue.assert_called_once_with()

    if agent.machine.state == AgentStates.WAITING:
        mock_event.return_value.wait.assert_called_once_with(
            timeout=mock_settings_collector.return_value.runtime.tasks_polling_interval
        )


@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_polling_failure_cases(mock_settings_collector, mock_event, mock_get_task_handler):
    mock_get_task_handler_instance = mock_get_task_handler.return_value
    mock_get_task_handler_instance.collect_tasks.side_effect = TasksCollectionError

    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine.set_state(AgentStates.WAITING)
    agent._is_time_to_update_settings = lambda: False
    agent.action_polling()

    assert agent.machine.state == AgentStates.IDLE


@pytest.mark.parametrize(
    "init_state,has_tasks_in_queue,target_state",
    [
        # No tasks in queue
        (AgentStates.ACTIVE, False, AgentStates.WAITING),
        # Agent has tasks in queue
        (AgentStates.ACTIVE, True, AgentStates.ACTIVE),
        # State doesn't match action
        (AgentStates.WAITING, None, AgentStates.WAITING),
    ],
)
@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_handle_tasks_success_cases(
    mock_settings_collector, mock_event, mock_get_task_handler, init_state, has_tasks_in_queue, target_state
):
    has_tasks_in_queue = PropertyMock(return_value=has_tasks_in_queue)
    type(mock_get_task_handler.return_value).has_tasks_in_queue = has_tasks_in_queue
    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine._state = init_state
    agent.action_handle_tasks()

    assert agent.machine.state == target_state

    if init_state == AgentStates.ACTIVE:
        mock_get_task_handler.return_value.handle_task.assert_called_once_with()


@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_handle_tasks_failure_cases(mock_settings_collector, mock_event, mock_get_task_handler):
    mock_get_task_handler_instance = mock_get_task_handler.return_value
    mock_get_task_handler_instance.handle_task.side_effect = TaskDeployError

    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine._state = AgentStates.ACTIVE
    agent.action_handle_tasks()

    assert agent.machine.state == AgentStates.RESTORE


@pytest.mark.parametrize(
    "init_state,target_state",
    [
        # Config restoration succeed
        (AgentStates.RESTORE, AgentStates.ROLLBACK),
        # State doesn't match action
        (AgentStates.ACTIVE, AgentStates.ACTIVE),
    ],
)
@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_restore_success_cases(
    mock_settings_collector, mock_event, mock_get_task_handler, init_state, target_state
):
    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine._state = init_state
    agent.action_restore()

    assert agent.machine.state == target_state

    if init_state == AgentStates.RESTORE:
        mock_get_task_handler.return_value.restore_config.assert_called_once_with()


@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_restore_failure_cases(mock_settings_collector, mock_event, mock_get_task_handler):
    mock_get_task_handler_instance = mock_get_task_handler.return_value
    mock_get_task_handler_instance.restore_config.side_effect = RestoreConfigError

    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine._state = AgentStates.RESTORE
    agent.action_restore()

    assert agent.machine.state == AgentStates.FAILURE


@pytest.mark.parametrize(
    "init_state,has_tasks_in_queue,target_state",
    [
        # No more tasks in queue
        (AgentStates.ROLLBACK, False, AgentStates.WAITING),
        # # Agent has tasks in queue after rollback
        (AgentStates.ROLLBACK, True, AgentStates.ACTIVE),
        # State doesn't match action
        (AgentStates.RESTORE, None, AgentStates.RESTORE),
    ],
)
@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_rollback_success_cases(
    mock_settings_collector, mock_event, mock_get_task_handler, init_state, has_tasks_in_queue, target_state
):
    has_tasks_in_queue = PropertyMock(return_value=has_tasks_in_queue)
    type(mock_get_task_handler.return_value).has_tasks_in_queue = has_tasks_in_queue
    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine._state = init_state
    agent.action_rollback()

    assert agent.machine.state == target_state

    if init_state == AgentStates.ROLLBACK:
        mock_get_task_handler.return_value.rollback_config.assert_called_once_with()


@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_rollback_failure_cases(mock_settings_collector, mock_event, mock_get_task_handler):
    mock_get_task_handler_instance = mock_get_task_handler.return_value
    mock_get_task_handler_instance.rollback_config.side_effect = RollbackConfigError

    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine._state = AgentStates.ROLLBACK
    agent.action_rollback()

    assert agent.machine.state == AgentStates.FAILURE


@pytest.mark.parametrize(
    "init_state,target_state",
    [
        # Agent reports failure and stays in failure state
        (AgentStates.FAILURE, AgentStates.FAILURE),
        # State doesn't match action
        (AgentStates.ROLLBACK, AgentStates.ROLLBACK),
    ],
)
@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector", new_callable=MagicMock)
def test_action_failure_success_cases(
    mock_settings_collector, mock_event, mock_get_task_handler, init_state, target_state
):
    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine._state = init_state
    agent.action_failure()

    assert agent.machine.state == target_state

    if init_state == AgentStates.FAILURE:
        mock_event.return_value.wait.assert_called_once_with(
            timeout=mock_settings_collector.return_value.runtime.signal_failure_interval
        )
        mock_get_task_handler.return_value.send_rollback_status_to_l3.assert_called_once_with()


@patch("balancer_agent.agent.get_task_handler", new_callable=MagicMock)
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_action_failure_failure_cases(mock_settings_collector, mock_event, mock_get_task_handler):
    mock_get_task_handler_instance = mock_get_task_handler.return_value
    mock_get_task_handler_instance.send_rollback_status_to_l3.side_effect = Exception

    agent = Agent(queue=Mock(), can_run=Mock)
    agent.machine._state = AgentStates.FAILURE
    agent.action_failure()

    assert agent.machine.state == AgentStates.FAILURE


@patch("balancer_agent.agent.get_task_handler")
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector")
def test_agent_loop_stops(
    mock_settings_collector,
    mock_event,
    mock_get_task_handler,
):
    def stop_agent(agent):
        agent.can_run.is_set = lambda: False

    agent = Agent(queue=Mock(), can_run=Mock())

    with patch("balancer_agent.agent.Agent.life_cycle", new=lambda *args: stop_agent(agent)):
        assert not (agent.agent_loop())
        assert agent.can_run.is_set() is False


@pytest.mark.parametrize(
    "polling_interval,expected_result",
    [
        # 1 second timout not reached, settings update not required
        (1, False),
        # 0 second interval triggers time to update settings to True
        (0, True),
    ],
)
@patch("balancer_agent.agent.get_task_handler")
@patch("balancer_agent.agent.Event")
@patch("balancer_agent.agent.SettingsCollector", new_callable=MagicMock)
def test__is_time_to_update_settings(
    mock_settings_collector, mock_event, mock_get_task_handler, polling_interval, expected_result
):
    collect_time = PropertyMock(return_value=time.monotonic())
    type(mock_settings_collector.return_value.runtime).collect_time = collect_time

    settings_polling_interval = PropertyMock(return_value=polling_interval)
    type(mock_settings_collector.return_value.runtime).settings_polling_interval = settings_polling_interval

    agent = Agent(queue=Mock(), can_run=Mock())
    assert agent._is_time_to_update_settings() == expected_result


def test_machine_transitions():
    for initial_state in Machine.TRANSITIONS.keys():
        for target_state in Machine.TRANSITIONS.keys():
            machine = Machine(queue=Mock(), initial_state=initial_state)

            if target_state in Machine.TRANSITIONS[initial_state]:
                assert not machine.set_state(target_state)
            else:
                try:
                    machine.set_state(target_state)
                except InvalidStateTransitionError:
                    assert True


def test_machine_unknown_transition():
    machine = Machine(queue=Mock())
    try:
        machine.set_state("unknown")
    except InvalidState:
        assert True
