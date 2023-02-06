import asyncio
import json

import pytest

from . import helpers


def _foo():
    pass


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.usefixtures('test_opentracing_app')
async def test_span_reporting(caplog, tracer):
    helpers.set_tracing_logging(caplog)

    async def foo1():
        return 1

    async def foo2():
        return 2

    _span = tracer.start_span('test-operation')
    _span.set_tag('some-tag', 'some-value')

    with tracer.scope_manager.activate(_span):
        result = await asyncio.gather(foo1(), foo2())
    assert result == [1, 2]

    spans = helpers.get_spans(caplog.records, expected=1)
    assert (
        json.loads(spans[0].extdict['body'])['operation_name']
        == 'test-operation'
    )


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.usefixtures('test_opentracing_app')
async def test_gather_nesting_spans(caplog, tracer):
    helpers.set_tracing_logging(caplog)
    outer_span = tracer.start_span('outer_span')
    with tracer.scope_manager.activate(outer_span):
        await helpers.test_inner_func(tracer, outer_span, 'inner_span1')
        await helpers.test_inner_func(tracer, outer_span, 'inner_span2')
        await asyncio.gather(
            helpers.test_inner_func(tracer, outer_span, 'inner_span3'),
            helpers.test_inner_func(tracer, outer_span, 'inner_span4'),
        )

    spans = helpers.get_spans(caplog.records, expected=5)
    parent = helpers.get_parent(spans)
    children = helpers.get_children(spans, expected=4)

    assert parent.extdict['body']['operation_name'] == 'outer_span'
    assert {x.extdict['body']['parent_id'] for x in children} == {
        parent.extdict['body']['span_id'],
    }


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.usefixtures('test_opentracing_app')
async def test_one_raises(caplog, tracer):
    helpers.set_tracing_logging(caplog)

    async def foo1():
        return 1

    async def foo2():
        raise RuntimeError

    _span = tracer.start_span('test-operation')
    _span.set_tag('some-tag', 'some-value')

    with pytest.raises(RuntimeError):
        with tracer.scope_manager.activate(_span):
            await asyncio.gather(foo1(), foo2())

    spans = helpers.get_spans(caplog.records, expected=1)
    parent = helpers.get_parent(spans)
    assert parent.extdict['body']['tags']['error']


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.usefixtures('test_opentracing_app')
async def test_return_exceptions(caplog, tracer):
    helpers.set_tracing_logging(caplog)

    async def foo1():
        return 1

    async def foo2():
        raise RuntimeError

    _span = tracer.start_span('test-operation')
    _span.set_tag('some-tag', 'some-value')

    with tracer.scope_manager.activate(_span):
        await asyncio.gather(foo1(), foo2(), return_exceptions=True)

    spans = helpers.get_spans(caplog.records, expected=1)
    parent = helpers.get_parent(spans)
    assert not parent.extdict['body']['tags']['error']
