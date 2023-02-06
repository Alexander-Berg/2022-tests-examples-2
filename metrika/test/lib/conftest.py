import pytest

import metrika.admin.python.cms.test.lib.mock_agent_api as mock_agent_api
import metrika.admin.python.cms.test.lib.mock_cluster_api as mock_cluster_api
import metrika.admin.python.cms.test.lib.mock_internal_api as mock_internal_api
import metrika.admin.python.cms.test.lib.mock_walle_api as mock_walle_api

from .steps import Steps, InputSteps, OutputSteps, Assert


@pytest.fixture()
def agent_api_mock():
    return mock_agent_api.MockAgentApi()


@pytest.fixture()
def cluster_api_mock():
    return mock_cluster_api.MockClusterApi()


@pytest.fixture()
def internal_api_mock():
    return mock_internal_api.MockInternalApi()


@pytest.fixture()
def walle_api_mock():
    return mock_walle_api.MockWalleApi()


@pytest.fixture()
def output_steps(monkeypatch, queue, internal_api_mock, cluster_api_mock, agent_api_mock, walle_api_mock):
    return OutputSteps(monkeypatch, queue, internal_api_mock, cluster_api_mock, agent_api_mock, walle_api_mock)


@pytest.fixture()
def input_steps(http_input_steps, queue, internal_api_mock, cluster_api_mock, agent_api_mock, walle_api_mock):
    return InputSteps(http_input_steps, queue, internal_api_mock, cluster_api_mock, agent_api_mock, walle_api_mock)


@pytest.fixture()
def assert_that(verification_steps, queue):
    return Assert(verification_steps, queue)


@pytest.fixture()
def steps(config, input_steps, output_steps, assert_that):
    steps = Steps(config, input_steps, output_steps, assert_that)
    yield steps
    steps.cleanup()
