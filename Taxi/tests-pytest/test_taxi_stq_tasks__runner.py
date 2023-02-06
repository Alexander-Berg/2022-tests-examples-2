import json
import logging

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import log
from taxi.core.log import util as log_util
from taxi.core.opentracing import const
from taxi.core.opentracing import reference
from taxi.core.opentracing import tags

from taxi_stq import _client
from taxi_stq.tasks import _runner
from taxi_stq.tasks import svo_order_prepare


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


@pytest.mark.parametrize('kwargs', [
    {},
    {'log_extra': log_util.create_log_extra()}
])
@pytest.mark.noputmock
def test_run_and_log(capsys, monkeypatch, patch, kwargs):
    _setup_logger('taxi')
    _setup_logger('taxi_stq')

    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    monkeypatch.setattr(settings, 'OPENTRACING_REPORT_SPAN_ENABLED', True)

    @patch('taxi.external.stq_agent.put')
    def mock_put(queue, eta, task_id, args, kwargs, log_extra,
                 src_tvm_service):
        target = targets[queue]
        return target(*args, **kwargs)

    @_runner.task('task')
    @async.inline_callbacks
    def task(log_extra=None):
        yield
        if log_extra is None:
            return
        log_extra = log_util.extend_log_extra(
            log_extra,
            some_tag='some_val'
        )
        logger = logging.getLogger('taxi_stq.some_task')
        logger.info('Some interesting thing', extra=log_extra)

        assert const.LOG_EXTRA_CONTEXT_FIELD in log_extra

    @_runner.task('task_no_args')
    def task_no_args():
        pass

    targets = {
        'task': task,
        'task_no_args': task_no_args
    }

    settings.STQ_CLIENTS |= {'task', 'task_no_args'}
    _client.put('task', kwargs=kwargs)
    _, err = capsys.readouterr()
    lines = err.splitlines()
    all_records = [_make_record_from_tsvk(x) for x in lines]
    records = [
        x for x in all_records
        if x.get(u'_type') == u'span'
    ]
    if kwargs:
        assert records
        assert len(records) == 2
    else:
        assert not records

    if records:
        child = records[0]
        child['body'] = json.loads(child['body'])
        parent = records[1]
        parent['body'] = json.loads(parent['body'])
        assert child['parent_id'] == parent['span_id']
        assert (child['reference_type'] ==
                reference.ReferenceType.FOLLOWS_FROM.value)
        assert child['trace_id'] == parent['trace_id']
        assert (child['body']['tags'][tags.SPAN_KIND] ==
                tags.SPAN_KIND_CONSUMER)
        assert (parent['body']['tags'][tags.SPAN_KIND] ==
                tags.SPAN_KIND_PRODUCER)

    if kwargs:
        stq_finish_logs = [
            x for x in all_records if x.get(u'_type') == u'stq_task_finish'
        ]
        assert len(stq_finish_logs) == 1
        assert stq_finish_logs[0]['level'] == 'INFO'
        assert stq_finish_logs[0]['trace_id'] == records[0]['trace_id']

        stq_task_run_logs = [
            x for x in all_records
            if x.get('stq_run_id') == stq_finish_logs[0]['stq_run_id']
        ]

        assert len(stq_task_run_logs) == 3
        assert stq_task_run_logs[1]['text'] == 'Some interesting thing'
        assert stq_task_run_logs[1]['some_tag'] == 'some_val'
        assert stq_task_run_logs[2]['some_tag'] == 'some_val'

        assert 'stq_task_id' not in stq_task_run_logs[1]
        assert (
            stq_task_run_logs[0]['stq_task_id'] ==
            stq_task_run_logs[2]['stq_task_id']
        )

    if not kwargs:
        _client.put('task_no_args')


@pytest.mark.noputmock
def test_right_queue_names_in_logs(capsys, patch):
    _setup_logger('taxi')
    _setup_logger('taxi_stq')

    @patch('taxi.external.stq_agent.put')
    def mock_put(queue, eta, task_id, args, kwargs, log_extra,
                 src_tvm_service):
        return svo_order_prepare.task(*args, **kwargs)

    assert 'svo_order_prepare_queue' in settings.STQ_CLIENTS
    _client.put(
        'svo_order_prepare_queue',
        args=('123',), kwargs={'log_extra': log_util.create_log_extra()},
    )
    _, err = capsys.readouterr()
    lines = err.splitlines()
    all_records = [_make_record_from_tsvk(x) for x in lines]
    stq_finish_logs = [
        x for x in all_records if x.get('_type') == 'stq_task_finish'
    ]
    assert len(stq_finish_logs) == 1
    assert stq_finish_logs[0]['queue'] == 'svo_order_prepare_queue'
    assert stq_finish_logs[0]['order_id'] == '123'


def _make_record_from_tsvk(raw_tsvk):
    return dict(key_val.split(u'=', 1)
                for key_val in raw_tsvk.split('\t')
                if u'=' in key_val)
