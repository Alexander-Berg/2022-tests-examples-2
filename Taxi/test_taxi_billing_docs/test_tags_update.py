import datetime

import pytest

NOW = datetime.datetime(2018, 9, 10, 10, 7, 52)


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'query',
    [
        {
            'kind': 'test',
            'external_obj_id': 'abc',
            'external_event_ref': 'ride_order_amended_again',
            'event_at': '2018-09-10T07:07:52.019582+00:00',
            'process_at': '2018-09-10T07:07:52.019582+00:00',
            'service': 'billing-docs',
            'service_user_id': 'foobar_user',
            'data': {},
            'status': 'complete',
            'journal_entries': [],
            'tags': [
                'order_id/alias_id1',
                'order_id/alias_id2',
                'order_id/alias_id3',
                'order_id/alias_id4',
                'order_id/alias_id5',
                'order_id/alias_id6',
                'order_id/alias_id7',
                'order_id/alias_id8',
                'custom_tag',
            ],
        },
        {
            'kind': 'test',
            'external_obj_id': 'doc_id_2',
            'external_event_ref': 'ride_order_amended_2',
            'event_at': '2018-09-10T09:07:52.019582+00:00',
            'process_at': '2018-09-10T09:07:52.019582+00:00',
            'service': 'billing-docs',
            'service_user_id': 'foobar_user',
            'data': {},
            'status': 'complete',
            'journal_entries': [],
            'tags': [
                'driver_id/alias_id1',
                'driver_id/alias_id2',
                'driver_id/alias_id3',
                'custom_tag',
            ],
        },
    ],
)
async def test_sync_tag_index_update_1(
        docs_app, taxi_billing_docs_client, request_headers, query,
):
    docs_app.config.BILLING_DOCS_TAG_INDEX_UPDATE_SYNC = True
    response = await taxi_billing_docs_client.post(
        '/v1/docs/create', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    doc_id = content['doc_id']
    request_tags = query['tags']
    by_tag_query = {
        'tags': request_tags,
        'event_at_begin': '2018-01-01T00:00:00.000000+00:00',
        'event_at_end': '2019-01-01T00:00:00.000000+00:00',
    }
    by_tag_response = await taxi_billing_docs_client.post(
        '/v3/docs/by_tag', json=by_tag_query, headers=request_headers,
    )
    assert by_tag_response.status == 200
    docs_by_tag = (await by_tag_response.json())['docs']
    assert len(docs_by_tag) == len(request_tags)
    for tag in request_tags:
        assert len(docs_by_tag[tag]) == 1
        assert docs_by_tag[tag][0]['doc_id'] == doc_id
