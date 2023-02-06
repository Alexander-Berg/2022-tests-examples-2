import json

import pytest


@pytest.mark.config(
    OPENTRACING_REPORT_SPAN_ENABLED={'__default__': True},
    TRACING_SAMPLING_PROBABILITY={'taxi_tracing': {'es': 1}},
)
@pytest.mark.dontfreeze
async def test_some(caplog, taxi_tracing_client):
    response = await taxi_tracing_client.get('/test-non-recursive')
    assert response.status == 200
    data = await response.json()
    assert data == {
        'contexts': [{'span_id': 1}, {'span_id': 2}],
        'more_contexts': [{'span_id': 1}, {'span_id': 2}],
        'contexts_count': 2,
        'contexts_find_count': 2,
    }
    records = caplog.records
    spans = [
        x for x in records if getattr(x, 'extdict', {}).get('_type') == 'span'
    ]
    assert len(spans) == 6
    assert (
        sorted(
            [
                'find.to_list',
                'find.iter',
                'find.count',
                'count',
                'test-op',
                '/test-non-recursive',
            ],
        )
        == sorted(
            [json.loads(x.extdict['body'])['operation_name'] for x in spans],
        )
    )
    assert {None, 'dbtracing.taxi_tracing_contexts'} == {
        json.loads(x.extdict['body'])['tags'].get('db.instance') for x in spans
    }
