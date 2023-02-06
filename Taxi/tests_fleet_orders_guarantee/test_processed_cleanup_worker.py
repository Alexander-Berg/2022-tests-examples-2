import dateutil.parser
import pytest

from tests_fleet_orders_guarantee import db_utils


ORDERS_BEFORE = [
    {
        'id': 'order_id1',
        'park_id': 'park_id1',
        'contractor_id': 'driver_id1',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'cancelled_at': None,
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
    },
    {
        'id': 'order_id2',
        'park_id': 'park_id2',
        'contractor_id': 'driver_id2',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': None,
        'cancelled_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
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
    },
    {
        'id': 'order_id3',
        'park_id': 'park_id3',
        'contractor_id': 'driver_id3',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-08-02T20:00:00Z'),
        'processed_at': None,
        'cancelled_at': None,
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
    },
    {
        'id': 'order_id4',
        'park_id': 'park_id4',
        'contractor_id': 'driver_id4',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': None,
        'cancelled_at': None,
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
    },
]

ORDERS_AFTER = [
    {
        'id': 'order_id1',
        'park_id': 'park_id1',
        'contractor_id': 'driver_id1',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
        'cancelled_at': None,
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
    },
    {
        'id': 'order_id2',
        'park_id': 'park_id2',
        'contractor_id': 'driver_id2',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': None,
        'cancelled_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
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
    },
    {
        'id': 'order_id4',
        'park_id': 'park_id4',
        'contractor_id': 'driver_id4',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': None,
        'cancelled_at': None,
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
    },
]


@pytest.mark.now('2021-09-02T22:00:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.config(
    FLEET_ORDERS_GUARANTEE_PROCESSED_CLEANUP_SETTINGS={
        'job_period_minutes': 5,
        'booked_at_offset_days': 7,
        'chunk_size': 100,
    },
)
async def test_worker(testpoint, pgsql, taxi_fleet_orders_guarantee):
    @testpoint('processed-cleanup-worker-finished')
    def handle_finished(arg):
        pass

    cursor = pgsql['fleet_orders_guarantee'].cursor()

    assert db_utils.get_orders(cursor) == ORDERS_BEFORE

    await taxi_fleet_orders_guarantee.run_distlock_task(
        'processed-cleanup-task',
    )

    result = handle_finished.next_call()
    assert result == {'arg': 1}

    assert db_utils.get_orders(cursor) == ORDERS_AFTER
