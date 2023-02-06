from taxi_tracing.lib import span


def test_span_conversion():
    span_as_dict = {
        'span_id': 1,
        'trace_id': 2,
        'link_id': 3,
        'operation_name': 'some-operation',
        'host': 'some-host',
        'endpoint': 'some-endpoint',
        'start_timestamp': '12345',
        'finish_timestamp': '12345',
        'leaf': False,
        'tags': {},
    }
    assert span_as_dict == span.span_to_dict(span.span_from_dict(span_as_dict))
