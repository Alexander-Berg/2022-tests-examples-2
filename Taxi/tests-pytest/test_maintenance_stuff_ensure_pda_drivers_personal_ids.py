import bson
import copy
import datetime
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import event_monitor
from taxi.external import personal
from taxi_maintenance.stuff import ensure_pda_drivers_personal_ids


PHONE_TO_ID_MAP = {
    'PHONE0': 'PHONE0_PDID',
    'PHONE1': 'PHONE1_PDID',
    'PHONE2': 'PHONE2_PDID',
}


EMAIL_TO_ID_MAP = {
    'EMAIL': 'EMAIL_PDID',
}


LICENSE_TO_ID_MAP = {
    'DRIVER_LICENSE': 'DRIVER_LICENSE_PDID',
}

IDS = ['correct_driver', 'empty_driver', 'wrong_ids', 'incorrect_driver',
       'not_full_data']


CORRECT_FIELDS = {
    'phones': ['PHONE0', 'PHONE1', 'PHONE2'],
    'email': 'EMAIL',
    'license_series': 'DRIVER_',
    'license_number': 'LICENSE',
    'license': 'DRIVER_LICENSE',
    'phone_pd_ids': ['PHONE0_PDID', 'PHONE1_PDID', 'PHONE2_PDID'],
    'email_pd_id': 'EMAIL_PDID',
    'driver_license_pd_id': 'DRIVER_LICENSE_PDID'
  }


@async.inline_callbacks
def _check_db():
    for id in IDS:
        real_doc = yield db.dbdrivers.find_one({'_id': id})
        if '_id' == 'empty_driver':
            expected_doc = {}
        else:
            expected_doc = copy.deepcopy(CORRECT_FIELDS)
            if '_id' == 'not_full_data':
                expected_doc['phones'] = []
                expected_doc['phone_pd_ids'] = []
        expected_doc['_id'] = real_doc['_id']
        expected_doc['updated_ts'] = real_doc['updated_ts']
        assert expected_doc == real_doc


def _set_updated_ts():
    index = 1
    for id in IDS:
        db.dbdrivers.update(
            {'_id': id},
            {'$set': {'updated_ts': bson.timestamp.Timestamp(1, index)}},
        )
        index += 1
    assert db.dbdrivers.find(
        {'updated_ts': {'$exists': False}}).cursor.count() == 0


@async.inline_callbacks
def _bulk_store(data_type, values, validate=True, log_extra=None):
    assert (data_type in (
        personal.PERSONAL_TYPE_PHONES,
        personal.PERSONAL_TYPE_EMAILS,
        personal.PERSONAL_TYPE_DRIVER_LICENSES,
    ))
    if data_type == personal.PERSONAL_TYPE_PHONES:
        response = [
            {'id': PHONE_TO_ID_MAP[phone], 'phone': phone}
            for phone in values
        ]
    if data_type == personal.PERSONAL_TYPE_EMAILS:
        response = [
            {'id': EMAIL_TO_ID_MAP[email], 'email': email}
            for email in values
        ]
    if data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES:
        response = [
            {'id': LICENSE_TO_ID_MAP[license], 'license': license}
            for license in values
        ]
    yield async.return_value(response)


@pytest.mark.config(ENSURE_PDA_DRIVERS_PD_SETTINGS={
    'enabled': False,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.inline_callbacks
def test_do_stuff_disabled():
    yield ensure_pda_drivers_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_pda_drivers_event.get_recent())
    assert event is None


@pytest.mark.config(ENSURE_PDA_DRIVERS_PD_SETTINGS={
    'enabled': True,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.mark.now('2019-10-25T11:00:00')
@pytest.inline_callbacks
def test_do_stuff_readonly(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        async.return_value((yield _bulk_store(data_type, values,
                                              validate, log_extra)))

    _set_updated_ts()
    yield ensure_pda_drivers_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_pda_drivers_event.get_recent())
    assert event['last_updated'] == bson.timestamp.Timestamp(1, 5)
