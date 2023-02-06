import datetime

import dateutil.parser
import pytest

from tests_fleet_orders import utils


INITIAL_PARK_ORDER_1_1 = {
    'park_id': 'park_id1',
    'id': 'order1_1',
    'last_order_alias_id': 'order_alias_id1',
    'status': 'transporting',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
    'ended_at': None,
    'is_creator': True,
    'event_index': 2,
    'last_contractor_id': 'contractor_id1',
    'last_contractor_park_id': 'park_id1',
    'last_contractor_car_id': None,
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'number': 1,
    'booked_at': None,
    'client_booked_at': None,
    'driving_at': None,
    'duration_estimate': None,
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'preorder_request_id': None,
    'source_park_id': None,
    'update_seq_no': 1,
}

EXPECTED_PARK_ORDER1_1 = {
    'park_id': 'park_id1',
    'id': 'order1_1',
    'last_order_alias_id': 'order_alias_id1',
    'status': 'completed',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
    'ended_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'is_creator': True,
    'event_index': 3,
    'last_contractor_park_id': 'park_id1',
    'last_contractor_id': 'contractor_id1',
    'last_contractor_car_id': 'car_id1',
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'number': 1,
    'booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
    'driving_at': None,
    'duration_estimate': None,
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'preorder_request_id': None,
    'source_park_id': 'park_id1',
    'update_seq_no': 2,
}

EXPECTED_PARK_ORDER1_2 = {
    'park_id': 'park_id1',
    'id': 'order1_2',
    'last_order_alias_id': None,
    'status': 'created',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'ended_at': None,
    'is_creator': True,
    'event_index': 0,
    'last_contractor_id': None,
    'last_contractor_park_id': None,
    'last_contractor_car_id': None,
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'number': 2,
    'booked_at': None,
    'client_booked_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'driving_at': None,
    'duration_estimate': datetime.timedelta(seconds=409),
    'forced_fixprice': None,
    'geopoint_from': [37.0, 50.0],
    'geopoints_to': [[37.0, 51.0], [37.0, 52.0]],
    'preorder_request_id': None,
    'source_park_id': 'park_id1',
    'update_seq_no': 3,
}

EXPECTED_PARK_ORDER2_1_1 = {
    'park_id': 'park_id2',
    'id': 'order2_1',
    'last_order_alias_id': None,
    'status': 'created',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'ended_at': None,
    'is_creator': True,
    'event_index': 0,
    'last_contractor_id': None,
    'last_contractor_park_id': None,
    'last_contractor_car_id': None,
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'number': 1,
    'booked_at': None,
    'client_booked_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'driving_at': None,
    'duration_estimate': datetime.timedelta(seconds=409),
    'forced_fixprice': None,
    'geopoint_from': [37.0, 50.0],
    'geopoints_to': [[37.0, 51.0], [37.0, 52.0]],
    'preorder_request_id': None,
    'source_park_id': 'park_id2',
    'update_seq_no': 4,
}

EXPECTED_PARK_ORDER2_1_2 = {
    'park_id': 'park_id2',
    'id': 'order2_1',
    'last_order_alias_id': 'order_alias_id2',
    'status': 'completed',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
    'ended_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'is_creator': True,
    'event_index': 3,
    'last_contractor_id': 'contractor_id3',
    'last_contractor_park_id': 'park_id3',
    'last_contractor_car_id': 'car_id3',
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'number': 1,
    'booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
    'driving_at': None,
    'duration_estimate': datetime.timedelta(seconds=409),
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'preorder_request_id': None,
    'source_park_id': 'park_id2',
    'update_seq_no': 5,
}

EXPECTED_PARK_ORDER2_1_3 = {
    'park_id': 'park_id3',
    'id': 'order2_1',
    'last_order_alias_id': 'order_alias_id2',
    'status': 'completed',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
    'ended_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'is_creator': False,
    'event_index': 3,
    'last_contractor_id': 'contractor_id3',
    'last_contractor_park_id': 'park_id3',
    'last_contractor_car_id': 'car_id3',
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'number': 1,
    'booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
    'driving_at': None,
    'duration_estimate': None,
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'preorder_request_id': None,
    'source_park_id': 'park_id2',
    'update_seq_no': 6,
}


STQ_FINISH_KWARGS = {
    'order_id': 'order1_1',
    'source_park_id': 'park_id1',
    'tariff_class': 'econom',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'personal_phone_id': 'phone_id1',
    'event_index': 3,
    'created': {'$date': '2021-02-09T17:00:00Z'},
    'booked': {'$date': '2021-02-09T17:30:00Z'},
    'due': {'$date': '2021-02-09T17:30:00Z'},
    'event_at': {'$date': '2021-02-09T18:00:00Z'},
    'order_alias_id': 'order_alias_id1',
    'contractor_id': 'contractor_id1',
    'contractor_park_id': 'park_id1',
    'contractor_car_id': 'car_id1',
}

STQ_CREATE1_KWARGS = {
    'order_id': 'order1_2',
    'source_park_id': 'park_id1',
    'tariff_class': 'econom',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'personal_phone_id': 'phone_id1',
    'event_index': 0,
    'created': {'$date': '2021-02-09T18:00:00Z'},
    'due': {'$date': '2021-02-09T18:00:00Z'},
    'geopoint_from': [37, 50],
    'geopoints_to': [[37, 51], [37, 52]],
    'event_at': {'$date': '2021-02-09T18:00:00Z'},
}

STQ_CREATE2_KWARGS = {
    'order_id': 'order2_1',
    'source_park_id': 'park_id2',
    'tariff_class': 'econom',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'personal_phone_id': 'phone_id1',
    'event_index': 0,
    'created': {'$date': '2021-02-09T18:00:00Z'},
    'due': {'$date': '2021-02-09T18:00:00Z'},
    'event_at': {'$date': '2021-02-09T18:00:00Z'},
    'geopoint_from': [37, 50],
    'geopoints_to': [[37, 51], [37, 52]],
}

STQ_FINISH2_KWARGS = {
    'order_id': 'order2_1',
    'source_park_id': 'park_id2',
    'tariff_class': 'econom',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'personal_phone_id': 'phone_id1',
    'event_index': 3,
    'created': {'$date': '2021-02-09T17:00:00Z'},
    'booked': {'$date': '2021-02-09T17:30:00Z'},
    'due': {'$date': '2021-02-09T17:30:00Z'},
    'event_at': {'$date': '2021-02-09T18:00:00Z'},
    'order_alias_id': 'order_alias_id2',
    'contractor_id': 'contractor_id3',
    'contractor_park_id': 'park_id3',
    'contractor_car_id': 'car_id3',
}


@pytest.mark.now('2021-02-09T19:00:00+00:00')
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_order_numbers(stq_runner, pgsql, mock_routes):
    mock_routes.set_geopoints([[37.0, 50.0], [37.0, 51.0], [37.0, 52.0]])
    cursor = pgsql['fleet_orders'].cursor()

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 1
    assert order_rows[0] == INITIAL_PARK_ORDER_1_1

    utils.reset_update_number_seq(cursor, 2)

    await stq_runner.fleet_orders_finish_handling.call(
        task_id='order1_1/3', kwargs=STQ_FINISH_KWARGS,
    )

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 1
    assert order_rows[0] == EXPECTED_PARK_ORDER1_1

    await stq_runner.fleet_orders_create_handling.call(
        task_id='order1_2/1', kwargs=STQ_CREATE1_KWARGS,
    )

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 2
    assert order_rows[0] == EXPECTED_PARK_ORDER1_1
    assert order_rows[1] == EXPECTED_PARK_ORDER1_2

    await stq_runner.fleet_orders_create_handling.call(
        task_id='order2_1/1', kwargs=STQ_CREATE2_KWARGS,
    )

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 3
    assert order_rows[0] == EXPECTED_PARK_ORDER1_1
    assert order_rows[1] == EXPECTED_PARK_ORDER1_2
    assert order_rows[2] == EXPECTED_PARK_ORDER2_1_1

    await stq_runner.fleet_orders_finish_handling.call(
        task_id='order2_1/3', kwargs=STQ_FINISH2_KWARGS,
    )

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 4
    assert order_rows[0] == EXPECTED_PARK_ORDER1_1
    assert order_rows[1] == EXPECTED_PARK_ORDER1_2
    assert order_rows[2] == EXPECTED_PARK_ORDER2_1_2
    assert order_rows[3] == EXPECTED_PARK_ORDER2_1_3
