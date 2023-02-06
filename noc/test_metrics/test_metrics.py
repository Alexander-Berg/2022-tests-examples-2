import random
from time import sleep
from unittest.mock import patch

import pytest
from tvmauth import TvmClientStatus

from balancer_agent.core.metrics import (
    MetricsReporter,
    RequestAuthProvider,
    SensorNameLabel,
    ThrottledPushApiReporter,
    TransitionTimeReporter,
)
from balancer_agent.core.tvm import TVMClient, TvmEnabledStatus, TvmRunningStatus

ERROR = KeyError


def foo_with_error():
    raise ERROR


SLEEP_TIME = 0.1


def foo_sleep():
    sleep(SLEEP_TIME)


def foo_sleep_with_error():
    foo_sleep()
    foo_with_error()


class MockedSession:
    verify = True


class StateName:
    def __init__(self, target):
        self._name = target

    @property
    def name(self):
        return str(self._name)


class FakeMachine:
    def set_state(self, target):
        self._state = StateName(target)

    @property
    def state(self):
        return self._state


class FakeTvmClient:
    TVM_LAST_ERROR = "OK"

    status = TVMClient.STATUS(
        TvmEnabledStatus.ENABLED.value, TvmRunningStatus.RUNNING.value, TvmClientStatus.Ok.value, TVM_LAST_ERROR
    )


@patch("balancer_agent.core.metrics.BasePushApiReporter.set_value")
def test_push_errors_sync_error_happened(mocked_set_value_sync):
    METRICS_REPORTER = MetricsReporter()

    with pytest.raises(ERROR):
        decorated = METRICS_REPORTER.push_errors()(foo_with_error)
        decorated()

    mocked_set_value_sync.assert_called_once_with(METRICS_REPORTER, ERROR.__name__, 1, labels={"Level": "error"})


@patch("balancer_agent.core.metrics.BasePushApiReporter.set_value")
def test_push_errors_sync_error_not_happened(mocked_set_value_sync):
    METRICS_REPORTER = MetricsReporter()

    decorated = METRICS_REPORTER.push_errors()(lambda: "No errors")
    decorated()

    mocked_set_value_sync.assert_not_called()


@patch("balancer_agent.core.metrics.ThrottledPushApiReporter.set_value")
def test_push_execution_time_error_not_happened(mocked_set_value_sync):
    METRICS_REPORTER = MetricsReporter()

    decorated = METRICS_REPORTER.push_execution_time(foo_sleep)
    decorated()

    call_foo_name, call_sleep_time = mocked_set_value_sync.call_args[0]
    assert call_foo_name == foo_sleep.__name__
    assert call_sleep_time >= SLEEP_TIME

    assert mocked_set_value_sync.call_args[1] == {"labels": {"exec_time": "exec_time"}}


@patch("balancer_agent.core.metrics.ThrottledPushApiReporter.set_value")
def test_push_execution_time_error_happened(mocked_set_value_sync):
    METRICS_REPORTER = MetricsReporter()

    with pytest.raises(ERROR):
        decorated = METRICS_REPORTER.push_execution_time(foo_sleep_with_error)
        decorated()

    call_foo_name, call_sleep_time = mocked_set_value_sync.call_args[0]

    assert call_foo_name == foo_sleep_with_error.__name__
    assert call_sleep_time >= SLEEP_TIME

    assert mocked_set_value_sync.call_args[1] == {"labels": {"exec_time": "exec_time"}}


@patch("balancer_agent.core.metrics.ThrottledPushApiReporter.__init__")
def test_init_metrics_reporter(mocked_base_reporter):
    ThrottledPushApiReporter._session = MockedSession

    MetricsReporter().start_client()

    assert mocked_base_reporter.call_args[0] == (
        MetricsReporter.METRICS_PUSH_INTERVAL_SECONDS,
        *MetricsReporter.L3AGENT_SOLOMON_IDS,
    )

    assert mocked_base_reporter.call_args[1]["url"] == MetricsReporter.SOLOMON_PROD_URL
    assert mocked_base_reporter.call_args[1]["timeout"] == MetricsReporter.SOLOMON_RESPONSE_TIMEOUT_SECONDS
    assert mocked_base_reporter.call_args[1]["common_labels"] == MetricsReporter.COMMON_LABELS
    assert mocked_base_reporter.call_args[1]["sensor_name_label"] == SensorNameLabel.METRIC
    assert isinstance(mocked_base_reporter.call_args[1]["request_auth_provider"], RequestAuthProvider)


@patch("balancer_agent.core.metrics.ThrottledPushApiReporter.set_value")
def test_push_time_delta_between_state_transitions(mocked_set_value):
    TRANSITION_TIME_REPORTER = TransitionTimeReporter()

    # to avoid waiting for the default interval
    TransitionTimeReporter.METRICS_COLLECTION_INTERVAL = 0.2

    decorated = TRANSITION_TIME_REPORTER.push_time_delta_between_state_transitions(FakeMachine.set_state)
    machine = FakeMachine()

    # First transition time cannot be measured, because there was no state before
    # So we pre-set the first state here
    decorated(machine, 0)

    transition_time_total = 0

    for i in range(1, 11):
        transition_time = random.uniform(0.015, 0.03)
        sleep(transition_time)
        transition_time_total += transition_time
        previous_state = machine.state

        decorated(machine, random.randint(1, 100))

        if transition_time_total > TransitionTimeReporter.METRICS_COLLECTION_INTERVAL:
            state, measured_transition_time = mocked_set_value.call_args[0]
            assert state == previous_state.name + "<->" + machine.state.name
            assert transition_time * 2 >= measured_transition_time >= round(transition_time / 2, 3)

            transition_time = 0


@patch("balancer_agent.core.metrics.ThrottledPushApiReporter.set_value")
def test_push_tvm_status(mocked_set_value):
    METRICS_REPORTER = MetricsReporter()
    decorated = METRICS_REPORTER.push_tvm_status(FakeTvmClient)(lambda: "dummy")
    decorated()

    mocked_set_value.assert_any_call("tvm_enabled", FakeTvmClient.status.enabled)
    mocked_set_value.assert_any_call("tvm_alive", FakeTvmClient.status.alive)
    mocked_set_value.assert_any_call("tvm_current_status", FakeTvmClient.status.status)


def test_metric_status():
    METRICS_REPORTER = MetricsReporter()
    METRICS_REPORTER.set_exception(RuntimeError("test exception"))

    with patch("balancer_agent.core.metrics.ThrottledPushApiReporter.set_value", return_value=lambda: None):
        METRICS_REPORTER.set_transition("WAITING<->IDLE", 0)
        METRICS_REPORTER.set_execution("collect_settings", 0.01)

        METRICS_REPORTER.set_tvm("tvm_enabled", 0)
        METRICS_REPORTER.set_tvm("tvm_current_status", 1)

    for metric, value in {
        "errors": 1,
        "exceptions": {"RuntimeError": 1},
        "transitions": {"WAITING<->IDLE": 0},
        "executions": {"collect_settings": 0.01},
        "tvm": {
            "tvm_enabled": 0,
            "tvm_current_status": 1,
        },
    }.items():
        assert METRICS_REPORTER.status[metric] == value

    assert METRICS_REPORTER.status["created_at"] > 0
    assert METRICS_REPORTER.status["updated_at"] > METRICS_REPORTER.status["created_at"]
