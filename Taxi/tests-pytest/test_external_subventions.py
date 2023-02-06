import datetime

import pytest

from taxi.core import async
from taxi.external import subventions as subventions_service


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    SUBVENTIONS_FULFILLED_LIMIT_SIZE=2,
)
@pytest.inline_callbacks
def test_find_fulfilled_subventions(patch):
    _mock_network_calls(patch)
    calls = []

    @async.inline_callbacks
    def on_task_failed():
        calls.append('first_fail')
        yield

    subventions = yield subventions_service.find_fulfilled_subventions(
        version=1,
        zone_name='moscow',
        date=datetime.date(2018, 8, 11),
        polling_interval=0,
        on_task_failed=on_task_failed
    )
    assert len(subventions) == 5
    assert calls == ['first_fail']


def _mock_network_calls(patch):
    task_ids = ['failing_task_id', 'succeeding_task_id']

    @patch('taxi.external.subventions._create_fulfilled_subventions_task')
    def _create_fulfilled_subventions_task(
            version, zone_name, date, **kwargs):
        assert version == 1
        return task_ids.pop(0)

    items = [1, 2, 3, 4, 5]
    statuses = [
        ('running', 'failing_task_id'),
        ('error', 'failing_task_id'),
        ('running', 'succeeding_task_id'),
        ('success', 'succeeding_task_id'),  # first success
        ('success', 'succeeding_task_id'),  # getting [1, 2]
        ('success', 'succeeding_task_id'),  # getting [3, 4]
        ('success', 'succeeding_task_id'),  # getting [5]
        ('success', 'succeeding_task_id'),  # getting []
    ]

    @patch('taxi.external.subventions._poll_fulfilled_subventions')
    def _poll_fulfilled_subventions(task_id, offset, limit, **kwargs):
        status, expected_task_id = statuses.pop(0)
        assert task_id == expected_task_id
        if status == 'running':
            return _Response({'status': status})
        if status == 'error':
            return _Response({'error': 'some_error_reason'})
        assert status == 'success'
        return _Response({'subventions': items[offset:offset + limit]})


class _Response(object):
    def __init__(self, result):
        self._result = result

    def json(self):
        return self._result
