import contextlib

import dateutil
import pytest

from testsuite import utils
from testsuite.utils import callinfo


# pylint: disable=invalid-name,redefined-builtin
def _mock_empty_handler(queue=None, id=None, args=None, kwargs=None, eta=None):
    return {}


def _mock_empty_handler_with_tag(
        queue=None, id=None, args=None, kwargs=None, eta=None, tag=None,
):
    return {}


@pytest.fixture
def stq_mocked_queues():
    """
    Override this to enable access to named queues within test module
    """
    return []


@pytest.fixture
def stq_mocked_queues_with_tags():
    """
    Override this to enable access to named queues
    with tags support within test module
    """
    return []


class QueueHandler:
    def __init__(self, queues_to_mock, queues_to_mock_with_tags=None):
        self._put_mocks = {}
        # pylint: disable=not-an-iterable
        for queue in queues_to_mock:
            put_mock = self._get_new_mock()
            setattr(self, queue, put_mock)
            self._put_mocks[queue] = put_mock
        if queues_to_mock_with_tags:
            for queue in queues_to_mock_with_tags:
                put_mock = self._get_new_mock(with_tag=True)
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
    def _get_new_mock(with_tag=False):
        return callinfo.acallqueue(
            _mock_empty_handler_with_tag if with_tag else _mock_empty_handler,
        )


@pytest.fixture
def stq(mockserver, stq_mocked_queues, stq_mocked_queues_with_tags):
    handler = QueueHandler(stq_mocked_queues, stq_mocked_queues_with_tags)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _mock_stq_agent_reschedule(request):
        data = request.json
        await handler[data['queue_name']](
            queue=data['queue_name'],
            id=data['task_id'],
            eta=utils.to_utc(dateutil.parser.parse(data['eta'])),
        )
        return {}

    @mockserver.json_handler('/stq-agent/queue')
    async def _mock_stq_agent_queue(request):
        data = request.json
        tag = data.get('tag')
        call_args = {
            'queue': data['queue_name'],
            'id': data['task_id'],
            'eta': utils.to_utc(dateutil.parser.parse(data['eta'])),
            'args': data['args'],
            'kwargs': data['kwargs'],
        }
        if tag:
            call_args['tag'] = tag
        await handler[data['queue_name']](**call_args)
        return {}

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _mock_stq_agent_queues_api_add(request, queue_name):
        data = request.json
        tag = data.get('tag')
        call_args = {
            'queue': queue_name,
            'id': data['task_id'],
            'eta': utils.to_utc(dateutil.parser.parse(data['eta'])),
            'args': data['args'],
            'kwargs': data['kwargs'],
        }
        if tag:
            call_args['tag'] = tag
        await handler[queue_name](**call_args)
        return {}

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)/bulk', regex=True,
    )
    async def _mock_stq_agent_api_add_bulk(request, queue_name):
        data = request.json
        response = {'tasks': []}
        for task in data['tasks']:
            response['tasks'].append(
                {'task_id': task['task_id'], 'add_result': {'code': 200}},
            )
            call_args = {
                'queue': queue_name,
                'id': task['task_id'],
                'eta': utils.to_utc(dateutil.parser.parse(task['eta'])),
                'args': task['args'],
                'kwargs': task['kwargs'],
            }
            tag = data.get('tag')
            if tag:
                call_args['tag'] = tag
            await handler[queue_name](**call_args)
        return response

    return handler
