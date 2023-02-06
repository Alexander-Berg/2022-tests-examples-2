from __future__ import absolute_import, division, print_function

import six
import threading

from sandbox.projects.yabs.sandbox_task_tracing.util import frozendict
from sandbox.projects.yabs.sandbox_task_tracing.writers.abstract import AbstractTraceWriter
from sandbox.projects.yabs.sandbox_task_tracing.writers.record import TraceRecord
from sandbox.projects.yabs.sandbox_task_tracing.writers.dict import DictTraceWriter

from sandbox.projects.yabs.sandbox_task_tracing.impl.buffer import (
    add_trace_record,
    clear_trace_record_queue,
    TraceWritingThread,
    TRACE_RECORD_QUEUE,
)


class Independence(object):
    '''
    Context manager ensuring tests do not interfer with each other.

    They may since global variables like TRACE_RECORD_QUEUE retain state,
    and there can also remain daemon threads.
    '''

    LOCK = threading.RLock()

    def __init__(self):
        self.threads_to_finish = []

    def add_thread_to_finish(self, thread):
        self.threads_to_finish.append(thread)

    def new_writing_thread(self, writer_factory):
        writing_thread = TraceWritingThread(writer_factory=writer_factory, set_task_kwargs=dict(task_id=1, iteration_id=2))
        self.add_thread_to_finish(writing_thread)
        writing_thread.start()
        return writing_thread

    def __enter__(self):
        assert self.LOCK.acquire(blocking=False)  # make sure these tests are never run in parallel threads
        clear_trace_record_queue()
        assert TRACE_RECORD_QUEUE.empty()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        try:
            for thread in self.threads_to_finish:
                thread.finish()
        finally:
            self.LOCK.release()


def test_clear_trace_record_queue():
    with Independence():
        assert TRACE_RECORD_QUEUE.empty()
        add_trace_record(record=1, parent=0, started=100, finished=200, type='parent', info=dict(key0='value0'))
        assert not TRACE_RECORD_QUEUE.empty()
        clear_trace_record_queue()
        assert TRACE_RECORD_QUEUE.empty()


class NullTraceWriter(AbstractTraceWriter):

    def set_task(self, task_id, iteration_id, task_info=frozendict()):
        pass

    def write_records(self, records):
        pass

    def flush(self, timeout=None):
        pass


def test_finish():
    with Independence() as independence:
        writing_thread = independence.new_writing_thread(NullTraceWriter)
        writing_thread.finish()
        assert not writing_thread.is_alive()


def test_flush():
    with Independence() as independence:

        flush_called = []

        def writer_factory():
            writer = NullTraceWriter()
            writer.flush = lambda *args, **kwargs: flush_called.append(True)
            return writer

        independence.new_writing_thread(writer_factory).flush()

        assert flush_called


def test_single_thread():
    with Independence() as independence:
        add_trace_record(record=2, parent=1, started=100, finished=150, type='child', info=dict(key='value1')),
        add_trace_record(record=3, parent=1, started=150, finished=200, type='child', info=dict(key='value2')),
        add_trace_record(record=1, parent=0, started=100, finished=200, type='parent', info=dict(key0='value0'))

        thread_idents_set = set()

        def writer_factory():
            writer = NullTraceWriter()
            save_thread_ident = lambda *args, **kwargs: thread_idents_set.add(threading.current_thread().ident)
            for name in ('__init__', 'set_task', 'write_records', 'flush'):
                assert hasattr(writer, name)
                setattr(writer, name, save_thread_ident)
            return writer

        independence.new_writing_thread(writer_factory).flush()

        assert len(thread_idents_set) == 1
        assert next(iter(thread_idents_set)) is not None


def test_writing():
    with Independence() as independence:
        info0 = dict(key=['value 0'])
        info1 = dict(key=['value 1'])
        info2 = dict(key=['value 2'])

        add_trace_record(record=2, parent=1, started=100, finished=150, type='child', info=info1),
        add_trace_record(record=3, parent=1, started=150, finished=200, type='child', info=info2),
        add_trace_record(record=1, parent=0, started=100, finished=200, type='parent', info=info0)

        # modify passed dict values
        info0['key'][0] = 'modified value 0'
        info1['key'][0] = 'modified value 1'
        info2['key'][0] = 'modified value 2'

        ids_record = {}

        def writer_factory():
            return DictTraceWriter(ids_record)

        independence.new_writing_thread(writer_factory).flush()

        assert sorted(six.itervalues(ids_record)) == [
            TraceRecord(record=1, parent=0, started=100, finished=200, type='parent', info=dict(key=['value 0'])),
            TraceRecord(record=2, parent=1, started=100, finished=150, type='child', info=dict(key=['value 1'])),
            TraceRecord(record=3, parent=1, started=150, finished=200, type='child', info=dict(key=['value 2'])),
        ]


def test_task_kwargs_modification():
    with Independence() as independence:
        passed_kwargs = {}

        def writer_factory():
            writer = NullTraceWriter()
            writer.set_task = lambda **kwargs: passed_kwargs.update(**kwargs)
            return writer

        set_task_kwargs = dict(task_id=1, iteration_id=2, task_info=dict(key=['value']))

        writing_thread = TraceWritingThread(writer_factory=writer_factory, set_task_kwargs=set_task_kwargs)
        independence.add_thread_to_finish(writing_thread)

        # modify passed dict values
        set_task_kwargs['task_info']['key'][0] = 'modified value'
        set_task_kwargs.update(task_id=3, iteration_id=4, task_info=dict(key=['modified value']))

        writing_thread.start()
        writing_thread.flush()

        assert passed_kwargs['task_id'] == 1
        assert passed_kwargs['iteration_id'] == 2
        assert passed_kwargs['task_info'] == dict(key=['value'])
