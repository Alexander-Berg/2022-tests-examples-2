import contextlib

import dateutil
import pytest

from taxi_tests import utils
from taxi_tests.utils import callinfo


# pylint: disable=invalid-name,redefined-builtin
def _mock_empty_handler(queue=None, id=None, args=None, kwargs=None, eta=None):
    return {}


@pytest.fixture
def stq_mocked_queues():
    """
    Override this to enable access to named queues within test module
    """
    return []


class QueueHandler:
    def __init__(self, queues_to_mock):
        self._put_mocks = {}
        # pylint: disable=not-an-iterable
        for queue in queues_to_mock:
            put_mock = self._get_new_mock()
            setattr(self, queue, put_mock)
            self._put_mocks[queue] = put_mock

    @property
    def is_empty(self):
        for mock in self._put_mocks.values():
            if mock.has_calls:
                return False
        return True

    def flush(self):
        for mock in self._put_mocks.values():
            mock.flush()

    @contextlib.contextmanager
    def flushing(self):
        try:
            self.flush()
            yield self
        finally:
            self.flush()

    def __getitem__(self, item):
        if item not in self._put_mocks:
            self._put_mocks[item] = self._get_new_mock()
        return self._put_mocks[item]

    @staticmethod
    def _get_new_mock():
        return callinfo.acallqueue(_mock_empty_handler)


@pytest.fixture
def stq(mockserver, stq_mocked_queues):
    handler = QueueHandler(stq_mocked_queues)

    @mockserver.json_handler('/stq-agent/queue')
    async def _mock_stq_agent_queue(request):
        data = request.json
        await handler[data['queue_name']](
            queue=data['queue_name'],
            id=data['task_id'],
            eta=utils.to_utc(dateutil.parser.parse(data['eta'])),
            args=data['args'],
            kwargs=data['kwargs'],
        )
        return {}

    return handler
