from __future__ import unicode_literals

import copy
import datetime
import logging

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import log
from taxi.core.log import util as log_util
from taxi.core.opentracing import const
from taxi.external import stq_agent
from taxi_stq import stq_task


@pytest.inline_callbacks
def test_max_retries(mock):
    queue = 'QUEUE'
    task_id = 'asdf'
    tasks = [
        (5, False, False, 5),
        (1, True, True, 1),
        (11, False, False, 11),
        (1, False, True, 0),
        (20, True, True, 20),
        (11, False, False, 11),
        (1, False, True, 0),
        (11, False, False, 11),
    ]

    @stq_task.task(
        queue=queue,
        max_retry_times=10,
    )
    @mock
    @async.inline_callbacks
    def func(x, y=None):
        if x != 1 or y != 2:
            raise Exception
        assert success
        yield

    counter = 0
    for num, success, good_run, calls in tasks:
        for _ in range(num):
            if good_run:
                yield func(task_id, None, 1, y=2, __stq_exec_tries=counter)
            else:
                with pytest.raises(AssertionError):
                    yield func(task_id, None, 1, y=2, __stq_exec_tries=counter)
            if good_run:
                counter = 0
            else:
                counter += 1
        assert len(func._task_function.calls) == calls


@pytest.inline_callbacks
def test_no_retries(mock):
    queue = 'QUEUE'
    task_id = 'asdf'

    @stq_task.task(
        queue=queue,
    )
    @mock
    @async.inline_callbacks
    def func(x, y=None):
        if x != 1 or y != 2:
            raise Exception
        assert success
        yield

    success = True
    yield func(task_id, None, 1, y=2)
    assert len(func._task_function.calls) == 1
    success = False
    for _ in range(50):
        with pytest.raises(AssertionError):
            yield func(task_id, None, 1, y=2)
    assert len(func._task_function.calls) == 50


@pytest.mark.now('2016-11-01T10:00:00.0+0300')
def test_call(patch, monkeypatch):
    @patch('taxi_stq._client.put')
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        pass

    @patch('uuid.uuid4')
    def uuid4():
        class _uuid4:
            hex = task_id2
        return _uuid4()

    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', False)

    queue = 'QUEUE'
    eta = 123
    task_id = 'task1_id'
    task_id2 = 'task2_id'
    args = (1, 2, 3)
    kwargs = {'x': 4, 'y': 5}

    @stq_task.task(
        queue=queue,
        setup_callback=lambda *args, **kwargs: {
            'lock_id': task_id,
            'log_extra': 'log',
        }
    )
    def task1(i, j, k, x, y):
        pass

    task1.call(*args, **kwargs)
    assert put.calls == [{
        'queue': queue,
        'eta': datetime.datetime.utcnow(),
        'task_id': task_id,
        'args': (task_id, 'log', 1, 2, 3),
        'kwargs': kwargs,
    }]

    task1.call_later(eta, *args, **kwargs)
    assert put.calls == [{
        'queue': queue,
        'eta': datetime.datetime.utcnow() + datetime.timedelta(seconds=eta),
        'task_id': task_id,
        'args': (task_id, 'log', 1, 2, 3),
        'kwargs': kwargs,
    }]

    @stq_task.task(
        queue=queue,
    )
    def task2(i, j, k, x, y):
        pass

    task2.call(*args, **kwargs)
    assert put.calls == [{
        'queue': queue,
        'eta': datetime.datetime.utcnow(),
        'task_id': task_id2,
        'args': (task_id2, None, 1, 2, 3),
        'kwargs': kwargs,
    }]
    task_id2 += '3'
    task2.call_later(eta, *args, **kwargs)
    assert put.calls == [{
        'queue': queue,
        'eta': datetime.datetime.utcnow() + datetime.timedelta(seconds=eta),
        'task_id': task_id2,
        'args': (task_id2, None, 1, 2, 3),
        'kwargs': kwargs,
    }]


@pytest.mark.now('2016-11-01T10:00:00.0+0300')
@pytest.mark.noputmock
def test_call_opentracing(patch, monkeypatch):

    @patch('uuid.uuid4')
    def uuid4():
        class _uuid4:
            hex = 'hex'

        return _uuid4()

    @patch('taxi.core.opentracing.tracer.generate_span_id')
    def generate_span_id():
        return 'hex'

    stq_agent_put_calls = []

    # cause i need explicit copying of all mutable arguments
    @async.inline_callbacks
    def mock_put(queue, eta, task_id, args, kwargs, log_extra,
                 src_tvm_service):
        yield
        stq_agent_put_calls.append({
            'queue': queue,
            'eta': eta,
            'task_id': task_id,
            'args': copy.deepcopy(args),
            'kwargs': copy.deepcopy(kwargs),
            'src_tvm_service': src_tvm_service,
        })
    stq_agent.put = mock_put

    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    monkeypatch.setattr(settings, 'TVM_SRC_SERVICE', 'test-src-service')

    queue = 'QUEUE'
    eta = 123
    task_id = 'task_id'
    task_id2 = 'hex'
    args = (1, 2, 3)
    kwargs = {'x': 4, 'y': 5}

    log_extra = log_util.create_log_extra()
    log_extra_with_opentracing = log_util.copy_extend_log_extra(
        log_extra, **{const.SPAN_ID: 'hex', const.TRACE_ID: 'hex'}
    )
    log_extra_with_opentracing[const.LOG_EXTRA_CONTEXT_FIELD] = {
        const.SPAN_ID: 'hex',
        const.TRACE_ID: 'hex'
    }
    settings.STQ_CLIENTS |= {queue}

    assert queue in settings.STQ_CLIENTS

    @stq_task.task(
        queue=queue,
        setup_callback=lambda *_args, **_kwargs: {
            'lock_id': task_id,
            'log_extra': log_extra,
        }
    )
    def task1(i, j, k, x, y):
        pass

    task1.call(*args, **kwargs)
    assert stq_agent_put_calls[-1] == {
        'queue': queue,
        'eta': datetime.datetime.utcnow(),
        'task_id': task_id,
        'args': (task_id, log_extra_with_opentracing, 1, 2, 3),
        'kwargs': kwargs,
        'src_tvm_service': 'test-src-service',
    }

    task1.call_later(eta, *args, **kwargs)
    assert stq_agent_put_calls[-1] == {
        'queue': queue,
        'eta': datetime.datetime.utcnow() + datetime.timedelta(seconds=eta),
        'task_id': task_id,
        'args': (task_id, log_extra_with_opentracing, 1, 2, 3),
        'kwargs': kwargs,
        'src_tvm_service': 'test-src-service',
    }

    @stq_task.task(
        queue=queue,
    )
    def task2(i, j, k, x, y):
        pass

    task2.call(*args, **kwargs)
    assert stq_agent_put_calls[-1] == {
        'queue': queue,
        'eta': datetime.datetime.utcnow(),
        'task_id': task_id2,
        'args': (task_id2, None, 1, 2, 3),
        'kwargs': kwargs,
        'src_tvm_service': 'test-src-service',
    }

    task2.call_later(eta, *args, **kwargs)
    assert stq_agent_put_calls[-1] == {
        'queue': queue,
        'eta': datetime.datetime.utcnow() + datetime.timedelta(seconds=eta),
        'task_id': task_id2,
        'args': (task_id2, None, 1, 2, 3),
        'kwargs': kwargs,
        'src_tvm_service': 'test-src-service',
    }


def _setup_logger(name):
    logger = logging.getLogger(name)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        log.SyslogConsoleFormatter(fmt=settings.LOG_CONSOLE_FORMAT)
    )
    stream_handler.setLevel(logging.DEBUG)

    while logger.handlers:
        logger.removeHandler(logger.handlers[0])
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)


@pytest.inline_callbacks
def test_logs(capsys, patch, mock):
    _setup_logger('taxi')
    _setup_logger('taxi_stq')

    @stq_task.task(
        queue='test-queue-2',
        setup_callback=lambda *args, **kwargs: {
            'lock_id': 'task_id', 'log_extra': kwargs['log_extra'],
        },
    )
    @mock
    @async.inline_callbacks
    def nested_task(log_extra=None):
        yield
        assert log_extra
        log_extra = log_util.extend_log_extra(
            log_extra,
            some_inner_tag='some_inner_val',
        )
        logger = logging.getLogger('taxi_stq.some_task')
        logger.info('Some inner thing', extra=log_extra)

    @stq_task.task(
        queue='test-queue-1',
        setup_callback=lambda *args, **kwargs: {
            'lock_id': 'task_id', 'log_extra': kwargs['log_extra'],
        },
    )
    @mock
    @async.inline_callbacks
    def task(*args, **kwargs):
        yield
        log_extra = kwargs.get('log_extra')
        assert log_extra
        log_extra = log_util.extend_log_extra(
            log_extra,
            some_tag='some_val',
        )
        logger = logging.getLogger('taxi_stq.some_task')
        logger.info('Some interesting thing', extra=log_extra)

        # mimic passing log_extra by full copy
        # (through mongo or any other external storage)
        _new_log_extra = copy.deepcopy(log_extra)
        yield nested_task(
            'inner_task_id', _new_log_extra, log_extra=_new_log_extra,
        )

    _log_extra = log_util.create_log_extra()
    yield task(
        'task_id', _log_extra, 1, 2, 3, some_arg_key='some_arg_value',
        log_extra=_log_extra,
    )

    _, err = capsys.readouterr()
    lines = err.splitlines()
    all_records = [_make_record_from_tsvk(x) for x in lines]
    stq_finish_logs = [
        x for x in all_records if x.get(u'_type') == u'stq_task_finish'
    ]

    assert len(stq_finish_logs) == 2
    assert stq_finish_logs[0]['level'] == 'INFO'
    stq_task_run_logs = [
        x for x in all_records
        if x.get('stq_run_id') == stq_finish_logs[1]['stq_run_id'] and
        x.get('text') != 'Do not use Write Concern - python'
    ]

    assert len(stq_task_run_logs) == 3
    assert stq_task_run_logs[0]['_type'] == 'stq_task_start'
    assert '\'args\': (1, 2, 3)' in stq_task_run_logs[0]['body']
    assert 'some_arg_key' in stq_task_run_logs[0]['body']
    assert 'some_arg_value' in stq_task_run_logs[0]['body']
    assert stq_task_run_logs[1]['text'] == 'Some interesting thing'
    assert stq_task_run_logs[1]['some_tag'] == 'some_val'
    assert stq_task_run_logs[2]['some_tag'] == 'some_val'
    assert 'some_inner_tag' not in stq_task_run_logs[1]
    assert 'some_inner_tag' not in stq_task_run_logs[2]

    assert 'stq_task_id' not in stq_task_run_logs[1]
    assert (
        stq_task_run_logs[0]['stq_task_id'] ==
        stq_task_run_logs[2]['stq_task_id']
    )

    assert stq_finish_logs[1]['level'] == 'INFO'
    stq_task_run_logs = [
        x for x in all_records
        if x.get('stq_run_id') == stq_finish_logs[0]['stq_run_id']
    ]

    assert len(stq_task_run_logs) == 3
    assert stq_task_run_logs[1]['text'] == 'Some inner thing'
    assert stq_task_run_logs[1]['some_tag'] == 'some_val'
    assert stq_task_run_logs[2]['some_tag'] == 'some_val'
    assert stq_task_run_logs[1]['some_inner_tag'] == 'some_inner_val'
    assert stq_task_run_logs[2]['some_inner_tag'] == 'some_inner_val'


def _make_record_from_tsvk(raw_tsvk):
    return dict(key_val.split(u'=')
                for key_val in raw_tsvk.split('\t')
                if u'=' in key_val)
