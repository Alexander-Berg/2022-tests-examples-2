import json

import pytest

from tests_billing_wallet import common


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.servicetest
@pytest.mark.parametrize(
    'x_idempotency_token, topup_request, execute_request, execute_response,'
    'expected_status, expected_response',
    [
        (
            'x_idempotency_token',
            {
                'yandex_uid': 'uid',
                'amount': '100.0',
                'currency': 'RUB',
                'service': 'eda',
                'wallet_id': 'non-existing',
                'payload': {'a': 'b'},
                'order_id': 'i',
            },
            {
                'data': {
                    'account': {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'non-existing',
                        'sub_account': 'deposit',
                    },
                    'wallet_id': 'non-existing',
                    'yandex_uid': 'uid',
                    'amount': '100.0',
                    'currency': 'RUB',
                    'service': 'eda',
                    'payload': {'a': 'b'},
                    'order_id': 'i',
                    'tags': ['w/oid/eda/i'],
                },
                'kind': 'billing_wallet_top_up',
                'external_ref': 'x_idempotency_token',
                'event_at': '2020-02-02T00:00:00+00:00',
            },
            common.Response(
                {'code': 'execute_error', 'message': 'Wallet not found'},
                status=404,
            ),
            404,
            {'code': 'wallet_not_found', 'message': 'Wallet not found'},
        ),
        (
            'x_idempotency_token',
            {
                'yandex_uid': 'uid',
                'amount': '100.0',
                'currency': 'RUB',
                'service': 'eda',
                'service_name': 'taxi',
                'wallet_id': 'wid',
                'payload': {'a': 'b'},
                'order_id': 'i',
            },
            {
                'data': {
                    'account': {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wid',
                        'sub_account': 'deposit',
                    },
                    'wallet_id': 'wid',
                    'yandex_uid': 'uid',
                    'amount': '100.0',
                    'currency': 'RUB',
                    'service': 'eda',
                    'service_name': 'taxi',
                    'payload': {'a': 'b'},
                    'order_id': 'i',
                    'tags': ['w/oid/eda/i'],
                },
                'kind': 'billing_wallet_top_up',
                'external_ref': 'x_idempotency_token',
                'event_at': '2020-02-02T00:00:00+00:00',
            },
            common.Response(
                {
                    'data': {'transaction_id': 'tid'},
                    'doc_id': 1,
                    'kind': 'billing_wallet_top_up',
                    'external_ref': 'x_idempotency_token',
                    'topic': 'topic',
                    'event_at': '2020-02-02T00:00:00+00:00',
                    'created': '2020-02-02T00:00:00+00:00',
                },
            ),
            200,
            {'transaction_id': 'tid'},
        ),
        (
            'x_idempotency_token',
            {
                'yandex_uid': 'uid',
                'amount': '100.0',
                'currency': 'RUB',
                'service': 'eda',
                'service_name': 'taxi',
                'wallet_id': 'wid',
                'payload': {'a': 'b'},
                'order_id': 'i',
                'transaction_type': 'payment',
            },
            {
                'data': {
                    'account': {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wid',
                        'sub_account': 'deposit',
                    },
                    'wallet_id': 'wid',
                    'yandex_uid': 'uid',
                    'amount': '100.0',
                    'currency': 'RUB',
                    'service': 'eda',
                    'service_name': 'taxi',
                    'payload': {'a': 'b'},
                    'order_id': 'i',
                    'tags': ['w/oid/eda/i'],
                    'transaction_type': 'payment',
                },
                'kind': 'billing_wallet_top_up',
                'external_ref': 'x_idempotency_token',
                'event_at': '2020-02-02T00:00:00+00:00',
            },
            common.Response(
                {
                    'data': {'transaction_id': 'tid'},
                    'doc_id': 1,
                    'kind': 'billing_wallet_top_up',
                    'external_ref': 'x_idempotency_token',
                    'topic': 'topic',
                    'event_at': '2020-02-02T00:00:00+00:00',
                    'created': '2020-02-02T00:00:00+00:00',
                },
            ),
            200,
            {'transaction_id': 'tid'},
        ),
        (
            'x_idempotency_token',
            {
                'yandex_uid': 'uid',
                'amount': '100.0',
                'currency': 'RUB',
                'service': 'eda',
                'service_name': 'taxi',
                'wallet_id': 'wid',
                'payload': {'a': 'b'},
                'order_id': 'i',
                'transaction_type': 'refund',
            },
            {
                'data': {
                    'account': {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wid',
                        'sub_account': 'deposit',
                    },
                    'wallet_id': 'wid',
                    'yandex_uid': 'uid',
                    'amount': '100.0',
                    'currency': 'RUB',
                    'service': 'eda',
                    'service_name': 'taxi',
                    'payload': {'a': 'b'},
                    'order_id': 'i',
                    'tags': ['w/oid/eda/i'],
                    'transaction_type': 'refund',
                },
                'kind': 'billing_wallet_top_up',
                'external_ref': 'x_idempotency_token',
                'event_at': '2020-02-02T00:00:00+00:00',
            },
            common.Response(
                {
                    'data': {'transaction_id': 'tid'},
                    'doc_id': 1,
                    'kind': 'billing_wallet_top_up',
                    'external_ref': 'x_idempotency_token',
                    'topic': 'topic',
                    'event_at': '2020-02-02T00:00:00+00:00',
                    'created': '2020-02-02T00:00:00+00:00',
                },
            ),
            200,
            {'transaction_id': 'tid'},
        ),
        (
            'x_idempotency_token',
            {
                'yandex_uid': 'uid',
                'amount': '100.0',
                'currency': 'RUB',
                'service': 'eda',
                'wallet_id': 'wid',
                'order_id': 'i',
            },
            {
                'data': {
                    'account': {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wid',
                        'sub_account': 'deposit',
                    },
                    'wallet_id': 'wid',
                    'yandex_uid': 'uid',
                    'amount': '100.0',
                    'currency': 'RUB',
                    'service': 'eda',
                    'order_id': 'i',
                    'tags': ['w/oid/eda/i'],
                },
                'kind': 'billing_wallet_top_up',
                'external_ref': 'x_idempotency_token',
                'event_at': '2020-02-02T00:00:00+00:00',
            },
            common.Response(
                {
                    'data': {'transaction_id': 'tid'},
                    'doc_id': 50000000001,
                    'kind': 'billing_wallet_top_up',
                    'external_ref': 'x_idempotency_token',
                    'topic': 'topic',
                    'event_at': '2020-02-02T00:00:00+00:00',
                    'created': '2020-02-02T00:00:00+00:00',
                },
            ),
            200,
            {'transaction_id': 'tid'},
        ),
    ],
)
async def test_topup(
        taxi_billing_wallet,
        mockserver,
        x_idempotency_token,
        topup_request,
        execute_request,
        execute_response,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/billing-orders/v1/execute')
    def _execute(request):
        assert request.json == execute_request
        return mockserver.make_response(
            json.dumps(execute_response.content),
            status=execute_response.status,
        )

    response = await taxi_billing_wallet.post(
        'topup',
        json=topup_request,
        headers={'X-Idempotency-Token': x_idempotency_token},
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response
