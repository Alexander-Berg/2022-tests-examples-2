import dateutil.parser
import pytest

from tests_fleet_orders import utils

EXPECTED_PARK_ORDER_1_OLD = {
    'park_id': 'park_id1',
    'id': 'order1',
    'last_order_alias_id': None,
    'status': 'created',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
    'booked_at': None,
    'ended_at': None,
    'is_creator': True,
    'event_index': 2,
    'last_contractor_id': None,
    'last_contractor_park_id': None,
    'last_contractor_car_id': None,
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'driving_at': None,
    'client_booked_at': None,
    'duration_estimate': None,
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'number': 1,
    'preorder_request_id': None,
    'source_park_id': None,
    'update_seq_no': 1,
}

EXPECTED_PARK_ORDER_1 = {
    'park_id': 'park_id1',
    'id': 'order1',
    'last_order_alias_id': None,
    'status': 'cancelled_by_park',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
    'booked_at': None,
    'ended_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'is_creator': True,
    'event_index': 3,
    'last_contractor_id': 'driver_id1',
    'last_contractor_park_id': 'park_id1',
    'last_contractor_car_id': 'car_id1',
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'driving_at': None,
    'client_booked_at': dateutil.parser.parse('2021-02-09T17:32:00Z'),
    'duration_estimate': None,
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'number': 1,
    'preorder_request_id': None,
    'source_park_id': 'park_id1',
    'update_seq_no': 3,
}

EXPECTED_PARK_ORDER_2_OLD = {
    'park_id': 'park_id2',
    'id': 'order2',
    'last_order_alias_id': 'order_alias2',
    'status': 'assigned',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_C',
    'addresses_to': ['address_D1', 'address_D2'],
    'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'booked_at': None,
    'ended_at': None,
    'is_creator': True,
    'event_index': 2,
    'last_contractor_id': None,
    'last_contractor_park_id': None,
    'last_contractor_car_id': None,
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'driving_at': None,
    'client_booked_at': None,
    'duration_estimate': None,
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'number': 1,
    'preorder_request_id': None,
    'source_park_id': None,
    'update_seq_no': 2,
}

EXPECTED_PARK_ORDER_2 = {
    'park_id': 'park_id2',
    'id': 'order2',
    'last_order_alias_id': 'order_alias2',
    'status': 'cancelled_by_user',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_C',
    'addresses_to': ['address_D1', 'address_D2'],
    'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'booked_at': None,
    'ended_at': dateutil.parser.parse('2021-02-09T18:20:00Z'),
    'is_creator': True,
    'event_index': 3,
    'last_contractor_id': None,
    'last_contractor_park_id': None,
    'last_contractor_car_id': None,
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'driving_at': None,
    'client_booked_at': dateutil.parser.parse('2021-02-09T17:32:00Z'),
    'duration_estimate': None,
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'number': 1,
    'preorder_request_id': None,
    'source_park_id': 'park_id2',
    'update_seq_no': 3,
}

STQ_KWARGS_1 = {
    'order_id': 'order1',
    'source_park_id': 'park_id1',
    'tariff_class': 'econom',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'personal_phone_id': 'phone_id1',
    'event_index': 3,
    'created': {'$date': '2021-02-09T17:00:00Z'},
    'event_at': {'$date': '2021-02-09T18:00:00Z'},
    'due': {'$date': '2021-02-09T17:32:00Z'},
    'cancel_by_park': True,
    'cancel_by_user': False,
    'contractor_park_id': 'park_id1',
    'contractor_id': 'driver_id1',
    'contractor_car_id': 'car_id1',
}

STQ_KWARGS_2 = {
    'order_id': 'order2',
    'source_park_id': 'park_id2',
    'tariff_class': 'econom',
    'address_from': 'address_C',
    'addresses_to': ['address_D1', 'address_D2'],
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'personal_phone_id': 'phone_id1',
    'event_index': 3,
    'created': {'$date': '2021-02-09T18:00:00Z'},
    'event_at': {'$date': '2021-02-09T18:20:00Z'},
    'due': {'$date': '2021-02-09T17:32:00Z'},
    'cancel_by_park': False,
    'cancel_by_user': True,
    'contractor_park_id': None,
}


@pytest.mark.now('2021-02-09T19:00:00+00:00')
@pytest.mark.pgsql('fleet_orders', files=['orders1.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, expected',
    [
        (STQ_KWARGS_1, [EXPECTED_PARK_ORDER_1, EXPECTED_PARK_ORDER_2_OLD]),
        (STQ_KWARGS_2, [EXPECTED_PARK_ORDER_1_OLD, EXPECTED_PARK_ORDER_2]),
    ],
)
async def test_cancel_handling(stq_runner, pgsql, stq_kwargs, expected):
    cursor = pgsql['fleet_orders'].cursor()

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 2
    assert order_rows[0] == EXPECTED_PARK_ORDER_1_OLD
    assert order_rows[1] == EXPECTED_PARK_ORDER_2_OLD

    utils.reset_update_number_seq(cursor, 3)

    await stq_runner.fleet_orders_cancel_handling.call(
        task_id='some_task_id', kwargs=stq_kwargs,
    )

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 2
    assert order_rows[0] == expected[0]
    assert order_rows[1] == expected[1]


STQ_KWARGS_3 = {
    'order_id': 'order3',
    'source_park_id': 'park_id1',
    'tariff_class': 'econom',
    'address_from': 'address_C',
    'addresses_to': ['address_D1', 'address_D2'],
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'personal_phone_id': 'phone_id1',
    'event_index': 3,
    'created': {'$date': '2021-02-09T18:00:00Z'},
    'booked': {'$date': '2021-02-09T18:15:00Z'},
    'event_at': {'$date': '2021-02-09T18:20:00Z'},
    'due': {'$date': '2021-02-09T17:32:00Z'},
    'cancel_by_park': False,
    'cancel_by_user': True,
    'contractor_park_id': 'park_id2',
    'contractor_id': 'some_driver_id',
    'contractor_car_id': 'some_car_id',
}


@pytest.mark.now('2021-02-09T18:08:00+00:00')
@pytest.mark.pgsql('fleet_orders', files=['orders2.sql'])
async def test_cancel_handling_other_park(stq_runner, pgsql):
    cursor = pgsql['fleet_orders'].cursor()

    assert utils.get_park_order(cursor) == [
        {
            'park_id': 'park_id1',
            'id': 'order3',
            'last_order_alias_id': None,
            'status': 'driving',
            'tariff_class': 'econom',
            'personal_phone_id': 'phone_id1',
            'address_from': 'address_A',
            'addresses_to': ['address_B1', 'address_B2'],
            'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
            'ended_at': None,
            'is_creator': True,
            'event_index': 2,
            'last_contractor_park_id': 'park_id2',
            'last_contractor_id': 'some_driver_id',
            'last_contractor_car_id': 'some_car_id',
            'booked_at': dateutil.parser.parse('2021-02-09T18:10:00Z'),
            'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
            'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
            'client_booked_at': dateutil.parser.parse('2021-02-09T18:10:00Z'),
            'driving_at': dateutil.parser.parse('2021-02-09T18:05:00Z'),
            'duration_estimate': None,
            'forced_fixprice': None,
            'geopoint_from': [37.6, 50.6],
            'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
            'number': 1,
            'preorder_request_id': None,
            'source_park_id': None,
            'update_seq_no': 1,
        },
        {
            'park_id': 'park_id2',
            'id': 'order3',
            'last_order_alias_id': 'order_alias2',
            'status': 'driving',
            'tariff_class': 'econom',
            'personal_phone_id': 'phone_id1',
            'address_from': 'address_A',
            'addresses_to': ['address_B1', 'address_B2'],
            'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
            'ended_at': None,
            'is_creator': False,
            'event_index': 2,
            'last_contractor_park_id': 'park_id2',
            'last_contractor_id': 'some_driver_id',
            'last_contractor_car_id': 'some_car_id',
            'booked_at': dateutil.parser.parse('2021-02-09T18:10:00Z'),
            'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
            'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
            'client_booked_at': dateutil.parser.parse('2021-02-09T18:10:00Z'),
            'driving_at': dateutil.parser.parse('2021-02-09T18:05:00Z'),
            'duration_estimate': None,
            'forced_fixprice': None,
            'geopoint_from': [37.6, 50.6],
            'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
            'number': 1,
            'preorder_request_id': None,
            'source_park_id': None,
            'update_seq_no': 2,
        },
    ]

    utils.reset_update_number_seq(cursor, 3)

    await stq_runner.fleet_orders_cancel_handling.call(
        task_id='some_task_id', kwargs=STQ_KWARGS_3,
    )

    assert utils.get_park_order(cursor) == [
        {
            'park_id': 'park_id1',
            'id': 'order3',
            'last_order_alias_id': None,
            'status': 'cancelled_by_user',
            'tariff_class': 'econom',
            'personal_phone_id': 'phone_id1',
            'address_from': 'address_C',
            'addresses_to': ['address_D1', 'address_D2'],
            'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
            'ended_at': dateutil.parser.parse('2021-02-09T18:20:00Z'),
            'is_creator': True,
            'event_index': 3,
            'last_contractor_park_id': 'park_id2',
            'last_contractor_id': 'some_driver_id',
            'last_contractor_car_id': 'some_car_id',
            'booked_at': dateutil.parser.parse('2021-02-09T18:15:00Z'),
            'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
            'record_updated_at': dateutil.parser.parse('2021-02-09T18:08:00Z'),
            'driving_at': dateutil.parser.parse('2021-02-09T18:05:00Z'),
            'client_booked_at': dateutil.parser.parse('2021-02-09T17:32:00Z'),
            'duration_estimate': None,
            'forced_fixprice': None,
            'geopoint_from': [37.6, 50.6],
            'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
            'number': 1,
            'preorder_request_id': None,
            'source_park_id': 'park_id1',
            'update_seq_no': 3,
        },
        {
            'park_id': 'park_id2',
            'id': 'order3',
            'last_order_alias_id': 'order_alias2',
            'status': 'cancelled_by_user',
            'tariff_class': 'econom',
            'personal_phone_id': 'phone_id1',
            'address_from': 'address_C',
            'addresses_to': ['address_D1', 'address_D2'],
            'created_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
            'ended_at': dateutil.parser.parse('2021-02-09T18:20:00Z'),
            'is_creator': False,
            'event_index': 3,
            'last_contractor_park_id': 'park_id2',
            'last_contractor_id': 'some_driver_id',
            'last_contractor_car_id': 'some_car_id',
            'booked_at': dateutil.parser.parse('2021-02-09T18:15:00Z'),
            'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
            'record_updated_at': dateutil.parser.parse('2021-02-09T18:08:00Z'),
            'driving_at': dateutil.parser.parse('2021-02-09T18:05:00Z'),
            'client_booked_at': dateutil.parser.parse('2021-02-09T17:32:00Z'),
            'duration_estimate': None,
            'forced_fixprice': None,
            'geopoint_from': [37.6, 50.6],
            'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
            'number': 1,
            'preorder_request_id': None,
            'source_park_id': 'park_id1',
            'update_seq_no': 4,
        },
    ]
