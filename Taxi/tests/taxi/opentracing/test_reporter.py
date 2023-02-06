# pylint: disable=invalid-name
import datetime
import json
import logging
import uuid

import freezegun
import pytest

from taxi import config
from taxi.logs import log
from taxi.opentracing import reporter
from taxi.opentracing import tags
from taxi.opentracing import tracer as tracer_kit
from taxi.util import dates

NOW = datetime.datetime(2018, 5, 7, 12, 34, 56)


def dummy_secret(*args, **kwargs):
    return 'hex'


class _DummyUUID:
    hex = 'hex'


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.usefixtures('test_opentracing_app')
async def test_log_reporter(tracer, caplog, monkeypatch):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID)
    monkeypatch.setattr(tracer_kit, 'generate_span_id', dummy_secret)

    _reporter = reporter.LogReporter(tracer)
    tracer.reporter = _reporter
    _span = tracer.start_span('test-operation')
    _span.set_tag('some-tag', 'some-value')
    with tracer.scope_manager.activate(_span):
        pass

    record = caplog.records[0]
    assert record.levelname == 'INFO'
    assert json.loads(record.extdict['body']) == {
        'operation_name': 'test-operation',
        'baggage': json.dumps({'report': 'true'}),
        'trace_id': 'hex',
        'span_id': 'hex',
        'start_time': dates.timestamp_us(NOW),
        'stop_time': dates.timestamp_us(NOW),
        'tags': {
            tags.SERVICE: 'testing',
            tags.ERROR: False,
            'some-tag': 'some-value',
        },
    }
    assert record.extdict['_type'] == 'span'
    assert record.extdict['span_id'] == 'hex'
    assert record.extdict['trace_id'] == 'hex'
    assert record.extdict['total_time'] == 0.0
    assert 'parent_id' not in record.extdict


@pytest.mark.config(OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True})
@pytest.mark.usefixtures('test_opentracing_app')
async def test_opentracing_reporter(tracer, caplog, monkeypatch):
    log.init_opentracing_logger('log-ident', True)
    caplog.set_level(logging.INFO, logger='opentracing-logger')
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID)
    monkeypatch.setattr(tracer_kit, 'generate_span_id', dummy_secret)

    _reporter = reporter.OpentracingReporter(tracer)
    tracer.reporter = _reporter
    tracer.service_name = 'test_service'

    _span = tracer.start_span('test-operation')
    _span.set_tag('http.status_code', 200)
    _span.set_tag('span.kind', 'server')
    _span.set_tag('excluded-tag', 'some-value')
    with freezegun.freeze_time('2020-03-23T13:40:00.123456') as timer:
        with tracer.scope_manager.activate(_span):
            timer.tick(200 / (10 ** 6))  # 200 micro seconds

    _reporter.stop()
    record = caplog.records[0]

    span_tags = {tag['key']: tag for tag in json.loads(record.extdict['tags'])}
    assert 'excluded-tag' not in span_tags
    assert span_tags == {
        'http.status_code': {
            'key': 'http.status_code',
            'type': 'int64',
            'value': '200',
        },
        'span.kind': {'key': 'span.kind', 'type': 'string', 'value': 'server'},
        'error': {'key': 'error', 'type': 'bool', 'value': 'false'},
    }

    assert record.extdict['span_id'] == 'hex'
    assert record.extdict['trace_id'] == 'hex'
    assert record.extdict['duration'] == 200
    assert record.extdict['start_time_millis'] == 1584970800123
    assert record.extdict['start_time'] == 1584970800123456
    assert record.extdict['operation_name'] == 'test-operation'
    assert record.extdict['service_name'] == 'test_service'
    assert 'parent_id' not in record.extdict
    log.init_opentracing_logger('log-ident', False)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.usefixtures('test_opentracing_app')
async def test_log_reporter_with_hierarchy(tracer, caplog, monkeypatch):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID)
    monkeypatch.setattr(tracer_kit, 'generate_span_id', dummy_secret)
    monkeypatch.setattr(
        config.Config,
        'OPENTRACING_REPORT_SPAN_ENABLED',
        {'__default__': True},
    )

    _reporter = reporter.LogReporter(tracer)
    tracer.reporter = _reporter

    _span = tracer.start_span('test-operation')
    _span.set_tag('some-tag', 'some-value')
    with tracer.scope_manager.activate(_span):
        _nested_span = tracer.start_span('test-nested-operation')
        with tracer.scope_manager.activate(_nested_span):
            pass

    record = caplog.records[0]
    assert record.extdict['_type'] == 'span'
    assert record.extdict['parent_id'] == 'hex'
    assert (
        json.loads(record.extdict['body'])['operation_name']
        == 'test-nested-operation'
    )

    record = caplog.records[1]
    assert record.extdict['_type'] == 'span'
    assert 'parent_id' not in record.extdict
    assert (
        json.loads(record.extdict['body'])['operation_name']
        == 'test-operation'
    )


@pytest.mark.now(NOW.isoformat())
async def test_log_reporter_without_basic_integration(
        tracer, caplog, monkeypatch,
):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID)
    monkeypatch.setattr(tracer_kit, 'generate_span_id', dummy_secret)

    _reporter = reporter.LogReporter(tracer)
    tracer.reporter = _reporter
    _span = tracer.start_span('test-operation')
    _span.set_tag('some-tag', 'some-value')
    with tracer.scope_manager.activate(_span):
        pass

    record = caplog.records[0]
    assert record.levelname == 'INFO'
    assert json.loads(record.extdict['body']) == {
        'operation_name': 'no op',
        'trace_id': '',
        'span_id': '',
        'start_time': dates.timestamp_us(NOW),
        'stop_time': dates.timestamp_us(NOW),
        'tags': {'some-tag': 'some-value', tags.ERROR: False},
    }
    assert record.extdict['_type'] == 'span'
    assert record.extdict['total_time'] == 0.0


def test_reporter_with_total_time(caplog, monkeypatch, tracer):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID)
    monkeypatch.setattr(tracer_kit, 'generate_span_id', dummy_secret)

    _reporter = reporter.LogReporter(tracer)
    tracer.reporter = _reporter
    _span = tracer.start_span('test-operation')
    _span.set_tag('some-tag', 'some-value')

    with freezegun.freeze_time(NOW) as timer:
        with tracer.scope_manager.activate(_span):
            timer.tick()

    record = caplog.records[0]
    assert record.levelname == 'INFO'
    assert json.loads(record.extdict['body']) == {
        'operation_name': 'no op',
        'trace_id': '',
        'span_id': '',
        'start_time': dates.timestamp_us(NOW),
        'stop_time': dates.timestamp_us(NOW + datetime.timedelta(seconds=1)),
        'tags': {'some-tag': 'some-value', tags.ERROR: False},
    }
    assert record.extdict['_type'] == 'span'
    assert record.extdict['total_time'] == 1.0


@pytest.mark.parametrize(
    'rate, conf, log_should_report, yt_should_report',
    [
        (0.5, {'testing': {'es': 1}}, True, False),
        (1, {'testing': {'es': 0.5}}, False, False),
        (
            0.5,
            {
                'testing': {
                    'es': 0.1,
                    'yt_additional_db': {
                        'base': 1.0,
                        'span_category': {'mongo': 0.6},
                    },
                },
            },
            False,
            True,
        ),
    ],
)
@pytest.mark.parametrize('span_type', ['common', 'db'])
def test_sampling(
        patch,
        monkeypatch,
        rate,
        conf,
        log_should_report,
        yt_should_report,
        span_type,
):
    monkeypatch.setattr(
        config.Config,
        'OPENTRACING_REPORT_SPAN_ENABLED',
        {'__default__': True},
    )
    monkeypatch.setattr(config.Config, 'TRACING_SAMPLING_PROBABILITY', conf)

    @patch('random.random')
    def _random():
        return rate

    _tracer = tracer_kit.Tracer(service_name='testing', config=config.Config)
    log_reporter = reporter.LogReporter(_tracer)
    yt_reporter = reporter.YTReporter(_tracer)

    _span = _tracer.start_span(
        operation_name=span_type,
        tags={tags.SPAN_KIND: tags.SPAN_KIND_RPC_CLIENT},
    )
    if span_type == 'db':
        _span.set_tag(tags.DATABASE_TYPE, tags.DATABASE_MONGO_TYPE)

    assert log_reporter.should_report(_span) == log_should_report

    if span_type == 'db':
        assert yt_reporter.should_report(_span) == yt_should_report

    if span_type == 'common':
        assert yt_reporter.should_report(_span) == log_should_report
