import pytest


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.servicetest
@pytest.mark.parametrize(
    'order_request, journal_by_tag_request, journal_by_tag_response, '
    'expected_status, expected_response',
    [
        (
            {
                'wallet_id': 'non-existing',
                'yandex_uid': 'uid',
                'service': '<service>',
                'order_id': '<order_id>',
            },
            {
                'accounts': [
                    {
                        'agreement_id': 'non-existing',
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'tags': ['w/oid/<service>/<order_id>'],
                'begin_time': '1970-01-01T00:00:00+00:00',
                'end_time': '2020-02-03T00:00:00+00:00',
            },
            {'entries': {}},
            200,
            {'transactions': []},
        ),
        (
            {
                'wallet_id': 'existing',
                'yandex_uid': 'uid',
                'service': '<service>',
                'order_id': '<order_id>',
            },
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'tags': ['w/oid/<service>/<order_id>'],
                'begin_time': '1970-01-01T00:00:00+00:00',
                'end_time': '2020-02-03T00:00:00+00:00',
            },
            {
                'entries': {
                    'w/oid/<service>/<order_id>': [
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
                        {
                            'entry_id': 50000000002,
                            'account': {
                                'account_id': 50000000002,
                                'entity_external_id': 'uid',
                                'agreement_id': 'existing-2',
                                'currency': 'RUB',
                                'sub_account': 'deposit',
                            },
                            'amount': '200.0',
                            'doc_ref': 50000000003,
                            'created': '2020-02-25T06:00:00+03:00',
                            'event_at': '2020-02-25T05:00:00+03:00',
                            'details': {
                                'transaction_id': 'a',
                                'service': 's',
                                'service_name': 'taxi',
                            },
                        },
                    ],
                },
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
                    {
                        'amount': '200.0',
                        'currency': 'RUB',
                        'event_at': '2020-02-25T02:00:00+00:00',
                        'id': 'a',
                        'service': 's',
                        'service_name': 'taxi',
                    },
                ],
            },
        ),
    ],
)
async def test_order(
        taxi_billing_wallet,
        mockserver,
        order_request,
        journal_by_tag_request,
        journal_by_tag_response,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    def _journal_by_tag(request):
        assert request.json == journal_by_tag_request
        return journal_by_tag_response

    response = await taxi_billing_wallet.post('order', json=order_request)
    assert response.status_code == expected_status
    assert response.json() == expected_response
