import jinja2
import pytest

from eats_integration_offline_orders.stq import notify_order_paid

TABLE_ID = 'table_id__1'
GROUP_CHAT_ID = 1000000
AMOUNT = 100.5


def telegram_render(context, template_name: str, **kwargs) -> str:
    templates = (
        context.config.EATS_INTEGRATION_OFFLINE_ORDERS_TELEGRAM_TEMPLATES
    )
    template = templates[template_name]
    environment = jinja2.Environment()
    return environment.from_string(template).render(**kwargs)


@pytest.mark.parametrize(
    ('task_kwargs',),
    (
        pytest.param(
            {
                'table': TABLE_ID,
                'amount': AMOUNT,
                'full_amount': AMOUNT,
                'is_fully_paid': True,
            },
            id='full',
        ),
        pytest.param(
            {
                'table': TABLE_ID,
                'amount': AMOUNT / 2,
                'full_amount': AMOUNT,
                'is_fully_paid': False,
                'not_paid_amount': AMOUNT / 4,
            },
            id='partial',
        ),
    ),
)
@pytest.mark.pgsql('eats_integration_offline_orders', files=['db.sql'])
async def test_ei_offline_orders_notify_order_paid(
        web_context, stq3_context, patch, place_id, task_kwargs,
):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, telegram_text, **kwargs):
        assert chat_id == GROUP_CHAT_ID
        text = telegram_render(web_context, 'check_paid', **task_kwargs)
        assert telegram_text == text

    await notify_order_paid.task(
        stq3_context, place_id=place_id, table_nr=TABLE_ID, **task_kwargs,
    )


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['db.sql', 'db_iiko_waiter.sql'],
)
@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_IIKO_WAITER={'host': '$mockserver'},
)
async def test_notify_order_paid_to_iiko(stq3_context, mockserver, patch):
    place_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    waiter_id = '1965cdbe-cac1-44ba-9355-d5da6fd87009'
    order_uuid = 'a6e96373-d50e-4217-a091-c969ee997411'
    inner_order_id = '0'

    @mockserver.handler('/api/v1/notifications/mobile/order-paid')
    def _get_test_call_waiter(request):
        assert request.json['userId'] == waiter_id
        assert request.json['orderId'] == order_uuid
        assert request.json['orderNumber'] == int(inner_order_id)
        return mockserver.make_response('', status=200)

    await notify_order_paid.task(
        stq3_context,
        place_id=place_id,
        table_nr='0',
        amount=0,
        waiter_id=waiter_id,
        order_uuid=order_uuid,
        inner_order_id=inner_order_id,
    )
