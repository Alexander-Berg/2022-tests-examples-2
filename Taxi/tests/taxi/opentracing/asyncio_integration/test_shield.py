import asyncio

import pytest

from . import helpers


def _check_logged_spans(records):
    spans = helpers.get_spans(records, expected=2)
    parent = helpers.get_parent(spans)
    children = helpers.get_children(spans, expected=1)

    assert parent.extdict['body']['operation_name'] == 'outer_span'
    assert {x.extdict['body']['parent_id'] for x in children} == {
        parent.extdict['body']['span_id'],
    }


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.usefixtures('test_opentracing_app')
async def test_nesting_spans(caplog, tracer):
    helpers.set_tracing_logging(caplog)

    outer = tracer.start_span('outer_span')
    with tracer.scope_manager.activate(outer):
        await asyncio.shield(helpers.test_inner_func(tracer, outer))

    _check_logged_spans(caplog.records)


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}},
)
@pytest.mark.usefixtures('test_opentracing_app')
async def test_cancelation(caplog, tracer):
    helpers.set_tracing_logging(caplog)

    result = {}

    async def inner_func():
        outer_span = tracer.start_span('outer_span')
        with tracer.scope_manager.activate(outer_span):
            result['result'] = 'some'
            await helpers.test_inner_func(tracer, outer_span)

    inner_coro = inner_func()
    task = asyncio.ensure_future(asyncio.shield(inner_coro))
    task.cancel()
    assert task.cancelled()

    with pytest.raises(asyncio.CancelledError):
        await task
    await inner_coro

    assert result == {'result': 'some'}

    _check_logged_spans(caplog.records)
