import datetime
import pytest

from taxi.core import async
from taxi.internal import event_monitor
from taxi_maintenance.stuff import ensure_order_proc_personal_ids


LICENSE_NUMBER_TO_ID_MAP = {
    'LICNUM1': 'LICID1',
    'LICNUM2': 'LICID2',
    'LICNUM3': 'LICID3'
}


PHONE_TO_ID_MAP = {
    'PHONE1': 'PHONEID1',
    'PHONE2': 'PHONEID2'
}


@async.inline_callbacks
def _bulk_store(data_type, values, validate=True, log_extra=None):
    assert (
            data_type == 'driver_licenses' or
            data_type == 'phones'
    )
    if data_type == 'driver_licenses':
        response = [
            {'id': LICENSE_NUMBER_TO_ID_MAP[license], 'license': license}
            for license in values
        ]
    if data_type == 'phones':
        response = [
            {'id': PHONE_TO_ID_MAP[phone], 'phone': phone}
            for phone in values
        ]
    yield async.return_value(response)


@pytest.mark.config(ENSURE_ORDER_PROC_PD_SETTINGS={
    'enabled': False,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 2,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.inline_callbacks
def test_do_stuff_disabled():
    yield ensure_order_proc_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_order_proc_event.get_recent())
    assert event is None


@pytest.mark.config(ENSURE_ORDER_PROC_PD_SETTINGS={
    'enabled': True,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 3,
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

    yield ensure_order_proc_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_order_proc_event.get_recent())
    assert event['last_updated'] == datetime.datetime(2019, 10, 1, 1, 0, 0)
    event = (yield event_monitor.
             ensure_personal_ids_in_order_proc_event.get_recent())
    assert event['last_updated'] == datetime.datetime(2019, 10, 1, 1, 0, 0)
