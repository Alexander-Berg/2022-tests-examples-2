import datetime

from tests_grocery_dispatch_tracking import constants as const

INSERT_ORDER = """
INSERT INTO dispatch_tracking.orders_statistics
(depot_id, order_id, performer_id, delivery_type, picked_up)
VALUES (%s, %s, %s, %s, %s);
"""


class PrepareOrder:
    def __init__(self):
        self.depot_id = '398791'
        self.order_id = const.ORDER_ID
        self.performer_id = const.PERFORMER_ID
        self.delivered_ts_str = const.NOW
        self.delivered_ts = datetime.datetime.strptime(
            self.delivered_ts_str, const.DATETIME_FORMAT,
        )
        self.picked_up_ts = self.delivered_ts - datetime.timedelta(minutes=15)
        self.picked_up_ts_str = self.picked_up_ts.strftime(
            const.DATETIME_FORMAT,
        )

    def setup_grocery_orders(self, mockserver):
        @mockserver.json_handler('/grocery-orders/internal/v1/get-info-bulk')
        def _get_info_bulk(_request):
            return [
                {
                    'order_id': '6e32572a76624cec812c733b1fcb3cff-grocery',
                    'status': 'delivering',
                    'created': self.picked_up_ts_str,
                    'cart_id': '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9',
                    'location': {'lat': 0.0, 'lon': 12.0},
                },
            ]

    def setup_grocery_depots(self, mockserver, load_json):
        @mockserver.json_handler(
            '/grocery-depots/internal/v1/depots/v1/depots',
        )
        def _handle_depots(_request):
            return load_json('gdepots-depots-paris.json')

    def setup_grocery_routing(self, mockserver):
        @mockserver.json_handler(
            '/grocery-routing/internal/grocery-routing/v1/route',
        )
        def _mock_route(request):
            assert request.json['transport_type'] == 'pedestrian'
            assert request.json['source'] == {
                'lat': 48.870283,
                'lon': 2.369513,
            }
            assert request.json['destination'] == {'lat': 0.0, 'lon': 12.0}
            return {'distance': 15, 'eta': 0}

    def setup_db(self, pgsql):
        db = pgsql['grocery_dispatch_tracking']
        db.cursor().execute(
            INSERT_ORDER,
            (
                self.depot_id,
                self.order_id,
                self.performer_id,
                'courier',
                self.picked_up_ts_str,
            ),
        )

    async def run_stq(self, stq_runner):
        await stq_runner.grocery_order_statistics_postprocessing.call(
            task_id='task_id',
            kwargs={
                'order_id': self.order_id,
                'depot_id': self.depot_id,
                'performer_id': self.performer_id,
                'timestamp': self.delivered_ts_str,
            },
        )


async def test_stq_order_speed_statistics_base(
        stq_runner, pgsql, load_json, mockserver,
):
    assist = PrepareOrder()
    assist.setup_grocery_orders(mockserver)
    assist.setup_grocery_depots(mockserver, load_json)
    assist.setup_grocery_routing(mockserver)
    assist.setup_db(pgsql)
    await assist.run_stq(stq_runner)

    db = pgsql['grocery_dispatch_tracking']
    cursor = db.cursor()
    cursor.execute('select * from dispatch_tracking.orders_statistics')
    res = list(cursor)
    assert len(res) == 1
    [
        (
            actual_depot_id,
            actual_order_id,
            _actual_performer_id,
            actual_delivery_type,
            actual_from,
            actual_to,
            actual_distance,
        ),
    ] = res
    assert actual_depot_id == assist.depot_id
    assert actual_order_id == assist.order_id
    assert actual_delivery_type == 'courier'
    assert actual_from == assist.picked_up_ts
    assert actual_to == assist.delivered_ts
    assert actual_distance == 15


async def test_stq_order_speed_statistics_not_found(
        stq_runner, pgsql, load_json, mockserver,
):
    assist = PrepareOrder()
    assist.setup_grocery_orders(mockserver)
    assist.setup_grocery_depots(mockserver, load_json)
    assist.setup_grocery_routing(mockserver)
    assist.setup_db(pgsql)

    @mockserver.json_handler('/grocery-orders/internal/v1/get-info-bulk')
    def _get_info_bulk(_request):
        return []

    await assist.run_stq(stq_runner)
