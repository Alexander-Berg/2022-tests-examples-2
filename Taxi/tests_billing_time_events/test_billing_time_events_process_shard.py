import datetime as dt

import pytest


@pytest.mark.config(
    BILLING_TIME_EVENTS_CHUNK_SETTINGS={
        'shard-jitter': 0,
        'drivers-jitter': 0,
        'drivers-count': 2,
    },
)
@pytest.mark.parametrize('test_data_json', ['test_data.json'])
@pytest.mark.now('2020-06-30T10:10:00+00:00')
async def test(
        stq_runner,
        stq,
        load,
        load_json,
        object_substitute,
        pgsql,
        test_data_json,
):
    test_data = load_json(test_data_json)

    sql_files = test_data['sql_files']
    queries = [load(sql_file) for sql_file in sql_files]
    pgsql['billing_time_events@0'].apply_queries(queries)

    await stq_runner.billing_time_events_process_shard.call(
        task_id='sample_task', kwargs={'pshard_id': 0, 'vshard_id': 0},
    )

    actual_tasks = _tasks(
        stq.billing_time_events_process_drivers, object_substitute,
    )
    assert actual_tasks == test_data['expected_stq_tasks']

    assert stq.billing_time_events_process_shard.times_called == 1
    next_call = stq.billing_time_events_process_shard.next_call()
    assert next_call['id'] == 'sample_task'
    assert next_call['eta'] == dt.datetime(2020, 6, 30, 10, 40)
    assert next_call['args'] == []
    assert next_call['kwargs']['pshard_id'] == 0
    assert next_call['kwargs']['vshard_id'] == 0


def _tasks(queue, object_substitute):
    result = []
    for _ in range(queue.times_called):
        task = object_substitute(_drop_link(queue.next_call()))
        result.append(task)
    return result


def _drop_link(task):
    task['kwargs']['log_extra'].pop('_link')
    return task
