import pytest

from taxi.stq import async_worker_ng


@pytest.fixture(name='task_info')
def _build_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=1, reschedule_counter=1, queue='',
    )


@pytest.fixture
def mock_solomon(mockserver):
    def _wrapper():
        @mockserver.json_handler('/solomon/')
        async def _handler(request):
            return {}

        return _handler

    return _wrapper
