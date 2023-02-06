import decimal

import dateutil.parser
import pytest

from tests_fleet_orders_guarantee import db_utils


DEFAULT_DB_ORDER = {
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

EXPECTED_NEW_ORDER = {
    'contractor_id': 'driver2',
    'id': 'order_id1',
    'location_from': [13.388379, 52.519895],
    'locations_to': [[13.396845, 52.502810]],
    'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T23:00:00Z'),
    'park_id': 'park1',
    'cancelled_at': None,
    'processed_at': None,
    'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'source_park_id': 'park1',
    'zone_id': 'moscow',
    'tariff_class': 'business',
    'duration_estimate': None,
    'address_from': 'A',
    'addresses_to': ['B', 'C'],
    'driver_price': decimal.Decimal('100.70'),
    'comment': 'Comment',
    'distance': None,
    'durations': None,
    'event_index': 1,
}


@pytest.mark.now('2021-09-02T17:00:00Z')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, db_state',
    [
        (
            {
                'order_id': 'order_id1',
                'source_park_id': 'park1',
                'contractor_id': 'park1_driver2',
                'created_at': {'$date': '2021-09-02T16:00:00Z'},
                'location_from': [13.388379, 52.519895],
                'address_from': 'A',
                'locations_to': [[13.396845, 52.502810]],
                'addresses_to': ['B', 'C'],
                'client_booked_at': {'$date': '2021-09-02T23:00:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'business',
                'duration': 300,
                'price': 100.70,
                'comment': 'Comment',
                'event_index': 1,
            },
            [EXPECTED_NEW_ORDER],
        ),
    ],
)
async def test_stq_handle(mockserver, stq_runner, pgsql, stq_kwargs, db_state):
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

    assert db_utils.get_orders(cursor) == [DEFAULT_DB_ORDER]

    await stq_runner.fleet_orders_guarantee_editing_handling.call(
        task_id='task_id', kwargs=stq_kwargs,
    )

    assert db_utils.get_orders(cursor) == db_state
