import pytest


@pytest.mark.servicetest
@pytest.mark.config(
    BILLING_WALLET_STATEMENT_MIN_TIME='2000-01-01T00:00:00+00:00',
)
@pytest.mark.parametrize(
    'statement_request, accounts_search_request, accounts_search_response,'
    'journal_select_request, journal_select_response, expected_status,'
    'expected_response',
    [
        (
            {
                'wallet_id': 'non-existing',
                'yandex_uid': 'uid',
                'start': '2020-02-25T00:00:00+00:00',
                'end': '2020-02-26T00:00:00+00:00',
            },
            {
                'agreement_id': 'non-existing',
                'entity_external_id': 'wallet_id/uid',
                'sub_account': 'deposit',
            },
            [],
            None,
            {'entries': [], 'cursor': {}},
            404,
            {'code': 'wallet_not_found', 'message': 'Wallet not found'},
        ),
        (
            {
                'wallet_id': 'existing',
                'yandex_uid': 'uid',
                'start': '2020-02-25T00:00:00+00:00',
                'end': '2020-02-26T00:00:00+00:00',
                'limit': 2,
            },
            {
                'agreement_id': 'existing',
                'entity_external_id': 'wallet_id/uid',
                'sub_account': 'deposit',
            },
            [
                {
                    'account_id': 50000000001,
                    'entity_external_id': 'uid',
                    'agreement_id': 'existing',
                    'currency': 'RUB',
                    'sub_account': 'deposit',
                    'opened': '2020-02-25T00:00:00+00:00',
                    'expired': '2021-02-25T00:00:00+00:00',
                },
            ],
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'entity_external_id': 'uid',
                        'sub_account': 'deposit',
                    },
                ],
                'begin_time': '2020-02-25T00:00:00+00:00',
                'cursor': {},
                'end_time': '2020-02-26T00:00:00+00:00',
                'limit': 2,
            },
            {
                'entries': [
                    {
                        'entry_id': 50000000001,
                        'account': {
                            'account_id': 50000000001,
                            'entity_external_id': 'uid',
                            'agreement_id': 'existing',
                            'currency': 'RUB',
                            'sub_account': 'deposit',
                        },
                        'amount': '100.0',
                        'doc_ref': 50000000002,
                        'created': '2020-02-25T06:00:00+03:00',
                        'event_at': '2020-02-25T05:00:00+03:00',
                        'details': {
                            'transaction_id': 'a',
                            'service': 's',
                            'service_name': 'taxi',
                        },
                    },
                ],
                'cursor': {},
            },
            200,
            {
                'transactions': [
                    {
                        'amount': '100.0',
                        'currency': 'RUB',
                        'event_at': '2020-02-25T02:00:00+00:00',
                        'id': 'a',
                        'service': 's',
                        'service_name': 'taxi',
                    },
                ],
            },
        ),
        (
            {
                'wallet_id': 'existing',
                'yandex_uid': 'uid',
                'start': '1999-12-31T23:00:00+00:00',
                'end': '2020-02-26T00:00:00+00:00',
                'limit': 2,
            },
            {
                'agreement_id': 'existing',
                'entity_external_id': 'wallet_id/uid',
                'sub_account': 'deposit',
            },
            [
                {
                    'account_id': 50000000001,
                    'entity_external_id': 'uid',
                    'agreement_id': 'existing',
                    'currency': 'RUB',
                    'sub_account': 'deposit',
                    'opened': '2020-02-25T00:00:00+00:00',
                    'expired': '2021-02-25T00:00:00+00:00',
                },
            ],
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'entity_external_id': 'uid',
                        'sub_account': 'deposit',
                    },
                ],
                'begin_time': '2000-01-01T00:00:00+00:00',
                'cursor': {},
                'end_time': '2020-02-26T00:00:00+00:00',
                'limit': 2,
            },
            {
                'entries': [
                    {
                        'entry_id': 50000000001,
                        'account': {
                            'account_id': 50000000001,
                            'entity_external_id': 'uid',
                            'agreement_id': 'existing',
                            'currency': 'RUB',
                            'sub_account': 'deposit',
                        },
                        'amount': '100.0',
                        'doc_ref': 50000000002,
                        'created': '2020-02-25T06:00:00+03:00',
                        'event_at': '2020-02-25T05:00:00+03:00',
                        'details': {
                            'transaction_id': 'a',
                            'service': 's',
                            'service_name': 'taxi',
                        },
                    },
                ],
                'cursor': {},
            },
            200,
            {
                'transactions': [
                    {
                        'amount': '100.0',
                        'currency': 'RUB',
                        'event_at': '2020-02-25T02:00:00+00:00',
                        'id': 'a',
                        'service': 's',
                        'service_name': 'taxi',
                    },
                ],
            },
        ),
        (
            {
                'wallet_id': 'existing',
                'yandex_uid': 'uid',
                'start': '2020-02-25T00:00:00+00:00',
                'end': '2020-02-26T00:00:00+00:00',
                'cursor': {'a': 'b'},
                'limit': 1,
            },
            {
                'agreement_id': 'existing',
                'entity_external_id': 'wallet_id/uid',
                'sub_account': 'deposit',
            },
            [
                {
                    'account_id': 50000000001,
                    'entity_external_id': 'uid',
                    'agreement_id': 'existing',
                    'currency': 'RUB',
                    'sub_account': 'deposit',
                    'opened': '2020-02-25T00:00:00+00:00',
                    'expired': '2021-02-25T00:00:00+00:00',
                },
            ],
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'entity_external_id': 'uid',
                        'sub_account': 'deposit',
                    },
                ],
                'begin_time': '2020-02-25T00:00:00+00:00',
                'cursor': {'a': 'b'},
                'end_time': '2020-02-26T00:00:00+00:00',
                'limit': 1,
            },
            {
                'entries': [
                    {
                        'entry_id': 50000000001,
                        'account': {
                            'account_id': 50000000001,
                            'entity_external_id': 'uid',
                            'agreement_id': 'existing',
                            'currency': 'RUB',
                            'sub_account': 'deposit',
                        },
                        'amount': '100.0',
                        'doc_ref': 50000000002,
                        'created': '2020-02-25T06:00:00+03:00',
                        'event_at': '2020-02-25T05:00:00+03:00',
                        'details': {'transaction_id': 'a', 'service': 's'},
                    },
                ],
                'cursor': {'key': 'value'},
            },
            200,
            {
                'transactions': [
                    {
                        'amount': '100.0',
                        'currency': 'RUB',
                        'event_at': '2020-02-25T02:00:00+00:00',
                        'id': 'a',
                        'service': 's',
                    },
                ],
                'next_cursor': {'key': 'value'},
            },
        ),
        (
            {
                'wallet_id': 'existing',
                'yandex_uid': 'uid',
                'start': '2020-02-25T00:00:00+00:00',
                'end': '2020-02-26T00:00:00+00:00',
                'cursor': {'a': 'b'},
                'limit': 4,
            },
            {
                'agreement_id': 'existing',
                'entity_external_id': 'wallet_id/uid',
                'sub_account': 'deposit',
            },
            [
                {
                    'account_id': 50000000001,
                    'entity_external_id': 'uid',
                    'agreement_id': 'existing',
                    'currency': 'RUB',
                    'sub_account': 'deposit',
                    'opened': '2020-02-25T00:00:00+00:00',
                    'expired': '2021-02-25T00:00:00+00:00',
                },
            ],
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'entity_external_id': 'uid',
                        'sub_account': 'deposit',
                    },
                ],
                'begin_time': '2020-02-25T00:00:00+00:00',
                'cursor': {'a': 'b'},
                'end_time': '2020-02-26T00:00:00+00:00',
                'limit': 4,
            },
            {
                'entries': [
                    {
                        'entry_id': 1,
                        'account': {
                            'account_id': 50000000001,
                            'entity_external_id': 'uid',
                            'agreement_id': 'existing',
                            'currency': 'RUB',
                            'sub_account': 'deposit',
                        },
                        'amount': '100.0',
                        'doc_ref': 50000000002,
                        'created': '2020-02-25T06:00:00+03:00',
                        'event_at': '2020-02-25T05:00:00+03:00',
                        'details': {
                            'transaction_id': 'a',
                            'service': 's',
                            'order_id': 'i',
                            'payload': {'q': 1},
                        },
                    },
                    {
                        'entry_id': 50000000002,
                        'account': {
                            'account_id': 50000000001,
                            'entity_external_id': 'uid',
                            'agreement_id': 'existing',
                            'currency': 'RUB',
                            'sub_account': 'deposit',
                        },
                        'amount': '10.0',
                        'doc_ref': 50000000003,
                        'created': '2020-02-25T06:00:00+03:00',
                        'event_at': '2020-02-25T05:00:00+03:00',
                        'details': {
                            'transaction_id': 'a',
                            'service': 's',
                            'payload': {},
                        },
                    },
                    {
                        'entry_id': 50000000003,
                        'account': {
                            'account_id': 50000000001,
                            'entity_external_id': 'uid',
                            'agreement_id': 'existing',
                            'currency': 'RUB',
                            'sub_account': 'deposit',
                        },
                        'amount': '12.0',
                        'doc_ref': 50000000004,
                        'created': '2020-02-25T06:00:00+03:00',
                        'event_at': '2020-02-25T05:00:00+03:00',
                        'details': {},
                    },
                ],
                'cursor': {'key': 'value'},
            },
            200,
            {
                'transactions': [
                    {
                        'amount': '100.0',
                        'currency': 'RUB',
                        'event_at': '2020-02-25T02:00:00+00:00',
                        'id': 'a',
                        'service': 's',
                        'order_id': 'i',
                        'payload': {'q': 1},
                    },
                    {
                        'amount': '10.0',
                        'currency': 'RUB',
                        'event_at': '2020-02-25T02:00:00+00:00',
                        'id': 'a',
                        'service': 's',
                        'payload': {},
                    },
                    {
                        'amount': '12.0',
                        'currency': 'RUB',
                        'event_at': '2020-02-25T02:00:00+00:00',
                        'id': '50000000003',
                    },
                ],
            },
        ),
    ],
)
async def test_statement(
        taxi_billing_wallet,
        mockserver,
        statement_request,
        accounts_search_request,
        accounts_search_response,
        journal_select_request,
        journal_select_response,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/billing-accounts/v1/accounts/search')
    def _accounts_search(request):
        assert request.json == accounts_search_request
        return accounts_search_response

    @mockserver.json_handler('/billing-reports/v1/journal/select')
    def _journal_select(request):
        assert request.json == journal_select_request
        return journal_select_response

    response = await taxi_billing_wallet.post(
        'statement', json=statement_request,
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response
