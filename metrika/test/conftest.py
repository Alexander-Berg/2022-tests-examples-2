import pytest
import logging

import yatest.common.network as network

import metrika.pylib.structures.dotdict as dotdict
import metrika.admin.python.cms.agent.lib.application as application
import metrika.admin.python.cms.agent.lib.agent as lib_agent

from pytest_flask.fixtures import *  # noqa
from pytest_localserver import plugin

from metrika.admin.python.cms.agent.test.mock_juggler_api import MockJugglerApi
from metrika.admin.python.cms.agent.test.steps import Steps
from metrika.admin.python.cms.agent.test.asserts import Assert
from metrika.admin.python.cms.lib import downtimes
from metrika.admin.python.cms.test_framework.utils import AllureFlaskTestClient

logger = logging.getLogger(__name__)

httpserver = plugin.httpserver


@pytest.fixture()
def config():
    with network.PortManager() as port_manager:
        config = {
            "debug": True,
            "environment": "unit-testing",
            "cluster": "unit-testing",
            "port": port_manager.get_port(),
            "frontend": "some url",
        }

        logger.info("config: {}".format(config))

        yield dotdict.DotDict(config)


@pytest.fixture()
def juggler_mock(monkeypatch):
    monkeypatch.setattr(downtimes, "CmsDowntime", MockJugglerApi)


@pytest.fixture()
def agent(config, juggler_mock):
    return lib_agent.Agent(config)


@pytest.fixture()
def app(agent):
    app = application.create_app()
    app.testing = True
    app.test_client_class = AllureFlaskTestClient
    agent.init_app(app)
    yield app


@pytest.fixture()
def assert_that(verification_steps):
    return Assert(verification_steps)


@pytest.fixture()
def steps(monkeypatch, agent, client, httpserver, verification_steps, assert_that):
    return Steps(monkeypatch, agent, client, httpserver, verification_steps, assert_that)
