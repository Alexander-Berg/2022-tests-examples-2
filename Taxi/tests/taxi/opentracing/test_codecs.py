# pylint: disable=protected-access
import json

import pytest

from taxi.opentracing import codecs
from taxi.opentracing import span_context


@pytest.mark.parametrize(
    'codec_cls',
    [codecs.MappingCodec, codecs.HTTPHeaderCodec, codecs.STQMappingCodec],
)
def test_context_identity(codec_cls):
    context = span_context.SpanContext(
        trace_id='1', span_id='2', baggage={'key': 'val'},
    )
    carrier = {}
    codec_cls.inject(context=context, carrier=carrier)
    assert context == codec_cls.extract(carrier=carrier)


@pytest.mark.parametrize(
    'codec_cls', [codecs.MappingCodec, codecs.HTTPHeaderCodec],
)
def test_carrier_identity(codec_cls):
    carrier = {
        codec_cls.TRACE_ID_KEY: '1',
        codec_cls.SPAN_ID_KEY: '2',
        codec_cls.BAGGAGE_KEY: json.dumps({'key': 'val'}),
    }
    context = codec_cls.extract(carrier=carrier)

    new_carrier = {}
    codec_cls.inject(context=context, carrier=new_carrier)
    assert carrier == new_carrier


def test_stq_carrier_identity():
    carrier = {
        codecs.STQMappingCodec.LOG_EXTRA_CONTEXT_FIELD: {
            codecs.STQMappingCodec.SPAN_ID_KEY: '1',
            codecs.STQMappingCodec.TRACE_ID_KEY: '2',
            codecs.STQMappingCodec.BAGGAGE_KEY: json.dumps({'key': 'val'}),
        },
    }
    context = codecs.STQMappingCodec.extract(carrier=carrier)

    new_carrier = {}
    codecs.STQMappingCodec.inject(context=context, carrier=new_carrier)
    assert carrier == new_carrier
