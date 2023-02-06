import json
import logging


def set_tracing_logging(caplog):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')


def get_spans(records, *, expected):
    spans = [
        x for x in records if getattr(x, 'extdict', {}).get('_type') == 'span'
    ]
    assert len(spans) == expected
    return spans


def get_parent(records):
    parent = [x for x in records if 'parent_id' not in x.extdict]
    assert len(parent) == 1
    parent = parent[0]
    parent.extdict['body'] = json.loads(parent.extdict['body'])
    return parent


def get_children(records, *, expected):
    children = [x for x in records if 'parent_id' in x.extdict]
    assert len(children) == expected
    ret = []
    for x in children:
        x.extdict['body'] = json.loads(x.extdict['body'])
        ret.append(x)
    return ret


async def test_inner_func(tracer, outer_span, name=None):
    inner = tracer.start_span(name or 'inner_span')
    with tracer.scope_manager.activate(inner):
        assert inner.context.trace_id == outer_span.context.trace_id
        assert inner.context.span_id != outer_span.context.span_id
        assert inner.reference.parent_id == outer_span.context.span_id
