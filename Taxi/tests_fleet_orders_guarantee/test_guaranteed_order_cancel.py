import dateutil.parser
import pytest

from tests_fleet_orders_guarantee import db_utils


DEFAULT_DB_ORDER_NOT_PROCESSED = {
    'contractor_id': 'driver_id1',
    'id': 'order_id1',
    'location_from': [13.388378, 52.519894],
    'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
    'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
    'park_id': 'park_id1',
    'cancelled_at': None,
    'processed_at': None,
    'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'source_park_id': None,
    'zone_id': None,
    'tariff_class': None,
    'duration_estimate': None,
    'address_from': None,
    'addresses_to': None,
    'driver_price': None,
    'comment': None,
    'distance': None,
    'durations': None,
    'event_index': 0,
}

DEFAULT_DB_ORDER_PROCESSED = {
    'contractor_id': None,
    'id': 'order_id2',
    'location_from': [13.2984, 52.5103],
    'locations_to': [[13.2536, 52.4778], [13.2736, 52.4602]],
    'created_at': dateutil.parser.parse('2021-09-02T11:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T13:00:00Z'),
    'park_id': None,
    'cancelled_at': None,
    'processed_at': dateutil.parser.parse('2021-09-02T12:23:00Z'),
    'record_created_at': dateutil.parser.parse('2021-09-02T11:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T12:23:00Z'),
    'source_park_id': None,
    'zone_id': None,
    'tariff_class': None,
    'duration_estimate': None,
    'address_from': None,
    'addresses_to': None,
    'driver_price': None,
    'comment': None,
    'distance': None,
    'durations': None,
    'event_index': 0,
}


DEFAULT_DB_ORDER_NOT_PROCESSED_AFTER = {
    'contractor_id': 'driver_id1',
    'id': 'order_id1',
    'location_from': [13.388378, 52.519894],
    'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
    'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
    'park_id': 'park_id1',
    'cancelled_at': dateutil.parser.parse('2021-09-02T16:59:00Z'),
    'processed_at': None,
    'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'source_park_id': None,
    'zone_id': None,
    'tariff_class': None,
    'duration_estimate': None,
    'address_from': None,
    'addresses_to': None,
    'driver_price': None,
    'comment': None,
    'distance': None,
    'durations': None,
    'event_index': 0,
}


@pytest.mark.now('2021-09-02T17:00:00+00:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, db_state, park_id',
    [
        (
            # non-processed order
            {
                'order_id': 'order_id1',
                'cancelled_at': {'$date': '2021-09-02T16:59:00Z'},
            },
            [DEFAULT_DB_ORDER_NOT_PROCESSED_AFTER, DEFAULT_DB_ORDER_PROCESSED],
            'park_id1',
        ),
        (
            # cancelled order
            {
                'order_id': 'order_id2',
                'cancelled_at': {'$date': '2021-09-02T22:00:00Z'},
            },
            [DEFAULT_DB_ORDER_NOT_PROCESSED, DEFAULT_DB_ORDER_PROCESSED],
            None,
        ),
    ],
)
async def test_stq_handle(
        mockserver, stq_runner, pgsql, stq_kwargs, db_state, park_id,
):
    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_v2_push(request):
        return {'notification_id': '024a3c5cd41e4a8ca5993bafb20e346b'}

    @mockserver.json_handler('/fleet-parks/v1/parks')
    async def _mock_parks(request):
        return {
            'id': 'park_id1',
            'login': 'login',
            'is_active': True,
            'city_id': 'city',
            'locale': 'en',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'demo_mode': False,
            'country_id': 'country_id',
            'name': 'some park name',
            'tz_offset': 4,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        }

    cursor = pgsql['fleet_orders_guarantee'].cursor()

    assert db_utils.get_orders(cursor) == [
        DEFAULT_DB_ORDER_NOT_PROCESSED,
        DEFAULT_DB_ORDER_PROCESSED,
    ]

    await stq_runner.fleet_orders_guarantee_cancel_handling.call(
        task_id='task_id', kwargs=stq_kwargs,
    )

    if park_id == 'park_id1':
        assert _mock_v2_push.times_called == 1
    else:
        assert _mock_v2_push.times_called == 0

    assert db_utils.get_orders(cursor) == db_state
