import asyncio
import json

import pytest

from . import helpers


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.usefixtures('test_opentracing_app')
async def test_nesting_spans_create_task_outside_scope(caplog, tracer):
    helpers.set_tracing_logging(caplog)

    async def inner_func():
        inner = tracer.start_span('inner')
        with tracer.scope_manager.activate(inner):
            await asyncio.sleep(0)

    task = asyncio.ensure_future(inner_func())
    outer = tracer.start_span('outer')
    with tracer.scope_manager.activate(outer):
        await task

    spans = helpers.get_spans(caplog.records, expected=2)
    assert len({json.loads(x.extdict['body'])['trace_id'] for x in spans}) == 2


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.usefixtures('test_opentracing_app')
async def test_nesting_spans_create_task_inside_scope(caplog, tracer):
    helpers.set_tracing_logging(caplog)

    async def inner_func():
        inner = tracer.start_span('inner')
        with tracer.scope_manager.activate(inner):
            pass

    outer = tracer.start_span('outer')
    with tracer.scope_manager.activate(outer):
        task = asyncio.ensure_future(inner_func())
        await task

    spans = helpers.get_spans(caplog.records, expected=2)
    helpers.get_parent(spans)  # expecting only one span without parent_id
