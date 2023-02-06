import pytest

from eats_integration_offline_orders.stq import pos_pay_order


@pytest.mark.parametrize(
    'order_uuid,stq_called',
    (
        pytest.param('order_uuid__1', True, id='success'),
        pytest.param('order_uuid__2', False, id='already_closed'),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'orders.sql'],
)
async def test_ei_offline_pos_pay_order(
        stq3_context,
        order_uuid,
        place_id,
        pos_type,
        pos_client_mock,
        stq_called,
):

    await pos_pay_order.task(
        stq3_context,
        order_uuid=order_uuid,
        place_id=place_id,
        pos_client=pos_type,
        result=True,
    )

    assert pos_client_mock.send_payment_result.called == stq_called
    order = await stq3_context.pg.secondary.fetchrow(
        f'SELECT * FROM orders where uuid=$1;', order_uuid,
    )
    assert order['status'] == 'closed'
