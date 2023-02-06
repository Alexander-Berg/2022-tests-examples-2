import pytest

from eda_region_points.common import orders as utils
from eda_region_points.generated.cron import run_cron


NO_COURIER_ALERT_ORDERS = [
    utils.Order.from_dict(
        {'order_type': 'no_courier_alert', 'order_nr': '1', 'subtotal': 2345},
    ),
]
EATS_NO_COURIER_ALERT_NOTIFICATION_TELEGRAM = {
    'is_active': True,
    'chat_id': '000',
    'separator_message': 'separator',
    'template_message': 'message',
}


def get_order_in_db(pgsql):
    cursor = pgsql['eats_misc'].cursor()
    cursor.execute(
        """
        SELECT order_nr
        FROM eats_misc.notified_orders
        WHERE notify_type = 'no_courier_alert'
        """,
    )
    return set(row[0] for row in cursor)


@pytest.fixture(name='no_courier_alert')
def _no_courier_alert(patch):
    class Context:
        patch_no_courier_alert_orders = None
        patch_sql_connect = None
        patch_send_notfication_telegram = None
        no_courier_alert_orders = []
        sent_messages = []

        def make_context(self, no_courier_alert_orders=None):
            if no_courier_alert_orders:
                self.no_courier_alert_orders = no_courier_alert_orders

    cntx = Context()

    @patch(
        'eda_region_points.no_courier_alert.notifications.'
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

    @patch('eda_region_points.no_courier_alert.orders.get_orders')
    async def _get_no_courier_alert_orders(*args, **kwargs):
        return cntx.no_courier_alert_orders

    cntx.patch_no_courier_alert_orders = _get_no_courier_alert_orders
    cntx.patch_sql_connect = _sql_connect
    cntx.patch_send_notfication_telegram = _send_notify_telegram

    return cntx


@pytest.mark.config(
    EATS_NO_COURIER_ALERT_SAVE_NOTIFIED_ORDERS_INTERVAL_SEC=259200,
)
@pytest.mark.now('2020-02-03T08:00:00.000000')
@pytest.mark.parametrize(
    'no_courier_alert_orders', [[], NO_COURIER_ALERT_ORDERS],
)
@pytest.mark.config(
    EATS_NO_COURIER_ALERT_NOTIFICATION_TELEGRAM=EATS_NO_COURIER_ALERT_NOTIFICATION_TELEGRAM,  # noqa: E501 pylint: disable=line-too-long
)
async def test_no_courier_alert(
        no_courier_alert_orders, pgsql, no_courier_alert,
):
    no_courier_alert.make_context(
        no_courier_alert_orders=no_courier_alert_orders,
    )

    await run_cron.main(
        [f'eda_region_points.crontasks.no_courier_alert', '-t', '0'],
    )

    orders_id = set(order.order_nr for order in no_courier_alert_orders)
    assert get_order_in_db(pgsql) == orders_id

    assert no_courier_alert.sent_messages == [
        order for order in no_courier_alert_orders
    ]

    expected_messages = len(no_courier_alert_orders)
    assert len(no_courier_alert.patch_send_notfication_telegram.calls) == (
        expected_messages + 1 if expected_messages else 0
    )
    assert len(no_courier_alert.patch_no_courier_alert_orders.calls) == 1
    assert len(no_courier_alert.patch_sql_connect.calls) == 1
