import json

import pytest
# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from subventions_candidates_reader_plugins import *  # noqa: F403 F401

from tests_subventions_candidates_reader import common


@pytest.fixture(name='logbroker')
def logbroker_fixture(testpoint):
    class Context:
        def __init__(self):
            self.publish = {'times_called': 0, 'data': []}

        def clean(self):
            self.publish = {'times_called': 0, 'data': []}

    context = Context()

    @testpoint('logbroker_publish')
    def commit(data):  # pylint: disable=W0612
        context.publish['times_called'] += 1
        context.publish['data'].append(json.loads(data['data']))

    return context


@pytest.fixture(name='default_conftest', autouse=True)
async def default_conftest(taxi_subventions_candidates_reader, testpoint):
    """
    Configures service to work in synchronous mode:
    * forces service to wait launched tasks
    * suspends all priodic tasks
    """

    @testpoint('wait_tasks_if_testsuite')
    def _handle_testpoint(data):
        pass

    await taxi_subventions_candidates_reader.suspend_periodic_tasks(
        common.PERIODIC_TASKS,
    )
