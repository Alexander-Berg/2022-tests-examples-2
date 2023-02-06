import json

import pytest

from tests_plugins import fastcgi

from .routehistory_mock import RoutehistoryFixture

pytest_plugins = [
    # settings fixture
    'tests_plugins.settings',
    # Testsuite plugins
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.translations',
    'taxi_tests.plugins.mocks.configs_service',
    'tests_plugins.daemons.plugins',
    'tests_plugins.testpoint',
    # Local mocks
    'tests_plugins.mock_experiments3_proxy',
    'tests_plugins.mock_geoareas',
    'tests_plugins.mock_taxi_exp',
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.config_service_defaults',
    'tests_plugins.mock_timetable_airport_queue',
    'tests_plugins.mock_individual_tariffs',
]

taxi_ml = fastcgi.create_client_fixture('taxi_ml')


@pytest.fixture
def routehistory(mockserver, tvm2_client, db, load_json):
    fixture = RoutehistoryFixture(mockserver, tvm2_client, db, load_json)
    yield fixture
    fixture.finalize()


# Add ticket in set_ticket instead of replacing it
@pytest.fixture(name='tvm2_client')
def tvm2_client_override(tvm2_client):
    def set_ticket_override(ticket):
        current = json.loads(tvm2_client.ticket) if tvm2_client.ticket else {}
        ticket = json.loads(ticket)
        current.update(ticket)
        tvm2_client.ticket = json.dumps(current)

    tvm2_client.set_ticket = set_ticket_override
    return tvm2_client
