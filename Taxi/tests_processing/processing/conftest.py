# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from processing_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='juggler_events', autouse=True)
def _juggler_events(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/juggler/events')
        def _events_handler(req):
            return {
                'accepted_events': 1,
                'events': [{'code': 200}],
                'success': True,
            }

    return Context()
