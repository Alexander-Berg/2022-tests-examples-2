import pytest

# root conftest for service api-proxy
pytest_plugins = ['api_proxy_plugins.pytest_plugins']


@pytest.fixture(name='juggler_events', autouse=True)
def juggler_events(mockserver):
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
