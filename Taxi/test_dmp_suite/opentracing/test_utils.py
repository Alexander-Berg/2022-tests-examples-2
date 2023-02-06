import dmp_suite.opentracing.span
import dmp_suite.opentracing.utils


def test_tracing_span_does_not_raise_error_on_generator_exit():
    span: dmp_suite.opentracing.span.Span

    def gen():
        nonlocal span
        with dmp_suite.opentracing.utils.tracing_span('test') as span:
            yield from 'foo'

    next(gen())

    assert not span.tags['error']
