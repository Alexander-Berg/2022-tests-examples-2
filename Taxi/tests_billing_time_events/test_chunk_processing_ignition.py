import datetime as dt

import pytest

_NOW = dt.datetime(2020, 6, 30, 10, 10)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('billing_time_events@0', files=[])
@pytest.mark.pgsql('billing_time_events@1', files=[])
async def test_chunk_processing_ignition(taxi_billing_time_events, pgsql, stq):
    await taxi_billing_time_events.run_distlock_task(
        'chunk-processing-ignition',
    )

    select_offsets = 'SELECT vshard_id, last_created FROM bte.consumer_offsets'
    cursor = pgsql['billing_time_events@0'].cursor()
    cursor.execute(select_offsets)

    actual_offsets = [(row[0], row[1]) for row in cursor]
    expected_offsets = _make_expected_offsets()
    assert actual_offsets == expected_offsets

    cursor = pgsql['billing_time_events@1'].cursor()
    cursor.execute(select_offsets)

    actual_offsets = [(row[0], row[1]) for row in cursor]
    expected_offsets = _make_expected_offsets()
    assert actual_offsets == expected_offsets

    actual_tasks = _tasks(stq.billing_time_events_process_shard)
    expected_tasks = _make_expected_tasks()
    assert actual_tasks == expected_tasks


def _tasks(queue):
    result = []
    for _ in range(queue.times_called):
        task = _drop_link(queue.next_call())
        result.append(task)
    return result


def _drop_link(task):
    task['kwargs']['log_extra'].pop('_link')
    return task


def _make_expected_offsets():
    now = _NOW.replace(tzinfo=dt.timezone.utc)
    return [(vshard, now) for vshard in range(2)]


def _make_expected_tasks():
    result = []
    for pshard in range(2):
        for vshard in range(2):
            task = {
                'queue': 'billing_time_events_process_shard',
                'id': f'{pshard}_{vshard}',
                'args': [],
                'kwargs': {
                    'pshard_id': pshard,
                    'vshard_id': vshard,
                    'log_extra': {},
                },
                'eta': _NOW,
            }
            result.append(task)
    return result
