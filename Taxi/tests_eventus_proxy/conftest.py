import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eventus_proxy_plugins import *  # noqa: F403 F401


@pytest.fixture(name='logbroker')
def logbroker_fixture(testpoint):
    class Context:
        def __init__(self):
            self.publish_data = []

            @testpoint('logbroker_publish')
            def commit(data):  # pylint: disable=W0612
                import json
                self.publish_data.append(
                    {'data': json.loads(data['data']), 'name': data['name']},
                )

            self.commit_testpoint = commit

        @property
        def times_called(self):
            return self.commit_testpoint.times_called

        @property
        def data(self):
            data = self.publish_data[:]
            return sorted(
                data,
                key=lambda x: (
                    x['data']['topic'],
                    x['data']['event']['idempotency_token'],
                ),
            )

        async def wait_publish(self, timeout=10):
            return await self.commit_testpoint.wait_call(timeout)

    return Context()
