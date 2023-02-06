import datetime

import pytest

NOW = datetime.datetime(2018, 9, 10, 10, 7, 52)


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@0', files=('doc@0.sql', 'event@0.sql'))
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'restore_query,search_query,restore_result,search_result',
    [
        (
            {
                'doc': {
                    'doc_id': 210000,
                    'prev_doc_id': 110000,
                    'topic': 'abc',
                    'external_ref': '456',
                    'kind': 'test',
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {'shoop': 'da whoop'},
                            'entry_ids': [10001, 10002],
                            'revision': 2,
                            'status': 'new',
                            'tags': ['deadfood'],
                            'idempotency_key': 'new',
                        },
                    ],
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-calculators',
                    'service_user_id': 'foo',
                },
                'idempotency_key': 'restore/1',
            },
            {
                'doc_id': 210000,
                'projection': [
                    'doc_id',
                    'prev_doc_id',
                    'kind',
                    'topic',
                    'external_ref',
                    'process_at',
                    'event_at',
                    'created',
                    'service',
                    'service_user_id',
                    'data',
                    'events',
                    'tags',
                ],
            },
            {
                'doc_id': 210000,
                'topic': 'abc',
                'external_ref': '456',
                'kind': 'test',
                'data': {'shoop': 'da whoop'},
                'created': '2018-09-10T07:07:52.019582+00:00',
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'service': 'billing-calculators',
                'service_user_id': 'foo',
                'status': 'new',
                'tags': ['deadfood'],
            },
            {
                'docs': [
                    {
                        'doc_id': 210000,
                        'prev_doc_id': 110000,
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': '456',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-calculators',
                        'service_user_id': 'foo',
                        'data': {'shoop': 'da whoop'},
                        'tags': ['deadfood'],
                        'events': [
                            {
                                'doc_id': 210000,
                                'revision': 2,
                                'data': {'shoop': 'da whoop'},
                                'tags': ['deadfood'],
                                'status': 'new',
                                'entry_ids': [10001, 10002],
                                'idempotency_key': 'new',
                            },
                            {
                                'doc_id': 210000,
                                'revision': 3,
                                'kind': 'restore',
                                'idempotency_key': 'restore/1',
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
async def test_successful_doc_restore(
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        restore_query,
        search_query,
        restore_result,
        search_result,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/restore', json=restore_query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == restore_result, content

    # check idempotency
    response = await taxi_billing_docs_client.post(
        '/v1/docs/restore', json=restore_query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == restore_result, content

    # fetch doc
    response = await taxi_billing_docs_client.post(
        '/v1/docs/search', json=search_query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['docs']) == 1
    doc = content['docs'][0]
    tags = doc['tags']
    for event in doc['events']:
        event.pop('created')
    assert content == search_result, content

    # fetch by tags
    doc_id = doc['doc_id']
    request_tags = tags
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


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@0', files=('doc@0.sql', 'event@0.sql'))
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'restore_query,search_query,search_result',
    [
        # attempt to restore a doc with existed pkey and topic+event_ref
        (
            {
                'doc': {
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'doc_id': 10002,
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {},
                            'doc_id': 10002,
                            'idempotency_key': 'basic idempotency key',
                            'revision': 1,
                            'status': 'new',
                            'tags': ['test_update_tag_index'],
                        },
                    ],
                    'external_ref': 'new->complete',
                    'kind': 'test',
                    'prev_doc_id': 0,
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-docs',
                    'topic': 'queue_3',
                },
                'idempotency_key': 'restore/1',
            },
            {
                'doc_id': 10002,
                'projection': [
                    'doc_id',
                    'prev_doc_id',
                    'kind',
                    'topic',
                    'external_ref',
                    'process_at',
                    'event_at',
                    'created',
                    'service',
                    'service_user_id',
                    'data',
                    'events',
                ],
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 10002,
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'events': [
                            {
                                'created': '2018-09-10T07:07:52.019582+00:00',
                                'doc_id': 10002,
                                'idempotency_key': 'basic idempotency key',
                                'revision': 1,
                                'status': 'new',
                                'tags': ['test_update_tag_index'],
                            },
                        ],
                        'external_ref': 'new->complete',
                        'kind': 'test',
                        'prev_doc_id': 0,
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'topic': 'queue_3',
                    },
                ],
            },
        ),
        # attempt to create a doc with existed pkey
        (
            {
                'doc': {
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'doc_id': 10002,
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {},
                            'doc_id': 10002,
                            'idempotency_key': 'basic idempotency key',
                            'revision': 1,
                            'status': 'new',
                            'tags': ['test_update_tag_index'],
                        },
                    ],
                    'external_ref': 'foo',
                    'kind': 'test',
                    'prev_doc_id': 0,
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-docs',
                    'topic': 'queue_3',
                },
                'idempotency_key': 'restore/1',
            },
            {
                'doc_id': 10002,
                'projection': [
                    'doc_id',
                    'prev_doc_id',
                    'kind',
                    'topic',
                    'external_ref',
                    'process_at',
                    'event_at',
                    'created',
                    'service',
                    'service_user_id',
                    'data',
                    'events',
                ],
            },
            {
                'docs': [
                    {
                        'doc_id': 10002,
                        'prev_doc_id': 0,
                        'kind': 'test',
                        'topic': 'queue_3',
                        'external_ref': 'new->complete',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'data': {},
                        'events': [
                            {
                                'doc_id': 10002,
                                'revision': 1,
                                'created': '2018-09-10T07:07:52.019582+00:00',
                                'tags': ['test_update_tag_index'],
                                'status': 'new',
                                'idempotency_key': 'basic idempotency key',
                            },
                        ],
                    },
                ],
            },
        ),
        # attempt to restore a doc with existed topic+event_ref
        (
            {
                'doc': {
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'doc_id': 110002,
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {},
                            'doc_id': 110002,
                            'idempotency_key': 'basic idempotency key',
                            'revision': 1,
                            'status': 'new',
                            'tags': ['test_update_tag_index'],
                        },
                    ],
                    'external_ref': 'new->complete',
                    'kind': 'test',
                    'prev_doc_id': 0,
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-docs',
                    'topic': 'queue_3',
                },
                'idempotency_key': 'restore/1',
            },
            {
                'external_obj_id': 'queue_3',
                'external_event_ref': 'new->complete',
                'projection': [
                    'doc_id',
                    'prev_doc_id',
                    'kind',
                    'topic',
                    'external_ref',
                    'process_at',
                    'event_at',
                    'created',
                    'service',
                    'service_user_id',
                    'data',
                    'events',
                ],
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 10002,
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'events': [
                            {
                                'created': '2018-09-10T07:07:52.019582+00:00',
                                'doc_id': 10002,
                                'idempotency_key': 'basic idempotency key',
                                'revision': 1,
                                'status': 'new',
                                'tags': ['test_update_tag_index'],
                            },
                        ],
                        'external_ref': 'new->complete',
                        'kind': 'test',
                        'prev_doc_id': 0,
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'topic': 'queue_3',
                    },
                ],
            },
        ),
    ],
)
async def test_restore_with_doc_created(
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        restore_query,
        search_query,
        search_result,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/restore', json=restore_query, headers=request_headers,
    )
    assert response.status == 409

    # fetch doc
    response = await taxi_billing_docs_client.post(
        '/v1/docs/search', json=search_query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == search_result, content


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@0', files=('doc@0.sql', 'event@0.sql'))
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'query',
    [
        (
            # invalid shard
            {
                'doc': {
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'doc_id': 10006,
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {},
                            'doc_id': 10002,
                            'idempotency_key': 'basic idempotency key',
                            'revision': 1,
                            'status': 'new',
                            'tags': ['test_update_tag_index'],
                        },
                    ],
                    'external_ref': 'new->complete',
                    'kind': 'test',
                    'prev_doc_id': 0,
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-docs',
                    'topic': 'queue_3',
                },
                'idempotency_key': 'restore/1',
            }
        ),
        (
            {
                'doc': {
                    'doc_id': 210000,
                    'prev_doc_id': 110000,
                    'topic': 'abc',
                    'external_ref': '456',
                    'kind': 'test',
                    'data': {'shoop': 'da whoop'},
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {'shoop': 'da whoop'},
                            'entry_ids': [10001, 10002],
                            'revision': 2,
                            'status': 'new',
                            'tags': ['deadfood'],
                            'idempotency_key': 'new',
                        },
                    ],
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-calculators',
                    'service_user_id': 'foo',
                },
                'idempotency_key': 'restore/1',
            }
        ),
        (
            {
                'doc': {
                    'doc_id': 210000,
                    'prev_doc_id': 110000,
                    'topic': 'abc',
                    'external_ref': '456',
                    'kind': 'test',
                    'journal_entries': [],
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {'shoop': 'da whoop'},
                            'entry_ids': [10001, 10002],
                            'revision': 2,
                            'status': 'new',
                            'tags': ['deadfood'],
                            'idempotency_key': 'new',
                        },
                    ],
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-calculators',
                    'service_user_id': 'foo',
                },
                'idempotency_key': 'restore/1',
            }
        ),
        {
            'doc': {
                'doc_id': 210000,
                'prev_doc_id': 220000,
                'topic': 'abc',
                'external_ref': '456',
                'kind': 'test',
                'events': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'entry_ids': [10001, 10002],
                        'revision': 2,
                        'status': 'new',
                        'tags': ['deadfood'],
                        'idempotency_key': 'new',
                    },
                ],
                'created': '2018-09-10T07:07:52.019582+00:00',
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'service': 'billing-calculators',
                'service_user_id': 'foo',
            },
            'idempotency_key': 'restore/1',
        },
    ],
)
async def test_restore_bad_requests(
        docs_app, taxi_billing_docs_client, request_headers, query,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/restore', json=query, headers=request_headers,
    )
    assert response.status == 400


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@0', files=('doc@0.sql', 'event@0.sql'))
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'restore_query',
    [
        # invalid doc_id
        (
            {
                'doc': {
                    'doc_id': 50002,
                    'prev_doc_id': 0,
                    'topic': 'abcde',
                    'external_ref': '456',
                    'kind': 'test',
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {'shoop': 'da whoop'},
                            'entry_ids': [10001, 10002],
                            'revision': 4,
                            'status': 'new',
                            'tags': ['deadfood'],
                            'idempotency_key': 'new',
                        },
                    ],
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-calculators',
                    'service_user_id': 'foo',
                },
                'idempotency_key': 'restore/1',
            }
        ),
        # invalid seq_id
        (
            {
                'doc': {
                    'doc_id': 210000,
                    'prev_doc_id': 110000,
                    'topic': 'abc',
                    'external_ref': '456',
                    'kind': 'test',
                    'events': [
                        {
                            'created': '2018-09-10T07:07:52.019582+00:00',
                            'data': {'shoop': 'da whoop'},
                            'entry_ids': [10001, 10002],
                            'revision': 2000,
                            'status': 'new',
                            'tags': ['deadfood'],
                            'idempotency_key': 'new',
                        },
                    ],
                    'created': '2018-09-10T07:07:52.019582+00:00',
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'process_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-calculators',
                    'service_user_id': 'foo',
                },
                'idempotency_key': 'restore/1',
            }
        ),
    ],
)
async def test_restore_with_invalid_sequenses(
        docs_app, taxi_billing_docs_client, request_headers, restore_query,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/restore', json=restore_query, headers=request_headers,
    )
    text = await response.text()
    assert response.status == 409, text
