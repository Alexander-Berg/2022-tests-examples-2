import pytest

from eda_region_points.common import orders as utils
from eda_region_points.generated.cron import run_cron

SPECIAL_ORDERS_SUPPORT_ORDERS = [
    utils.Order.from_dict(
        {
            'order_type': 'special_orders_support',
            'order_nr': '1',
            'subtotal': 2345,
        },
    ),
    utils.Order.from_dict(
        {
            'order_type': 'special_orders_support',
            'order_nr': '2',
            'subtotal': 3345,
        },
    ),
    utils.Order.from_dict(
        {
            'order_type': 'special_orders_support',
            'order_nr': '5',
            'subtotal': 4345,
        },
    ),
]
EATS_SPECIAL_ORDERS_SUPPORT_NOTIFICATION_TELEGRAM = {
    'is_active': True,
    'chat_id': '000',
    'separator_message': 'separator',
    'template_message': 'message',
}


def get_special_orders_in_db(pgsql):
    cursor = pgsql['eats_misc'].cursor()
    cursor.execute(
        """
        SELECT order_nr
        FROM eats_misc.notified_orders
        WHERE notify_type = 'special_orders_support'
        """,
    )
    return set(row[0] for row in cursor)


@pytest.fixture(name='special_orders_support')
def _special_orders_support(patch):
    class Context:
        patch_special_orders_support = None
        patch_sql_connect = None
        patch_send_notfication_telegram = None
        special_orders_support_orders = []
        sent_messages = []

        def make_context(self, special_orders_support_orders=None):
            if special_orders_support_orders:
                self.special_orders_support_orders = (
                    special_orders_support_orders
                )

    cntx = Context()

    @patch(
        'eda_region_points.special_orders_support.notifications.'
        'TelegramNotificationContext.notify',
    )
    async def _send_notify_telegram(order):
        if order:
            cntx.sent_messages.append(order)

    @patch('sqlalchemy.engine.Engine.connect')
    def _sql_connect(*args, **kwargs):
        class ConnectMock:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return ConnectMock()

    @patch('eda_region_points.special_orders_support.orders.get_orders')
    async def _get_special_orders_support_orders(*args, **kwargs):
        return cntx.special_orders_support_orders

    cntx.patch_special_orders_support = _get_special_orders_support_orders
    cntx.patch_sql_connect = _sql_connect
    cntx.patch_send_notfication_telegram = _send_notify_telegram

    return cntx


@pytest.mark.config(
    EATS_SPECIAL_ORDERS_SUPPORT_SAVE_NOTIFIED_ORDERS_INTERVAL_SEC=259200,
)
@pytest.mark.now('2020-02-03T08:00:00.000000')
@pytest.mark.parametrize(
    'special_orders_support_orders', [[], SPECIAL_ORDERS_SUPPORT_ORDERS],
)
@pytest.mark.config(
    EATS_SPECIAL_ORDERS_SUPPORT_NOTIFICATION_TELEGRAM=EATS_SPECIAL_ORDERS_SUPPORT_NOTIFICATION_TELEGRAM,  # noqa: E501 pylint: disable=line-too-long
)
async def test_special_orders_support(
        special_orders_support_orders, pgsql, special_orders_support,
):
    special_orders_support.make_context(
        special_orders_support_orders=special_orders_support_orders,
    )

    assert get_special_orders_in_db(pgsql) == {'111-111', '222-222'}

    await run_cron.main(
        [f'eda_region_points.crontasks.special_orders_support', '-t', '0'],
    )

    # should be ids of all new orders and previous order '111-111'
    # in db after execution cron-task
    # order '222-222' is too old, that's why it shouldn't be in db
    orders_id = set(order.order_nr for order in special_orders_support_orders)
    orders_id.add('111-111')
    assert get_special_orders_in_db(pgsql) == orders_id

    assert special_orders_support.sent_messages == [
        order for order in special_orders_support_orders
    ]

    expected_messages = len(special_orders_support_orders)
    assert len(
        special_orders_support.patch_send_notfication_telegram.calls,
    ) == (expected_messages + 1 if expected_messages else 0)
    assert len(special_orders_support.patch_special_orders_support.calls) == 1
    assert len(special_orders_support.patch_sql_connect.calls) == 1
