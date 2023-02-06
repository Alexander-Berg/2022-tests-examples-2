from __future__ import absolute_import, division, print_function

import pytest

import functools
import multiprocessing
import six
import time
import threading

from sandbox.projects.yabs.sandbox_task_tracing.defaults import DEFAULTS
from sandbox.projects.yabs.sandbox_task_tracing.exceptions import BufferTimeout
from sandbox.projects.yabs.sandbox_task_tracing.info import jsonified
from sandbox.projects.yabs.sandbox_task_tracing.util import coalesce, frozendict, microseconds_from_utc_iso
from sandbox.projects.yabs.sandbox_task_tracing.writers.abstract import AbstractTraceWriter
from sandbox.projects.yabs.sandbox_task_tracing.writers.dict import DictTraceWriter

from sandbox.projects.yabs.sandbox_task_tracing import (
    flush_trace,
    trace,
    trace_calls,
    trace_entry_point,
    trace_new_resources,
    trace_new_tasks,
    trace_subprocess,
    trace_subprocess_calls,
)

from sandbox.projects.yabs.sandbox_task_tracing.test.lib.mocks import (
    DEFAULT_ITERATION_STARTED_MICROSECONDS,
    TASK_DEFAULTS,
    patch_current_task_property,
    mock_resource,
    mock_task,
)


class Tracing(object):

    def __init__(self, action, writer_factory=None, mocks_spec=frozendict(), trace_entry_point_spec=frozendict()):
        trace_entry_point_spec = frozendict(finish_on_exit=True, clear_queue_on_exit=True) + trace_entry_point_spec

        self.mocks_spec = mocks_spec

        self.ids_record = {}
        self.writers = []
        self.return_values = return_values = []

        if writer_factory is None:
            writer_factory = functools.partial(DictTraceWriter, self.ids_record)

        def saving_writer_factory():
            writer = writer_factory()
            self.writers.append(writer)
            return writer

        class Task(object):

            def __init__(self):
                self.id = mocks_spec.get('task_id', TASK_DEFAULTS['task_id'])

            @trace_entry_point(writer_factory=saving_writer_factory, spec=trace_entry_point_spec)
            def on_execute(self):
                return_values.append(action())

        self.task_type = Task

    def execute(self):
        with patch_current_task_property(spec=self.mocks_spec):
            self.task_type().on_execute()

    @property
    def writer(self):
        [writer] = self.writers
        return writer

    def __iter__(self):
        return six.itervalues(self.ids_record)

    def __getitem__(self, record_id):
        [result] = filter(lambda record: record.record == record_id, self)
        return result

    def records_of_type(self, record_type):
        return sorted(filter(lambda record: record.type == record_type, self))

    @property
    def entry_point_record(self):
        [result] = filter(lambda record: record.info.get('entry_point'), self)
        assert result.type == 'call'
        return result

    @property
    def current_audit_record(self):
        result = self[self.entry_point_record.parent]
        assert result.type == 'audit'
        return result

    @property
    def current_iteration_record(self):
        result = self[self.current_audit_record.parent]
        assert result.type == 'iteration'
        return result


def test_flush_trace():

    class SlowTraceWriter(DictTraceWriter):

        def __init__(self):
            super(SlowTraceWriter, self).__init__(tracing.ids_record)

        def set_task(self, task_id, iteration_id, task_info=frozendict()):
            time.sleep(1)
            super(SlowTraceWriter, self).set_task(task_id, iteration_id, task_info)

        def write_records(self, records):
            time.sleep(1)
            super(SlowTraceWriter, self).write_records(records)

        def flush(self, timeout=None):
            time.sleep(1)
            super(SlowTraceWriter, self).flush(timeout)

    records_lists = []

    def action():
        with trace('trace_name', info=dict(key='value')):
            pass
        records_lists.append(tracing.records_of_type('trace'))

        flush_trace(timeout=0.1, ignore_errors=True)
        records_lists.append(tracing.records_of_type('trace'))

        with pytest.raises(BufferTimeout):
            flush_trace(timeout=0.1, ignore_errors=False)
        records_lists.append(tracing.records_of_type('trace'))

        flush_trace()
        records_lists.append(tracing.records_of_type('trace'))

    tracing = Tracing(action=action, writer_factory=SlowTraceWriter)
    tracing.execute()

    assert records_lists[:-1] == [[], [], []]

    [[record]] = records_lists[-1:]
    assert record.parent == tracing.entry_point_record.record
    assert record.info['name'] == 'trace_name'
    assert record.info['key'] == 'value'


def test_trace():

    def action():
        with trace('trace_name', info=dict(key='value')):
            pass

    tracing = Tracing(action=action)
    tracing.execute()
    [record] = tracing.records_of_type('trace')
    assert record.parent == tracing.entry_point_record.record
    assert record.info['name'] == 'trace_name'
    assert record.info['key'] == 'value'


def test_trace_exception():

    class ExceptionType(Exception):
        pass

    def action():
        try:
            with trace('trace_name', info=dict(key='value')):
                raise ExceptionType()
        except ExceptionType:
            pass

    tracing = Tracing(action=action)
    tracing.execute()
    [record] = tracing.records_of_type('trace')
    assert record.parent == tracing.entry_point_record.record
    assert record.info['exception']['type']['name'] == ExceptionType.__name__
    assert record.info['exception']['type']['module'] == ExceptionType.__module__
    assert record.info['name'] == 'trace_name'
    assert record.info['key'] == 'value'


def test_trace_nesting():

    def action():
        with trace('outer_trace', info=dict(key='outer_trace_value')):
            with trace('inner_trace', info=dict(key='inner_trace_value')):
                pass

    tracing = Tracing(action=action)
    tracing.execute()
    outer_record, inner_record = tracing.records_of_type('trace')

    assert outer_record.parent == tracing.entry_point_record.record
    assert outer_record.info['name'] == 'outer_trace'
    assert outer_record.info['key'] == 'outer_trace_value'

    assert inner_record.parent == outer_record.record
    assert inner_record.info['name'] == 'inner_trace'
    assert inner_record.info['key'] == 'inner_trace_value'


def test_trace_multithreading():

    def thread_action():
        with trace('separate_outer_trace', info=dict(key='separate_outer_trace_value')):
            with trace('separate_inner_trace', info=dict(key='separate_inner_trace_value')):
                pass

    def action():
        with trace('main_outer_trace', info=dict(key='main_outer_trace_value')):
            thread = threading.Thread(target=thread_action)
            thread.start()
            time.sleep(1)
            with trace('main_inner_trace', info=dict(key='main_inner_trace_value')):
                time.sleep(1)
            thread.join()

    tracing = Tracing(action=action)
    tracing.execute()
    main_outer_record, separate_outer_record, separate_inner_record, main_inner_record = tracing.records_of_type('trace')

    assert main_outer_record.parent == tracing.entry_point_record.record
    assert main_outer_record.info['name'] == 'main_outer_trace'
    assert main_outer_record.info['key'] == 'main_outer_trace_value'

    assert main_inner_record.parent == main_outer_record.record
    assert main_inner_record.info['name'] == 'main_inner_trace'
    assert main_inner_record.info['key'] == 'main_inner_trace_value'

    assert separate_outer_record.parent == tracing.current_iteration_record.record
    assert separate_outer_record.info['name'] == 'separate_outer_trace'
    assert separate_outer_record.info['key'] == 'separate_outer_trace_value'

    assert separate_inner_record.parent == separate_outer_record.record
    assert separate_inner_record.info['name'] == 'separate_inner_trace'
    assert separate_inner_record.info['key'] == 'separate_inner_trace_value'


# must be defined at top level to be callable from `subprocess_action`
@trace_calls
def subprocess_subaction(value):
    return value


# must be defined at top level to be pickle-able
@trace_calls
def subprocess_action(value):
    with trace('subprocess_trace', info=dict(key='subprocess_trace_value')):
        return subprocess_subaction(value)


def test_trace_multiprocessing():

    values = list(range(10000))

    def action():
        with trace('main_trace', info=dict(key='main_trace_value')):
            pool = multiprocessing.Pool()
            try:
                return list(pool.map(subprocess_action, values))
            finally:
                pool.close()
                pool.join()

    tracing = Tracing(action=action)
    tracing.execute()

    assert tracing.return_values == [values]

    [main_trace_record] = tracing.records_of_type('trace')
    assert main_trace_record.parent == tracing.entry_point_record.record
    assert main_trace_record.info['name'] == 'main_trace'
    assert main_trace_record.info['key'] == 'main_trace_value'

    [entry_point_record] = tracing.records_of_type('call')
    assert entry_point_record == tracing.entry_point_record


def test_trace_calls():

    @trace_calls(info=dict(key='subvalue'), save_arguments='all', save_return_value=True)
    def subaction(argument0, argument1):
        return len(argument0) + len(argument1)

    @trace_calls(info=dict(key='value'), save_arguments='all', save_return_value=True)
    def action():
        return subaction('0', argument1='1') - 1

    tracing = Tracing(action=action)
    tracing.execute()

    assert tracing.return_values == [1]

    entry_point_record, action_record, subaction_record = tracing.records_of_type('call')

    assert entry_point_record == tracing.entry_point_record

    assert action_record.parent == entry_point_record.record
    assert action_record.info['arguments'] == dict(args=[], kwargs={})
    assert action_record.info['function']['name'] == action._wrapped.__name__
    assert action_record.info['function']['module'] == action._wrapped.__module__
    assert action_record.info['return_value'] == 1
    assert action_record.info['key'] == 'value'

    assert subaction_record.parent == action_record.record
    assert subaction_record.info['arguments'] == dict(args=['0'], kwargs=dict(argument1='1'))
    assert subaction_record.info['function']['name'] == subaction._wrapped.__name__
    assert subaction_record.info['function']['module'] == subaction._wrapped.__module__
    assert subaction_record.info['return_value'] == 2
    assert subaction_record.info['key'] == 'subvalue'


def test_trace_entry_point():
    tracing = Tracing(action=(lambda: time.sleep(1)))
    tracing.execute()

    task_info = tracing.writer.task_info
    assert task_info['_raw']['id'] == TASK_DEFAULTS['task_id']
    assert task_info['_raw']['requirements'] == TASK_DEFAULTS['requirements']
    assert task_info['audit'] == jsonified(TASK_DEFAULTS['audit'])
    assert task_info['gsid']['_raw'] == TASK_DEFAULTS['gsid']
    assert task_info['id'] == TASK_DEFAULTS['task_id']
    assert task_info['type']['name'] == tracing.task_type.__name__
    assert task_info['type']['module'] == tracing.task_type.__module__

    [iteration_record] = tracing.records_of_type('iteration')
    assert iteration_record.parent == 0
    assert iteration_record.started == DEFAULT_ITERATION_STARTED_MICROSECONDS
    assert iteration_record.info['requirements'] == TASK_DEFAULTS['requirements']

    [executing_record] = tracing.records_of_type('audit')
    assert executing_record.parent == iteration_record.record
    assert executing_record.started == DEFAULT_ITERATION_STARTED_MICROSECONDS
    assert executing_record.info['record'] == TASK_DEFAULTS['audit'][0]

    [call_record] = tracing.records_of_type('call')
    assert call_record.parent == executing_record.record
    assert call_record.info['entry_point']
    assert call_record.info['function']['name'] == tracing.task_type.on_execute._wrapped.__name__
    assert call_record.info['function']['module'] == tracing.task_type.on_execute._wrapped.__module__

    assert 0.5E6 < call_record.finished - call_record.started < 5E6
    assert DEFAULT_ITERATION_STARTED_MICROSECONDS < call_record.finished <= executing_record.finished <= iteration_record.finished


@pytest.mark.parametrize('initialization_error', (False, True))
@pytest.mark.parametrize('thread_error_stage', ('set_task', 'write_records', 'flush'))
@pytest.mark.parametrize('action_error', (False, True))
@pytest.mark.parametrize('ignore_initialization_errors', (None, False, True))
@pytest.mark.parametrize('ignore_exit_errors', (None, False, True))
def test_ignore_errors(
    initialization_error,
    thread_error_stage,
    action_error,
    ignore_initialization_errors,
    ignore_exit_errors,
):

    class InitializationError(Exception):
        pass

    class ThreadError(Exception):
        pass

    class ActionError(Exception):
        pass

    class NoError(Exception):
        pass

    class RaisingTraceWriter(AbstractTraceWriter):

        def set_task(self, task_id, iteration_id, task_info=frozendict()):
            if thread_error_stage == 'set_task':
                raise ThreadError()

        def write_records(self, records):
            if thread_error_stage == 'write_records':
                raise ThreadError()

        def flush(self, timeout=None):
            if thread_error_stage == 'flush':
                raise ThreadError()

    action_finished = []

    def action():
        if action_error:
            raise ActionError
        action_finished.append(True)
        return 1

    mocks_spec = dict(sandbox_exception=InitializationError) if initialization_error else {}

    trace_entry_point_spec = {}
    if ignore_initialization_errors is not None:
        trace_entry_point_spec.update(ignore_initialization_errors=ignore_initialization_errors)
    if ignore_exit_errors is not None:
        trace_entry_point_spec.update(ignore_exit_errors=ignore_exit_errors)

    ignore_initialization_errors = coalesce(
        ignore_initialization_errors,
        DEFAULTS['entry_point_spec']['ignore_initialization_errors'],
    )
    ignore_exit_errors = coalesce(
        ignore_exit_errors,
        DEFAULTS['entry_point_spec']['ignore_exit_errors'],
    )

    expected_error_type = (
        InitializationError if initialization_error and not ignore_initialization_errors else
        ThreadError if not initialization_error and not ignore_exit_errors else
        ActionError if action_error else
        NoError
    )

    with pytest.raises(expected_error_type):
        tracing = Tracing(
            action=action,
            writer_factory=RaisingTraceWriter,
            mocks_spec=mocks_spec,
            trace_entry_point_spec=trace_entry_point_spec,
        )
        tracing.execute()
        assert tracing.return_values == [1]
        raise NoError

    if not ((initialization_error and not ignore_initialization_errors) or action_error):
        assert action_finished

    tracing = Tracing(action=(lambda: time.sleep(0.1)))
    tracing.execute()
    assert sum(1 for _ in tracing) == 3


def test_trace_entry_point_audit():
    input_records = [
        frozendict(status=None,        time='2022-02-28T12:34:32.123456Z'),
        frozendict(status='ENQUEUED',  time='2022-02-28T12:35:12.123456Z'),
        frozendict(status=None,        time='2022-02-28T12:35:32.123456Z'),
        frozendict(status='EXECUTING', time='2022-02-28T12:36:12.123456Z'),
        frozendict(status=None,        time='2022-02-28T12:36:32.123456Z'),
        frozendict(status='STOPPING',  time='2022-02-28T12:37:12.123456Z'),
        frozendict(status=None,        time='2022-02-28T12:37:32.123456Z'),
        frozendict(status='ENQUEUED',  time='2022-02-28T12:38:12.123456Z'),
        frozendict(status=None,        time='2022-02-28T12:38:32.123456Z'),
        frozendict(status='EXECUTING', time='2022-02-28T12:39:12.123456Z'),
        frozendict(status=None,        time='2022-02-28T12:39:32.123456Z'),
    ]

    tracing = Tracing(action=(lambda: None), mocks_spec=dict(audit=input_records))
    tracing.execute()
    audit_records = tracing.records_of_type('audit')
    assert len(audit_records) == 3

    last_input_record_with_status = lambda status: next(record for record in reversed(input_records) if record['status'] == status)

    stopping_input_record = last_input_record_with_status('STOPPING')
    enqueued_input_record = last_input_record_with_status('ENQUEUED')
    executing_input_record = last_input_record_with_status('EXECUTING')

    assert audit_records[0].started == microseconds_from_utc_iso(stopping_input_record['time'])
    assert audit_records[0].finished == microseconds_from_utc_iso(enqueued_input_record['time'])
    assert audit_records[0].info == dict(record=stopping_input_record)

    assert audit_records[1].started == microseconds_from_utc_iso(enqueued_input_record['time'])
    assert audit_records[1].finished == microseconds_from_utc_iso(executing_input_record['time'])
    assert audit_records[1].info == dict(record=enqueued_input_record, semaphores=TASK_DEFAULTS['requirements']['semaphores'])

    assert audit_records[2] == tracing.current_audit_record
    assert audit_records[2].started == microseconds_from_utc_iso(executing_input_record['time'])
    assert audit_records[2].info == dict(record=executing_input_record)


def test_trace_new_resources():

    def action():
        with trace_new_resources(info=dict(key='value')) as new_resources:
            new_resources.append(mock_resource(501))
            new_resources.append(mock_resource(502))
            new_resources.extend(mock_resource(resource_id) for resource_id in (503, 504, 505))

    tracing = Tracing(action=action)
    tracing.execute()
    [record] = tracing.records_of_type('new_resources')
    assert record.info['key'] == 'value'
    assert sorted(resource['id'] for resource in record.info['resources']) == [501, 502, 503, 504, 505]
    for resource in record.info['resources']:
        assert isinstance(resource['path'], str)
        assert isinstance(resource['size'], int)
        assert isinstance(resource['state'], str)
        assert set(resource['type']) >= {'module', 'name'}


def test_trace_new_tasks():

    def action():
        with trace_new_tasks(info=dict(key='value')) as new_tasks:
            new_tasks.append(mock_task(501))
            new_tasks.append(mock_task(502))
            new_tasks.extend(mock_task(task_id) for task_id in (503, 504, 505))

    other_tasks_spec = {task_id: dict(input_parameters=dict(task_id=task_id)) for task_id in (501, 502, 503, 504, 505)}
    tracing = Tracing(action=action, mocks_spec=dict(other_tasks_spec=other_tasks_spec))
    tracing.execute()
    [record] = tracing.records_of_type('new_tasks')
    assert record.info['key'] == 'value'
    assert sorted(task['id'] for task in record.info['tasks']) == [501, 502, 503, 504, 505]
    for task in record.info['tasks']:
        assert task['task_type'] == TASK_DEFAULTS['type']
        assert set(task['type']) >= {'module', 'name'}


def test_trace_subprocess():

    def action():
        with trace_subprocess(command=['env', 'time', 'ls', 999], info=dict(key='value')):
            pass

    tracing = Tracing(action=action)
    tracing.execute()
    [record] = tracing.records_of_type('subprocess')
    assert record.info['key'] == 'value'
    assert record.info['command'] == ['env', 'time', 'ls', '999']


@pytest.mark.parametrize('type_', (iter, list, str, tuple), ids=(lambda type_: type_.__name__))
def test_trace_subprocess_calls(type_):
    intended_command = ['ls', '-l', '1 2', 3]
    argument_command = 'ls -l "1 2" 3' if type_ is str else type_(intended_command)

    @trace_subprocess_calls(info=dict(key='value'), save_arguments='all', save_return_value=True)
    def subprocess_run(args, arg1, check=False):
        return [args, arg1, check]

    def action():
        return subprocess_run(argument_command, 'argument1', check=True)

    tracing = Tracing(action=action)
    tracing.execute()

    assert tracing.return_values == [[intended_command if type_ is iter else argument_command, 'argument1', True]]

    [record] = tracing.records_of_type('subprocess')
    assert record.info['command'] == ['ls', '-l', '1 2', '3']
    assert record.info['arguments'] == dict(
        args=[argument_command if type_ is str else intended_command, 'argument1'],
        kwargs=dict(check=True),
    )
    assert record.info['function']['name'] == subprocess_run._wrapped.__name__
    assert record.info['function']['module'] == subprocess_run._wrapped.__module__
    assert record.info['return_value'] == [argument_command if type_ is str else intended_command, 'argument1', True]
    assert record.info['key'] == 'value'
