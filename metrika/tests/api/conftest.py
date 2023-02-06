import pytest

from metrika.admin.python.cms.frontend.tests.api.steps import Steps
from metrika.admin.python.cms.frontend.tests.api.steps import Assert
from metrika.admin.python.cms.frontend.tests.api.steps import Config


@pytest.fixture
def steps(client, assert_that, config):
    return Steps(client, assert_that, config)


@pytest.fixture
def assert_that(verification_steps):
    return Assert(verification_steps)


@pytest.fixture
def config():
    return Config()
