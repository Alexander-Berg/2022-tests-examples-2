# pylint: disable=import-error

import datetime

import bson
from dap_tools.dap import dap_fixture  # noqa: F401 C5521
import dateutil.parser
import pytest

from tests_fleet_orders_guarantee import db_utils


ENDPOINT = '/driver/v1/fleet-orders-guarantee/v1/preorder/reject'


DEFAUL_ORDERS_AFTER = [
    {
        'address_from': 'ул. Ленина',
        'addresses_to': ['ул. Маркса', 'ул. Энгельса'],
        'cancelled_at': None,
        'client_booked_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
        'comment': 'Call the apartment and I will come down',
        'contractor_id': None,
        'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'distance': 5491,
        'driver_price': None,
        'duration_estimate': datetime.timedelta(seconds=420),
        'durations': None,
        'event_index': 0,
        'id': 'order_id1',
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'park_id': None,
        'processed_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-01T17:30:00Z'),
        'source_park_id': None,
        'tariff_class': None,
        'zone_id': None,
    },
    {
        'address_from': None,
        'addresses_to': None,
        'cancelled_at': None,
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:20:00Z'),
        'comment': None,
        'contractor_id': 'driver_id2',
        'created_at': dateutil.parser.parse('2021-09-02T16:11:00Z'),
        'distance': None,
        'driver_price': None,
        'duration_estimate': None,
        'durations': None,
        'event_index': 0,
        'id': 'order_id2',
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'park_id': 'park_id1',
        'processed_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T16:12:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T16:12:00Z'),
        'source_park_id': None,
        'tariff_class': None,
        'zone_id': None,
    },
    {
        'address_from': 'ул. Ленина',
        'addresses_to': ['ул. Маркса', 'ул. Энгельса'],
        'cancelled_at': None,
        'client_booked_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
        'comment': 'Call the apartment and I will come down',
        'contractor_id': None,
        'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'distance': 5491,
        'driver_price': None,
        'duration_estimate': datetime.timedelta(seconds=420),
        'durations': None,
        'event_index': 0,
        'id': 'order_id4',
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'park_id': None,
        'processed_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-01T17:30:00Z'),
        'source_park_id': None,
        'tariff_class': None,
        'zone_id': None,
    },
    {
        'address_from': 'ул. Ленина',
        'addresses_to': ['ул. Маркса', 'ул. Энгельса'],
        'cancelled_at': dateutil.parser.parse('2021-09-02T16:42:00Z'),
        'client_booked_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
        'comment': 'Call the apartment and I will come down',
        'contractor_id': None,
        'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'distance': 5491,
        'driver_price': None,
        'duration_estimate': datetime.timedelta(seconds=420),
        'durations': None,
        'event_index': 0,
        'id': 'order_id5',
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'park_id': None,
        'processed_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'source_park_id': None,
        'tariff_class': None,
        'zone_id': None,
    },
    {
        'address_from': 'ул. Ленина',
        'addresses_to': ['ул. Маркса', 'ул. Энгельса'],
        'cancelled_at': None,
        'client_booked_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
        'comment': 'Call the apartment and I will come down',
        'contractor_id': None,
        'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'distance': 5491,
        'driver_price': None,
        'duration_estimate': datetime.timedelta(seconds=420),
        'durations': None,
        'event_index': 0,
        'id': 'order_id6',
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'park_id': None,
        'processed_at': dateutil.parser.parse('2021-09-02T16:42:00Z'),
        'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'source_park_id': None,
        'tariff_class': None,
        'zone_id': None,
    },
    {
        'address_from': 'ул. Ленина',
        'addresses_to': ['ул. Маркса', 'ул. Энгельса'],
        'cancelled_at': None,
        'client_booked_at': dateutil.parser.parse('2021-08-02T18:00:00Z'),
        'comment': 'Call the apartment and I will come down',
        'contractor_id': None,
        'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'distance': 5491,
        'driver_price': None,
        'duration_estimate': datetime.timedelta(seconds=420),
        'durations': None,
        'event_index': 0,
        'id': 'order_id7',
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'park_id': None,
        'processed_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'source_park_id': None,
        'tariff_class': None,
        'zone_id': None,
    },
    {
        'address_from': 'ул. Ленина',
        'addresses_to': ['ул. Маркса', 'ул. Энгельса'],
        'cancelled_at': None,
        'client_booked_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
        'comment': 'Call the apartment and I will come down',
        'contractor_id': 'driver_id1',
        'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'distance': 5491,
        'driver_price': None,
        'duration_estimate': datetime.timedelta(seconds=420),
        'durations': None,
        'event_index': 0,
        'id': 'order_id8',
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'park_id': 'park_id1',
        'processed_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'source_park_id': None,
        'tariff_class': None,
        'zone_id': None,
    },
]

DEFAUL_REJECT_HISTORY_AFTER = [
    {
        'contractor_id': 'driver_id1',
        'order_id': 'order_id1',
        'park_id': 'park_id1',
        'reject_ts': dateutil.parser.parse('2021-09-01T17:30:00Z'),
    },
    {
        'contractor_id': 'driver_id1',
        'order_id': 'order_id4',
        'park_id': 'park_id1',
        'reject_ts': dateutil.parser.parse('2021-09-01T17:30:00Z'),
    },
]


@pytest.mark.parametrize(
    [
        'park_id',
        'driver_id',
        'order_ids',
        'orders_to_reject',
        'accept_language',
        'response_code',
        'response_json',
        'orders_after',
        'reject_history_after',
        'orders_to_fail',
    ],
    [
        pytest.param(
            'park_id1',
            'driver_id1',
            [
                'order_id1',
                'order_id2',
                'order_id3',
                'order_id4',
                'order_id5',
                'order_id6',
                'order_id7',
                'order_id8',
            ],
            ['order_id1', 'order_id4', 'order_id8'],
            'ru',
            200,
            {
                'rejected_ids': ['order_id1', 'order_id4'],
                'not_rejected_ids': [
                    {
                        'order_id': 'order_id2',
                        'reason': 'accepted_by_other_driver',
                    },
                    {'order_id': 'order_id3', 'reason': 'not_found'},
                    {'order_id': 'order_id5', 'reason': 'canceled'},
                    {'order_id': 'order_id6', 'reason': 'processed'},
                    {'order_id': 'order_id7', 'reason': 'outdated'},
                    {'order_id': 'order_id8', 'reason': 'update_failed'},
                ],
            },
            DEFAUL_ORDERS_AFTER,
            DEFAUL_REJECT_HISTORY_AFTER,
            ['order_id8'],
        ),
    ],
)
@pytest.mark.now('2021-09-01T20:30:00+03:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
async def test_driver_v1_preorder_reject(
        taxi_fleet_orders_guarantee,
        pgsql,
        mockserver,
        dap,
        park_id,
        driver_id,
        order_ids,
        orders_to_reject,
        accept_language,
        response_code,
        response_json,
        orders_after,
        reject_history_after,
        orders_to_fail,
):
    processed_orders = []

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        order_id = request.args['order_id']
        assert order_id in orders_to_reject

        return mockserver.make_response(
            bson.BSON.encode(
                {
                    'document': {'_id': order_id},
                    'revision': {
                        'processing.version': 42,
                        'order.version': 42,
                    },
                },
            ),
            200,
            content_type='application/bson',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        order_id = request.args['order_id']
        assert order_id in orders_to_reject
        processed_orders.append(order_id)

        if order_id in orders_to_fail:
            return mockserver.make_response(
                bson.BSON.encode({}), 500, content_type='application/bson',
            )

        assert bson.BSON.decode(request.get_data()) == {
            'update': {
                '$unset': {
                    'order.request.dispatch_type': True,
                    'order.request.lookup_extra.performer_id': True,
                },
            },
            'revision': {'order.version': 42, 'processing.version': 42},
        }
        return mockserver.make_response(
            bson.BSON.encode({}), 200, content_type='application/bson',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/handle_editing',
    )
    def _mock_handle_editing(request):
        assert request.args['order_id'] in orders_to_reject
        body = bson.BSON.decode(request.get_data())
        assert body == {}
        return {}

    taxi_fleet_orders_guarantee = dap.create_driver_wrapper(
        taxi_fleet_orders_guarantee,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent='Taximeter 9.1 (1234)',
    )

    query = {'order_ids': order_ids}

    cursor = pgsql['fleet_orders_guarantee'].cursor()

    response = await taxi_fleet_orders_guarantee.post(
        ENDPOINT, json=query, headers={'Accept-Language': accept_language},
    )

    assert response.status_code == response_code
    assert response.json() == response_json

    assert processed_orders == orders_to_reject

    assert db_utils.get_orders(cursor) == orders_after
    assert db_utils.get_reject_history(cursor) == reject_history_after
