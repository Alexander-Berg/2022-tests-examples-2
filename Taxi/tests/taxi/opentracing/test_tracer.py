import pytest

from taxi.opentracing import span


@pytest.mark.usefixtures('test_opentracing_app')
async def test_span_activation(tracer):
    assert tracer.active_span is None

    new_span = tracer.start_span('test operation')
    assert tracer.active_span is not new_span

    scope = tracer.scope_manager.activate(new_span)
    assert tracer.active_span is new_span
    scope.close()

    assert tracer.active_span is not new_span


@pytest.mark.usefixtures('test_opentracing_app')
async def test_span_finalization(tracer):
    new_span = tracer.start_span('test operation')

    assert new_span.stop_time is None

    with tracer.scope_manager.activate(new_span):
        pass

    assert new_span.stop_time is not None


def test_do_nothing_tracer(tracer):
    assert isinstance(tracer.active_span, span.NoOpSpan)
    new_span = tracer.start_span('test operation')
    assert new_span is tracer.active_span

    with tracer.scope_manager.activate(new_span):
        assert new_span is tracer.active_span

    assert new_span is tracer.active_span


@pytest.mark.usefixtures('test_opentracing_app')
async def test_nesting_spans(tracer):
    outer_span = tracer.start_span('outer span')
    with tracer.scope_manager.activate(outer_span):
        assert outer_span is tracer.active_span
        inner_span = tracer.start_span('inner span')
        with tracer.scope_manager.activate(inner_span):
            assert inner_span is tracer.active_span
