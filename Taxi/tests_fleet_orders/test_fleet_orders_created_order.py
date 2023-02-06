import datetime
import decimal

import dateutil.parser
import pytest

from tests_fleet_orders import utils


class DriverProfilesContext:
    def __init__(self):
        self.profiles = []

    def set_profiles(self, profiles):
        self.profiles = profiles


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):

    context = DriverProfilesContext()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _v1_driver_profiles_retrieve(request):
        return {'profiles': [t for t in context.profiles]}

    return context


@pytest.mark.now('2021-02-09T19:00:00+00:00')
@pytest.mark.parametrize('with_point_to', [True, False])
@pytest.mark.config(FLEET_ORDERS_DEFAULT_ORDER_DURATION_MINUTES=15)
async def test_stq_insert(
        taxi_fleet_orders, stq_runner, pgsql, mock_routes, with_point_to,
):
    mock_routes.set_geopoints([[37.6, 50.6], [37.6, 51.6], [37.6, 52.6]])

    kwargs = {
        'order_id': '0_created_id',
        'source_park_id': 'park_id1',
        'tariff_class': 'econom',
        'address_from': 'address_A',
        'addresses_to': ['address_B1', 'address_B2'],
        'personal_phone_id': 'phone_id1',
        'event_index': 0,
        'created': {'$date': '2021-02-09T18:00:00Z'},
        'due': {'$date': '2021-02-09T19:00:00Z'},
        'geopoint_from': [37.6, 50.6],
        'geopoints_to': [[37.6, 51.6], [37.6, 52.6]] if with_point_to else [],
        'forced_fixprice': 100.70,
    }

    cursor = pgsql['fleet_orders'].cursor()

    cursor.execute(
        f"""
        SELECT id FROM fleet.park_order
        """,
    )

    pg_result = cursor.fetchall()
    assert not pg_result

    cursor.execute(
        'ALTER SEQUENCE fleet.seq_park_order_update_number RESTART 1;',
    )

    await stq_runner.fleet_orders_create_handling.call(
        task_id='order1/0', kwargs=kwargs,
    )

    orders = utils.get_park_order(cursor)
    assert len(orders) == 1

    assert orders[0] == {
        'park_id': 'park_id1',
        'id': '0_created_id',
        'number': 1,
        'source_park_id': 'park_id1',
        'last_order_alias_id': None,
        'status': 'created',
        'tariff_class': 'econom',
        'personal_phone_id': 'phone_id1',
        'address_from': 'address_A',
        'addresses_to': ['address_B1', 'address_B2'],
        'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
        'booked_at': None,
        'ended_at': None,
        'is_creator': True,
        'event_index': 0,
        'last_contractor_id': None,
        'last_contractor_park_id': None,
        'last_contractor_car_id': None,
        'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'client_booked_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'geopoint_from': [37.6, 50.6],
        'geopoints_to': [[37.6, 51.6], [37.6, 52.6]] if with_point_to else [],
        'forced_fixprice': decimal.Decimal('100.70'),
        'preorder_request_id': None,
        'duration_estimate': datetime.timedelta(
            seconds=409 if with_point_to else 900,
        ),
        'driving_at': None,
        'update_seq_no': 1,
    }


@pytest.mark.now('2021-02-09T20:00:00+00:00')
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_stq_retry(stq_runner, pgsql, mock_routes, mock_driver_profiles):
    mock_routes.set_geopoints([[37.6, 50.6], [37.6, 51.6], [37.6, 52.6]])

    driver_profiles = [
        {
            'data': {'car_id': 'car_id1'},
            'park_driver_profile_id': 'park_id1_driver_id1',
        },
    ]
    mock_driver_profiles.set_profiles(driver_profiles)

    kwargs = {
        'order_id': '0_created_id',
        'source_park_id': 'park_id1',
        'tariff_class': 'econom',
        'address_from': 'address_A',
        'addresses_to': ['address_B1', 'address_B2'],
        'personal_phone_id': 'phone_id1',
        'event_index': 1,
        'created': {'$date': '2021-02-09T18:00:00Z'},
        'due': {'$date': '2021-02-09T19:00:00Z'},
        'geopoint_from': [37.6, 50.6],
        'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
        'contractor_id': 'park_id1_performer_id1',
        'forced_fixprice': 100.7,
        'preorder_request_id': 'some_text',
    }
    cursor = pgsql['fleet_orders'].cursor()

    orders = utils.get_park_order(cursor)
    assert len(orders) == 1
    assert orders[0] == {
        'park_id': 'park_id1',
        'id': '0_created_id',
        'number': 1,
        'source_park_id': 'park_id1',
        'last_order_alias_id': None,
        'status': 'created',
        'tariff_class': 'econom',
        'personal_phone_id': 'phone_id1',
        'address_from': 'address_A',
        'addresses_to': ['address_B1', 'address_B2'],
        'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
        'booked_at': None,
        'ended_at': None,
        'is_creator': True,
        'event_index': 0,
        'last_contractor_id': 'performer_id1',
        'last_contractor_park_id': None,
        'last_contractor_car_id': None,
        'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'client_booked_at': dateutil.parser.parse('2021-02-09T20:00:00Z'),
        'geopoint_from': [37.6, 50.6],
        'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
        'forced_fixprice': decimal.Decimal('100.70'),
        'preorder_request_id': None,
        'duration_estimate': None,
        'driving_at': None,
        'update_seq_no': 1,
    }

    utils.reset_update_number_seq(cursor, 2)

    await stq_runner.fleet_orders_create_handling.call(
        task_id='order1/0', kwargs=kwargs,
    )

    orders = utils.get_park_order(cursor)
    assert len(orders) == 1
    assert orders[0] == {
        'park_id': 'park_id1',
        'id': '0_created_id',
        'number': 1,
        'source_park_id': 'park_id1',
        'last_order_alias_id': None,
        'status': 'created',
        'tariff_class': 'econom',
        'personal_phone_id': 'phone_id1',
        'address_from': 'address_A',
        'addresses_to': ['address_B1', 'address_B2'],
        'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
        'booked_at': None,
        'ended_at': None,
        'is_creator': True,
        'event_index': 1,
        'last_contractor_id': 'performer_id1',
        'last_contractor_park_id': 'park_id1',
        'last_contractor_car_id': 'car_id1',
        'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-02-09T20:00:00Z'),
        'client_booked_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'geopoint_from': [37.6, 50.6],
        'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
        'forced_fixprice': decimal.Decimal('100.70'),
        'preorder_request_id': 'some_text',
        'duration_estimate': datetime.timedelta(seconds=409),
        'driving_at': None,
        'update_seq_no': 2,
    }
