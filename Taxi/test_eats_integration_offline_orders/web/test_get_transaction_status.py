import pytest

from eats_integration_offline_orders.internal import enums


@pytest.mark.parametrize(
    'transaction_front_uuid, expected_request_status, '
    'expected_front_status,'
    'expected_reason',
    [
        pytest.param(
            'transaction_front_uuid__4',
            404,
            None,
            None,
            id='no transaction found',
        ),
        pytest.param(
            'transaction_front_uuid__1',
            200,
            enums.PaymentTransactionFrontStatus.IN_PROGRESS.value,
            None,
            id='success',
        ),
        pytest.param(
            'transaction_front_uuid__2',
            200,
            enums.PaymentTransactionFrontStatus.FAILED.value,
            enums.PaymentTransactionStatus.CANCELED.value,
            id='success',
        ),
        pytest.param(
            'transaction_front_uuid__3',
            200,
            enums.PaymentTransactionFrontStatus.SUCCESS.value,
            None,
            id='success',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'orders.sql', 'payment_transactions.sql'],
)
async def test_get_transaction_status(
        web_app_client,
        web_context,
        mock_tinkoff_securepay,
        mockserver,
        load_json,
        transaction_front_uuid,
        expected_request_status,
        expected_front_status,
        expected_reason,
):
    response = await web_app_client.get(
        f'/v1/pay/get_transaction_status?transaction_uuid='
        f'{transaction_front_uuid}',
    )
    assert response.status == expected_request_status
    if expected_request_status == 200:
        data = await response.json()
        expected_data = {'status': expected_front_status, 'poling_period': 3}
        if expected_reason:
            expected_data['reason'] = expected_reason
        assert data == expected_data
