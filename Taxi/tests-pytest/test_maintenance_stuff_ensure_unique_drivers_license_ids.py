import bson
import datetime
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import event_monitor
from taxi_maintenance.stuff import ensure_unique_drivers_license_ids

LICENSE_NUMBER_TO_ID_MAP = {
    'LICNUM1': 'LICID1',
    'LICNUM2': 'LICID2',
    'LICNUM3': 'LICID3',
    'LICNUM4': 'LICID4',
    'LICNUM5': 'LICID5',
    'LICNUM6': 'LICID6',
    '': '',
}


IDS = ['correct_driver', 'incorrect_driver_no_ids',
       'incorrect_driver_wrong_ids', 'incorrect_driver_no_licenses',
       'incorrect_driver_broken_licenses']


def _set_updated_ts():
    for index, id in enumerate(IDS):
        db.unique_drivers.update(
            {'_id': id},
            {'$set': {'updated_ts': bson.timestamp.Timestamp(1, index + 1)}},
        )
    assert db.unique_drivers.find(
        {'updated_ts': {'$exists': False}}).cursor.count() == 0


@pytest.mark.config(ENSURE_UNIQUE_DRIVERS_LICENSE_IDS_SETTINGS={
    'enabled': False,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.inline_callbacks
def test_do_stuff_disabled():
    yield ensure_unique_drivers_license_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_unique_drivers_event.get_recent())
    assert event is None


@pytest.mark.config(ENSURE_UNIQUE_DRIVERS_LICENSE_IDS_SETTINGS={
    'enabled': True,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.mark.now('2018-05-22T11:00:00')
@pytest.inline_callbacks
def test_do_stuff_readonly(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        assert data_type == 'driver_licenses'
        response = [
            {'id': LICENSE_NUMBER_TO_ID_MAP[license], 'license': license}
            for license in values
        ]
        yield async.return_value(response)

    _set_updated_ts()
    yield ensure_unique_drivers_license_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_unique_drivers_event.get_recent())
    assert event['last_updated'] == bson.timestamp.Timestamp(1, 5)


@pytest.mark.config(ENSURE_UNIQUE_DRIVERS_LICENSE_IDS_SETTINGS={
    'enabled': True,
    'add_ids': True,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.mark.now('2018-05-25T02:00:00')
@pytest.inline_callbacks
def test_do_stuff_dryrun(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        assert data_type == 'driver_licenses'
        response = [
            {'id': LICENSE_NUMBER_TO_ID_MAP[license], 'license': license}
            for license in values
        ]
        yield async.return_value(response)

    _set_updated_ts()
    yield ensure_unique_drivers_license_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_unique_drivers_event.get_recent())
    assert event['last_updated'] > bson.timestamp.Timestamp(1, 5)
    assert set(id['id'] for id in db.unique_drivers.find_one(
        {'_id': 'correct_driver'}, ['license_ids']).result['license_ids']
               ) == set(id['id'] for id in [{'id': 'LICID1'}, {'id': 'LICID2'}])
    assert db.unique_drivers.find_one(
        {'_id': 'correct_driver'},
        ['updated_ts']).result['updated_ts'] == bson.timestamp.Timestamp(1, 1)
    assert set(id['id'] for id in db.unique_drivers.find_one(
        {'_id': 'incorrect_driver_no_ids'},
        ['license_ids']).result['license_ids']) == set(
        id['id'] for id in [{'id': 'LICID3'}]
    )
    no_ids_timestamp = db.unique_drivers.find_one(
        {'_id': 'incorrect_driver_no_ids'},
        ['updated_ts']).result['updated_ts']
    assert no_ids_timestamp > bson.timestamp.Timestamp(1, 2)
    assert set(id['id'] for id in db.unique_drivers.find_one(
        {'_id': 'incorrect_driver_wrong_ids'},
        ['license_ids']).result['license_ids']) == set(
        id['id'] for id in [{'id': 'LICID4'}]
    )
    wrong_ids_timestamp = db.unique_drivers.find_one(
        {'_id': 'incorrect_driver_wrong_ids'},
        ['updated_ts']).result['updated_ts']
    assert wrong_ids_timestamp > bson.timestamp.Timestamp(1, 3)
    assert 'license_ids' not in db.unique_drivers.find_one(
        {'_id': 'incorrect_driver_no_licenses'}).result
    no_licenses_timestamp = db.unique_drivers.find_one(
        {'_id': 'incorrect_driver_no_licenses'},
        ['updated_ts']).result['updated_ts']
    assert no_licenses_timestamp > bson.timestamp.Timestamp(1, 4)
    assert db.unique_drivers.find_one(
        {'_id': 'incorrect_driver_broken_licenses'},
        ['license_ids']).result['license_ids'] == [{'id': ''}]
    broken_licenses_licenses_timestamp = db.unique_drivers.find_one(
        {'_id': 'incorrect_driver_broken_licenses'},
        ['updated_ts']).result['updated_ts']
    assert broken_licenses_licenses_timestamp > bson.timestamp.Timestamp(1, 5)
    yield ensure_unique_drivers_license_ids.do_stuff(datetime.datetime.now())
    yield ensure_unique_drivers_license_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_unique_drivers_event.get_recent())
    assert event['last_updated'] == max(
        no_licenses_timestamp,
        no_ids_timestamp,
        wrong_ids_timestamp,
        broken_licenses_licenses_timestamp
    )
