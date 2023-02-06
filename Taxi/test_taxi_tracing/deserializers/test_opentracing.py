import pytest

from taxi.opentracing import tags

from taxi_tracing.lib import span
from taxi_tracing.lib.deserializers import opentracing


@pytest.mark.usefixtures('dummy_uuid4_hex')
def test_eda_format():
    log_record = {
        '_source': {
            'type': 'span',
            'body': (
                '{"start_time":1574934859.4803953,'
                '"stop_time":1574934859.5671186,'
                '"operation_name":"/server/api/v1/export/settings/'
                'couriers-stats",'
                '"trace_id":"a091d055ae5f10f4b70e7f81c33ef42b",'
                '"span_id":"aa950542e102b7019508fb15e2d9bf04",'
                '"parent_id":"aef45798861bec440599ab961d3ed807",'
                '"reference_type":"child_of",'
                '"tags":{"component":"httplib","span.kind":"client",'
                '"http.method":"GET",'
                '"http.url":"https://c3po.eda.tst.yandex.net/'
                'server/api/v1/export/settings/couriers-stats",'
                '"error":true,'
                '"baggage":"{\\\\"report\\\\": \\\\"true\\\\"}"}}'
            ),
            'level': 'INFO',
            'parent_id': 'aef45798861bec440599ab961d3ed807',
            'reference_type': 'child_of',
            'span_id': 'aa950542e102b7019508fb15e2d9bf04',
            'text': '/server/api/v1/export/settings/couriers-stats',
            '@timestamp': '2019-11-28T09:54:19.981Z',
            'total_time': '0.086723',
            'trace_id': 'a091d055ae5f10f4b70e7f81c33ef42b',
            'host': 'myt2-607cdbad1b5c.qloud-c.yandex.net',
            'path': '/var/www/catalog-service/trace.log',
        },
    }
    parsed = (
        opentracing.OpentracingDeserializer().fmt_single(log_record).as_dict()
    )
    assert (
        parsed
        == span.Span(
            span_id='aa950542e102b7019508fb15e2d9bf04',
            trace_id='a091d055ae5f10f4b70e7f81c33ef42b',
            link_id='hex',
            host='myt2-607cdbad1b5c.qloud-c.yandex.net',
            endpoint=(
                'https://c3po.eda.tst.yandex.net/'
                'server/api/v1/export/settings/couriers-stats'
            ),
            start_timestamp=1574934859.4803953,
            finish_timestamp=1574934859.5671186,
            leaf=False,
            operation_name='/server/api/v1/export/settings/couriers-stats',
            tags={
                tags.COMPONENT: 'httplib',
                tags.SPAN_KIND: tags.SPAN_KIND_RPC_CLIENT,
                tags.HTTP_METHOD: 'GET',
                tags.HTTP_URL: (
                    'https://c3po.eda.tst.yandex.net/'
                    'server/api/v1/export/settings/couriers-stats'
                ),
                tags.ERROR: True,
                'baggage': '{"report": "true"}',
            },
        ).as_dict()
    )


@pytest.mark.usefixtures('dummy_uuid4_hex')
def test_json_logged(load_json):
    log_record = load_json('unescaped_span.json')
    parsed = (
        opentracing.OpentracingDeserializer().fmt_single(log_record).as_dict()
    )
    assert (
        parsed
        == span.Span(
            span_id='20fbf7fa6b81cb6e',
            trace_id='ea6ce4ce9c004d6dade376ecf9b0ebd3',
            link_id='hex',
            host='cmvnik5p7gvf2ksg.sas.yp-c.yandex.net',
            endpoint='/v1/available-accounts?service=taxi',
            start_timestamp=1654084299.07062,
            finish_timestamp=1654084299.081998,
            leaf=False,
            operation_name='/v1/balances',
            tags={
                tags.ERROR: False,
                tags.SPAN_KIND: tags.SPAN_KIND_RPC_CLIENT,
                tags.HTTP_METHOD: 'GET',
                tags.SERVICE: 'taxi_personal_wallet_web',
                tags.HTTP_URL: (
                    'http://plus-wallet.taxi.tst.yandex.net/v1/balances'
                ),
                tags.HTTP_STATUS_CODE: 200,
            },
        ).as_dict()
    )
