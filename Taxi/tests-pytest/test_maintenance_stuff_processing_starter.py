import pytest
import datetime

from taxi.core import async
from taxi.conf import settings
from taxi_maintenance.stuff import run_stq_processing_starter

_NOW = datetime.datetime(2021, 5, 19, 17, 50, 0)
_NEXT_CALL = _NOW + datetime.timedelta(seconds=settings.PROC_RESTART_ABANDONED_INTERVAL)


@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_processing_starter(patch):
    @patch('taxi_stq._client.put')
    @async.inline_callbacks
    def put(*args, **kwargs):
        yield

    yield run_stq_processing_starter.do_stuff()
    assert put.calls == [{
        'args': ('processing_starter',),
        'kwargs': {'eta': (_NEXT_CALL - datetime.datetime(1970, 1, 1)).total_seconds(),
                   'task_id': 'processing_starter_recall'}
    }]
