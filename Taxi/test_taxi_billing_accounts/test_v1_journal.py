# pylint: disable=too-many-lines
from typing import Optional

from aiohttp import web
import pytest

from taxi_billing_accounts import context as ba_context


@pytest.mark.parametrize(
    'request_body, account_id, expected_response',
    [
        (
            {
                'account_id': 41000,
                'amount': '-358.0000',
                'balance': '358.0000',
                'doc_ref': 'uniq_doc_ref/1',
                'reason': 'some comment',
                'idempotency_key': '41000',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            41000,
            web.HTTPOk,
        ),
        (
            {
                'account_id': 41000,
                'amount': '-358.0000',
                'balance': '359.0000',
                'doc_ref': 'uniq_doc_ref/2',
                'reason': 'some comment',
                'idempotency_key': '41000',
                'event_at': '2018-10-18T18:26:31.000000+00:00',
                'details': {'alias_id': 'some_alias_id'},
            },
            41000,
            web.HTTPOk,
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'journal@0.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'journal@1.sql',
        'balance_at@1.sql',
        'rollups@1.sql',
    ),
)
async def test_journal_append_if(
        billing_accounts_client,
        request_headers,
        request_body,
        account_id,
        expected_response,
):

    account_id = request_body['account_id']

    balance = await get_live_balance(
        billing_accounts_client, request_headers, account_id,
    )
    # 50 - last rolled up balance, 300 - new transactions,
    # 9 - transactions not rolled up yet
    assert balance == '359.0000'

    first = await billing_accounts_client.post(
        '/v1/journal/append_if', json=request_body, headers=request_headers,
    )

    second = await billing_accounts_client.post(
        '/v1/journal/append_if', json=request_body, headers=request_headers,
    )

    assert expected_response.status_code == first.status
    assert expected_response.status_code == second.status

    # check idempotency feature
    assert first.status == second.status
    assert await first.json() == await second.json()

    assert first.status == web.HTTPOk.status_code
    ans = await first.json()

    assert ans.get('entry_id') is not None
    ans.pop('entry_id')

    # current version doesn't return created
    assert ans.get('created') is None

    request_body.pop('balance')
    assert ans == request_body

    balance = await get_live_balance(
        billing_accounts_client, request_headers, account_id,
    )
    assert balance == '1.0000'


@pytest.mark.parametrize(
    'request_body, account_id, expected_response',
    [
        (
            {
                'account_id': 41000,
                'amount': '-125.0000',
                'balance': '126.0000',
                'doc_ref': 'uniq_doc_ref/1',
                'reason': 'some comment',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            41000,
            {
                'account_id': 41000,
                'amount': '-125.0000',
                'doc_ref': 'uniq_doc_ref/1',
                'reason': 'some comment',
                'idempotency_key': '41000',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
        ),
        (
            {
                'account_id': 41000,
                'amount': '-125.0000',
                'balance': '126.0000',
                'doc_ref': 'uniq_doc_ref/2',
                'reason': 'some comment',
                'idempotency_key': 'some_idempotency_key',
                'event_at': '2018-10-18T18:26:31.000000+00:00',
                'details': {'alias_id': 'some_alias_id'},
            },
            41000,
            {
                'account_id': 41000,
                'amount': '-125.0000',
                'doc_ref': 'uniq_doc_ref/2',
                'reason': 'some comment',
                'idempotency_key': 'some_idempotency_key',
                'event_at': '2018-10-18T18:26:31.000000+00:00',
                'details': {'alias_id': 'some_alias_id'},
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'journal@0.sql',
        'balance_at@0.sql',
        'rollups@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'journal@1.sql',
        'balance_at@1.sql',
        'rollups@1.sql',
    ),
)
async def test_journal_append_if_idempotency_key(
        billing_accounts_client,
        request_headers,
        request_body,
        account_id,
        expected_response,
):

    account_id = request_body['account_id']

    balance = await get_live_balance(
        billing_accounts_client, request_headers, account_id,
    )
    assert balance == '359.0000'

    first = await billing_accounts_client.post(
        '/v1/journal/append_if', json=request_body, headers=request_headers,
    )

    second = await billing_accounts_client.post(
        '/v1/journal/append_if', json=request_body, headers=request_headers,
    )

    # check idempotency feature
    assert first.status == second.status
    assert await first.json() == await second.json()

    assert first.status == web.HTTPOk.status_code
    ans = await first.json()

    assert ans.get('entry_id') is not None
    ans.pop('entry_id')

    # current version doesn't return created
    assert ans.get('created') is None

    assert ans == expected_response

    balance = await get_live_balance(
        billing_accounts_client, request_headers, account_id,
    )
    assert balance == '234.0000'


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        # Wrong request bodies
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Test everything is fine with valid test request
        (
            {
                'account_id': 40000,
                'amount': '-7.0000',
                'balance': '7.0000',
                'doc_ref': 'uniq_doc_ref/1',
                'reason': 'some comment',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            web.HTTPOk,
        ),
        # Not enough funds
        (
            {
                'account_id': 40000,
                'amount': '-8.0000',
                'balance': '8.0000',
                'doc_ref': 'uniq_doc_ref/1',
                'reason': 'not enough funds',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            web.HTTPConflict,
        ),
        # Invalid requests
        (
            # missed account
            {
                'amount': '0',
                'balance': '0',
                'doc_ref': 'uniq_doc_ref/1',
                'reason': 'zero amount',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed doc_ref
            {
                'account_id': 40000,
                'amount': '-0.0001',
                'balance': '0',
                'reason': 'max negative amount',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed amount
            {
                'account_id': 40000,
                'doc_ref': 'uniq_doc_ref/2',
                'balance': '0',
                'reason': 'missed amount',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed balance
            {
                'account_id': 40000,
                'doc_ref': 'uniq_doc_ref/2',
                'amount': '0.1000',
                'reason': 'missed balance',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed event_at
            {
                'account_id': 40000,
                'amount': '0',
                'balance': '0',
                'doc_ref': 'uniq_doc_ref/3',
                'reason': 'missed event_at',
            },
            web.HTTPBadRequest,
        ),
        (
            # no such account-id
            {
                'account_id': 0,
                'amount': '2001.3400',
                'balance': '0',
                'doc_ref': 'uniq_doc_ref/4',
                'reason': 'integrity constrain',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # wrong details (number)
            {
                'account_id': 40000,
                'amount': '2001.3400',
                'balance': '0',
                'doc_ref': 'uniq_doc_ref/2',
                'reason': 'some comment',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
                'details': 1,
            },
            web.HTTPBadRequest,
        ),
        (
            # wrong details (string)
            {
                'account_id': 40000,
                'amount': '2001.3400',
                'balance': '0',
                'doc_ref': 'uniq_doc_ref/2',
                'reason': 'some comment',
                'event_at': '2018-10-18T17:26:31.000000+00:00',
                'details': '',
            },
            web.HTTPBadRequest,
        ),
        (
            # no time zone in event_at
            {
                'account_id': 40000,
                'amount': '2001.3400',
                'balance': '0',
                'doc_ref': 'uniq_doc_ref/2',
                'reason': 'some comment',
                'event_at': '2018-10-18T17:26:31.000000',
            },
            web.HTTPBadRequest,
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql', 'journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql', 'journal@1.sql'),
)
async def test_journal_append_if_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v1/journal/append_if', json=request_body, headers=request_headers,
    )
    assert response.status == expected_response.status_code


@pytest.mark.parametrize(
    'request_body,entries',
    [
        (
            {
                'account': {'account_id': 40000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [
                {
                    'entry_id': 34720250000,
                    'event_at': '2018-12-20T17:45:42.000000+00:00',
                    'cursor': '2018-12-20T17:45:42.000000+00:00/34720250000',
                    'account_id': 40000,
                    'amount': '1.0000',
                    'doc_ref': 'brand_new/858895/1',
                    'reason': 'test',
                    'idempotency_key': '40000',
                    'created': '2018-12-20T17:45:42.000000+00:00',
                    'account': {
                        'account_id': 40000,
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'num_orders',
                    },
                },
                {
                    'entry_id': 34720270000,
                    'event_at': '2018-12-20T17:45:44.000000+00:00',
                    'cursor': '2018-12-20T17:45:44.000000+00:00/34720270000',
                    'account_id': 40000,
                    'amount': '2.0000',
                    'doc_ref': 'brand_new/858895/2',
                    'reason': 'test',
                    'idempotency_key': '40000',
                    'created': '2018-12-20T17:45:44.000000+00:00',
                    'account': {
                        'account_id': 40000,
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'num_orders',
                    },
                },
            ],
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'agreement_id': 'ag-rule-nMFG-000',
                    'currency': 'RUB',
                    'sub_account': 'income',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [
                {
                    'entry_id': 34720260000,
                    'event_at': '2018-12-20T17:45:43.000000+00:00',
                    'cursor': '2018-12-20T17:45:43.000000+00:00/34720260000',
                    'account_id': 41000,
                    'amount': '3.0000',
                    'doc_ref': 'brand_new/858895/3',
                    'reason': 'test',
                    'idempotency_key': '41000',
                    'created': '2018-12-20T17:45:43.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                        'account_id': 41000,
                    },
                },
                {
                    'entry_id': 34720280000,
                    'event_at': '2018-12-20T17:45:44.000000+00:00',
                    'cursor': '2018-12-20T17:45:44.000000+00:00/34720280000',
                    'account_id': 41000,
                    'amount': '300.0000',
                    'doc_ref': 'brand_new/858895/4',
                    'reason': 'test',
                    'idempotency_key': '41000',
                    'created': '2018-12-20T17:45:44.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                        'account_id': 41000,
                    },
                },
            ],
        ),
        (
            {
                'account': {'account_id': 40000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.001+00:00',
                'cursor': '',
                'limit': 4,
                'sort': 'desc',
            },
            [
                {
                    'entry_id': 34720270000,
                    'account_id': 40000,
                    'amount': '2.0000',
                    'doc_ref': 'brand_new/858895/2',
                    'event_at': '2018-12-20T17:45:44.000000+00:00',
                    'reason': 'test',
                    'idempotency_key': '40000',
                    'created': '2018-12-20T17:45:44.000000+00:00',
                    'cursor': '2018-12-20T17:45:44.000000+00:00/34720270000',
                    'account': {
                        'account_id': 40000,
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'num_orders',
                    },
                },
                {
                    'entry_id': 34720250000,
                    'account_id': 40000,
                    'amount': '1.0000',
                    'doc_ref': 'brand_new/858895/1',
                    'event_at': '2018-12-20T17:45:42.000000+00:00',
                    'reason': 'test',
                    'idempotency_key': '40000',
                    'created': '2018-12-20T17:45:42.000000+00:00',
                    'cursor': '2018-12-20T17:45:42.000000+00:00/34720250000',
                    'account': {
                        'account_id': 40000,
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'num_orders',
                    },
                },
            ],
        ),
        (
            {
                'account': {'account_id': 40000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.001+00:00',
                'cursor': '',
                'limit': 1,
                'sort': 'desc',
            },
            [
                {
                    'entry_id': 34720270000,
                    'account_id': 40000,
                    'amount': '2.0000',
                    'doc_ref': 'brand_new/858895/2',
                    'event_at': '2018-12-20T17:45:44.000000+00:00',
                    'reason': 'test',
                    'idempotency_key': '40000',
                    'created': '2018-12-20T17:45:44.000000+00:00',
                    'cursor': '2018-12-20T17:45:44.000000+00:00/34720270000',
                    'account': {
                        'account_id': 40000,
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'num_orders',
                    },
                },
            ],
        ),
        (
            {
                'account': {'account_id': 40000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.001+00:00',
                'cursor': '2018-12-20T17:45:44.000000+00:00/34720270000',
                'limit': 4,
                'sort': 'desc',
            },
            [
                {
                    'entry_id': 34720250000,
                    'account_id': 40000,
                    'amount': '1.0000',
                    'doc_ref': 'brand_new/858895/1',
                    'event_at': '2018-12-20T17:45:42.000000+00:00',
                    'reason': 'test',
                    'idempotency_key': '40000',
                    'created': '2018-12-20T17:45:42.000000+00:00',
                    'cursor': '2018-12-20T17:45:42.000000+00:00/34720250000',
                    'account': {
                        'account_id': 40000,
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'num_orders',
                    },
                },
            ],
        ),
        (
            {
                'account': {'account_id': 40000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.001+00:00',
                'cursor': '2018-12-20T17:45:42.000000+00:00/34720250000',
                'limit': 4,
            },
            [
                {
                    'entry_id': 34720270000,
                    'account_id': 40000,
                    'amount': '2.0000',
                    'doc_ref': 'brand_new/858895/2',
                    'event_at': '2018-12-20T17:45:44.000000+00:00',
                    'reason': 'test',
                    'idempotency_key': '40000',
                    'created': '2018-12-20T17:45:44.000000+00:00',
                    'cursor': '2018-12-20T17:45:44.000000+00:00/34720270000',
                    'account': {
                        'account_id': 40000,
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'num_orders',
                    },
                },
            ],
        ),
        (
            {
                'account': {'account_id': 45000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.001+00:00',
                'cursor': '2018-12-20T17:45:45.000000+00:00/34720330000',
                'limit': 1,
                'sort': 'desc',
                'skip_zero_entries': True,
            },
            [
                {
                    'entry_id': 34720310000,
                    'account_id': 45000,
                    'amount': '0.0001',
                    'doc_ref': 'doc_ref/111111/1',
                    'event_at': '2018-12-20T17:45:43.000000+00:00',
                    'reason': 'test',
                    'idempotency_key': '45000',
                    'created': '2018-12-20T17:45:43.000000+00:00',
                    'cursor': '2018-12-20T17:45:43.000000+00:00/34720310000',
                    'account': {
                        'account_id': 45000,
                        'agreement_id': 'some_agreement',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'some_sub_account',
                    },
                },
            ],
        ),
        (
            {
                'account': {'account_id': 45000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.001+00:00',
                'cursor': '2018-12-20T17:45:45.000000+00:00/34720330000',
                'limit': 1,
                'sort': 'desc',
            },
            [
                {
                    'entry_id': 34720320000,
                    'account_id': 45000,
                    'amount': '0.0000',
                    'doc_ref': 'doc_ref/111111/2',
                    'event_at': '2018-12-20T17:45:44.000000+00:00',
                    'reason': 'test',
                    'idempotency_key': '45000',
                    'created': '2018-12-20T17:45:44.000000+00:00',
                    'cursor': '2018-12-20T17:45:44.000000+00:00/34720320000',
                    'account': {
                        'account_id': 45000,
                        'agreement_id': 'some_agreement',
                        'currency': 'XXX',
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'sub_account': 'some_sub_account',
                    },
                },
            ],
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'agreement_id': 'ag%',
                    'currency': 'RUB',
                    'sub_account': 'income',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [
                {
                    'entry_id': 34720260000,
                    'event_at': '2018-12-20T17:45:43.000000+00:00',
                    'cursor': '2018-12-20T17:45:43.000000+00:00/34720260000',
                    'account_id': 41000,
                    'amount': '3.0000',
                    'doc_ref': 'brand_new/858895/3',
                    'reason': 'test',
                    'idempotency_key': '41000',
                    'created': '2018-12-20T17:45:43.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                        'account_id': 41000,
                    },
                },
                {
                    'entry_id': 34720280000,
                    'event_at': '2018-12-20T17:45:44.000000+00:00',
                    'cursor': '2018-12-20T17:45:44.000000+00:00/34720280000',
                    'account_id': 41000,
                    'amount': '300.0000',
                    'doc_ref': 'brand_new/858895/4',
                    'reason': 'test',
                    'idempotency_key': '41000',
                    'created': '2018-12-20T17:45:44.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                        'account_id': 41000,
                    },
                },
                {
                    'entry_id': 34720300000,
                    'event_at': '2018-12-20T17:50:00.000000+00:00',
                    'cursor': '2018-12-20T17:50:00.000000+00:00/34720300000',
                    'account_id': 43000,
                    'amount': '100.0000',
                    'doc_ref': 'brand_new/322228/2',
                    'reason': 'test',
                    'idempotency_key': '43000',
                    'created': '2018-12-20T17:50:00.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-001',
                        'currency': 'RUB',
                        'sub_account': 'income',
                        'account_id': 43000,
                    },
                },
            ],
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'currency': 'RUB',
                    'sub_account': 'inc%',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [
                {
                    'entry_id': 34720260000,
                    'event_at': '2018-12-20T17:45:43.000000+00:00',
                    'cursor': '2018-12-20T17:45:43.000000+00:00/34720260000',
                    'account_id': 41000,
                    'amount': '3.0000',
                    'doc_ref': 'brand_new/858895/3',
                    'reason': 'test',
                    'idempotency_key': '41000',
                    'created': '2018-12-20T17:45:43.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                        'account_id': 41000,
                    },
                },
                {
                    'entry_id': 34720280000,
                    'event_at': '2018-12-20T17:45:44.000000+00:00',
                    'cursor': '2018-12-20T17:45:44.000000+00:00/34720280000',
                    'account_id': 41000,
                    'amount': '300.0000',
                    'doc_ref': 'brand_new/858895/4',
                    'reason': 'test',
                    'idempotency_key': '41000',
                    'created': '2018-12-20T17:45:44.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                        'account_id': 41000,
                    },
                },
                {
                    'entry_id': 34720300000,
                    'event_at': '2018-12-20T17:50:00.000000+00:00',
                    'cursor': '2018-12-20T17:50:00.000000+00:00/34720300000',
                    'account_id': 43000,
                    'amount': '100.0000',
                    'doc_ref': 'brand_new/322228/2',
                    'reason': 'test',
                    'idempotency_key': '43000',
                    'created': '2018-12-20T17:50:00.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-001',
                        'currency': 'RUB',
                        'sub_account': 'income',
                        'account_id': 43000,
                    },
                },
            ],
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'currency': 'RUB',
                    'sub_account': 'inc_me',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [],
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'agreement_id': 'ag-rule-nMFG-001',
                    'currency': 'XXX',
                    'sub_account': 'num_%',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [
                {
                    'entry_id': 34720290000,
                    'event_at': '2018-12-20T17:50:00.000000+00:00',
                    'cursor': '2018-12-20T17:50:00.000000+00:00/34720290000',
                    'account_id': 42000,
                    'amount': '1.0000',
                    'doc_ref': 'brand_new/322228/1',
                    'reason': 'test',
                    'idempotency_key': '42000',
                    'created': '2018-12-20T17:50:00.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-001',
                        'currency': 'XXX',
                        'sub_account': 'num_orders',
                        'account_id': 42000,
                    },
                },
            ],
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'agreement_id': 'ag-rule-nMFG-001',
                    'currency': 'XXX',
                    'sub_account': 'num_orders',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [
                {
                    'entry_id': 34720290000,
                    'event_at': '2018-12-20T17:50:00.000000+00:00',
                    'cursor': '2018-12-20T17:50:00.000000+00:00/34720290000',
                    'account_id': 42000,
                    'amount': '1.0000',
                    'doc_ref': 'brand_new/322228/1',
                    'reason': 'test',
                    'idempotency_key': '42000',
                    'created': '2018-12-20T17:50:00.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-001',
                        'currency': 'XXX',
                        'sub_account': 'num_orders',
                        'account_id': 42000,
                    },
                },
            ],
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'agreement_id': 'some_agreement',
                    'currency': 'XXX',
                    'sub_account': 'su!_account',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [
                {
                    'entry_id': 34720340000,
                    'event_at': '2018-12-20T17:50:00.000000+00:00',
                    'cursor': '2018-12-20T17:50:00.000000+00:00/34720340000',
                    'account_id': 46000,
                    'amount': '56.0000',
                    'doc_ref': 'brand_new/322228/3',
                    'reason': 'test',
                    'idempotency_key': '46000',
                    'created': '2018-12-20T17:50:00.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'some_agreement',
                        'currency': 'XXX',
                        'sub_account': 'su!_account',
                        'account_id': 46000,
                    },
                },
            ],
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'agreement_id': 'some_agreement',
                    'currency': 'XXX',
                    'sub_account': 'su!%',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [
                {
                    'entry_id': 34720340000,
                    'event_at': '2018-12-20T17:50:00.000000+00:00',
                    'cursor': '2018-12-20T17:50:00.000000+00:00/34720340000',
                    'account_id': 46000,
                    'amount': '56.0000',
                    'doc_ref': 'brand_new/322228/3',
                    'reason': 'test',
                    'idempotency_key': '46000',
                    'created': '2018-12-20T17:50:00.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'some_agreement',
                        'currency': 'XXX',
                        'sub_account': 'su!_account',
                        'account_id': 46000,
                    },
                },
                {
                    'entry_id': 34720350000,
                    'event_at': '2018-12-20T17:50:00.000000+00:00',
                    'cursor': '2018-12-20T17:50:00.000000+00:00/34720350000',
                    'account_id': 47000,
                    'amount': '56.0000',
                    'doc_ref': 'brand_new/322228/4',
                    'reason': 'test',
                    'idempotency_key': '47000',
                    'created': '2018-12-20T17:50:00.000000+00:00',
                    'account': {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'some_agreement',
                        'currency': 'XXX',
                        'sub_account': 'su!maccount',
                        'account_id': 47000,
                    },
                },
            ],
        ),
    ],
    ids=[
        'by-account-id-40000',
        'by-account-properties',
        'sort-order-descending',
        'limit',
        'cursor-desc',
        'cursor-asc',
        'skip-zero-cursor-limit-desc-45000',
        'do-not-skip-zero-cursor-limit-desc-45000',
        'by-agreement-prefix',
        'by-sub-acc-prefix',
        'escape-undescore-symbol',
        'escape-undescore-symbol-2',
        'escape-undescore-symbol-3',
        'escape-escape-symbol',
        'do-not-escape-%-symbol',
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'test_select_advanced/journal@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql', 'journal@1.sql'),
)
async def test_journal_select_advanced(
        billing_accounts_client, request_headers, request_body, entries,
):
    response = await billing_accounts_client.post(
        '/v1/journal/select_advanced',
        json=request_body,
        headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code
    actual_response = await response.json()
    assert actual_response == entries


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        # Wrong request bodies
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Test everything is fine with valid test request
        (
            {
                'account': {'account_id': 40000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.1+00:00',
                'cursor': '',
                'limit': 30,
            },
            web.HTTPOk,
        ),
        (
            {
                'account': {
                    'entity_external_id': (
                        'unique_driver_id/583d4789250dd4071d3f6c09'
                    ),
                    'agreement_id': 'ag-rule-nMFG-000',
                    'currency': 'XXX',
                    'sub_account': 'num_orders',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.001+00:00',
                'cursor': '',
                'limit': 3,
            },
            web.HTTPOk,
        ),
        # Invalid requests
        (
            # missed account
            {
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.1+00:00',
                'cursor': '',
                'limit': 30,
            },
            web.HTTPBadRequest,
        ),
        (
            # missed entity causes internal error now
            # 'More than one shard match to account filter'
            {
                'account': {
                    'agreement_id': 'ag-rule-nMFG-000',
                    'currency': 'XXX',
                    'sub_account': 'num_orders',
                },
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.001+00:00',
                'cursor': '',
                'limit': 3,
            },
            web.HTTPBadRequest,
        ),
        (
            # missed date range
            {'account': {'account_id': 40000}, 'cursor': '', 'limit': 30},
            web.HTTPBadRequest,
        ),
        (
            # zero limit
            {
                'account': {'account_id': 40000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.1+00:00',
                'cursor': '',
                'limit': 0,
            },
            web.HTTPBadRequest,
        ),
        (
            # invalid sort
            {
                'account': {'account_id': 40000},
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.1+00:00',
                'cursor': '',
                'sort': 'foo',
                'limit': 1,
            },
            web.HTTPBadRequest,
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql', 'journal@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql', 'journal@1.sql'),
)
# pylint: disable=invalid-name
async def test_journal_select_advanced_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v1/journal/select_advanced',
        json=request_body,
        headers=request_headers,
    )
    assert response.status == expected_response.status_code


@pytest.mark.parametrize(
    'request_body,entries',
    [
        (
            {'entry_ids': [34720250000]},
            {
                'entries': [
                    {
                        'account': {
                            'account_id': 40000,
                            'agreement_id': 'ag-rule-nMFG-000',
                            'currency': 'XXX',
                            'entity_external_id': (
                                'unique_driver_id/583d4789250dd4071d3f6c09'
                            ),
                            'sub_account': 'num_orders',
                        },
                        'account_id': 40000,
                        'amount': '1.0000',
                        'created': '2018-12-20T17:45:42.000000+00:00',
                        'doc_ref': 'brand_new/858895/1',
                        'entry_id': 34720250000,
                        'event_at': '2018-12-20T17:45:42.000000+00:00',
                        'idempotency_key': '40000',
                        'reason': 'test',
                    },
                ],
            },
        ),
        (
            {'entry_ids': [34720250000, 34720260000, 34720270000]},
            {
                'entries': [
                    {
                        'account': {
                            'account_id': 40000,
                            'agreement_id': 'ag-rule-nMFG-000',
                            'currency': 'XXX',
                            'entity_external_id': (
                                'unique_driver_id/583d4789250dd4071d3f6c09'
                            ),
                            'sub_account': 'num_orders',
                        },
                        'account_id': 40000,
                        'amount': '2.0000',
                        'created': '2018-12-20T17:45:44.000000+00:00',
                        'doc_ref': 'brand_new/858895/2',
                        'entry_id': 34720270000,
                        'event_at': '2018-12-20T17:45:44.000000+00:00',
                        'idempotency_key': '40000',
                        'reason': 'test',
                    },
                    {
                        'account': {
                            'account_id': 40000,
                            'agreement_id': 'ag-rule-nMFG-000',
                            'currency': 'XXX',
                            'entity_external_id': (
                                'unique_driver_id/583d4789250dd4071d3f6c09'
                            ),
                            'sub_account': 'num_orders',
                        },
                        'account_id': 40000,
                        'amount': '1.0000',
                        'created': '2018-12-20T17:45:42.000000+00:00',
                        'doc_ref': 'brand_new/858895/1',
                        'entry_id': 34720250000,
                        'event_at': '2018-12-20T17:45:42.000000+00:00',
                        'idempotency_key': '40000',
                        'reason': 'test',
                    },
                    {
                        'account': {
                            'account_id': 41000,
                            'agreement_id': 'ag-rule-nMFG-000',
                            'currency': 'RUB',
                            'entity_external_id': (
                                'unique_driver_id/583d4789250dd4071d3f6c09'
                            ),
                            'sub_account': 'income',
                        },
                        'account_id': 41000,
                        'amount': '3.0000',
                        'created': '2018-12-20T17:45:43.000000+00:00',
                        'doc_ref': 'brand_new/858895/3',
                        'entry_id': 34720260000,
                        'event_at': '2018-12-20T17:45:43.000000+00:00',
                        'idempotency_key': '41000',
                        'reason': 'test',
                    },
                ],
            },
        ),
        (
            {'entry_ids': [34720250000, 34720260000, 34720250004]},
            {
                'entries': [
                    {
                        'account': {
                            'account_id': 40000,
                            'agreement_id': 'ag-rule-nMFG-000',
                            'currency': 'XXX',
                            'entity_external_id': (
                                'unique_driver_id/583d4789250dd4071d3f6c09'
                            ),
                            'sub_account': 'num_orders',
                        },
                        'account_id': 40000,
                        'amount': '1.0000',
                        'created': '2018-12-20T17:45:42.000000+00:00',
                        'doc_ref': 'brand_new/858895/1',
                        'entry_id': 34720250000,
                        'event_at': '2018-12-20T17:45:42.000000+00:00',
                        'idempotency_key': '40000',
                        'reason': 'test',
                    },
                    {
                        'account': {
                            'account_id': 41000,
                            'agreement_id': 'ag-rule-nMFG-000',
                            'currency': 'RUB',
                            'entity_external_id': (
                                'unique_driver_id/583d4789250dd4071d3f6c09'
                            ),
                            'sub_account': 'income',
                        },
                        'account_id': 41000,
                        'amount': '3.0000',
                        'created': '2018-12-20T17:45:43.000000+00:00',
                        'doc_ref': 'brand_new/858895/3',
                        'entry_id': 34720260000,
                        'event_at': '2018-12-20T17:45:43.000000+00:00',
                        'idempotency_key': '41000',
                        'reason': 'test',
                    },
                    {
                        'account': {
                            'account_id': 40004,
                            'agreement_id': 'ag-subv-001',
                            'currency': 'RUB',
                            'entity_external_id': (
                                'unique_driver_id/5b6b177a41e102a72fa4e223'
                            ),
                            'sub_account': 'income',
                        },
                        'account_id': 40004,
                        'amount': '2.0000',
                        'created': '2018-12-20T17:45:42.811977+00:00',
                        'doc_ref': 'brand_new/858895/1',
                        'entry_id': 34720250004,
                        'event_at': '2018-12-20T17:45:42.000000+00:00',
                        'idempotency_key': '40004',
                        'reason': 'test',
                    },
                ],
            },
        ),
        ({'entry_ids': [34720990000]}, {'entries': []}),
    ],
    ids=[
        'search entry',
        'search multiple entries',
        'search multiple entries and shards',
        'result not in pg',
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'test_select_advanced/journal@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql', 'journal@1.sql'),
)
async def test_journal_search_by_id(
        billing_accounts_client, request_headers, request_body, entries,
):
    response = await billing_accounts_client.post(
        '/v1/journal/by_id', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code
    actual_response = await response.json()
    assert actual_response == entries


@pytest.mark.parametrize(
    'request_body',
    [({'entry_ids': []},), ({'entry_ids': ['string']},)],
    ids=['empty request', 'wrong type in array'],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'test_select_advanced/journal@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql', 'journal@1.sql'),
)
async def test_journal_search_by_id_invalid(
        billing_accounts_client, request_headers, request_body,
):
    response = await billing_accounts_client.post(
        '/v1/journal/by_id', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPBadRequest.status_code


def patch_id_delay(context: ba_context.Context, delay: int):
    context.config.BILLING_ACCOUNTS_GLOBAL_SELECT_ID_DELAY = delay


async def get_live_balance(
        billing_accounts_client, request_headers, account_id: int,
) -> Optional[str]:
    request_body = {
        'accounts': [{'account_id': account_id}],
        'accrued_at': ['2099-01-01T00:00:00+00:00'],
        'offset': 0,
        'limit': 1,
    }
    response = await billing_accounts_client.post(
        '/v1/balances/select', json=request_body, headers=request_headers,
    )
    response_data = await response.json()
    for balance_entry in response_data:
        for balance_at in balance_entry['balances']:
            return balance_at['balance']
    return None
