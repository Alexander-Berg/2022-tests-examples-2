import datetime
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import event_monitor
from taxi_maintenance.stuff import ensure_orders_personal_ids


LICENSE_NUMBER_TO_ID_MAP = {
    'LICNUM1': 'LICID1'
}


INN_TO_ID_MAP = {
    'INN1': 'INNID1'
}


@async.inline_callbacks
def _bulk_store(data_type, values, validate=True, log_extra=None):
    assert (
            data_type == 'driver_licenses' or
            data_type == 'tins'
    )
    if data_type == 'driver_licenses':
        response = [
            {'id': LICENSE_NUMBER_TO_ID_MAP[license], 'license': license}
            for license in values
        ]
    if data_type == 'tins':
        response = [
            {'id': INN_TO_ID_MAP[inn], 'tin': inn}
            for inn in values
        ]
    yield async.return_value(response)


@pytest.mark.config(ENSURE_ORDERS_PD_SETTINGS={
    'enabled': False,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 2,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.inline_callbacks
def test_do_stuff_disabled():
    yield ensure_orders_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_orders_event.get_recent())
    assert event is None


@pytest.mark.config(ENSURE_ORDERS_PD_SETTINGS={
    'enabled': True,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 2,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.mark.now('2019-10-03T11:00:00')
@pytest.inline_callbacks
def test_do_stuff_readonly(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        async.return_value((yield _bulk_store(data_type, values,
                                              validate, log_extra)))

    yield ensure_orders_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_orders_event.get_recent())
    assert event['last_updated'] == datetime.datetime(2019, 10, 1, 5, 0, 0)


@pytest.mark.config(ENSURE_ORDERS_PD_SETTINGS={
    'enabled': True,
    'add_ids': True,
    'log_mismatch': True,
    'sleep_time': 1,
    'chunk_size': 6,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.mark.now('2019-10-03T11:00:00')
@pytest.inline_callbacks
def test_do_stuff_dryrun(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        async.return_value((yield _bulk_store(data_type, values,
                                              validate, log_extra)))

    yield ensure_orders_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_orders_event.get_recent())
    assert event['last_updated'] == datetime.datetime(2019, 10, 1, 5, 0, 0)
    full_correct_order = yield db.orders.find_one(
        {'_id': 'full_correct_order'})
    assert full_correct_order.get(
        'performer', {}).get('driver_license_personal_id') == 'LICID1'
    assert full_correct_order.get(
        'payment_tech', {}).get('inn_for_receipt_id') == 'INNID1'
    assert full_correct_order[
               'updated'] == datetime.datetime(2019, 10, 1, 0, 0, 0)

    correct_order_no_license = yield db.orders.find_one(
        {'_id': 'correct_order_no_license'})
    assert correct_order_no_license.get(
        'performer', {}).get('driver_license_personal_id') is None
    assert correct_order_no_license.get(
        'payment_tech', {}).get('inn_for_receipt_id') == 'INNID1'
    assert correct_order_no_license[
               'updated'] == datetime.datetime(2019, 10, 1, 1, 0, 0)

    correct_order_no_inn = yield db.orders.find_one(
        {'_id': 'correct_order_no_inn'})
    assert correct_order_no_inn.get(
        'performer', {}).get('driver_license_personal_id') == 'LICID1'
    assert correct_order_no_inn.get(
        'payment_tech', {}).get('inn_for_receipt_id') is None
    assert correct_order_no_inn[
               'updated'] == datetime.datetime(2019, 10, 1, 2, 0, 0)

    incorrect_order = yield db.orders.find_one(
        {'_id': 'incorrect_order'})
    assert incorrect_order.get(
        'performer', {}).get('driver_license_personal_id') == 'LICID1'
    assert incorrect_order.get(
        'payment_tech', {}).get('inn_for_receipt_id') == 'INNID1'
    assert incorrect_order[
               'updated'] > datetime.datetime(2019, 10, 1, 3, 0, 0)

    incorrect_order_no_license_id = yield db.orders.find_one(
        {'_id': 'incorrect_order_no_license_id'})
    assert incorrect_order_no_license_id.get(
        'performer', {}).get('driver_license_personal_id') == 'LICID1'
    assert incorrect_order_no_license_id.get(
        'payment_tech', {}).get('inn_for_receipt_id') == 'INNID1'
    assert incorrect_order_no_license_id[
               'updated'] > datetime.datetime(2019, 10, 1, 4, 0, 0)

    incorrect_order_no_inn_id = yield db.orders.find_one(
        {'_id': 'incorrect_order_no_inn_id'})
    assert incorrect_order_no_inn_id.get(
        'performer', {}).get('driver_license_personal_id') == 'LICID1'
    assert incorrect_order_no_inn_id.get(
        'payment_tech', {}).get('inn_for_receipt_id') == 'INNID1'
    assert incorrect_order_no_inn_id[
               'updated'] > datetime.datetime(2019, 10, 1, 5, 0, 0)

    yield ensure_orders_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_orders_event.get_recent())
    assert event['last_updated'] == datetime.datetime(2019, 10, 1, 5, 0, 0)
