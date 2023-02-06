import pytest


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.servicetest
@pytest.mark.parametrize(
    'search_request, execute_request, execute_response, expected_status,'
    'expected_response',
    [
        (
            {'yandex_uid': 'uid', 'currency': 'RUB'},
            {
                'data': {
                    'account': {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': (
                            'w/b8f2d769-f1fb-572a-a943-347f87988b0c'
                        ),
                        'sub_account': 'deposit',
                    },
                    'currency': 'RUB',
                    'wallet_id': 'w/b8f2d769-f1fb-572a-a943-347f87988b0c',
                    'yandex_uid': 'uid',
                },
                'kind': 'billing_wallet_create',
                'external_ref': 'w/b8f2d769-f1fb-572a-a943-347f87988b0c',
                'event_at': '2020-02-02T00:00:00+00:00',
            },
            {
                'data': {
                    'account': {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wid',
                        'sub_account': 'deposit',
                    },
                    'currency': 'RUB',
                    'wallet_id': 'wid',
                    'yandex_uid': 'uid',
                },
                'doc_id': 10000000000,
                'kind': 'billing_wallet_create',
                'external_ref': 'w/b8f2d769-f1fb-572a-a943-347f87988b0c',
                'topic': 'topic',
                'event_at': '2020-02-02T00:00:00+00:00',
                'created': '2020-02-02T00:00:00+00:00',
            },
            200,
            {'wallet_id': 'wid'},
        ),
    ],
)
async def test_create(
        taxi_billing_wallet,
        mockserver,
        search_request,
        execute_request,
        execute_response,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/billing-orders/v1/execute')
    def _execute(request):
        assert request.json == execute_request
        return execute_response

    response = await taxi_billing_wallet.post('create', json=search_request)
    assert response.status_code == expected_status
    assert response.json() == expected_response
