# pylint: disable=too-many-lines
from aiohttp import web
import pytest


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '0.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'zero amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '1.0000',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'one',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '0.0001',
                        'doc_ref': 'uniq_doc_ref/3',
                        'reason': 'min non zero abs amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '-999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/4',
                        'reason': 'min amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/5',
                        'reason': 'max amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            # empty details
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/5',
                        'reason': 'max amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': {},
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            # non-empty details
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/5',
                        'reason': 'max amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': {'alias_id': 'some_alias_id'},
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            # multiple entries
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40000,
                        'amount': '4042.0003',
                        'doc_ref': 'uniq_doc_ref/3',
                        'reason': 'long comment ' * 30,
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '0.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'zero amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '1.0000',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'one',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '0.0001',
                        'doc_ref': 'uniq_doc_ref/3',
                        'reason': 'min non zero abs amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '-999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/4',
                        'reason': 'min amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_v2_journal_append(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    first = await billing_accounts_client.post(
        '/v2/journal/append', json=request_body, headers=request_headers,
    )

    assert first.status == web.HTTPOk.status_code

    second = await billing_accounts_client.post(
        '/v2/journal/append', json=request_body, headers=request_headers,
    )

    # check idempotency feature
    assert first.status == second.status
    assert await first.json() == await second.json()

    def key(entry):
        return entry['account_id'], entry['doc_ref']

    result = sorted((await first.json())['entries'], key=key)
    expected = sorted(request_body['entries'], key=key)

    assert len(result) == len(expected)

    for res, exp in zip(result, expected):
        assert res.get('entry_id') is not None
        res.pop('entry_id')

        assert res.get('created') is not None
        res.pop('created')

        assert res.get('idempotency_key') is not None
        res.pop('idempotency_key')

        assert res == exp


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/5',
                        'reason': 'max amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': {'alias_id': 'some_alias_id'},
                        'idempotency_key': 'some_idempotency_key',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/5',
                        'reason': 'max amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': {'alias_id': 'some_alias_id'},
                        'idempotency_key': 'some_idempotency_key',
                    },
                ],
            },
        ),
        (
            # multiple entries
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40000,
                        'amount': '4042.0003',
                        'doc_ref': 'uniq_doc_ref/3',
                        'reason': 'long comment ' * 30,
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '0.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'zero amount',
                        'idempotency_key': 'some_idempotency_key',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '1.0000',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'one',
                        'idempotency_key': 'some_idempotency_key',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'idempotency_key': '40000',
                    },
                    {
                        'account_id': 40000,
                        'amount': '4042.0003',
                        'doc_ref': 'uniq_doc_ref/3',
                        'reason': 'long comment ' * 30,
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'idempotency_key': '40000',
                    },
                    {
                        'account_id': 40004,
                        'amount': '0.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'zero amount',
                        'idempotency_key': 'some_idempotency_key',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '1.0000',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'one',
                        'idempotency_key': 'some_idempotency_key',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
        ),
        (
            # multiple entries
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'idempotency_key': 'key_entry_1',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40000,
                        'amount': '4042.0003',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'long comment ' * 5,
                        'idempotency_key': 'key_entry_2',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40000,
                        'amount': '5.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'small amount',
                        'idempotency_key': 'key_entry_3',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'idempotency_key': 'key_entry_1',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40000,
                        'amount': '4042.0003',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'long comment ' * 5,
                        'idempotency_key': 'key_entry_2',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40000,
                        'amount': '5.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'small amount',
                        'idempotency_key': 'key_entry_3',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_v2_journal_append_idempotency_key(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    first = await billing_accounts_client.post(
        '/v2/journal/append', json=request_body, headers=request_headers,
    )

    assert first.status == web.HTTPOk.status_code

    second = await billing_accounts_client.post(
        '/v2/journal/append', json=request_body, headers=request_headers,
    )

    # check idempotency feature
    assert first.status == second.status
    assert await first.json() == await second.json()

    def key(entry):
        return entry['account_id'], entry['doc_ref'], entry['idempotency_key']

    result = sorted((await first.json())['entries'], key=key)
    expected = sorted(expected_response['entries'], key=key)

    assert len(result) == len(expected)

    for res, exp in zip(result, expected):
        assert res.get('entry_id') is not None
        res.pop('entry_id')

        assert res.get('created') is not None
        res.pop('created')

        assert res == exp


@pytest.mark.parametrize(
    'first_request_body,first_expected_response,second_request_body',
    [
        (
            {
                'entries': [
                    {
                        'account_id': 41004,
                        'amount': '512.3500',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'idempotency_key': 'key_entry_1',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                    {
                        'account_id': 41004,
                        'amount': '420.00',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some new comment',
                        'idempotency_key': 'key_entry_2',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                    {
                        'account_id': 41004,
                        'amount': '5.00',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some more comment',
                        'idempotency_key': 'key_entry_3',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 41004,
                        'amount': '512.3500',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'idempotency_key': 'key_entry_1',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                    {
                        'account_id': 41004,
                        'amount': '420.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some new comment',
                        'idempotency_key': 'key_entry_2',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                    {
                        'account_id': 41004,
                        'amount': '5.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some more comment',
                        'idempotency_key': 'key_entry_3',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 41004,
                        'amount': '987.8300',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'existing entry',
                        'idempotency_key': 'key_entry_2',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                    {
                        'account_id': 41004,
                        'amount': '20.0000',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'existing entry',
                        'idempotency_key': 'key_entry_3',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                    {
                        'account_id': 41004,
                        'amount': '67.0150',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'idempotency_key': 'key_entry_4',
                        'event_at': '2021-03-18T12:56:41.000000+00:00',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_v2_journal_append_idempotency_resolving(
        billing_accounts_client,
        request_headers,
        first_request_body,
        first_expected_response,
        second_request_body,
):
    first = await billing_accounts_client.post(
        '/v2/journal/append', json=first_request_body, headers=request_headers,
    )

    assert first.status == web.HTTPOk.status_code

    second = await billing_accounts_client.post(
        '/v2/journal/append',
        json=second_request_body,
        headers=request_headers,
    )

    assert second.status == web.HTTPConflict.status_code

    def key(entry):
        return entry['account_id'], entry['doc_ref'], entry['idempotency_key']

    result = sorted((await first.json())['entries'], key=key)
    expected = sorted(first_expected_response['entries'], key=key)

    assert len(result) == len(expected)

    for res, exp in zip(result, expected):
        assert res.get('entry_id') is not None
        res.pop('entry_id')

        assert res.get('created') is not None
        res.pop('created')

        assert res == exp


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        # Wrong request bodies
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Test everything is fine with valid test request
        (
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        (
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': {'alias_id': 'some_alias_id'},
                    },
                ],
            },
            web.HTTPOk,
        ),
        # Invalid requests
        (
            # missed account
            {
                'entries': [
                    {
                        'amount': '0',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'zero amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # missed doc_ref
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '2001.3400',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # missed amount
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # missed event_at
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # no such account-id
            {
                'entries': [
                    {
                        'account_id': 140000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # no such account-id: 0
            {
                'entries': [
                    {
                        'account_id': 0,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # wrong details (number)
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': 1,
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # wrong details (string)
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': '',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # no time zone in event_at
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
        (
            # no time in event_at
            {
                'entries': [
                    {
                        'account_id': 40004,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18',
                    },
                ],
            },
            web.HTTPBadRequest,
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_v2_journal_append_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v2/journal/append', json=request_body, headers=request_headers,
    )
    assert response.status == expected_response.status_code


@pytest.mark.parametrize(
    'request_body_1, request_body_2, expected_response',
    [
        # Ok
        (
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        # Ok
        (
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '3.00',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPOk,
        ),
        # Ok
        (
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/1',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'reason': 'some comment',
                        'details': {'alias_id': 'some_id'},
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '3.00',
                        'doc_ref': 'uniq_doc_ref/2',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'reason': 'some comment',
                        'details': {'alias_id': 'some_id'},
                    },
                ],
            },
            web.HTTPOk,
        ),
        # diff amount
        (
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '-2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPConflict,
        ),
        # diff reason
        (
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment 1',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment 2',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPConflict,
        ),
        # diff reason (empty, non empty)
        (
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment 2',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            web.HTTPConflict,
        ),
        # diff details
        (
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': {'alias_id': 'some_id'},
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/1',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                        'details': {'alias_id': 'some_id', 'prop': 1},
                    },
                ],
            },
            web.HTTPConflict,
        ),
        (
            # multiple entries
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '1.0000',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'one',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '-999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/4',
                        'reason': 'min amount',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                ],
            },
            {
                'entries': [
                    {
                        'account_id': 40000,
                        'amount': '2001.3400',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'some comment',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    {
                        'account_id': 40004,
                        'amount': '1.0000',
                        'doc_ref': 'uniq_doc_ref/2',
                        'reason': 'one',
                        'event_at': '2018-10-18T17:26:31.000000+00:00',
                    },
                    # diff event_at
                    {
                        'account_id': 40004,
                        'amount': '-999999999999999.9999',
                        'doc_ref': 'uniq_doc_ref/4',
                        'reason': 'min amount',
                        'event_at': '2018-10-18T17:26:32.000000+00:00',
                    },
                ],
            },
            web.HTTPConflict,
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_v2_journal_conflict(
        billing_accounts_client,
        request_headers,
        request_body_1,
        request_body_2,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v2/journal/append', json=request_body_1, headers=request_headers,
    )
    assert response.status == web.HTTPOk.status_code

    response = await billing_accounts_client.post(
        '/v2/journal/append', json=request_body_2, headers=request_headers,
    )
    assert response.status == expected_response.status_code


@pytest.mark.parametrize(
    'request_body,expected_exntry_ids,expected_cursor',
    [
        (
            {
                'accounts': [
                    {'account_id': 40000},
                    {
                        'entity_external_id': (
                            'unique_driver_id/5b6b177a41e102a72fa4e223'
                        ),
                        'agreement_id': 'ag-subv-001',
                        'currency': 'RUB',
                    },
                ],
                'doc_refs': ['doc_ref_01', 'doc_ref_11'],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {},
                'limit': 10,
            },
            [34720250000, 34720250004],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720250000},
                    {'vshard_id': 4, 'last_entry_id': 34720250004},
                ],
                'current_vshard_id': 4,
            },
        ),
        (
            {
                'accounts': [
                    {'account_id': 40000},
                    {
                        'entity_external_id': (
                            'unique_driver_id/5b6b177a41e102a72fa4e223'
                        ),
                        'agreement_id': 'ag-subv-001',
                        'currency': 'RUB',
                    },
                ],
                'doc_refs': ['doc_ref_01', 'doc_ref_11'],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {},
                'limit': 1,
            },
            [34720250000],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720250000},
                    {'vshard_id': 4, 'last_entry_id': 0},
                ],
                'current_vshard_id': 0,
            },
        ),
        (
            {
                'accounts': [
                    {'account_id': 40000},
                    {
                        'entity_external_id': (
                            'unique_driver_id/5b6b177a41e102a72fa4e223'
                        ),
                        'agreement_id': 'ag-subv-001',
                        'currency': 'RUB',
                    },
                ],
                'doc_refs': ['doc_ref_01', 'doc_ref_11'],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {
                    'vshard_cursors': [
                        {'vshard_id': 0, 'last_entry_id': 34720250000},
                        {'vshard_id': 4, 'last_entry_id': 0},
                    ],
                    'current_vshard_id': 4,
                },
                'limit': 1,
            },
            [34720250004],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720250000},
                    {'vshard_id': 4, 'last_entry_id': 34720250004},
                ],
                'current_vshard_id': 4,
            },
        ),
        (
            {
                'accounts': [
                    {'account_id': 40000},
                    {
                        'entity_external_id': (
                            'unique_driver_id/5b6b177a41e102a72fa4e223'
                        ),
                        'agreement_id': 'ag-subv-001',
                        'currency': 'RUB',
                    },
                ],
                'doc_refs': ['doc_ref_01', 'doc_ref_03', 'doc_ref_11'],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {
                    'vshard_cursors': [
                        {'vshard_id': 0, 'last_entry_id': 34720250000},
                        {'vshard_id': 4, 'last_entry_id': 0},
                    ],
                    'current_vshard_id': 0,
                },
                'limit': 1,
            },
            [34720270000],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720270000},
                    {'vshard_id': 4, 'last_entry_id': 0},
                ],
                'current_vshard_id': 0,
            },
        ),
        (
            {
                'accounts': [{'account_id': 40000}],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'limit': 100,
            },
            [34720250000, 34720270000],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720270000},
                ],
                'current_vshard_id': 0,
            },
        ),
        (
            {
                'accounts': [{'account_id': 40000}],
                'doc_refs': [],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'limit': 100,
            },
            [],
            {
                'vshard_cursors': [{'vshard_id': 0, 'last_entry_id': 0}],
                'current_vshard_id': 0,
            },
        ),
        (
            {
                'accounts': [{'account_id': 45000}, {'account_id': 45004}],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {},
                'limit': 2,
                'skip_zero_entries': True,
            },
            [34720300000, 34720270004],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720300000},
                    {'vshard_id': 4, 'last_entry_id': 34720270004},
                ],
                'current_vshard_id': 4,
            },
        ),
        (
            {
                'accounts': [{'account_id': 45000}, {'account_id': 45004}],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {
                    'vshard_cursors': [
                        {'vshard_id': 0, 'last_entry_id': 34720300000},
                        {'vshard_id': 4, 'last_entry_id': 0},
                    ],
                    'current_vshard_id': 0,
                },
                'limit': 2,
                'skip_zero_entries': True,
            },
            [34720270004],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720300000},
                    {'vshard_id': 4, 'last_entry_id': 34720270004},
                ],
                'current_vshard_id': 4,
            },
        ),
        (
            {
                'accounts': [{'account_id': 45000}, {'account_id': 45004}],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {},
                'limit': 2,
            },
            [34720290000, 34720300000],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720300000},
                    {'vshard_id': 4, 'last_entry_id': 0},
                ],
                'current_vshard_id': 0,
            },
        ),
        (
            {
                'accounts': [{'account_id': 45000}, {'account_id': 45004}],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {
                    'vshard_cursors': [
                        {'vshard_id': 0, 'last_entry_id': 34720300000},
                        {'vshard_id': 4, 'last_entry_id': 0},
                    ],
                    'current_vshard_id': 0,
                },
                'limit': 2,
            },
            [34720260004, 34720270004],
            {
                'vshard_cursors': [
                    {'vshard_id': 0, 'last_entry_id': 34720300000},
                    {'vshard_id': 4, 'last_entry_id': 34720270004},
                ],
                'current_vshard_id': 4,
            },
        ),
        (
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/5b6b177a41e102a72fa4e223'
                        ),
                        'currency': 'RUB',
                    },
                    {
                        'entity_external_id': (
                            'unique_driver_id/5b6b177a41e102a72fa4e223'
                        ),
                        'sub_account': 'income',
                    },
                ],
                'doc_refs': ['doc_ref_01', 'doc_ref_11'],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': {},
                'limit': 10,
            },
            [34720250004],
            {
                'vshard_cursors': [
                    {'vshard_id': 4, 'last_entry_id': 34720250004},
                ],
                'current_vshard_id': 4,
            },
        ),
    ],
    ids=[
        '2accounts-2doc_refs-2shards',
        '2accounts-2doc_refs-2shard-1limit-first-query-first-shard',
        '2accounts-2doc_refs-2shard-cursor-second-query-second-shard',
        '2accounts-3doc_refs-2shard-1limit-second-query-still-first-shard',
        '1accounts-null-doc_refs',
        '1accounts-empty-doc_refs',
        '2accounts-skip-zero-both-shards',
        '2accounts-skip-zero-second-shard',
        '2accounts-do-not-skip-zero-first-shard',
        '2accounts-do-not-skip-zero-second-shard',
        '2filters-match-1-account-1shard',
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'entities@0.sql',
        'accounts@0.sql',
        'test_select/journal@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'entities@1.sql',
        'accounts@1.sql',
        'test_select/journal@1.sql',
    ),
)
async def test_v2_journal_select(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_exntry_ids,
        expected_cursor,
):
    response = await billing_accounts_client.post(
        '/v2/journal/select', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code
    actual_response = await response.json()
    actual_entry_ids = [it['entry_id'] for it in actual_response['entries']]
    assert expected_exntry_ids == actual_entry_ids
    assert actual_response['cursor'] == expected_cursor


@pytest.mark.parametrize(
    'request_body,entries',
    [
        (
            {
                'accounts': [{'account_id': 40000}],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                ],
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
                'accounts': [{'account_id': 40000}],
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
                'accounts': [{'account_id': 40000}],
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
                'accounts': [{'account_id': 40000}],
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
                'accounts': [{'account_id': 40000}],
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
                'accounts': [{'account_id': 45000}],
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
                'accounts': [{'account_id': 45000}],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag%',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                ],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'currency': 'RUB',
                        'sub_account': 'inc%',
                    },
                ],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'currency': 'RUB',
                        'sub_account': 'inc_me',
                    },
                ],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 10,
            },
            [],
        ),
        (
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-001',
                        'currency': 'XXX',
                        'sub_account': 'num_%',
                    },
                ],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-001',
                        'currency': 'XXX',
                        'sub_account': 'num_orders',
                    },
                ],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'some_agreement',
                        'currency': 'XXX',
                        'sub_account': 'su!_account',
                    },
                ],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'some_agreement',
                        'currency': 'XXX',
                        'sub_account': 'su!%',
                    },
                ],
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
        (
            {
                'accounts': [
                    {'account_id': 40000},
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                ],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '',
                'limit': 2,
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
            ],
        ),
        (
            {
                'accounts': [
                    {'account_id': 40000},
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                ],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T18:45:43.1+00:00',
                'cursor': '2018-12-20T17:45:43.000000+00:00/34720260000',
                'limit': 10,
            },
            [
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag%',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                ],
                'skip_accounts': [{'agreement_id': 'ag-rule-nMFG-001'}],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag%',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'some_agreement',
                    },
                ],
                'skip_accounts': [
                    {'agreement_id': 'ag-rule-nMFG-001'},
                    {'currency': 'XXX'},
                ],
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
                'accounts': [
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': 'ag%',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                    {
                        'entity_external_id': (
                            'unique_driver_id/583d4789250dd4071d3f6c09'
                        ),
                        'agreement_id': '%nMFG%',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                ],
                'skip_accounts': [{'agreement_id': 'ag-rule-nMFG-001'}],
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
        'few-accounts',
        'few-accounts-cursor',
        'by-agreement-prefix-with-blacklist',
        'by-agreement-prefix-multiple-filters-and-blacklists',
        'by-agreement-prefix-overlapping-filters',
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=(
        'meta.sql',
        'test_v2_journal_select_advanced/entities@0.sql',
        'test_v2_journal_select_advanced/accounts@0.sql',
        'test_v2_journal_select_advanced/journal@0.sql',
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=(
        'meta.sql',
        'test_v2_journal_select_advanced/entities@1.sql',
        'test_v2_journal_select_advanced/accounts@1.sql',
        'test_v2_journal_select_advanced/journal@1.sql',
    ),
)
async def test_v2_journal_select_advanced(
        billing_accounts_client, request_headers, request_body, entries,
):
    response = await billing_accounts_client.post(
        '/v2/journal/select_advanced',
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
            # Empty accounts
            {
                'accounts': [],
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
                'accounts': [
                    {
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'sub_account': 'num_orders',
                    },
                ],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.001+00:00',
                'cursor': '',
                'limit': 3,
            },
            web.HTTPBadRequest,
        ),
        (
            # Few accounts from different vshards
            # 'More than one shard match to account filter'
            {
                'accounts': [{'account_id': 40000}, {'account_id': 40001}],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.001+00:00',
                'cursor': '',
                'limit': 3,
            },
            web.HTTPBadRequest,
        ),
        (
            # missed date range
            {'accounts': [{'account_id': 40000}], 'cursor': '', 'limit': 30},
            web.HTTPBadRequest,
        ),
        (
            # zero limit
            {
                'accounts': [{'account_id': 40000}],
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
                'accounts': [{'account_id': 40000}],
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
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
# pylint: disable=invalid-name
async def test_v2_journal_select_advanced_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v2/journal/select_advanced',
        json=request_body,
        headers=request_headers,
    )
    assert response.status == expected_response.status_code
