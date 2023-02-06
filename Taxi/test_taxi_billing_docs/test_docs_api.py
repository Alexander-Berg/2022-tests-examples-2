# pylint: disable=redefined-outer-name,too-many-lines
import datetime
import decimal
import json

import pytest

from taxi.billing import clients as billing_clients
from taxi.billing import util
from taxi.billing.clients.models import billing_accounts
from taxi.billing.util import dates

from taxi_billing_docs import config as docs_config
from taxi_billing_docs.common import db
from taxi_billing_docs.common import models

NOW = datetime.datetime(2018, 9, 10, 10, 7, 52)


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.now(NOW.isoformat())
async def test_duplicate_account_id(taxi_billing_docs_client, request_headers):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/create',
        json={
            'kind': 'test',
            'external_obj_id': 'abc',
            'external_event_ref': 'ride_order_completed',
            'event_at': '2018-09-10T07:07:52.019582+00:00',
            'service': 'billing-docs',
            'data': {},
            'status': 'new',
            'journal_entries': [
                {
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                },
                {
                    'account_id': 10000,
                    'amount': '223.0000',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                },
            ],
        },
        headers=request_headers,
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'status': 'error',
        'message': 'Account IDs must be unique across journal entries',
        'code': 'duplicate-journal-entry-account-id',
    }


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.config(BILLING_DOCS_PAYLOAD_LIMIT=10)
async def test_request_too_large(taxi_billing_docs_client, request_headers):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/create',
        json={
            'kind': 'test',
            'external_obj_id': 'abc',
            'external_event_ref': 'ride_order_completed',
            'event_at': '2018-09-10T07:07:52.019582+00:00',
            'service': 'billing-docs',
            'data': {},
            'status': 'new',
            'journal_entries': [],
        },
        headers=request_headers,
    )
    assert response.status == 413
    content = await response.text()
    assert (
        content
        == 'Maximum request body size 10 exceeded, actual body size 215'
    )


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.now(NOW.isoformat())
async def test_wrong_journal_entry_amount(
        taxi_billing_docs_client, request_headers,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/create',
        json={
            'kind': 'test',
            'external_obj_id': 'abc',
            'external_event_ref': 'ride_order_completed',
            'event_at': '2018-09-10T07:07:52.019582+00:00',
            'service': 'billing-docs',
            'data': {},
            'status': 'new',
            'journal_entries': [
                {
                    'account_id': 10000,
                    'amount': '1E21',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                },
                {
                    'account_id': 10001,
                    'amount': '223.0000',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                },
            ],
        },
        headers=request_headers,
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'status': 'error',
        'message': (
            'Doc contains an entry with amount greater than 1000000000.0'
        ),
        'code': 'invalid-doc-data',
    }


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_DOCS_EMPTY_DOC_DATA={'__default__': False},
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_DOCS_EMPTY_DOC_DATA={'__default__': True},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'query,result,expected_journal_entries',
    [
        (
            {
                'kind': 'test',
                'external_obj_id': 'abc',
                'external_event_ref': 'ride_order_amended_again',
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'service': 'billing-docs',
                'data': {'shoop': 'da whoop'},
                'status': 'new',
                'journal_entries': [
                    {
                        'account_id': 10000,
                        'amount': '123.00001234',
                        'event_at': '2018-09-10T10:07:52.019582+00:00',
                        'reason': '',
                        'details': {'a': 'b'},
                    },
                ],
            },
            {
                'data': {'shoop': 'da whoop'},
                'doc_id': 30000,
                'entry_ids': [],
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'external_event_ref': 'ride_order_amended_again',
                'external_obj_id': 'abc',
                'kind': 'test',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'revision': 3,
                'service': 'billing-docs',
                'status': 'new',
                'tags': [],
            },
            [
                {
                    'journal_entry_id': None,
                    'doc_id': 30000,
                    'amount': decimal.Decimal('123.0000'),
                    'details': json.dumps({'a': 'b'}),
                    'reason': '',
                },
            ],
        ),
        (
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
                'journal_entries': [
                    {
                        'account_id': 10000,
                        'amount': '123.0000',
                        'event_at': '2018-09-10T10:07:52.019582+00:00',
                        'reason': '',
                    },
                    {
                        'account_id': 20000,
                        'amount': '123.00006',
                        'event_at': '2018-09-10T10:07:52.019582+00:00',
                        'reason': 'treason',
                    },
                ],
                'tags': ['order_id/deadf00d'],
            },
            {
                'data': {},
                'doc_id': 30000,
                'entry_ids': [],
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'external_event_ref': 'ride_order_amended_again',
                'external_obj_id': 'abc',
                'kind': 'test',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'revision': 3,
                'service': 'billing-docs',
                'service_user_id': 'foobar_user',
                'status': 'complete',
                'tags': ['order_id/deadf00d'],
            },
            [
                {
                    'journal_entry_id': None,
                    'doc_id': 30000,
                    'amount': decimal.Decimal('123.0000'),
                    'details': None,
                    'reason': '',
                },
                {
                    'journal_entry_id': None,
                    'doc_id': 30000,
                    'amount': decimal.Decimal('123.0001'),
                    'details': None,
                    'reason': 'treason',
                },
            ],
        ),
        (
            {
                'kind': 'test',
                'external_obj_id': 'abc',
                'external_event_ref': 'ride_order_amended_again',
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'service': 'billing-docs',
                'data': {},
                'journal_entries': [],
                'tags': [],
            },
            {
                'data': {},
                'doc_id': 30000,
                'entry_ids': [],
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'external_event_ref': 'ride_order_amended_again',
                'external_obj_id': 'abc',
                'kind': 'test',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'revision': 3,
                'service': 'billing-docs',
                'status': 'new',
                'tags': [],
            },
            [],
        ),
        (
            {
                'kind': 'test',
                'external_obj_id': 'abc',
                'external_event_ref': 'ride_order_amended_again',
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'service': 'billing-docs',
                'data': {'shoop': 'da whoop'},
                'status': 'new',
                'journal_entries': [],
            },
            {
                'data': {'shoop': 'da whoop'},
                'doc_id': 30000,
                'entry_ids': [],
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'external_event_ref': 'ride_order_amended_again',
                'external_obj_id': 'abc',
                'kind': 'test',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'revision': 3,
                'service': 'billing-docs',
                'status': 'new',
                'tags': [],
            },
            [],
        ),
        (
            {
                'kind': 'test',
                'external_obj_id': 'abc',
                'external_event_ref': 'custom_status',
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'service': 'billing-docs',
                'data': {'shoop': 'da whoop'},
                'status': 'custom',
                'journal_entries': [],
            },
            {
                'data': {'shoop': 'da whoop'},
                'doc_id': 30000,
                'entry_ids': [],
                'event_at': '2018-09-10T07:07:52.019582+00:00',
                'external_event_ref': 'custom_status',
                'external_obj_id': 'abc',
                'kind': 'test',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'revision': 3,
                'service': 'billing-docs',
                'status': 'custom',
                'tags': [],
            },
            [],
        ),
    ],
)
async def test_successful_doc_creation(
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        query,
        result,
        expected_journal_entries,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/create', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    content.pop('created')
    assert content == result

    # check idempotency
    response = await taxi_billing_docs_client.post(
        '/v1/docs/create', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    content.pop('created')
    assert content == result

    actual_journal_entries = await _fetch_journal_entries(
        docs_app, result['doc_id'],
    )
    assert expected_journal_entries == actual_journal_entries


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(BILLING_DOCS_TAG_INDEX_UPDATE_SYNC=True)
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
            'journal_entries': [
                {
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                },
                {
                    'account_id': 20000,
                    'amount': '123.00006',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': 'treason',
                },
            ],
            'tags': ['order_id/deadf00d'],
        },
    ],
)
async def test_sync_tag_index_update(
        docs_app, taxi_billing_docs_client, request_headers, query,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/create', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    doc_id = content['doc_id']
    request_tags = query['tags']
    by_tag_query = {
        'tags': request_tags,
        'event_at_begin': '2001-01-01T00:00:00.000000+00:00',
        'event_at_end': '2199-01-01T00:00:00.000000+00:00',
    }
    by_tag_response = await taxi_billing_docs_client.post(
        '/v3/docs/by_tag', json=by_tag_query, headers=request_headers,
    )
    assert by_tag_response.status == 200
    docs_by_tag = (await by_tag_response.json())['docs']
    for tag in request_tags:
        assert docs_by_tag[tag][0]['doc_id'] == doc_id


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'query',
    [
        {'doc_id': 'isteklyal'},
        {'doc_id': None},
        {'doc_id': 0},
        {'doc_id': -1},
        {'doc_id': 10000, 'external_obj_id': 'abc'},
        {'external_obj_id': 123},
        {'external_obj_id': None},
        {'external_obj_id': 'abc', 'additional_property': 'value'},
        {'external_obj_id': 'abc', 'projection': ['doc_id', 'unknown_field']},
    ],
)
async def test_bad_search_requests(
        taxi_billing_docs_client, query, request_headers,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/search', json=query, headers=request_headers,
    )
    assert response.status == 400


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'query,result',
    [
        ({'doc_id': 22220004}, {'docs': []}),
        (
            {'doc_id': 10004},
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 10004,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_completed',
                        'external_obj_id': 'abcdef',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [],
                    },
                ],
            },
        ),
        (
            {'doc_id': 20000},
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': ['deadfood'],
                    },
                ],
            },
        ),
        (
            {'doc_id': 20000, 'use_master': True},
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': ['deadfood'],
                    },
                ],
            },
        ),
        (
            {'external_obj_id': 'abc'},
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 10000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_completed',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [],
                    },
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': ['deadfood'],
                    },
                ],
            },
        ),
        (
            {'external_obj_id': 'abc', 'use_master': True},
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 10000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_completed',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [],
                    },
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': ['deadfood'],
                    },
                ],
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'external_event_ref': 'ride_order_amended',
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': ['deadfood'],
                    },
                ],
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'external_event_ref': 'ride_order_amended',
                'projection': [],
            },
            {'docs': [{'doc_id': 20000}]},
        ),
        (
            {
                'doc_id': 20000,
                'projection': [
                    'doc_id',
                    'prev_doc_id',
                    'kind',
                    'kind',
                    'external_obj_id',
                    'external_event_ref',
                    'process_at',
                    'event_at',
                    'created',
                    'service',
                    'service_user_id',
                    'data',
                    'status',
                    'tags',
                    'revision',
                    'entry_ids',
                    'events',
                    'journal_entries',
                ],
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'events': [
                            {
                                'created': '2018-09-10T07:07:52.019582+00:00',
                                'doc_id': 20000,
                                'revision': 2,
                                'status': 'new',
                                'tags': ['deadfood'],
                            },
                        ],
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': 'abc',
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '123.0000',
                                'details': {'a': 1},
                                'doc_id': 20000,
                                'event_at': '2018-09-10T10:07:52.000000+00:00',
                                'reason': '',
                            },
                        ],
                        'kind': 'test',
                        'prev_doc_id': 10000,
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': ['deadfood'],
                    },
                ],
            },
        ),
    ],
)
async def test_good_search_requests(
        taxi_billing_docs_client, query, result, request_headers,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/search', json=query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == result, content


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'query,result',
    [
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 10000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_completed',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [],
                    },
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': ['deadfood'],
                    },
                ],
                'cursor': '2018-09-10T07:07:52.019582+00:00/20000',
                'limit': 100,
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-10-10T07:07:52.019582+00:00',
                'event_at_end': '2018-11-10T07:07:52.019582+00:00',
            },
            {'docs': [], 'limit': 100, 'cursor': ''},
        ),
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 10000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_completed',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [],
                    },
                ],
                'cursor': '2018-09-10T07:07:52.019582+00:00/10000',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'cursor': '2018-09-10T07:07:52.019582+00:00/10000',
                'limit': 1,
                'use_master': False,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': 'abc',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': ['deadfood'],
                    },
                ],
                'cursor': '2018-09-10T07:07:52.019582+00:00/20000',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'cursor': '2018-09-10T07:07:52.019582+00:00/20000',
                'limit': 1,
                'use_master': True,
            },
            {
                'docs': [],
                'limit': 1,
                'cursor': '2018-09-10T07:07:52.019582+00:00/20000',
            },
        ),
        (
            {
                'external_obj_id': 'select_docs_test',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'sort': 'desc',
                'limit': 2,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-11T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 80002,
                        'entry_ids': [],
                        'event_at': '2018-09-11T07:07:52.019582+00:00',
                        'external_event_ref': '4',
                        'external_obj_id': 'select_docs_test',
                        'kind': 'test',
                        'process_at': '2018-09-11T07:07:52.019582+00:00',
                        'revision': 4,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                    {
                        'created': '2018-09-11T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 70002,
                        'entry_ids': [],
                        'event_at': '2018-09-11T07:07:52.019582+00:00',
                        'external_event_ref': '3',
                        'external_obj_id': 'select_docs_test',
                        'kind': 'test',
                        'process_at': '2018-09-11T07:07:52.019582+00:00',
                        'revision': 3,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                ],
                'cursor': '2018-09-11T07:07:52.019582+00:00/70002',
                'limit': 2,
            },
        ),
        (
            {
                'external_obj_id': 'select_docs_test',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'sort': 'desc',
                'cursor': '2018-09-11T07:07:52.019582+00:00/70002',
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 60002,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': '2',
                        'external_obj_id': 'select_docs_test',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                ],
                'cursor': '2018-09-10T07:07:52.019582+00:00/60002',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'select_docs_test',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'sort': 'desc',
                'cursor': '2018-09-10T07:07:52.019582+00:00/60002',
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 50002,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': '1',
                        'external_obj_id': 'select_docs_test',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                ],
                'cursor': '2018-09-10T07:07:52.019582+00:00/50002',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'select_docs_test',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'sort': 'asc',
                'limit': 2,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 50002,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': '1',
                        'external_obj_id': 'select_docs_test',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 60002,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': '2',
                        'external_obj_id': 'select_docs_test',
                        'kind': 'test',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                ],
                'cursor': '2018-09-10T07:07:52.019582+00:00/60002',
                'limit': 2,
            },
        ),
        (
            {
                'external_obj_id': 'select_docs_test',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'sort': 'asc',
                'cursor': '2018-09-10T07:07:52.019582+00:00/60002',
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-11T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 70002,
                        'entry_ids': [],
                        'event_at': '2018-09-11T07:07:52.019582+00:00',
                        'external_event_ref': '3',
                        'external_obj_id': 'select_docs_test',
                        'kind': 'test',
                        'process_at': '2018-09-11T07:07:52.019582+00:00',
                        'revision': 3,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                ],
                'cursor': '2018-09-11T07:07:52.019582+00:00/70002',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'select_docs_test',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'sort': 'asc',
                'cursor': '2018-09-11T07:07:52.019582+00:00/70002',
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-11T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 80002,
                        'entry_ids': [],
                        'event_at': '2018-09-11T07:07:52.019582+00:00',
                        'external_event_ref': '4',
                        'external_obj_id': 'select_docs_test',
                        'kind': 'test',
                        'process_at': '2018-09-11T07:07:52.019582+00:00',
                        'revision': 4,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                ],
                'cursor': '2018-09-11T07:07:52.019582+00:00/80002',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'select_test_dets',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'sort': 'asc',
                'cursor': '',
                'limit': 2,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-11T07:07:52.019582+00:00',
                        'data': {'reason': 'Skipped by version'},
                        'doc_id': 90002,
                        'entry_ids': [],
                        'event_at': '2018-09-11T07:07:52.019582+00:00',
                        'external_event_ref': '5',
                        'external_obj_id': 'select_test_dets',
                        'kind': 'test_details',
                        'process_at': '2018-09-11T07:07:52.019582+00:00',
                        'revision': 5,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                    {
                        'created': '2018-09-11T07:07:52.019582+00:00',
                        'data': {
                            'doc_field': {'some_key': 'some_data'},
                            'field_1': 'info_1',
                            'field_2': 'info_2',
                            'reason': 'reason_2',
                        },
                        'doc_id': 100002,
                        'entry_ids': [],
                        'event_at': '2018-09-11T07:07:52.019582+00:00',
                        'external_event_ref': '6',
                        'external_obj_id': 'select_test_dets',
                        'kind': 'test_details',
                        'process_at': '2018-09-11T07:07:52.019582+00:00',
                        'revision': 7,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                    },
                ],
                'cursor': '2018-09-11T07:07:52.019582+00:00/100002',
                'limit': 2,
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'projection': [],
                'limit': 1,
            },
            {
                'docs': [{'doc_id': 10000}],
                'cursor': '2018-09-10T07:07:52.019582+00:00/10000',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'projection': ['external_event_ref', 'external_obj_id'],
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'doc_id': 10000,
                        'external_event_ref': 'ride_order_completed',
                        'external_obj_id': 'abc',
                    },
                ],
                'cursor': '2018-09-10T07:07:52.019582+00:00/10000',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'projection': ['external_ref', 'topic'],
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'doc_id': 10000,
                        'external_ref': 'ride_order_completed',
                        'topic': 'abc',
                    },
                ],
                'cursor': '2018-09-10T07:07:52.019582+00:00/10000',
                'limit': 1,
            },
        ),
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'projection': [
                    'doc_id',
                    'prev_doc_id',
                    'kind',
                    'kind',
                    'external_obj_id',
                    'external_event_ref',
                    'process_at',
                    'event_at',
                    'created',
                    'service',
                    'service_user_id',
                    'data',
                    'status',
                    'tags',
                    'revision',
                    'entry_ids',
                    'events',
                    'journal_entries',
                ],
                'limit': 1,
            },
            {
                'cursor': '2018-09-10T07:07:52.019582+00:00/10000',
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 10000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'events': [
                            {
                                'created': '2018-09-10T07:07:52.019582+00:00',
                                'doc_id': 10000,
                                'revision': 1,
                                'status': 'new',
                            },
                        ],
                        'external_event_ref': 'ride_order_completed',
                        'external_obj_id': 'abc',
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '123.0000',
                                'doc_id': 10000,
                                'event_at': '2018-09-10T10:07:52.019582+00:00',
                                'reason': '',
                            },
                        ],
                        'kind': 'test',
                        'prev_doc_id': 0,
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [],
                    },
                ],
                'limit': 1,
            },
        ),
    ],
)
async def test_select(
        taxi_billing_docs_client, query, result, request_headers,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/select', json=query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == result, content


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'query',
    [
        (
            {
                'external_obj_id': 'abc',
                'event_at_begin': '2018-08-10T07:07:52.019582+00:00',
                'event_at_end': '2018-10-10T07:07:52.019582+00:00',
                'projection': ['doc_id', 'unknown_field'],
                'limit': 1,
            }
        ),
    ],
)
async def test_invalid_select(
        taxi_billing_docs_client, query, request_headers,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/select', json=query, headers=request_headers,
    )
    assert response.status == 400


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
async def test_is_ready_for_processing(
        taxi_billing_docs_client, request_headers,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/is_ready_for_processing',
        json={'doc_id': 20004},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['ready']

    response = await taxi_billing_docs_client.post(
        '/v1/docs/is_ready_for_processing',
        json={'doc_id': 30004},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['ready']

    response = await taxi_billing_docs_client.post(
        '/v1/docs/is_ready_for_processing',
        json={'doc_id': 40004},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['ready']

    response = await taxi_billing_docs_client.post(
        '/v1/docs/is_ready_for_processing',
        json={'doc_id': 50004},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert not content['ready']


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(BILLING_DOCS_EVENT_KIND_UPDATE=False),
        ),
        pytest.param(
            marks=pytest.mark.config(BILLING_DOCS_EVENT_KIND_UPDATE=True),
        ),
    ],
)
async def test_finish_processing(taxi_billing_docs_client, request_headers):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/finish_processing',
        json={'doc_id': 10002},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['status'] == 'complete'

    response = await taxi_billing_docs_client.post(
        '/v1/docs/finish_processing',
        json={'doc_id': 20002, 'details': {'reason': 'ok'}},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['status'] == 'complete'

    response = await taxi_billing_docs_client.post(
        '/v1/docs/finish_processing',
        json={'doc_id': 30002},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['status'] == 'complete'

    response = await taxi_billing_docs_client.post(
        '/v1/docs/finish_processing',
        json={'doc_id': 30002, 'details': {'reason': 'again'}},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['status'] == 'complete'


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(BILLING_DOCS_EVENT_KIND_UPDATE=False),
        ),
        pytest.param(
            marks=pytest.mark.config(BILLING_DOCS_EVENT_KIND_UPDATE=True),
        ),
    ],
)
async def test_docs_update(taxi_billing_docs_client, request_headers):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/update', json={}, headers=request_headers,
    )
    assert response.status == 400

    request = {
        'doc_id': 10002,
        'data': {'some data': 'some value'},
        'idempotency_key': 'change document state',
        'status': 'new',
    }
    expected_response = {
        'created': '2018-09-10T07:07:52.019582+00:00',
        'data': {'some data': 'some value'},
        'doc_id': 10002,
        'entry_ids': [],
        'event_at': '2018-09-10T07:07:52.019582+00:00',
        'external_event_ref': 'new->complete',
        'external_obj_id': 'queue_3',
        'kind': 'test',
        'process_at': '2018-09-10T07:07:52.019582+00:00',
        'revision': 5,
        'service': 'billing-docs',
        'status': 'new',
        'tags': ['test_update_tag_index'],
    }
    response = await taxi_billing_docs_client.post(
        '/v1/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response

    request = {
        'doc_id': 10002,
        'data': {},
        'idempotency_key': 'finish document',
        'status': 'complete',
    }
    expected_response = {
        'created': '2018-09-10T07:07:52.019582+00:00',
        'data': {'some data': 'some value'},
        'doc_id': 10002,
        'entry_ids': [],
        'event_at': '2018-09-10T07:07:52.019582+00:00',
        'external_event_ref': 'new->complete',
        'external_obj_id': 'queue_3',
        'kind': 'test',
        'process_at': '2018-09-10T07:07:52.019582+00:00',
        'revision': 6,
        'service': 'billing-docs',
        'status': 'complete',
        'tags': ['test_update_tag_index'],
    }
    response = await taxi_billing_docs_client.post(
        '/v1/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response

    request = {
        'doc_id': 10002,
        'data': {},
        'idempotency_key': 'change finished document',
        'status': 'complete',
    }
    response = await taxi_billing_docs_client.post(
        '/v1/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 409

    request = {
        'doc_id': 20002,
        'data': {'reason': 'ok'},
        'idempotency_key': 'change document state',
        'status': 'new',
    }
    expected_response = {
        'created': '2018-09-10T07:07:52.019582+00:00',
        'data': {'reason': 'ok'},
        'doc_id': 20002,
        'entry_ids': [],
        'event_at': '2018-09-10T07:07:52.019582+00:00',
        'external_event_ref': 'new->complete with details',
        'external_obj_id': 'queue_3',
        'kind': 'test',
        'process_at': '2018-09-10T07:07:52.019582+00:00',
        'revision': 7,
        'service': 'billing-docs',
        'status': 'new',
        'tags': [],
    }
    response = await taxi_billing_docs_client.post(
        '/v1/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response

    request = {
        'doc_id': 20002,
        'data': {'test': 'test'},
        'idempotency_key': 'previous idempotency_key',
        'status': 'new',
    }
    expected_response = {
        'created': '2018-09-10T07:07:52.019582+00:00',
        'data': {'reason': 'ok', 'test': 'test'},
        'doc_id': 20002,
        'entry_ids': [],
        'event_at': '2018-09-10T07:07:52.019582+00:00',
        'external_event_ref': 'new->complete with details',
        'external_obj_id': 'queue_3',
        'kind': 'test',
        'process_at': '2018-09-10T07:07:52.019582+00:00',
        'revision': 8,
        'service': 'billing-docs',
        'status': 'new',
        'tags': [],
    }
    response = await taxi_billing_docs_client.post(
        '/v1/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response

    request = {
        'doc_id': 20002,
        'data': {'new test': 'new test'},
        'idempotency_key': 'previous idempotency_key',
        'status': 'new',
    }
    expected_response = {
        'created': '2018-09-10T07:07:52.019582+00:00',
        'data': {'reason': 'ok', 'test': 'test'},
        'doc_id': 20002,
        'entry_ids': [],
        'event_at': '2018-09-10T07:07:52.019582+00:00',
        'external_event_ref': 'new->complete with details',
        'external_obj_id': 'queue_3',
        'kind': 'test',
        'process_at': '2018-09-10T07:07:52.019582+00:00',
        'revision': 8,
        'service': 'billing-docs',
        'status': 'new',
        'tags': [],
    }
    response = await taxi_billing_docs_client.post(
        '/v1/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response

    request = {
        'doc_id': 30002,
        'data': {},
        'idempotency_key': 'change document state',
        'status': 'new',
    }
    response = await taxi_billing_docs_client.post(
        '/v1/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 409


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
async def test_docs_update_v2(taxi_billing_docs_client, request_headers):
    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json={}, headers=request_headers,
    )
    assert response.status == 400

    request = {
        'doc_id': 10002,
        'data': {'some data': 'some value'},
        'revision': 1,
        'entry_ids': [12345],
        'idempotency_key': 'change document state',
        'status': 'new',
    }
    expected_response = {
        'data': {'some data': 'some value'},
        'doc_id': 10002,
        'entry_ids': [12345],
        'idempotency_key': 'change document state',
        'revision': 5,
        'status': 'new',
    }
    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    content.pop('created')
    assert content == expected_response

    request = {
        'doc_id': 10002,
        'data': {},
        'revision': 5,
        'entry_ids': [],
        'idempotency_key': 'finish document',
        'status': 'complete',
    }
    expected_response = {
        'data': {},
        'entry_ids': [],
        'doc_id': 10002,
        'idempotency_key': 'finish document',
        'revision': 6,
        'status': 'complete',
    }
    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    content.pop('created')
    assert content == expected_response

    request = {
        'doc_id': 10002,
        'data': {},
        'revision': 6,
        'entry_ids': [],
        'idempotency_key': 'change finished document',
        'status': 'complete',
    }
    expected_response = {
        'doc_id': 10002,
        'revision': 7,
        'data': {},
        'status': 'complete',
        'entry_ids': [],
        'idempotency_key': 'change finished document',
    }
    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    content.pop('created')
    assert content == expected_response

    request = {
        'doc_id': 20002,
        'data': {'reason': 'ok'},
        'revision': 2,
        'entry_ids': [],
        'idempotency_key': 'change document state',
        'status': 'new',
    }
    expected_response = {
        'data': {'reason': 'ok'},
        'entry_ids': [],
        'doc_id': 20002,
        'idempotency_key': 'change document state',
        'revision': 8,
        'status': 'new',
    }
    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    content.pop('created')
    assert content == expected_response

    request = {
        'doc_id': 20002,
        'data': {'test': 'test'},
        'revision': 8,
        'entry_ids': [],
        'idempotency_key': 'previous idempotency_key',
        'status': 'new',
    }
    expected_response = {
        'data': {'test': 'test'},
        'entry_ids': [],
        'doc_id': 20002,
        'idempotency_key': 'previous idempotency_key',
        'revision': 9,
        'status': 'new',
    }
    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    content.pop('created')
    assert content == expected_response

    request = {
        'doc_id': 20002,
        'data': {'new test': 'new test'},
        'revision': 9,
        'entry_ids': [51324323, 32351122],
        'idempotency_key': 'previous idempotency_key',
        'status': 'new',
    }
    expected_response = {
        'data': {'test': 'test'},
        'entry_ids': [],
        'doc_id': 20002,
        'idempotency_key': 'previous idempotency_key',
        'revision': 9,
        'status': 'new',
    }
    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    content.pop('created')
    assert content == expected_response

    request = {
        'doc_id': 20002,
        'data': {'new test': 'new test'},
        'revision': 9,
        'entry_ids': [51324323, 32351122],
        'idempotency_key': 'new idempotency_key',
        'status': 'new',
    }
    expected_response = {
        'data': {'new test': 'new test'},
        'entry_ids': [51324323, 32351122],
        'doc_id': 20002,
        'idempotency_key': 'new idempotency_key',
        'revision': 10,
        'status': 'new',
    }
    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    content.pop('created')
    assert content == expected_response

    request = {
        'doc_id': 20002,
        'data': {'new test': 'new test'},
        'revision': 9,
        'entry_ids': [51324323, 32351122],
        'idempotency_key': 'new idempotency_key but old revision',
        'status': 'new',
    }

    response = await taxi_billing_docs_client.post(
        '/v2/docs/update', json=request, headers=request_headers,
    )
    assert response.status == 409


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=(
        'test_by_tag/doc@0.sql',
        'test_by_tag/event@0.sql',
        'test_by_tag/tag_index@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_docs@1',
    files=('test_by_tag/doc@1.sql', 'test_by_tag/event@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'query,result',
    [
        # Searching by tag that does not exist
        (
            {
                'tag': 'abcdef',
                'event_at_begin': '2018-01-01T00:00:00.000000+00:00',
                'event_at_end': '2020-01-01T00:00:00.000000+00:00',
            },
            {
                'docs': [],
                'cursor': {
                    'event_at': '0001-01-01T00:00:00.000000+00:00',
                    'doc_id': 0,
                },
            },
        ),
        # Searching in an unpopulated date range
        (
            {
                'tag': 'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                'event_at_begin': '2016-01-01T00:00:00.000000+00:00',
                'event_at_end': '2017-01-01T00:00:00.000000+00:00',
            },
            {
                'docs': [],
                'cursor': {
                    'event_at': '0001-01-01T00:00:00.000000+00:00',
                    'doc_id': 0,
                },
            },
        ),
        # Searching without limit, expecting the handle to use the default
        # limit of 100, thus retrieving all the docs.
        (
            {
                'tag': 'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                'event_at_begin': '2018-09-09T00:00:00.000000+00:00',
                'event_at_end': '2019-01-01T00:00:00.000000+00:00',
            },
            {
                'docs': [
                    {
                        'created': '2018-09-09T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 50002,
                        'entry_ids': [],
                        'event_at': '2018-09-09T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/1/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/ee2c3590533744cda11b5e5fc00ffebf'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-09T07:07:52.019582+00:00',
                        'revision': 5,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': (
                            'alias_id/10b3a1c7dff04f0cb17a2374ef1bfe4d'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 60004,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/1/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/6c41503787c149cbb7b650ab3d6ea44c'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 7,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                    {
                        'created': '2018-09-11T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 60002,
                        'entry_ids': [],
                        'event_at': '2018-09-11T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/2/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/ee2c3590533744cda11b5e5fc00ffebf'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-11T07:07:52.019582+00:00',
                        'revision': 6,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                    {
                        'created': '2018-09-12T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 70004,
                        'entry_ids': [],
                        'event_at': '2018-09-12T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/2/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/6c41503787c149cbb7b650ab3d6ea44c'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-12T07:07:52.019582+00:00',
                        'revision': 8,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                    {
                        'created': '2018-09-13T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 70002,
                        'entry_ids': [],
                        'event_at': '2018-09-13T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/3/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/ee2c3590533744cda11b5e5fc00ffebf'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-13T07:07:52.019582+00:00',
                        'revision': 7,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                    {
                        'created': '2018-09-14T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 80004,
                        'entry_ids': [],
                        'event_at': '2018-09-14T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/3/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/6c41503787c149cbb7b650ab3d6ea44c'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-14T07:07:52.019582+00:00',
                        'revision': 9,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                ],
                'cursor': {
                    'event_at': '2018-09-14T07:07:52.019582+00:00',
                    'doc_id': 80004,
                },
            },
        ),
        # Repeat the same request and specify the cursor from response
        # We expect an empty result
        (
            {
                'tag': 'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                'event_at_begin': '2018-09-09T00:00:00.000000+00:00',
                'event_at_end': '2019-01-01T00:00:00.000000+00:00',
                'cursor': {
                    'event_at': '2018-09-14T07:07:52.019582+00:00',
                    'doc_id': 80004,
                },
            },
            {
                'docs': [],
                'cursor': {
                    'event_at': '2018-09-14T07:07:52.019582+00:00',
                    'doc_id': 80004,
                },
            },
        ),
        # We expect the handle to retrieve 1 doc when limit is set to 1
        (
            {
                'tag': 'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                'event_at_begin': '2018-09-10T00:00:00.000000+00:00',
                'event_at_end': '2019-01-01T00:00:00.000000+00:00',
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 20000,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': 'ride_order_amended',
                        'external_obj_id': (
                            'alias_id/10b3a1c7dff04f0cb17a2374ef1bfe4d'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                ],
                'cursor': {
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'doc_id': 20000,
                },
            },
        ),
        # We expect the handle to retrieve next document
        (
            {
                'tag': 'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                'event_at_begin': '2018-09-10T00:00:00.000000+00:00',
                'event_at_end': '2019-01-01T00:00:00.000000+00:00',
                'cursor': {
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'doc_id': 20000,
                },
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-10T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 60004,
                        'entry_ids': [],
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/1/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/6c41503787c149cbb7b650ab3d6ea44c'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-10T07:07:52.019582+00:00',
                        'revision': 7,
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [
                            'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
                        ],
                    },
                ],
                'cursor': {
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'doc_id': 60004,
                },
            },
        ),
        # We expect the handle to skip over non-existent docs and retrieve
        # existing ones
        (
            {
                'tag': 'taxi/unique_driver_id/5c6527563fd6940450db7483',
                'event_at_begin': '2018-01-01T00:00:00.000000+00:00',
                'event_at_end': '2019-01-01T00:00:00.000000+00:00',
                'limit': 3,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-04T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 40001,
                        'entry_ids': [],
                        'event_at': '2018-09-04T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/4/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/b078333377f94f9b8c30e13c783906d7'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-04T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c6527563fd6940450db7483',
                        ],
                    },
                    {
                        'created': '2018-09-05T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 50001,
                        'entry_ids': [],
                        'event_at': '2018-09-05T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/5/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/b078333377f94f9b8c30e13c783906d7'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-05T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c6527563fd6940450db7483',
                        ],
                    },
                    {
                        'created': '2018-09-06T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 60001,
                        'entry_ids': [],
                        'event_at': '2018-09-06T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/6/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/b078333377f94f9b8c30e13c783906d7'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-06T07:07:52.019582+00:00',
                        'revision': 3,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c6527563fd6940450db7483',
                        ],
                    },
                ],
                'cursor': {
                    'event_at': '2018-09-06T07:07:52.019582+00:00',
                    'doc_id': 60001,
                },
            },
        ),
        # We expect the handle to skip over non-existent docs and retrieve
        # existing ones
        (
            {
                'tag': 'taxi/unique_driver_id/5c6527563fd6940450db7483',
                'event_at_begin': '2018-01-01T00:00:00.000000+00:00',
                'event_at_end': '2019-01-01T00:00:00.000000+00:00',
                'limit': 1,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-04T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 40001,
                        'entry_ids': [],
                        'event_at': '2018-09-04T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/4/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/b078333377f94f9b8c30e13c783906d7'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-04T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c6527563fd6940450db7483',
                        ],
                    },
                ],
                'cursor': {
                    'event_at': '2018-09-04T07:07:52.019582+00:00',
                    'doc_id': 40001,
                },
            },
        ),
        # We expect the handle to skip over non-existent docs and retrieve
        # existing ones
        (
            {
                'tag': 'taxi/unique_driver_id/5c6527563fd6940450db7483',
                'event_at_begin': '2018-01-01T00:00:00.000000+00:00',
                'event_at_end': '2019-01-01T00:00:00.000000+00:00',
                'limit': 10,
            },
            {
                'docs': [
                    {
                        'created': '2018-09-04T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 40001,
                        'entry_ids': [],
                        'event_at': '2018-09-04T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/4/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/b078333377f94f9b8c30e13c783906d7'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-04T07:07:52.019582+00:00',
                        'revision': 1,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c6527563fd6940450db7483',
                        ],
                    },
                    {
                        'created': '2018-09-05T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 50001,
                        'entry_ids': [],
                        'event_at': '2018-09-05T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/5/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/b078333377f94f9b8c30e13c783906d7'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-05T07:07:52.019582+00:00',
                        'revision': 2,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c6527563fd6940450db7483',
                        ],
                    },
                    {
                        'created': '2018-09-06T07:07:52.019582+00:00',
                        'data': {},
                        'doc_id': 60001,
                        'entry_ids': [],
                        'event_at': '2018-09-06T07:07:52.019582+00:00',
                        'external_event_ref': (
                            'order_subvention_changed/6/subvention_handled'
                        ),
                        'external_obj_id': (
                            'alias_id/b078333377f94f9b8c30e13c783906d7'
                        ),
                        'kind': 'subvention_journal',
                        'process_at': '2018-09-06T07:07:52.019582+00:00',
                        'revision': 3,
                        'service': 'billing-docs',
                        'status': 'new',
                        'tags': [
                            'taxi/unique_driver_id/5c6527563fd6940450db7483',
                        ],
                    },
                ],
                'cursor': {
                    'event_at': '2018-09-06T07:07:52.019582+00:00',
                    'doc_id': 60001,
                },
            },
        ),
    ],
)
async def test_docs_by_tag(
        taxi_billing_docs_client, query, result, request_headers,
):
    response = await taxi_billing_docs_client.post(
        '/v1/docs/by_tag', json=query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == result, content


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=(
        'test_process_doc/doc@0.sql',
        'test_process_doc/event@0.sql',
        'test_process_doc/doc_journal@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_docs@1',
    files=(
        'test_process_doc/doc@1.sql',
        'test_process_doc/event@1.sql',
        'test_process_doc/doc_journal@1.sql',
    ),
)
@pytest.mark.parametrize(
    'doc_id,expected_finish_flag,expected_status',
    [
        (20004, False, models.Status.NEW.value),
        (30004, False, models.Status.NEW.value),
        (10002, True, models.Status.COMPLETE.value),
        (20002, True, models.Status.COMPLETE.value),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_process_doc(
        mock_journal_append_bulk,
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        doc_id,
        expected_finish_flag,
        expected_status,
):
    response = await taxi_billing_docs_client.post(
        '/v1/internal/process_doc',
        json={'doc_id': doc_id},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['finished'] == expected_finish_flag
    doc = await fetch_doc(docs_app, doc_id)
    assert doc.status == expected_status


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.parametrize(
    'doc_id, tags, event_at, expected',
    [
        (10002, ['test_update_tag_index'], '2018-09-10T07:07:52.019582Z', 200),
        # no tags passed
        (10002, [], '2018-09-10T07:07:52.019582Z', 400),
        # wrong date format
        (10002, ['test_update_tag_index'], '2018-09-10T07:07:52.019582', 400),
    ],
)
async def test_update_tag_index(
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        doc_id,
        tags,
        event_at,
        expected,
):
    tag = 'test_update_tag_index'
    query = {
        'tags': [tag],
        'event_at_begin': '2001-01-01T00:00:00.000000+00:00',
        'event_at_end': '2199-01-01T00:00:00.000000+00:00',
    }
    # at first: we have no tag spread so we unable to find it
    response = await taxi_billing_docs_client.post(
        '/v3/docs/by_tag', json=query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert not content['docs'][tag]

    data = {'doc_id': doc_id, 'tags': tags, 'event_at': event_at}
    response = await taxi_billing_docs_client.post(
        '/v1/internal/update_tag_index', json=data, headers=request_headers,
    )
    assert response.status == expected

    response = await taxi_billing_docs_client.post(
        '/v3/docs/by_tag', json=query, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    if expected == 200:  # ... on success
        # now... "we must because we can"
        assert content['docs'][tag]
        for entry in content['docs'][tag]:
            assert entry['doc_id'] == doc_id
    else:
        # still can not. such a pity =(
        assert not content['docs'][tag]


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@0', files=('doc@0.sql', 'doc_journal@0.sql'))
@pytest.mark.pgsql('billing_docs@1', files=('doc@1.sql', 'doc_journal@1.sql'))
@pytest.mark.parametrize(
    'doc_id,entries',
    (
        (1, []),
        (
            10000,
            [
                {
                    'doc_id': 10000,
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                    'details': None,
                    'journal_entry_id': None,
                },
            ],
        ),
        (
            10004,
            [
                {
                    'doc_id': 10004,
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                    'details': None,
                    'journal_entry_id': None,
                },
            ],
        ),
        (
            20000,
            [
                {
                    'doc_id': 20000,
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.000000+00:00',
                    'reason': '',
                    'details': {'a': 1},
                    'journal_entry_id': None,
                },
            ],
        ),
    ),
)
async def test_journal_search(
        taxi_billing_docs_client, doc_id, entries, request_headers,
):
    url, data = '/v1/journal/search', {'doc_id': doc_id}
    response = await taxi_billing_docs_client.post(
        url, json=data, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'entries': entries}


async def fetch_doc(app, doc_id: int) -> models.Doc:
    db_columns = [
        'doc.id AS doc_id',
        'doc.prev_doc_id',
        'doc.kind',
        'doc.external_obj_id',
        'doc.external_event_ref',
        'doc.service',
        'doc.service_user_id',
        'doc.data',
        'doc.event_at',
        'doc.process_at',
        'doc.created',
    ]
    db_projection = db.DBProjection(
        db_columns=db_columns, fetch_events=True, fetch_journal=True,
    )
    docs = await db.DocStore(storage=app.storage, config=app.config).search(
        doc_id=doc_id,
        external_obj_id=None,
        external_event_ref=None,
        kind=None,
        projection=db_projection,
        fetch_is_ready_for_processing=False,
        event_at_begin=None,
        event_at_end=None,
        use_master=False,
        log_extra={},
    )
    return util.not_none(util.first(docs))


@pytest.fixture
def mock_journal_append_bulk(monkeypatch):
    """
    Mock for function that uses bulk append v2 journal billing-accounts API.
    :return: Response with billing-accounts entry_id emulation
    """

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.counter = 10000

        async def append_journal_entry_bulk(
                self, entries, *args, **kwargs,
        ) -> dict:
            response_entries = []
            for item in entries:
                response_entries.append(
                    {'entry_id': self.counter, 'account_id': item.account_id},
                )
                self.counter += 1
            response = {'entries': response_entries}
            return response

    monkeypatch.setattr(billing_clients, 'BillingAccountsClient', MockClient)


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@0', files=('doc@0.sql', 'doc_journal@0.sql'))
@pytest.mark.pgsql('billing_docs@1', files=('doc@1.sql', 'doc_journal@1.sql'))
@pytest.mark.parametrize(
    'query,entries',
    (
        # no entries
        ([{'doc_id': 1}], []),
        # same shard
        (
            [{'doc_id': 10000}, {'doc_id': 20000}],
            [
                {
                    'doc_id': 10000,
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                    'details': None,
                    'journal_entry_id': None,
                },
                {
                    'doc_id': 20000,
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.000000+00:00',
                    'reason': '',
                    'details': {'a': 1},
                    'journal_entry_id': None,
                },
            ],
        ),
        # different shards
        (
            [{'doc_id': 10004}, {'doc_id': 20000}],
            [
                {
                    'doc_id': 20000,
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.000000+00:00',
                    'reason': '',
                    'details': {'a': 1},
                    'journal_entry_id': None,
                },
                {
                    'doc_id': 10004,
                    'account_id': 10000,
                    'amount': '123.0000',
                    'event_at': '2018-09-10T10:07:52.019582+00:00',
                    'reason': '',
                    'details': None,
                    'journal_entry_id': None,
                },
            ],
        ),
    ),
)
async def test_journal_search_v2(
        taxi_billing_docs_client, query, entries, request_headers,
):
    url, data = '/v2/journal/search', {'docs': query}
    response = await taxi_billing_docs_client.post(
        url, json=data, headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'entries': entries}


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_DOCS_FETCH_TAGS_SEQUENTIALLY=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_DOCS_FETCH_TAGS_SEQUENTIALLY=False,
            ),
        ),
    ],
)
@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=(
        'test_by_tag/doc@0.sql',
        'test_by_tag/event@0.sql',
        'test_by_tag/tag_index@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_docs@1',
    files=('test_by_tag/doc@1.sql', 'test_by_tag/event@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
async def test_docs_by_tag_v3(
        taxi_billing_docs_client, load_json, request_headers,
):
    data = load_json('docs_by_tag_v3.json')
    test_samples = data['test_samples']
    for item in test_samples:
        request = item['request']
        result = item['expected_response']
        response = await taxi_billing_docs_client.post(
            '/v3/docs/by_tag', json=request, headers=request_headers,
        )
        assert response.status == 200
        content = await response.json()
        assert content == result


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_DOCS_FETCH_TAGS_SEQUENTIALLY=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_DOCS_FETCH_TAGS_SEQUENTIALLY=False,
            ),
        ),
    ],
)
@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=(
        'test_by_tag/doc@0.sql',
        'test_by_tag/event@0.sql',
        'test_by_tag/tag_index@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_docs@1',
    files=('test_by_tag/doc@1.sql', 'test_by_tag/event@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
async def test_doc_ids_by_tag(
        taxi_billing_docs_client, load_json, request_headers,
):
    data = load_json('doc_ids_by_tag.json')
    test_samples = data['test_samples']
    for item in test_samples:
        request = item['request']
        result = item['expected_response']
        response = await taxi_billing_docs_client.post(
            '/v1/doc_ids/by_tag', json=request, headers=request_headers,
        )
        assert response.status == 200
        content = await response.json()
        assert result == content


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0',
    files=(
        'test_process_doc/doc@0.sql',
        'test_process_doc/event@0.sql',
        'test_process_doc/doc_journal@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_docs@1',
    files=(
        'test_process_doc/doc@1.sql',
        'test_process_doc/event@1.sql',
        'test_process_doc/doc_journal@1.sql',
    ),
)
@pytest.mark.parametrize(
    'doc_id,expected_finish_flag,expected_status',
    [
        (20004, False, models.Status.NEW.value),
        (30004, False, models.Status.NEW.value),
        (10002, True, models.Status.COMPLETE.value),
        (20002, True, models.Status.COMPLETE.value),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_process_doc_journal_billing_accounts(
        mock_journal_append_bulk,
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        doc_id,
        expected_finish_flag,
        expected_status,
):
    """
    Check doc processing with new billing-account API v2 for journal append.
    """
    response = await taxi_billing_docs_client.post(
        '/v1/internal/process_doc',
        json={'doc_id': doc_id},
        headers=request_headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content['finished'] == expected_finish_flag
    doc = await fetch_doc(docs_app, doc_id)
    assert doc.status == expected_status


async def test_journal_dataset_processing():
    """
    Check prepared data format for model of billing-accounts journal API.
    """
    sample_data = {
        'account_id': 10000,
        'amount': '50.5',
        'doc_ref': '1777555',
        'event_at': '2019-07-29T18:25:00.000000+00:00',
        'reason': 'test',
    }

    raw_data = billing_accounts.DocJournalEntry(
        account_id=10000,
        amount=decimal.Decimal(50.5),
        doc_ref=1777555,
        event_at=dates.parse_datetime_to_naive_utc(
            '2019-07-29T18:25:00.000000+00:00',
        ),
        reason='test',
        details=None,
    )

    prepared_data = raw_data.prepare_billing_accounts_format()
    assert sample_data == prepared_data


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_DOCS_EMPTY_DOC_DATA={'__default__': False},
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_DOCS_EMPTY_DOC_DATA={'__default__': True},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'query,append_mode,result,expected_journal_entries',
    [
        # one doc
        (
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'data': {'shoop': 'da whoop'},
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '123.00001234',
                                'event_at': '2018-09-10T10:07:52.019582+00:00',
                                'details': {'a': 'b'},
                            },
                        ],
                    },
                ],
            },
            'append',
            {
                'docs': [
                    {
                        'doc_id': 30000,
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'process_at': '2018-09-10T10:07:52.000000+00:00',
                        'service': 'billing-docs',
                        'data': {'shoop': 'da whoop'},
                        'status': 'complete',
                        'tags': [],
                    },
                ],
            },
            [
                {
                    'journal_entry_id': 10000,
                    'doc_id': 30000,
                    'amount': decimal.Decimal('123.0000'),
                    'reason': '',
                    'details': json.dumps({'a': 'b'}),
                },
            ],
        ),
        # many docs
        (
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': '123/reversed',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'data': {'shoop': 'da whoop'},
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '-123.00001234',
                                'event_at': '2018-09-10T10:07:52.019582+00:00',
                                'details': {'a': 'b'},
                            },
                        ],
                    },
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': '123/journal',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'service_user_id': 'foobar_user',
                        'data': {},
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '123.0000',
                                'event_at': '2018-09-10T10:07:52.019582+00:00',
                                'reason': '',
                            },
                            {
                                'account_id': 20000,
                                'amount': '436.00006',
                                'event_at': '2018-09-10T10:07:52.019582+00:00',
                                'reason': 'treason',
                            },
                        ],
                        'tags': ['order_id/deadf00d'],
                    },
                ],
            },
            'append',
            {
                'docs': [
                    {
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 30000,
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_ref': '123/reversed',
                        'kind': 'test',
                        'process_at': '2018-09-10T10:07:52.000000+00:00',
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                        'topic': 'abc',
                    },
                    {
                        'data': {},
                        'doc_id': 40000,
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'external_ref': '123/journal',
                        'kind': 'test',
                        'process_at': '2018-09-10T10:07:52.000000+00:00',
                        'service': 'billing-docs',
                        'service_user_id': 'foobar_user',
                        'status': 'complete',
                        'tags': ['order_id/deadf00d'],
                        'topic': 'abc',
                    },
                ],
            },
            [
                {
                    'journal_entry_id': 10000,
                    'doc_id': 30000,
                    'amount': decimal.Decimal('-123.0000'),
                    'reason': '',
                    'details': json.dumps({'a': 'b'}),
                },
                {
                    'journal_entry_id': 10001,
                    'doc_id': 40000,
                    'amount': decimal.Decimal('123.0000'),
                    'reason': '',
                    'details': None,
                },
                {
                    'journal_entry_id': 10002,
                    'doc_id': 40000,
                    'amount': decimal.Decimal('436.0001'),
                    'reason': 'treason',
                    'details': None,
                },
            ],
        ),
        # append_if
        (
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'data': {
                            'execution_modes': {
                                'append_mode': 'append_if',
                                'append_mode_settings': {
                                    'balance': '123.0000',
                                },
                            },
                        },
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '-123.0000',
                                'event_at': '2018-09-10T10:07:52.019582+00:00',
                                'details': {'a': 'b'},
                            },
                        ],
                    },
                ],
            },
            'append_if',
            {
                'docs': [
                    {
                        'doc_id': 30000,
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'process_at': '2018-09-10T10:07:52.000000+00:00',
                        'service': 'billing-docs',
                        'data': {
                            'execution_modes': {
                                'append_mode': 'append_if',
                                'append_mode_settings': {
                                    'balance': '123.0000',
                                },
                            },
                            'status_info': {'status': 'success'},
                        },
                        'status': 'complete',
                        'tags': [],
                    },
                ],
            },
            [
                {
                    'journal_entry_id': 10000,
                    'doc_id': 30000,
                    'amount': decimal.Decimal('-123.0000'),
                    'reason': '',
                    'details': json.dumps({'a': 'b'}),
                },
            ],
        ),
        # append_if, zero balance
        (
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'data': {
                            'execution_modes': {
                                'append_mode': 'append_if',
                                'append_mode_settings': {'balance': '0.0000'},
                            },
                        },
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '-123.0000',
                                'event_at': '2018-09-10T10:07:52.019582+00:00',
                                'details': {'a': 'b'},
                            },
                        ],
                    },
                ],
            },
            'append_if',
            {
                'docs': [
                    {
                        'doc_id': 30000,
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'process_at': '2018-09-10T10:07:52.000000+00:00',
                        'service': 'billing-docs',
                        'data': {
                            'execution_modes': {
                                'append_mode': 'append_if',
                                'append_mode_settings': {'balance': '0.0000'},
                            },
                            'status_info': {'status': 'success'},
                        },
                        'status': 'complete',
                        'tags': [],
                    },
                ],
            },
            [
                {
                    'journal_entry_id': 10000,
                    'doc_id': 30000,
                    'amount': decimal.Decimal('-123.0000'),
                    'reason': '',
                    'details': json.dumps({'a': 'b'}),
                },
            ],
        ),
    ],
)
async def test_v2_docs_execute(
        docs_app,
        taxi_billing_docs_client,
        mockserver,
        request_headers,
        query,
        append_mode,
        result,
        expected_journal_entries,
):
    journal_idx = 10000

    @mockserver.json_handler('/billing-accounts/v1/journal/append_if')
    def _patch_billing_accounts_append_if(request):
        nonlocal journal_idx

        assert append_mode == 'append_if'
        response = request.json.copy()
        response['entry_id'] = journal_idx
        journal_idx += 1
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-accounts/v2/journal/append')
    def _patch_billing_accounts_append(request):
        nonlocal journal_idx

        assert append_mode == 'append'
        response_entries = []
        for entry in request.json['entries']:
            entry = entry.copy()
            entry['entry_id'] = journal_idx
            response_entries.append(entry)
            journal_idx += 1
        response = {'entries': response_entries}
        return response

    response = await taxi_billing_docs_client.post(
        '/v2/docs/execute', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    for doc in content['docs']:
        doc.pop('created')
    assert content == result

    # check idempotency
    response = await taxi_billing_docs_client.post(
        '/v2/docs/execute', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    for doc in content['docs']:
        doc.pop('created')
    assert content == result

    actual_journal_entries = []
    for doc in content['docs']:
        actual_journal_entries.extend(
            await _fetch_journal_entries(docs_app, doc['doc_id']),
        )
    assert expected_journal_entries == actual_journal_entries


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'query,result,expected_journal_entries',
    [
        (
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'data': {
                            'execution_modes': {
                                'append_mode': 'append_if',
                                'append_mode_settings': {
                                    'balance': '123.0000',
                                },
                            },
                        },
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '-123.0000',
                                'event_at': '2018-09-10T10:07:52.019582+00:00',
                                'details': {'a': 'b'},
                            },
                        ],
                    },
                ],
            },
            {
                'docs': [
                    {
                        'doc_id': 50000,
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'process_at': '2018-09-10T10:07:52.000000+00:00',
                        'service': 'billing-docs',
                        'data': {
                            'execution_modes': {
                                'append_mode': 'append_if',
                                'append_mode_settings': {
                                    'balance': '123.0000',
                                },
                            },
                            'status_info': {
                                'code': 'no_funds',
                                'status': 'failed',
                            },
                        },
                        'status': 'complete',
                        'tags': [],
                    },
                ],
            },
            [
                {
                    'journal_entry_id': None,
                    'doc_id': 50000,
                    'amount': decimal.Decimal('-123.0000'),
                    'reason': '',
                    'details': json.dumps({'a': 'b'}),
                },
            ],
        ),
    ],
)
async def test_v2_docs_execute_append_if_no_funds(
        docs_app,
        taxi_billing_docs_client,
        mockserver,
        request_headers,
        query,
        result,
        expected_journal_entries,
):
    @mockserver.json_handler('/billing-accounts/v1/journal/append_if')
    def _patch_billing_accounts_append_if(request):
        min_balance = request.json['balance']
        return mockserver.make_response(
            response=(
                f'Failed to append Journal with min balance {min_balance} '
                'on account'
            ),
            status=409,
        )

    response = await taxi_billing_docs_client.post(
        '/v2/docs/execute', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    for doc in content['docs']:
        doc.pop('created')
    assert content == result

    # check idempotency
    response = await taxi_billing_docs_client.post(
        '/v2/docs/execute', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    for doc in content['docs']:
        doc.pop('created')
    assert content == result

    actual_journal_entries = []
    for doc in content['docs']:
        actual_journal_entries.extend(
            await _fetch_journal_entries(docs_app, doc['doc_id']),
        )
    assert expected_journal_entries == actual_journal_entries


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('sync_update_tag_index', (False, True))
@pytest.mark.parametrize(
    'query',
    [
        {
            'docs': [
                {
                    'kind': 'test',
                    'topic': 'abc',
                    'external_ref': '123/reversed',
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-docs',
                    'data': {'shoop': 'da whoop'},
                    'journal_entries': [],
                    'tags': ['order_id/deadf00d', 'parent_doc_id/12345'],
                },
                {
                    'kind': 'test',
                    'topic': 'abc',
                    'external_ref': '123/journal',
                    'event_at': '2018-09-10T07:07:52.019582+00:00',
                    'service': 'billing-docs',
                    'service_user_id': 'foobar_user',
                    'data': {},
                    'journal_entries': [],
                    'tags': ['order_id/deadf00d', 'parent_doc_id/67890'],
                },
            ],
        },
    ],
)
async def test_v2_docs_execute_updates_tag_index(
        docs_app,
        taxi_billing_docs_client,
        patch,
        request_headers,
        query,
        sync_update_tag_index,
):
    @patch('taxi_billing_docs.stq.client.schedule_tag_index_update')
    async def schedule_tag_index_update(*args, **kwargs):
        pass

    docs_app.config.BILLING_DOCS_TAG_INDEX_UPDATE_SYNC = sync_update_tag_index
    response = await taxi_billing_docs_client.post(
        '/v2/docs/execute', json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    tags_by_doc_id = {}
    for doc in content['docs']:
        assert doc['tags']
        tags_by_doc_id[doc['doc_id']] = doc['tags']
    assert tags_by_doc_id
    if sync_update_tag_index:
        expected_doc_ids_by_tag = {}
        for doc_id, tags in tags_by_doc_id.items():
            for tag in tags:
                if tag in expected_doc_ids_by_tag:
                    expected_doc_ids_by_tag[tag].add(doc_id)
                else:
                    expected_doc_ids_by_tag[tag] = set([doc_id])
        by_tag_query = {
            'tags': list(expected_doc_ids_by_tag),
            'event_at_begin': '2001-01-01T00:00:00.000000+00:00',
            'event_at_end': '2199-01-01T00:00:00.000000+00:00',
        }
        by_tag_response = await taxi_billing_docs_client.post(
            '/v3/docs/by_tag', json=by_tag_query, headers=request_headers,
        )
        assert by_tag_response.status == 200
        docs_by_tag = (await by_tag_response.json())['docs']
        doc_ids_by_tag = {}
        for tag in expected_doc_ids_by_tag:
            doc_ids_by_tag[tag] = {doc['doc_id'] for doc in docs_by_tag[tag]}
        assert doc_ids_by_tag == expected_doc_ids_by_tag
    else:
        assert schedule_tag_index_update.calls


async def _fetch_journal_entries(docs_app, doc_id):
    vid = docs_app.storage.vshard_from_id(doc_id)
    schema = docs_app.storage.vshard_schema(vid)
    replica = await docs_app.storage.replica(vid)
    rows = await replica.fetch(
        f"""
        SELECT journal_entry_id, doc_id, amount, reason, details
          FROM {schema}.doc_journal
         WHERE doc_id = {doc_id}
        """,
        log_extra={},
    )
    return [dict(row) for row in rows]


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'request_body, limit_days, '
    'status_code, result, expected_journal_entries',
    [
        (
            {
                'kind': 'test',
                'external_obj_id': 'abc',
                'external_event_ref': 'ride_order_amended_again',
                'event_at': '2018-08-01T00:00:00.000000+00:00',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'service': 'billing-docs',
                'data': {'shoop': 'da whoop'},
                'status': 'new',
                'journal_entries': [
                    {
                        'account_id': 10000,
                        'amount': '123.00001234',
                        'event_at': '2018-09-10T10:07:52.019582+00:00',
                        'reason': '',
                        'details': {'a': 'b'},
                    },
                ],
            },
            365,
            200,
            {
                'data': {'shoop': 'da whoop'},
                'doc_id': 30000,
                'entry_ids': [],
                'event_at': '2018-08-01T00:00:00.000000+00:00',
                'external_event_ref': 'ride_order_amended_again',
                'external_obj_id': 'abc',
                'kind': 'test',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'revision': 3,
                'service': 'billing-docs',
                'status': 'new',
                'tags': [],
            },
            [
                {
                    'journal_entry_id': None,
                    'doc_id': 30000,
                    'amount': decimal.Decimal('123.0000'),
                    'details': json.dumps({'a': 'b'}),
                    'reason': '',
                },
            ],
        ),
        (
            {
                'kind': 'test',
                'external_obj_id': 'abc',
                'external_event_ref': 'ride_order_amended_again',
                'event_at': '2018-08-01T00:00:00.000000+00:00',
                'process_at': '2018-09-10T07:07:52.019582+00:00',
                'service': 'billing-docs',
                'data': {'shoop': 'da whoop'},
                'status': 'new',
                'journal_entries': [
                    {
                        'account_id': 10000,
                        'amount': '123.00001234',
                        'event_at': '2018-08-01T00:00:00.000000+00:00',
                        'reason': '',
                        'details': {'a': 'b'},
                    },
                ],
            },
            1,
            400,
            {
                'code': 'old-event-at',
                'message': 'Journal entry is more than 1 days old',
                'status': 'error',
            },
            None,
        ),
    ],
)
async def test_docs_create_validate_journal_event_at(
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        request_body,
        limit_days,
        status_code,
        result,
        expected_journal_entries,
        monkeypatch,
        mockserver,
):
    monkeypatch.setattr(
        docs_config.Config, 'BILLING_OLD_JOURNAL_LIMIT_DAYS', limit_days,
    )

    response = await taxi_billing_docs_client.post(
        '/v1/docs/create', json=request_body, headers=request_headers,
    )
    content = await response.json()
    assert response.status == status_code, content
    content.pop('created', None)
    assert content == result

    if status_code == 200:
        actual_journal_entries = await _fetch_journal_entries(
            docs_app, result['doc_id'],
        )
        assert expected_journal_entries == actual_journal_entries


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.pgsql(
    'billing_docs@0', files=('doc@0.sql', 'event@0.sql', 'doc_journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('doc@1.sql', 'event@1.sql', 'doc_journal@1.sql'),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'request_body, limit_days, '
    'status_code, result, expected_journal_entries',
    [
        (
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-08-01T00:00:00.000000+00:00',
                        'service': 'billing-docs',
                        'data': {'shoop': 'da whoop'},
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '123.00001234',
                                'event_at': '2018-08-01T00:00:00.000000+00:00',
                                'details': {'a': 'b'},
                            },
                        ],
                    },
                ],
            },
            365,
            200,
            {
                'docs': [
                    {
                        'data': {'shoop': 'da whoop'},
                        'doc_id': 30000,
                        'event_at': '2018-08-01T00:00:00.000000+00:00',
                        'external_ref': 'ride_order_amended_again',
                        'kind': 'test',
                        'process_at': '2018-09-10T10:07:52.000000+00:00',
                        'service': 'billing-docs',
                        'status': 'complete',
                        'tags': [],
                        'topic': 'abc',
                    },
                ],
            },
            [
                {
                    'amount': decimal.Decimal('123.0000'),
                    'details': '{"a": "b"}',
                    'doc_id': 30000,
                    'journal_entry_id': 10000,
                    'reason': '',
                },
            ],
        ),
        (
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-08-01T00:00:00.000000+00:00',
                        'service': 'billing-docs',
                        'data': {'shoop': 'da whoop'},
                        'journal_entries': [
                            {
                                'account_id': 10000,
                                'amount': '123.00001234',
                                'event_at': '2018-08-01T00:00:00.000000+00:00',
                                'details': {'a': 'b'},
                            },
                        ],
                    },
                ],
            },
            1,
            400,
            {
                'code': 'old-event-at',
                'message': 'Journal entry is more than 1 days old',
                'status': 'error',
            },
            None,
        ),
    ],
)
async def test_docs_execute_validate_journal_event_at(
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        request_body,
        limit_days,
        status_code,
        result,
        expected_journal_entries,
        monkeypatch,
        mockserver,
):
    monkeypatch.setattr(
        docs_config.Config, 'BILLING_OLD_JOURNAL_LIMIT_DAYS', limit_days,
    )

    @mockserver.json_handler('/billing-accounts/v2/journal/append')
    def _patch_billing_accounts_append(request):
        journal_idx = 10000
        response_entries = []
        for entry in request.json['entries']:
            entry = entry.copy()
            entry['entry_id'] = journal_idx
            response_entries.append(entry)
            journal_idx += 1
        response = {'entries': response_entries}
        return response

    response = await taxi_billing_docs_client.post(
        '/v2/docs/execute', json=request_body, headers=request_headers,
    )
    content = await response.json()
    assert response.status == status_code, content
    for doc in content.get('docs', []):
        doc.pop('created')
    assert content == result

    if status_code == 200:
        actual_journal_entries = []
        for doc in content['docs']:
            actual_journal_entries.extend(
                await _fetch_journal_entries(docs_app, doc['doc_id']),
            )
        assert expected_journal_entries == actual_journal_entries


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
@pytest.mark.config(BILLING_DOCS_TAG_INDEX_UPDATE_SYNC=True)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'request_uri,query,enable_fallback,expected_stq_calls',
    [
        (
            '/v1/docs/create',
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
                'tags': ['order_id/alias_id1', 'custom_tag'],
            },
            False,
            0,
        ),
        (
            '/v1/docs/create',
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
                'tags': ['order_id/alias_id1', 'custom_tag'],
            },
            True,
            1,
        ),
        (
            '/v2/docs/execute',
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'data': {'shoop': 'da whoop'},
                        'journal_entries': [],
                        'tags': ['order_id/alias_id1', 'custom_tag'],
                    },
                ],
            },
            False,
            0,
        ),
        (
            '/v2/docs/execute',
            {
                'docs': [
                    {
                        'kind': 'test',
                        'topic': 'abc',
                        'external_ref': 'ride_order_amended_again',
                        'event_at': '2018-09-10T07:07:52.019582+00:00',
                        'service': 'billing-docs',
                        'data': {'shoop': 'da whoop'},
                        'journal_entries': [],
                        'tags': ['order_id/alias_id1', 'custom_tag'],
                    },
                ],
            },
            True,
            1,
        ),
    ],
)
async def test_update_tag_index_stq_fallback(
        docs_app,
        taxi_billing_docs_client,
        request_headers,
        request_uri,
        query,
        enable_fallback,
        expected_stq_calls,
        patch,
        monkeypatch,
):
    class MockTagIndexStore:
        def __init__(self, *args, **kwargs):
            pass

        async def insert_entries(self, *args, **kwargs) -> None:
            if enable_fallback:
                raise db.StorageError

    monkeypatch.setattr(db, 'TagIndexStore', MockTagIndexStore)

    @patch('taxi_billing_docs.stq.client.schedule_tag_index_update')
    async def schedule_tag_index_update(*args, **kwargs):
        pass

    response = await taxi_billing_docs_client.post(
        request_uri, json=query, headers=request_headers,
    )
    content = await response.json()
    assert response.status == 200, content
    assert len(schedule_tag_index_update.calls) == expected_stq_calls
