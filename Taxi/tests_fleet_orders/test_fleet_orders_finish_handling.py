import dateutil.parser
import pytest

from tests_fleet_orders import utils


EXPECTED_PARK_ORDER = {
    'park_id': 'park_id1',
    'id': 'order1',
    'last_order_alias_id': 'order_alias_id1',
    'status': 'completed',
    'tariff_class': 'econom',
    'personal_phone_id': 'phone_id1',
    'address_from': 'address_A',
    'addresses_to': ['address_B1', 'address_B2'],
    'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
    'booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
    'ended_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
    'is_creator': True,
    'event_index': 3,
    'last_contractor_park_id': 'park_id1',
    'last_contractor_id': 'contractor_id1',
    'last_contractor_car_id': 'car_id1',
    'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
    'driving_at': None,
    'client_booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
    'duration_estimate': None,
    'forced_fixprice': None,
    'geopoint_from': [37.6, 50.6],
    'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
    'number': 1,
    'preorder_request_id': None,
    'source_park_id': 'park_id1',
}


STQ_KWARGS = {
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
    'booked': {'$date': '2021-02-09T17:30:00Z'},
    'due': {'$date': '2021-02-09T17:30:00Z'},
    'event_at': {'$date': '2021-02-09T18:00:00Z'},
    'order_alias_id': 'order_alias_id1',
    'contractor_id': 'contractor_id1',
    'contractor_park_id': 'park_id1',
    'contractor_car_id': 'car_id1',
    'forced_fixprice': -100,
}


@pytest.mark.now('2021-02-09T19:00:00+00:00')
@pytest.mark.pgsql('fleet_orders', files=['orders1.sql'])
async def test_completed_handling(stq_runner, pgsql):
    expected_park_order_old = {
        'park_id': 'park_id1',
        'id': 'order1',
        'last_order_alias_id': 'order_alias_id1',
        'status': 'transporting',
        'tariff_class': 'econom',
        'personal_phone_id': 'phone_id1',
        'address_from': 'address_A',
        'addresses_to': ['address_B1', 'address_B2'],
        'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
        'booked_at': None,
        'ended_at': None,
        'is_creator': True,
        'event_index': 2,
        'last_contractor_id': 'contractor_id1',
        'last_contractor_park_id': 'park_id1',
        'last_contractor_car_id': 'car_id1',
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

    cursor = pgsql['fleet_orders'].cursor()

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 1
    assert order_rows[0] == expected_park_order_old

    utils.reset_update_number_seq(cursor, 2)

    await stq_runner.fleet_orders_finish_handling.call(
        task_id='order1/1', kwargs=STQ_KWARGS,
    )

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 1
    assert order_rows[0] == {**EXPECTED_PARK_ORDER, 'update_seq_no': 2}


@pytest.mark.now('2021-02-09T19:00:00+00:00')
async def test_completed_handling_without_transport(stq_runner, pgsql):
    cursor = pgsql['fleet_orders'].cursor()

    assert not utils.get_park_order(cursor)

    utils.reset_update_number_seq(cursor, 1)

    await stq_runner.fleet_orders_finish_handling.call(
        task_id='order1/2', kwargs=STQ_KWARGS,
    )

    order_rows = utils.get_park_order(cursor)

    assert len(order_rows) == 1
    assert order_rows[0] == {**EXPECTED_PARK_ORDER, 'update_seq_no': 1}


@pytest.mark.now('2021-02-09T23:00:00+00:00')
@pytest.mark.pgsql('fleet_orders', files=['orders2.sql'])
async def test_transporting_handling_retry(stq_runner, pgsql):
    cursor = pgsql['fleet_orders'].cursor()

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 1
    assert order_rows[0] == {**EXPECTED_PARK_ORDER, 'update_seq_no': 1}

    utils.reset_update_number_seq(cursor, 2)

    await stq_runner.fleet_orders_finish_handling.call(
        task_id='order1/1', kwargs=STQ_KWARGS,
    )

    order_rows = utils.get_park_order(cursor)
    assert len(order_rows) == 1
    assert order_rows[0] == {**EXPECTED_PARK_ORDER, 'update_seq_no': 1}


@pytest.mark.now('2021-02-09T19:00:00+00:00')
async def test_completed_other_park(stq_runner, pgsql):
    cursor = pgsql['fleet_orders'].cursor()

    kwargs = {
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
        'booked': {'$date': '2021-02-09T17:30:00Z'},
        'due': {'$date': '2021-02-09T17:30:00Z'},
        'event_at': {'$date': '2021-02-09T18:00:00Z'},
        'order_alias_id': 'order_alias_id2',
        'contractor_id': 'contractor_id2',
        'contractor_park_id': 'park_id2',
        'contractor_car_id': 'car_id2',
    }

    expected_creator_order = {
        'park_id': 'park_id1',
        'id': 'order1',
        'last_order_alias_id': 'order_alias_id2',
        'status': 'completed',
        'tariff_class': 'econom',
        'personal_phone_id': 'phone_id1',
        'address_from': 'address_A',
        'addresses_to': ['address_B1', 'address_B2'],
        'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
        'booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
        'ended_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
        'is_creator': True,
        'event_index': 3,
        'last_contractor_park_id': 'park_id2',
        'last_contractor_id': 'contractor_id2',
        'last_contractor_car_id': 'car_id2',
        'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'driving_at': None,
        'client_booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
        'duration_estimate': None,
        'forced_fixprice': None,
        'geopoint_from': [37.6, 50.6],
        'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
        'number': 1,
        'preorder_request_id': None,
        'source_park_id': 'park_id1',
        'update_seq_no': 1,
    }

    expected_contractor_order = {
        'park_id': 'park_id2',
        'id': 'order1',
        'last_order_alias_id': 'order_alias_id2',
        'status': 'completed',
        'tariff_class': 'econom',
        'personal_phone_id': 'phone_id1',
        'address_from': 'address_A',
        'addresses_to': ['address_B1', 'address_B2'],
        'created_at': dateutil.parser.parse('2021-02-09T17:00:00Z'),
        'booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
        'ended_at': dateutil.parser.parse('2021-02-09T18:00:00Z'),
        'is_creator': False,
        'event_index': 3,
        'last_contractor_park_id': 'park_id2',
        'last_contractor_id': 'contractor_id2',
        'last_contractor_car_id': 'car_id2',
        'record_created_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-02-09T19:00:00Z'),
        'driving_at': None,
        'client_booked_at': dateutil.parser.parse('2021-02-09T17:30:00Z'),
        'duration_estimate': None,
        'forced_fixprice': None,
        'geopoint_from': [37.6, 50.6],
        'geopoints_to': [[37.6, 51.6], [37.6, 52.6]],
        'number': 1,
        'preorder_request_id': None,
        'source_park_id': 'park_id1',
        'update_seq_no': 2,
    }

    utils.reset_update_number_seq(cursor, 1)

    await stq_runner.fleet_orders_finish_handling.call(
        task_id='order1/2', kwargs=kwargs,
    )

    order_rows = utils.get_park_order(cursor)

    assert len(order_rows) == 2
    assert order_rows[0] == expected_creator_order
    assert order_rows[1] == expected_contractor_order
