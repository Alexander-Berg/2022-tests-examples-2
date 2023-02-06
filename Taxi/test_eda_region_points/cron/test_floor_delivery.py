import pytest

from eda_region_points.floor_delivery import orders
from eda_region_points.generated.cron import run_cron

FLOOR_DELIVERY_ORDERS = [
    orders.FloorOrder.to_floor_order(
        {
            'order_type': 'floor_delivery',
            'order_nr': '1',
            'items_cost': 4345,
            'subtotal': 2345,
            'place_name': 'place_name1',
            'place_address': 'place_address1',
            'items_name': ['item_name1'],
            'items_quantity': ['item_quantity1'],
            'is_asap': 'ASAP',
            'planned_time': None,
        },
    ),
    orders.FloorOrder.to_floor_order(
        {
            'order_type': 'floor_delivery',
            'order_nr': '2',
            'items_cost': 4345,
            'subtotal': 3345,
            'place_name': 'place_name2',
            'place_address': 'place_address2',
            'items_name': ['item_name2'],
            'items_quantity': ['item_quantity2'],
            'is_asap': 'ASAP',
            'planned_time': None,
        },
    ),
    orders.FloorOrder.to_floor_order(
        {
            'order_type': 'floor_delivery',
            'order_nr': '5',
            'items_cost': 4345,
            'subtotal': 4345,
            'place_name': 'place_name3',
            'place_address': 'place_address3',
            'items_name': ['item_name3'],
            'items_quantity': ['item_quantity3'],
            'is_asap': 'ASAP',
            'planned_time': None,
        },
    ),
]
EATS_FLOOR_DELIVERY_NOTIFICATION_TELEGRAM = {
    'is_active': True,
    'chat_id': '000',
    'separator_message': 'separator',
    'template_message': 'message',
}


def get_floor_delivery_order_in_db(pgsql):
    cursor = pgsql['eats_misc'].cursor()
    cursor.execute(
        """
        SELECT order_nr
        FROM eats_misc.notified_orders
        WHERE notify_type = 'floor_delivery'
        """,
    )
    return set(row[0] for row in cursor)


@pytest.fixture(name='floor_delivery')
def _floor_delivery(patch):
    class Context:
        patch_floor_delivery_orders = None
        patch_sql_connect = None
        patch_send_notfication_telegram = None
        floor_delivery_orders = []
        sent_messages = []

        def make_context(self, floor_delivery_orders=None):
            if floor_delivery_orders:
                self.floor_delivery_orders = floor_delivery_orders

    cntx = Context()

    @patch(
        'eda_region_points.floor_delivery.notifications.'
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

    @patch('eda_region_points.floor_delivery.orders.get_orders')
    async def _get_floor_delivery_orders(*args, **kwargs):
        return cntx.floor_delivery_orders

    cntx.patch_floor_delivery_orders = _get_floor_delivery_orders
    cntx.patch_sql_connect = _sql_connect
    cntx.patch_send_notfication_telegram = _send_notify_telegram

    return cntx


@pytest.mark.config(
    EATS_FLOOR_DELIVERY_SAVE_NOTIFIED_ORDERS_INTERVAL_SEC=259200,
)
@pytest.mark.now('2020-02-03T08:00:00.000000')
@pytest.mark.parametrize('floor_delivery_orders', [[], FLOOR_DELIVERY_ORDERS])
@pytest.mark.config(
    EATS_FLOOR_DELIVERY_NOTIFICATION_TELEGRAM=EATS_FLOOR_DELIVERY_NOTIFICATION_TELEGRAM,  # noqa: E501 pylint: disable=line-too-long
)
async def test_floor_delivery(floor_delivery_orders, pgsql, floor_delivery):
    floor_delivery.make_context(floor_delivery_orders=floor_delivery_orders)

    assert get_floor_delivery_order_in_db(pgsql) == {'111-111', '222-222'}

    await run_cron.main(
        [f'eda_region_points.crontasks.floor_delivery', '-t', '0'],
    )

    # should be ids of all new orders and previous order '111-111'
    # in db after execution cron-task
    # order '222-222' is too old, that's why it shouldn't be in db
    orders_id = set(order.order_nr for order in floor_delivery_orders)
    orders_id.add('111-111')
    assert get_floor_delivery_order_in_db(pgsql) == orders_id

    assert floor_delivery.sent_messages == [
        order for order in floor_delivery_orders
    ]

    expected_messages = len(floor_delivery_orders)
    assert len(floor_delivery.patch_send_notfication_telegram.calls) == (
        expected_messages + 1 if expected_messages else 0
    )
    assert len(floor_delivery.patch_floor_delivery_orders.calls) == 1
    assert len(floor_delivery.patch_sql_connect.calls) == 1
