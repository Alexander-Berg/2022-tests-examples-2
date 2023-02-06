# pylint: skip-file
# flake8: noqa
import bson.json_util
import pytest


class BaseError(Exception):
    pass


class UnexpectedTaskStatus(BaseError):
    pass


class StqQueueCaller:
    def __init__(self, queue_name, dispatcher_client):
        self._queue = queue_name
        self._dispatcher_client = dispatcher_client

    async def call(self, *, task_id=None, args=None, kwargs=None, tag=None,
                   exec_tries=None, reschedule_counter=None, eta=None,
                   expect_fail=False):
        json_options = bson.json_util.DEFAULT_JSON_OPTIONS
        json_options.datetime_representation = (
            bson.json_util.DatetimeRepresentation.ISO8601
        )
        response = await self._dispatcher_client.post(
            'testsuite/stq',
            data=bson.json_util.dumps({
                'queue_name': self._queue,
                'args': args or (),
                'kwargs': kwargs or {},
                'tag': tag,
                'task_id': task_id,
                'exec_tries': exec_tries,
                'reschedule_counter': reschedule_counter,
                'eta': eta,
            }, json_options=json_options),
        )
        response.raise_for_status()
        body = response.json()
        failed = body.get('failed')
        error_msg = ''
        if failed and not expect_fail:
            error_msg = 'failed when success'
        elif not failed and expect_fail:
            error_msg = 'succeeded when failure'

        if error_msg:
            raise UnexpectedTaskStatus(
                f'stq-task of queue \'{self._queue}\' with id {task_id} '
                f'{error_msg} was expected'
            )


class StqRunner:
    def __init__(self, dispatcher_client):
        self.test = StqQueueCaller(
            'test', dispatcher_client,
        )

@pytest.fixture
async def stq_runner(taxi_test_service):
    return StqRunner(taxi_test_service)
