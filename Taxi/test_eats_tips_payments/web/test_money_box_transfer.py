import datetime
import decimal

import pytest

NOW = datetime.datetime(2022, 1, 24, 14, 30, 15, tzinfo=datetime.timezone.utc)
BOX_1_ID = '00000000-0000-0000-0000-000000000001'
BOX_2_ID = '00000000-0000-0000-0000-000000000002'
BOX_1_PERIOD = '10000000-0000-0000-0000-000000000001'
RECEIVER_1 = {
    'amount': '100',
    'partner_id': '00000000-0000-0000-1000-000000000001',
    'receiver_id_b2p': '00000000-0000-1000-0000-000000000001',
}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    (
        'request_body',
        'idempotency_token',
        'expected_orders',
        'expected_status',
        'expected_response',
    ),
    (
        pytest.param(
            {'box_id': BOX_1_ID, 'receivers': [RECEIVER_1]},
            'token1',
            [
                {
                    'idempotency_token': f'token1-{RECEIVER_1["partner_id"]}',
                    'recipient_id': RECEIVER_1['partner_id'],
                    'recipient_id_b2p': RECEIVER_1['receiver_id_b2p'],
                    'recipient_type': 'partner',
                    'payment_type': 'b2p',
                    'guest_amount': decimal.Decimal(100),
                    'commission': decimal.Decimal(0),
                    'status': 'CREATED',
                    'payer_type': 'MONEY_BOX',
                    'payer_id': BOX_1_ID,
                    'money_box_period_id': BOX_1_PERIOD,
                },
            ],
            200,
            '',
            id='success',
        ),
        pytest.param(
            {'box_id': BOX_1_ID, 'receivers': [RECEIVER_1]},
            'token2',
            '',
            409,
            {'code': 'duplicate_token', 'message': 'token already exists'},
            id='duplicate-token',
        ),
        pytest.param(
            {'box_id': BOX_2_ID, 'receivers': [RECEIVER_1]},
            'token1',
            '',
            400,
            {'code': 'client_error', 'message': 'money box is not active'},
            id='duplicate-token',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_money_box_transfer(
        web_app_client,
        web_context,
        mock_best2pay,
        mock_eats_tips_partners,
        pgsql,
        request_body,
        idempotency_token,
        expected_orders,
        expected_status,
        expected_response,
):
    response = await web_app_client.post(
        '/internal/v1/money-box/transfer',
        json=request_body,
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status == expected_status
    if expected_status != 200:
        response_json = await response.json()
        assert response_json == expected_response

    with pgsql['eats_tips_payments'].dict_cursor() as cursor:
        cursor.execute(
            'select idempotency_token, recipient_id, recipient_id_b2p, '
            'recipient_type, payment_type, guest_amount, commission, '
            'payer_type, payer_id, status, money_box_period_id '
            'from eats_tips_payments.orders '
            'where payer_id = %s order by created_at',
            (request_body['box_id'],),
        )
        orders = cursor.fetchall()
    for actual, expected in zip(orders, expected_orders):
        assert dict(actual) == expected
