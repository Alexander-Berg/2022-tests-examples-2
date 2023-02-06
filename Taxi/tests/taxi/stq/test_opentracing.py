# pylint: disable=protected-access,too-many-locals
import asyncio
import copy
import datetime
import json
import logging

import pytest

from stq.server.dbhandlers import task_tuple
from taxi import config
from taxi import opentracing
from taxi import settings
from taxi.clients import stq_agent
from taxi.opentracing import tags
from taxi.stq import async_worker_old
from taxi.stq import client


NOW = datetime.datetime(2018, 5, 7, 12, 34, 56)


def dummy_secret(*args, **kwargs):
    return 'hex'


@pytest.mark.parametrize('sampling', [False, True])
@pytest.mark.now(NOW.isoformat())
async def test_producer_creation(
        patch, monkeypatch, mock, loop, caplog, sampling, simple_secdist,
):
    # pylint: disable=too-many-statements
    client.init(
        simple_secdist, set(), None, config.Config(), settings.Settings(),
    )

    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    class ExchangeMock:
        def __init__(self):
            self.identifier = 'worker-queue'
            self.exec_func = None
            self.stop_func = None

        def register_exec(self, func):
            self.exec_func = func

        def register_stop(self, func):
            self.stop_func = func

        @staticmethod
        def recv_command(arg):
            return False

        def exec_callback(self, task_id, *args, **kwargs):
            self.exec_func(task_id, *args, **kwargs)

        @staticmethod
        @mock
        def mark_done(task_id, exec_time):
            pass

        @staticmethod
        @mock
        def mark_failed(task_id, exec_time):
            pass

        @staticmethod
        @mock
        def notify_ready():
            pass

    service_name = 'stq3-test'
    opentracing.init_tracing(
        service_name,
        opentracing.config_mock(
            report_span_enabled=True,
            sampling_probability={service_name: {'es': 1 if sampling else 0}},
        ),
    )

    _reporting_baggage = {'baggage': '{"report": "true"}'}
    test_queue = 'test_queue'
    test_worker_id = async_worker_old.WorkerId(test_queue, 0)
    test_args = ('task_id',)
    _log_extra = {'extdict': {}, '_link': 'hex'}
    _tracing_log_extra_extension = {'trace_id': 'hex', 'span_id': 'hex'}
    test_kwargs = {'some_kwarg': 'kwarg', 'log_extra': _log_extra}
    _log_extra_with_tracing = {'_ot_ctx': _tracing_log_extra_extension}
    if sampling:
        _log_extra_with_tracing['_ot_ctx'] = {
            **_tracing_log_extra_extension,
            **_reporting_baggage,
        }
    kwargs_with_extended_log_extra = {
        **test_kwargs,
        'log_extra': {
            **copy.deepcopy(_log_extra),
            **copy.deepcopy(_log_extra_with_tracing),
        },
    }

    async def task(app, task_id, some_kwarg=None, log_extra=None):
        task_extras = {
            'task_id': 'hex',
            'stq_task_id': 'hex',
            'queue': test_queue,
        }
        assert (task_id,) == test_args
        assert some_kwarg == test_kwargs['some_kwarg']
        expected_log_extra = {
            **_log_extra_with_tracing,
            '_link': 'hex',
            'extdict': {
                **_tracing_log_extra_extension,
                **task_extras,
                'stq_run_id': 'hex',
            },
        }
        assert log_extra == expected_log_extra

    monkeypatch.setattr(async_worker_old._Context, 'task_function', task)
    monkeypatch.setattr(async_worker_old._Context, 'data', object())
    monkeypatch.setattr(async_worker_old._Context, 'exchange', ExchangeMock())
    monkeypatch.setattr(async_worker_old._Context, 'worker_id', test_worker_id)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    # pylint: disable=unused-variable
    @patch('uuid.uuid4')
    def uuid4():
        class _uuid4:
            hex = 'hex'

        return _uuid4()

    put_calls = []
    future = None

    # pylint: disable=unused-variable

    async def mock_put(self, _queue, _eta, _task_id, _args, _kwargs):
        nonlocal future
        put_calls.append(
            {
                'queue': _queue,
                'eta': _eta,
                'task_id': _task_id,
                'args': copy.deepcopy(_args),
                'kwargs': copy.deepcopy(_kwargs),
            },
        )
        future = asyncio.ensure_future(
            async_worker_old._async_exec_task(
                task_tuple.Task(
                    _task_id,
                    exec_tries=0,
                    args=test_args,
                    kwargs=test_kwargs,
                    reschedule_counter=0,
                ),
            ),
            loop=loop,
        )

    monkeypatch.setattr(stq_agent.StqAgentClient, 'put_task', mock_put)

    await client.put(
        queue=test_queue,
        task_id='hex',
        args=test_args,
        kwargs=test_kwargs,
        loop=loop,
    )

    assert put_calls[-1] == {
        'queue': test_queue,
        'eta': None,
        'task_id': 'hex',
        'args': test_args,
        'kwargs': kwargs_with_extended_log_extra,
    }
    await future

    records = [
        x
        for x in caplog.records
        if getattr(x, 'extdict', {}).get('_type') == 'span'
    ]

    if not sampling:
        return

    assert len(records) == 2
    record = records[0]
    assert record.levelname == 'INFO'
    assert json.loads(record.extdict['body']) == {
        **_reporting_baggage,
        'operation_name': test_queue,
        'trace_id': 'hex',
        'span_id': 'hex',
        'start_time': 1525696496.0,
        'stop_time': 1525696496.0,
        'tags': {
            tags.SERVICE: 'stq3-test',
            tags.SPAN_KIND: tags.SPAN_KIND_PRODUCER,
            tags.ERROR: False,
        },
    }
    assert record.extdict['_type'] == 'span'
    assert record.extdict['span_id'] == 'hex'
    assert record.extdict['trace_id'] == 'hex'
    assert 'parent_id' not in record.extdict

    record = records[1]
    body = json.loads(record.extdict['body'])
    assert body == {
        **_reporting_baggage,
        'operation_name': 'task',
        'trace_id': 'hex',
        'span_id': 'hex',
        'start_time': 1525696496.0,
        'stop_time': 1525696496.0,
        'tags': {
            tags.SERVICE: 'stq3-test',
            tags.SPAN_KIND: tags.SPAN_KIND_CONSUMER,
            tags.ERROR: False,
        },
        'parent_id': 'hex',
        'reference_type': 'child_of',
    }
    assert record.extdict['parent_id'] == 'hex'
