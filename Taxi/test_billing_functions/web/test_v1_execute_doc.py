import copy

import pytest


@pytest.fixture
def taxi_billing_functions_mocks():
    """Put your mocks here"""


@pytest.mark.parametrize(
    'data_path, expected_path',
    [
        ('charge.json', 'charge_expected.json'),
        ('charge_refund.json', 'charge_refund_expected.json'),
        ('not_enought_funds.json', 'not_enought_funds_expected.json'),
        ('deposit.json', 'deposit_expected.json'),
    ],
)
@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_billing_functions_mocks')
@pytest.mark.now('2021-10-18T12:00:00+03:00')
async def test_v1_execute_doc(
        taxi_billing_functions_web,
        mockserver,
        do_mock_billing_accounts,
        do_mock_billing_docs,
        load_json,
        data_path,
        expected_path,
):
    data = load_json(data_path)
    expected = load_json(expected_path)

    billing_accounts = do_mock_billing_accounts()
    billing_docs = do_mock_billing_docs(data['existing_docs'])

    actual_entries = []

    @mockserver.json_handler('/billing-accounts/v1/journal/append_if')
    def _journal_append_if(request):
        actual_entries.append(copy.deepcopy(request.json))
        if data['handle_status'] == 'failed':
            return mockserver.make_response('Not enough funds', status=409)
        return mockserver.make_response(
            json={
                'entry_id': 1,
                'account_id': request.json['account_id'],
                'amount': request.json['amount'],
                'doc_ref': request.json['doc_ref'],
                'event_at': request.json['event_at'],
                'reason': '',
            },
        )

    response = await taxi_billing_functions_web.post(
        '/v1/execute_doc', json=data['request'],
    )
    assert response.status == 200
    json = await response.json()
    assert json == expected['response']

    actual_entries += billing_accounts.created_entries
    assert billing_accounts.created_entities == expected['entities']
    assert billing_accounts.created_accounts == expected['accounts']
    assert billing_docs.update_requests[0] == expected['doc_update_request']
    assert len(billing_docs.update_requests) == 1
    assert actual_entries == expected['entries']
