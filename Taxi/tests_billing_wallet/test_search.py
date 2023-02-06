import pytest


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'search_request, accounts_search_request, accounts_search_response,'
    'expected_status, expected_response',
    [
        (
            {'wallet_id': 'non-existing', 'yandex_uid': 'uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'non-existing',
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
            },
            {'accounts': []},
            200,
            {'wallets': []},
        ),
        (
            {'yandex_uid': 'uid'},
            {
                'accounts': [
                    {
                        'sub_account': 'deposit',
                        'entity_external_id': 'wallet_id/uid',
                    },
                ],
            },
            {
                'accounts': [
                    {
                        'account_id': 50000000001,
                        'entity_external_id': 'uid',
                        'agreement_id': '11',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                        'opened': '2020-02-02T00:00:00+00:00',
                        'expired': '2021-02-02T00:00:00+00:00',
                    },
                ],
            },
            200,
            {
                'wallets': [
                    {'yandex_uid': 'uid', 'id': '11', 'currency': 'RUB'},
                ],
            },
        ),
        (
            {'wallet_id': 'existing', 'yandex_uid': 'uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
            },
            {
                'accounts': [
                    {
                        'account_id': 50000000001,
                        'entity_external_id': 'uid',
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                        'opened': '2020-02-02T00:00:00+00:00',
                        'expired': '2021-02-02T00:00:00+00:00',
                    },
                ],
            },
            200,
            {
                'wallets': [
                    {'yandex_uid': 'uid', 'id': 'existing', 'currency': 'RUB'},
                ],
            },
        ),
    ],
)
async def test_search(
        taxi_billing_wallet,
        mockserver,
        search_request,
        accounts_search_request,
        accounts_search_response,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _accounts_select(request):
        assert request.json == accounts_search_request
        return accounts_search_response

    response = await taxi_billing_wallet.post('search', json=search_request)
    assert response.status_code == expected_status
    assert response.json() == expected_response
