from __future__ import absolute_import, division, print_function

import six

from sandbox.projects.yabs.sandbox_task_tracing.writers.record import TraceRecord

from sandbox.projects.yabs.sandbox_task_tracing.writers.dict import DictTraceWriter


def test():
    ids_record = {}
    writer = DictTraceWriter(ids_record)
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

    assert writer.task_id == 1
    assert writer.iteration_id == 2
    assert sorted(six.itervalues(ids_record)) == [
        TraceRecord(record=1, parent=0, started=100, finished=200, type='parent', info=dict(key0='value0')),
        TraceRecord(record=2, parent=1, started=100, finished=150, type='child', info=dict(key='value1')),
        TraceRecord(record=3, parent=1, started=150, finished=200, type='child', info=dict(key='value2')),
    ]
