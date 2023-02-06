import pytest


from eats_tips_payments.common import payments
from test_eats_tips_payments import conftest


@pytest.mark.parametrize(
    ('min_id', 'max_id', 'expected_affected_orders'),
    ((43, 43, [43]), (42, 45, [43, 45]), (1, 200, [43, 45]), (44, 44, [])),
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_manual_retry_charge_plus(
        web_context, stq, min_id, max_id, expected_affected_orders,
):
    affected_orders = await payments.manual_retry_charge_plus(
        context=web_context, min_order_id=min_id, max_order_id=max_id,
    )
    assert stq.eats_tips_payments_charge_plus.times_called == len(
        expected_affected_orders,
    )
    for expected_order_id in expected_affected_orders:
        conftest.check_task_queued(
            stq,
            stq.eats_tips_payments_charge_plus,
            {'order_id': expected_order_id},
            ['operation'],
        )
    assert affected_orders == expected_affected_orders


@pytest.mark.parametrize(
    ('min_id', 'max_id', 'expected_affected_orders'),
    ((42, 45, [42]), (1, 200, [42]), (44, 44, []), (42, 42, [42])),
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_manual_retry_poll_plus(
        web_context, stq, min_id, max_id, expected_affected_orders,
):
    affected_orders = await payments.manual_retry_poll_plus(
        context=web_context, min_order_id=min_id, max_order_id=max_id,
    )
    assert stq.eats_tips_payments_poll_plus_status.times_called == len(
        expected_affected_orders,
    )
    for expected_order_id in expected_affected_orders:
        conftest.check_task_queued(
            stq,
            stq.eats_tips_payments_poll_plus_status,
            {'order_id': expected_order_id},
            drop={'order_id_str'},
        )
    assert affected_orders == expected_affected_orders
