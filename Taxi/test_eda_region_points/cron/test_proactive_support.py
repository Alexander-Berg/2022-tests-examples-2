import pytest

from eda_region_points.common import orders as utils
from eda_region_points.generated.cron import run_cron
from eda_region_points.proactive_support import orders

VIP_ORDERS = [
    utils.Order.from_dict(
        {'order_type': 'vip_order', 'order_nr': '1', 'subtotal': 2345},
    ),
    utils.Order.from_dict(
        {'order_type': 'vip_order', 'order_nr': '2', 'subtotal': 3345},
    ),
    utils.Order.from_dict(
        {'order_type': 'vip_order', 'order_nr': '5', 'subtotal': 4345},
    ),
]
BIG_ORDERS = [
    utils.Order.from_dict(
        {'order_type': 'big_order', 'order_nr': None, 'subtotal': 15345},
    ),
    utils.Order.from_dict(
        {'order_type': 'big_order', 'order_nr': '3', 'subtotal': 12345},
    ),
    utils.Order.from_dict(
        {'order_type': 'big_order', 'order_nr': '4', 'subtotal': 22345},
    ),
]
ROVER_ORDERS = [
    utils.Order.from_dict(
        {'order_type': 'rover_order', 'order_nr': '6', 'subtotal': 715},
    ),
    utils.Order.from_dict(
        {'order_type': 'rover_order', 'order_nr': '7', 'subtotal': 975},
    ),
]
MARKET_ORDERS = [
    utils.Order.from_dict(
        {'order_type': 'market_order', 'order_nr': '8', 'subtotal': 7159},
    ),
    utils.Order.from_dict(
        {'order_type': 'market_order', 'order_nr': '9', 'subtotal': 9758},
    ),
]
PLACES_ORDERS = [
    utils.Order.from_dict(
        {'order_type': 'places_order', 'order_nr': '10', 'subtotal': 7151},
    ),
    utils.Order.from_dict(
        {'order_type': 'places_order', 'order_nr': '11', 'subtotal': 9752},
    ),
]
CORP_ORDERS = [
    utils.Order.from_dict(
        {'order_type': 'corp_order', 'order_nr': '220', 'subtotal': 7154},
    ),
    utils.Order.from_dict(
        {'order_type': 'corp_order', 'order_nr': '221', 'subtotal': 9758},
    ),
]
PLACE_UNCONFIRMED_ORDER = [
    utils.Order.from_dict(
        {'order_type': 'big_order', 'order_nr': '444-444', 'subtotal': 12000},
    ),
]
NOT_ADOPTED_BY_COURIER = [
    utils.Order.from_dict(
        {'order_type': 'vip_order', 'order_nr': '111-111', 'subtotal': 1000},
    ),
    utils.Order.from_dict(
        {'order_type': 'big_order', 'order_nr': '333-333', 'subtotal': 12000},
    ),
]
ORDERS_BY_ADDRESSES = [
    utils.Order.from_dict(
        {
            'order_type': 'stadium_order',
            'order_nr': '080-799',
            'subtotal': 666,
        },
    ),
]
EATS_PROACTIVE_SUPPORT_NOTIFICATION_TELEGRAM = {
    'is_active': True,
    'chat_id': '000',
    'separator_message': 'separator',
    'template_message': 'message',
}
EATS_PROACTIVE_SUPPORT_NOTIFICATION_TRACKER = {
    'is_active': True,
    'queue': 'test',
    'template_summary': 'summary',
    'template_description': 'description',
    'template_comment': 'comment',
}


def get_order_in_process_in_db(pgsql):
    cursor = pgsql['eats_misc'].cursor()
    cursor.execute(
        """
        SELECT order_nr
        FROM eats_misc.notified_orders
        WHERE notify_type = 'in_process'
        """,
    )
    return set(row[0] for row in cursor)


@pytest.fixture(name='proactive_support')
def _proactive_support(patch):
    class Context:
        patch_find_problems = None
        patch_vip_phones = None
        patch_vip_orders = None
        patch_expensive_orders = None
        patch_rover_orders = None
        patch_market_orders = None
        patch_orders_by_places = None
        patch_sql_connect = None
        patch_send_notfication_telegram = None
        patch_send_notfication_tracker = None
        patch_corp_orders = None
        patch_addresses_orders = None
        vip_phone_ids = []
        vip_orders = []
        expensive_orders = []
        rover_orders = []
        market_orders = []
        places_orders = []
        place_unconfirmed_orders = []
        not_adopted_by_courier = []
        sent_messages = []
        corp_orders = []
        addresses_orders = []

        def make_context(
                self,
                vip_phone_ids=None,
                vip_orders=None,
                expensive_orders=None,
                rover_orders=None,
                market_orders=None,
                places_orders=None,
                place_unconfirmed_orders=None,
                not_adopted_by_courier=None,
                corp_orders=None,
                addresses_orders=None,
        ):
            if vip_phone_ids:
                self.vip_phone_ids = vip_phone_ids
            if vip_orders:
                self.vip_orders = vip_orders
            if expensive_orders:
                self.expensive_orders = expensive_orders
            if rover_orders:
                self.rover_orders = rover_orders
            if market_orders:
                self.market_orders = market_orders
            if places_orders:
                self.places_orders = places_orders
            if place_unconfirmed_orders:
                self.place_unconfirmed_orders = place_unconfirmed_orders
            if not_adopted_by_courier:
                self.not_adopted_by_courier = not_adopted_by_courier
            if corp_orders:
                self.corp_orders = corp_orders
            if addresses_orders:
                self.addresses_orders = addresses_orders

    cntx = Context()

    @patch(
        'eda_region_points.proactive_support.notifications.'
        'TelegramNotificationContext.send_notify',
    )
    async def _send_notify_telegram(order, problem_status):
        cntx.sent_messages.append(
            f'Order {order}, problem_status: {problem_status}',
        )

    @patch(
        'eda_region_points.proactive_support.notifications.'
        'TrackerNotificationContext.send_notify',
    )
    async def _send_notify_tracker(order, problem_status):
        cntx.sent_messages.append(
            f'Order {order}, problem_status: {problem_status}',
        )

    @patch('sqlalchemy.engine.Engine.connect')
    def _sql_connect(*args, **kwargs):
        class ConnectMock:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return ConnectMock()

    @patch(
        'eda_region_points.proactive_support.problem_orders.find_problems',  # noqa  # pylint: disable=line-too-long
    )
    async def _get_problems(*args, **kwargs):
        return {
            orders.PLACE_UNCONFIRMED_ORDER: cntx.place_unconfirmed_orders,
            orders.NOT_ADOPTED_BY_COURIER: cntx.not_adopted_by_courier,
            orders.NO_TAXI_FOR_ORDER: [],
            orders.COURIER_NOT_ARRIVED_TO_PLACE: [],
            orders.ORDER_NOT_TAKEN: [],
            orders.COURIER_NOT_ARRIVED_TO_CUSTOMER: [],
            orders.NOT_FINISHED_ORDER: [],
            orders.NOT_FINISHED_MARKETPLACE_ORDER: [],
        }

    @patch('eda_region_points.proactive_support.users.get_vip_users_phone_ids')
    async def _get_vip_phones(*args, **kwargs):
        return cntx.vip_phone_ids

    @patch(
        'eda_region_points.proactive_support.orders.get_orders_by_phone_ids',
    )
    async def _get_vip_orders(context, conn, phone_ids):
        assert phone_ids == cntx.vip_phone_ids
        return cntx.vip_orders

    @patch('eda_region_points.proactive_support.orders.get_orders_by_cost')
    async def _get_expensive_orders(context, conn, min_cost):
        return cntx.expensive_orders

    @patch('eda_region_points.proactive_support.orders.get_rover_orders')
    async def _get_rover_orders(context, conn):
        return cntx.rover_orders

    @patch('eda_region_points.proactive_support.orders.get_market_orders')
    async def _get_market_orders(context, conn):
        return cntx.market_orders

    @patch('eda_region_points.proactive_support.orders.get_orders_by_places')
    async def _get_orders_by_places(context, conn, places):
        return cntx.places_orders

    @patch('eda_region_points.proactive_support.orders.get_corp_orders')
    async def _get_corp_orders(context, conn, min_items):
        return cntx.corp_orders

    @patch(
        'eda_region_points.proactive_support.orders.get_orders_by_addresses',
    )
    async def _get_orders_by_addresses(context, conn, min_items):
        return cntx.addresses_orders

    cntx.patch_find_problems = _get_problems
    cntx.patch_vip_phones = _get_vip_phones
    cntx.patch_vip_orders = _get_vip_orders
    cntx.patch_expensive_orders = _get_expensive_orders
    cntx.patch_rover_orders = _get_rover_orders
    cntx.patch_market_orders = _get_market_orders
    cntx.patch_orders_by_places = _get_orders_by_places
    cntx.patch_sql_connect = _sql_connect
    cntx.patch_send_notfication_telegram = _send_notify_telegram
    cntx.patch_send_notfication_tracker = _send_notify_tracker
    cntx.patch_corp_orders = _get_corp_orders
    cntx.patch_addresses_orders = _get_orders_by_addresses

    return cntx


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_SAVE_NOTIFIED_ORDERS_INTERVAL_SEC=259200,
)
@pytest.mark.now('2020-02-03T08:00:00.000000')
@pytest.mark.parametrize('vip_phone_ids', [[], ['phone1', 'phone2']])
@pytest.mark.parametrize('vip_orders', [[], VIP_ORDERS])
@pytest.mark.parametrize('expensive_orders', [[], BIG_ORDERS])
@pytest.mark.parametrize('rover_orders', [[], ROVER_ORDERS])
@pytest.mark.parametrize('market_orders', [[], MARKET_ORDERS])
@pytest.mark.parametrize('places_orders', [[], PLACES_ORDERS])
@pytest.mark.parametrize('corp_orders', [[], CORP_ORDERS])
@pytest.mark.parametrize('addresses_orders', [[], ORDERS_BY_ADDRESSES])
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_NOTIFICATION_TELEGRAM=EATS_PROACTIVE_SUPPORT_NOTIFICATION_TELEGRAM,  # noqa: E501 pylint: disable=line-too-long
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_NOTIFICATION_TRACKER=EATS_PROACTIVE_SUPPORT_NOTIFICATION_TRACKER,  # noqa: E501 pylint: disable=line-too-long
)
async def test_proactive_support(
        patch,
        response_mock,
        vip_phone_ids,
        vip_orders,
        expensive_orders,
        rover_orders,
        market_orders,
        places_orders,
        corp_orders,
        addresses_orders,
        pgsql,
        proactive_support,
):
    proactive_support.make_context(
        vip_phone_ids=vip_phone_ids,
        vip_orders=vip_orders,
        expensive_orders=expensive_orders,
        rover_orders=rover_orders,
        market_orders=market_orders,
        places_orders=places_orders,
        corp_orders=corp_orders,
        addresses_orders=addresses_orders,
    )

    assert get_order_in_process_in_db(pgsql) == {'111-111', '222-222'}

    all_orders = expensive_orders.copy()
    all_orders.extend(rover_orders)
    if vip_phone_ids:
        all_orders.extend(vip_orders)
    all_orders.extend(market_orders)
    all_orders.extend(places_orders)
    all_orders.extend(corp_orders)
    all_orders.extend(addresses_orders)
    all_orders = list(
        filter(
            lambda order: order.order_nr != orders.NULL_FIELD_STR, all_orders,
        ),
    )

    await run_cron.main(
        [f'eda_region_points.crontasks.proactive_support', '-t', '0'],
    )

    # should be ids of all new orders and previous order '111-111'
    # in db after execution cron-task
    # order '222-222' is too old, that's why it shouldn't be in db
    orders_id = set(order.order_nr for order in all_orders)
    orders_id.add('111-111')
    assert get_order_in_process_in_db(pgsql) == orders_id

    expected_messages = len(all_orders)

    # TODO: check messages
    assert len(proactive_support.patch_send_notfication_telegram.calls) == (
        expected_messages + 1 if expected_messages else 0
    )
    assert (
        len(proactive_support.patch_send_notfication_tracker.calls)
        == expected_messages
    )
    assert len(proactive_support.patch_find_problems.calls) == 1
    assert len(proactive_support.patch_vip_phones.calls) == 1
    if vip_phone_ids:
        assert len(proactive_support.patch_vip_orders.calls) == 1
    assert len(proactive_support.patch_expensive_orders.calls) == 1
    assert len(proactive_support.patch_rover_orders.calls) == 1
    assert len(proactive_support.patch_market_orders.calls) == 1
    assert len(proactive_support.patch_orders_by_places.calls) == 1
    assert len(proactive_support.patch_sql_connect.calls) == 1
    assert len(proactive_support.patch_addresses_orders.calls) == 1


@pytest.mark.now('2020-02-03T08:00:00.000000')
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_SAVE_NOTIFIED_ORDERS_INTERVAL_SEC=259200,
)
@pytest.mark.pgsql('eats_misc', files=['pg_eats_misc_problem_orders.sql'])
@pytest.mark.parametrize(
    'place_unconfirmed_orders', [[], PLACE_UNCONFIRMED_ORDER],
)
@pytest.mark.parametrize(
    'not_adopted_by_courier', [[], NOT_ADOPTED_BY_COURIER],
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_NOTIFICATION_TELEGRAM=EATS_PROACTIVE_SUPPORT_NOTIFICATION_TELEGRAM,  # noqa: E501 pylint: disable=line-too-long
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_NOTIFICATION_TRACKER=EATS_PROACTIVE_SUPPORT_NOTIFICATION_TRACKER,  # noqa: E501 pylint: disable=line-too-long
)
async def test_sync_problem_orders(
        place_unconfirmed_orders,
        not_adopted_by_courier,
        patch,
        response_mock,
        pgsql,
        proactive_support,
):
    proactive_support.make_context(
        place_unconfirmed_orders=place_unconfirmed_orders,
        not_adopted_by_courier=not_adopted_by_courier,
    )

    orders_in_process = get_order_in_process_in_db(pgsql)

    await run_cron.main(
        [f'eda_region_points.crontasks.proactive_support', '-t', '0'],
    )

    notification_cnt = len(place_unconfirmed_orders) + len(
        not_adopted_by_courier,
    )
    telegram_messages = list(
        proactive_support.patch_send_notfication_telegram.calls,
    )
    tracker_messages = list(
        proactive_support.patch_send_notfication_tracker.calls,
    )
    assert len(telegram_messages) == notification_cnt
    assert len(tracker_messages) == notification_cnt
    assert len(proactive_support.patch_find_problems.calls) == 1
    assert len(proactive_support.patch_vip_phones.calls) == 1
    assert len(proactive_support.patch_expensive_orders.calls) == 1
    assert len(proactive_support.patch_rover_orders.calls) == 1
    assert len(proactive_support.patch_sql_connect.calls) == 1

    # make except result in base
    expected_in_base = set()
    expected_in_base.update(
        set(
            (order.order_nr, 'not_adopted_by_courier')
            for order in not_adopted_by_courier
        ),
    )
    expected_in_base.update(
        set(
            (order.order_nr, 'place_unconfirmed_order')
            for order in place_unconfirmed_orders
        ),
    )
    # '888-888' is old order
    orders_in_process.remove('888-888')
    expected_in_base.update(
        set((order, 'in_process') for order in orders_in_process),
    )

    cursor = pgsql['eats_misc'].cursor()
    cursor.execute(
        """
        SELECT order_nr, notify_type
        FROM eats_misc.notified_orders
        """,
    )
    assert expected_in_base == set((row[0], row[1]) for row in cursor)
