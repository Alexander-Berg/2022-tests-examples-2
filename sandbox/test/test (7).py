from __future__ import absolute_import, division, print_function

import time
import os

import yt.wrapper
import yt.yson

from sandbox.projects.yabs.sandbox_task_tracing.writers.record import TraceRecord

from sandbox.projects.yabs.sandbox_task_tracing.writers.yt import YtTraceWriter


def create_table(yt_client, path, columns, account=None):
    schema = yt.yson.YsonList(columns)
    schema.attributes = dict(strict=True, unique_keys=True)
    attributes = dict(
        atomicity='none',
        dynamic=True,
        enable_dynamic_store_read=True,
        max_data_ttl=31557600000,
        max_data_versions=1,
        min_data_ttl=0,
        min_data_versions=0,
        merge_rows_on_flush=True,
        schema=schema,
    )
    if account is not None:
        attributes.update(account=account)
    yt_client.create(path=path, type='table', recursive=True, attributes=attributes)
    yt_client.mount_table(path)
    for _ in range(10):
        tablet_states = set(tablet['state'] for tablet in yt_client.get_attribute(path, 'tablets'))
        if tablet_states == 'mounted':
            break
        assert tablet_states <= {'mounted', 'mounting'}, tablet_states
        time.sleep(1)


def create_tables(yt_client, tasks_path, records_path, account=None):
    create_table(yt_client, tasks_path, (
        dict(name='task', required=True, sort_order='ascending', type='int64'),
        dict(name='info', type='any'),
    ))
    create_table(yt_client, records_path, (
        dict(name='task', required=True, sort_order='ascending', type='int64'),
        dict(name='iteration', required=True, sort_order='ascending', type='uint32'),
        dict(name='record', required=True, sort_order='ascending', type='uint32'),
        dict(name='parent', required=True, type='uint32'),
        dict(name='started', required=True, type='timestamp'),
        dict(name='finished', required=True, type='timestamp'),
        dict(name='type', required=True, type='utf8'),
        dict(name='info', type='any'),
    ))


def read_table(yt_client, path):
    return list(yt_client.select_rows('* from [{}] limit 1000'.format(path)))


def test():
    yt_proxy = os.environ['YT_PROXY']
    yt_path = '//home/test/tracing'

    yt_client = yt.wrapper.YtClient(proxy=yt_proxy)

    yt_tasks_path = yt.wrapper.ypath_join(yt_path, 'tasks')
    yt_records_path = yt.wrapper.ypath_join(yt_path, 'records')
    create_tables(yt_client, yt_tasks_path, yt_records_path)

    writer = YtTraceWriter(proxy=yt_proxy, path=yt_path, token='')
    writer.set_task(
        task_id=1,
        iteration_id=2,
        task_info=dict(task_info_field=3),
    )

    writer.write_records([
        TraceRecord(record=2, parent=1, started=100, finished=150, type='child', info=dict(key='value1')),
        TraceRecord(record=3, parent=1, started=150, finished=200, type='child', info=dict(key='value2')),
    ])
    writer.write_records([TraceRecord(record=1, parent=0, started=100, finished=200, type='parent', info=dict(key0='value0'))])

    writer.flush()

    assert read_table(yt_client, yt_tasks_path) == [dict(task=1, info=dict(task_info_field=3))]
    assert read_table(yt_client, yt_records_path) == [
        dict(task=1, iteration=2, record=1, parent=0, started=100, finished=200, type='parent', info=dict(key0='value0')),
        dict(task=1, iteration=2, record=2, parent=1, started=100, finished=150, type='child', info=dict(key='value1')),
        dict(task=1, iteration=2, record=3, parent=1, started=150, finished=200, type='child', info=dict(key='value2')),
    ]
