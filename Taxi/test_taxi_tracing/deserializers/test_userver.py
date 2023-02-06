import pytest

from taxi.opentracing import tags

from taxi_tracing.lib import span
from taxi_tracing.lib.deserializers import userver


def _parse_tskv(item: str):
    pairs = [pairs.split('=', maxsplit=1) for pairs in item.split('\t')]
    return {k: v for k, v in filter(lambda x: len(x) == 2, pairs)}


def _enrich_with_elastic_fields(raw_data: dict):
    raw_data.setdefault('@timestamp', raw_data['timestamp'])
    raw_data.setdefault('cgroups', ['test_service'])
    raw_data.setdefault('host', 'test-host')
    raw_data.setdefault('path', '/var/log/test.log')
    raw_data.setdefault('type', 'log')

    return {'_source': raw_data}


@pytest.mark.usefixtures('dummy_uuid4_hex')
def test_old_format():
    log_record = (
        'tskv	'
        'timestamp=2019-02-25T18:39:52.584088	'
        'timezone=+03:00	'
        'level=INFO	'
        'module=~Impl ( userver/core/src/tracing/span.cpp:92 ) 	'
        'task_id=7FDFCB7FEB00	'
        'coro_id=7FE165A34C68	'
        'text=	'
        'stopwatch_name=http_request	'
        'start_timestamp=1551109192.582381	'
        'total_time=1.70473	'
        'span_ref_type=child	'
        'stopwatch_units=ms	'
        'link=431c4f3666fe4ea9bcf97e203e5bcb98	'
        'http_url=/queue?queue=send_messages_slave	'
        'http_method=POST	'
        'http_status_code=200	'
        'trace_id=70974c7fd6a84d69b550a3adeafe52bd	'
        'span_id=9067eab203e04304a4cc9b2b1d8d5ee8	'
        'parent_id=69ec5a0ccb0344f5a35fd0bb5e15c758'
    )

    elastic_item = _parse_tskv(log_record)
    elastic_item = _enrich_with_elastic_fields(elastic_item)

    deserializer = userver.UserverDeserializer()
    assert (
        deserializer.fmt_single(elastic_item).as_dict()
        == span.Span(
            span_id='9067eab203e04304a4cc9b2b1d8d5ee8',
            trace_id='70974c7fd6a84d69b550a3adeafe52bd',
            link_id='431c4f3666fe4ea9bcf97e203e5bcb98',
            host='test-host',
            endpoint='',
            start_timestamp=1551109192.582381,
            finish_timestamp=1551109192.5840857,
            leaf=False,
            operation_name='http_request',
            tags={
                tags.SERVICE: 'test_service',
                tags.HTTP_URL: '/queue?queue=send_messages_slave',
                tags.HTTP_METHOD: 'POST',
                tags.HTTP_STATUS_CODE: 200,
                tags.ERROR: False,
                tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
            },
        ).as_dict()
    )


@pytest.mark.usefixtures('dummy_uuid4_hex')
def test_new_format():
    log_record = (
        'tskv	'
        'timestamp=2019-02-23T03:26:29.725733	'
        'timezone=+03:00	'
        'level=INFO	'
        'module=~Impl ( userver/core/src/tracing/span.cpp:94 ) 	'
        'task_id=7F07C41C2620	'
        'coro_id=1512160	'
        'thread_id=0x00007F07E9FAF700	'
        'text=	'
        'link=09471b93c12147bb89ec282afb5c7f7a	'
        'meta_type=/tests/control	'
        'type=response	'
        'method=POST	'
        'trace_id=ad51696d48ab4184a0f04b230a50b3ce	'
        'span_id=96b0079cfbb14b84987448bda8e73cf7	'
        'parent_id=82f67033f86e410fa961fdc4bdfdc5fd	'
        'stopwatch_name=cache_invalidate	'
        'start_timestamp=1550881589.113487	'
        'total_time=612.244	'
        'delay=0.612244	'
        'span_ref_type=child	'
        'stopwatch_units=ms '
    )

    elastic_item = _parse_tskv(log_record)
    elastic_item = _enrich_with_elastic_fields(elastic_item)

    deserializer = userver.UserverDeserializer()
    assert (
        deserializer.fmt_single(elastic_item).as_dict()
        == span.Span(
            span_id='96b0079cfbb14b84987448bda8e73cf7',
            trace_id='ad51696d48ab4184a0f04b230a50b3ce',
            link_id='09471b93c12147bb89ec282afb5c7f7a',
            host='test-host',
            endpoint='',
            start_timestamp=1550881589.113487,
            finish_timestamp=1550881589.725731,
            leaf=False,
            operation_name='cache_invalidate',
            tags={
                tags.SERVICE: 'test_service',
                tags.HTTP_URL: '/tests/control',
                tags.HTTP_METHOD: 'POST',
                tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
            },
        ).as_dict()
    )
