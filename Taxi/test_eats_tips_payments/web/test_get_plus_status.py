import pytest

from test_eats_tips_payments import conftest


@pytest.mark.parametrize(
    ('invoice_id', 'expected_status', 'expected_response'),
    (
        (42, 200, {'amount': 11, 'status': 'in-progress'}),
        (43, 200, {'amount': 10, 'status': 'in-progress'}),
        (44, 200, {'amount': 12, 'status': 'success'}),
        (45, 200, {'amount': 13, 'status': 'failed'}),
    ),
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_get_plus_status(
        taxi_eats_tips_payments_web,
        invoice_id,
        expected_status,
        expected_response,
):
    headers = {'X-Yandex-UID': '42', 'X-Ya-User-Ticket': ''}
    response = await taxi_eats_tips_payments_web.get(
        '/v1/payments/plus/status',
        params={'order_id': invoice_id},
        headers=headers,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_response


@pytest.mark.config(
    TVM_USER_TICKETS_ENABLED=True, TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.parametrize(
    ('headers', 'expected_response'),
    conftest.get_tvm_user_ticket_cases(ticket_required=True),
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_get_plus_status_tvm(
        taxi_eats_tips_payments_web, mocked_tvm, headers, expected_response,
):
    response = await taxi_eats_tips_payments_web.get(
        '/v1/payments/plus/status', headers=headers, params={'order_id': 42},
    )
    assert response.status == expected_response
