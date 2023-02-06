import pymongo.errors
import pytest

from taxi_tracing.lib import db as db_
from taxi_tracing.lib import span


async def test_add_context(db):
    _db = db_.DB(db)
    await _db.add_context(span.SpanContext(None, 'link-id', None))
    assert (await _db.context(link_id='link-id')) is None

    cxt = span.SpanContext(
        span_id='span-id', trace_id='trace-id', link_id=None,
    )
    await _db.add_context(cxt)
    with pytest.raises(pymongo.errors.DuplicateKeyError):
        await _db.add_context(cxt)


async def test_add_span_opentracing(db):
    _db = db_.DB(db)
    _span = span.Span(
        span_id='span-id',
        trace_id='trace-id',
        link_id=None,
        host='localhost',
        endpoint='test-endpoint',
        start_timestamp=1,
        finish_timestamp=2,
        operation_name='test-operation',
        leaf=False,
    )
    await _db.add_span_opentracing(None, _span)

    cxt = await _db.context(span_id='span-id')
    assert cxt == span.context_from_span(_span)
