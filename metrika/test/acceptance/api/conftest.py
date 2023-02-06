import pytest

from metrika.admin.python.cms.test.acceptance.api.steps import Steps, Assert, Components, Frontend, Judge, Marshal, InputSteps, OutputSteps, ClusterOutputSteps, AgentOutputSteps, WalleOutputSteps


@pytest.fixture
def agent_output_steps(port_manager):
    steps = AgentOutputSteps(port_manager)
    yield steps
    steps.cleanup()


@pytest.fixture
def walle_output_steps(port_manager):
    steps = WalleOutputSteps(port_manager)
    yield steps
    steps.cleanup()


@pytest.fixture
def cluster_output_steps(port_manager):
    steps = ClusterOutputSteps(port_manager)
    yield steps
    steps.cleanup()


@pytest.fixture
def output_steps(cluster_output_steps, agent_output_steps, walle_output_steps):
    return OutputSteps(cluster_output_steps, agent_output_steps, walle_output_steps)


@pytest.fixture
def input_steps(port_manager):
    return InputSteps(port_manager)


@pytest.fixture
def marshal(port_manager, input_steps, output_steps):
    return Marshal(port_manager, input_steps, output_steps)


@pytest.fixture
def judge(port_manager, input_steps, output_steps):
    return Judge(port_manager, input_steps, output_steps)


@pytest.fixture
def frontend(input_steps, output_steps):
    return Frontend(input_steps, output_steps)


@pytest.fixture
def components_steps(frontend, judge, marshal):
    return Components(frontend, judge, marshal)


@pytest.fixture
def assert_that(verification_steps):
    return Assert(verification_steps)


@pytest.fixture
def steps(input_steps, output_steps, components_steps, assert_that):
    s = Steps(input_steps, output_steps, components_steps, assert_that)
    yield s
    s.teardown()
