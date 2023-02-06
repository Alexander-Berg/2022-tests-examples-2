import collections
import copy
import itertools
import json
import logging
import os

import pytest

from taxi.conf import settings
from taxi.core.opentracing import codecs
from taxi.core.opentracing import const
from taxi.core.opentracing import reference
from taxi.core.opentracing import span
from taxi.core.opentracing import tracer


def _make_log_extra(context_num):
    return {
        '_link': 'some link',
        'extdict': {},
        const.LOG_EXTRA_CONTEXT_FIELD: {
            'span_id': 'span-' + str(context_num),
            'trace_id': 'trace-' + str(context_num)
        },
    }


def _span_is_active(_span, log_extra):
    return log_extra[const.LOG_EXTRA_CONTEXT_FIELD] == _span.context.as_dict()


class CaptureHandler(logging.StreamHandler):
    def __init__(self):
        self._fp = open(os.devnull, 'w')
        super(CaptureHandler, self).__init__(stream=self._fp)
        self.records = collections.defaultdict(list)

    def handle(self, record):
        self.records[record.levelname].append(record)
        return super(CaptureHandler, self).handle(record)

    def close(self):
        self._fp.close()
        super(CaptureHandler, self).close()


class LogCaptureFixture(object):
    def __init__(self):
        self._handler = CaptureHandler()
        self._handler.setLevel(logging.DEBUG)
        self._initial_log_levels = {}

    def finalize(self):
        for logger_name, level in self._initial_log_levels.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            logger.removeHandler(self.handler)
        self.handler.records.clear()

    @property
    def handler(self):
        return self._handler

    @property
    def records(self):
        return itertools.chain.from_iterable(self.handler.records.values())

    def set_level(self, level, logger=None):
        logger_name = logger
        logger = logging.getLogger(logger_name)
        # save the original log-level to restore it during teardown
        self._initial_log_levels.setdefault(logger_name, logger.level)
        logger.setLevel(level)
        if self.handler not in logger.handlers:
            logger.addHandler(self.handler)


@pytest.yield_fixture
def caplog():
    result = LogCaptureFixture()
    yield result
    result.finalize()


@pytest.mark.parametrize(
    'format,carrier',
    [
        (codecs.Format.HTTP_HEADERS, {}),
        (codecs.Format.MAPPING, {}),
    ]
)
def test_span_context_serialization(monkeypatch, format, carrier):
    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    context = span.SpanContext(span_id='span-id', trace_id='trace-id')
    _tracer = tracer.global_tracer()
    _tracer.inject(format, context, carrier)
    assert _tracer.extract(format, carrier) == context


@pytest.mark.parametrize(
    'log_extra,expects',
    [
        (None, None),
        ({}, None),
        (_make_log_extra(0), span.SpanContext('span-0', 'trace-0'))
    ]
)
def test_extract_from(monkeypatch, log_extra, expects):
    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    _tracer = tracer.global_tracer()
    log_extra = copy.deepcopy(log_extra)
    assert expects == _tracer.scope_manager.extract_from(log_extra)


@pytest.mark.parametrize(
    'log_extra,context',
    [
        (None, None),
        ({}, None),
        (_make_log_extra(0), span.SpanContext('span-0', 'trace-0'))
    ]
)
def test_inject_to(monkeypatch, log_extra, context):
    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    _tracer = tracer.global_tracer()
    log_extra = copy.deepcopy(log_extra)
    _tracer.scope_manager.inject_to(context, log_extra)
    if context is not None:
        assert (context.as_dict() ==
                log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD))
    elif log_extra is not None:
        assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None


def test_span_creation(monkeypatch):
    def _inner_action(log_extra=None):
        _tracer = tracer.global_tracer()
        _ctx = _tracer.scope_manager.extract_from(log_extra)
        _span = _tracer.start_span(
            'inner-test-op',
            reference=reference.child_of(_ctx),
            log_extra=log_extra
        )
        with _tracer.scope_manager.activate_span(_span, log_extra) as _scope:
            assert _ctx == _scope._to_restore
            assert _span_is_active(_span, log_extra)

    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)

    log_extra = {'_link': 'link'}
    _tracer = tracer.global_tracer()
    _span = _tracer.start_span(operation_name='test-op', log_extra=log_extra)

    assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None
    with _tracer.scope_manager.activate_span(_span, log_extra) as _scope:
        assert _span_is_active(_span, log_extra)
        _inner_action(log_extra=log_extra)
    _scope.close()


def test_span_stack_creation(monkeypatch):
    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    _tracer = tracer.global_tracer()
    log_extra = {}
    assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None
    _span = _tracer.start_span('test-op', log_extra=log_extra)

    with _tracer.scope_manager.activate_span(_span, log_extra):
        assert _span_is_active(_span, log_extra)
        _new_span = _tracer.start_span('test-op-2', log_extra=log_extra)

        with _tracer.scope_manager.activate_span(_new_span, log_extra):
            assert not _span_is_active(_span, log_extra)
            assert _span_is_active(_new_span, log_extra)
            assert _new_span.reference is not None
            assert _new_span.reference.ref_context == _span.context

        assert _span_is_active(_span, log_extra)
    assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None


def test_no_op_tracer(monkeypatch):
    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', False)
    _tracer = tracer.global_tracer()
    log_extra = {}
    assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None
    _span = _tracer.start_span('test-op', log_extra=log_extra)

    with _tracer.scope_manager.activate_span(_span, log_extra):
        assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None
        _new_span = _tracer.start_span('test-op-2', log_extra=log_extra)

        with _tracer.scope_manager.activate_span(_new_span, log_extra):
            assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None
            assert _new_span is _span

        assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None
    assert log_extra.get(const.LOG_EXTRA_CONTEXT_FIELD) is None


def test_reporter_enabled(monkeypatch, caplog):
    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    monkeypatch.setattr(settings, 'OPENTRACING_REPORT_SPAN_ENABLED', True)

    caplog.set_level(logging.INFO, 'taxi.core.opentracing.reporter')

    _tracer = tracer.global_tracer()
    log_extra = {}

    _span = _tracer.start_span('test-op-1', log_extra=log_extra)
    with _tracer.scope_manager.activate_span(_span, log_extra):
        _span = _tracer.start_span('test-op-2', log_extra=log_extra)
        with _tracer.scope_manager.activate_span(_span, log_extra):
            pass

    records = [
        x for x in caplog.records
        if getattr(x, u'extdict', {}).get(u'_type') == u'span'
    ]
    assert len(records) == 2
    record = records[0]
    assert record.levelname == u'INFO'
    assert record.message == u'Span finished'
    assert isinstance(json.loads(record.extdict[u'body']), dict)
    assert records[1].extdict[u'span_id'] == records[0].extdict[u'parent_id']


def test_reporter_disabled(monkeypatch, caplog):
    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    monkeypatch.setattr(settings, 'OPENTRACING_REPORT_SPAN_ENABLED', False)
    caplog.set_level(logging.INFO, 'taxi.core.opentracing.reporter')

    _tracer = tracer.global_tracer()
    log_extra = {}

    _span = _tracer.start_span('test-op-1', log_extra=log_extra)
    with _tracer.scope_manager.activate_span(_span, log_extra):
        _span = _tracer.start_span('test-op-2', log_extra=log_extra)
        with _tracer.scope_manager.activate_span(_span, log_extra):
            pass

    records = [
        x for x in caplog.records
        if getattr(x, u'extdict', {}).get(u'_type') == u'span'
    ]
    assert not records


def test_logging(monkeypatch, caplog):
    monkeypatch.setattr(settings, 'OPENTRACING_ENABLED', True)
    monkeypatch.setattr(settings, 'OPENTRACING_REPORT_SPAN_ENABLED', True)
    caplog.set_level(logging.INFO, 'taxi.core.opentracing.reporter')
    caplog.set_level(logging.INFO, 'test')

    logger = logging.getLogger('test')

    _tracer = tracer.global_tracer()
    log_extra = {}

    _span = _tracer.start_span('test-op-1', log_extra=log_extra)
    with _tracer.scope_manager.activate_span(_span, log_extra):
        _span = _tracer.start_span('test-op-2', log_extra=log_extra)
        with _tracer.scope_manager.activate_span(_span, log_extra):
            logger.info('some test message')

    logs = [
        x for x in caplog.records if
        x and getattr(x, u'extdict', {}).get(u'_type') != u'span' and
        x.levelname == u'INFO'
    ]
    assert logs
