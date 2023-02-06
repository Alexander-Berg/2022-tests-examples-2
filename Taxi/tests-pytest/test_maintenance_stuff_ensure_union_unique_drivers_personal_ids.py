import datetime
import pytest

from taxi.core import async
from taxi.core import db
from taxi.external import personal
from taxi_maintenance.stuff import ensure_union_unique_drivers_personal_ids
from taxi_maintenance.monrun.common import (
    union_unique_drivers_personal_ids_monitorings
)

LOGIN_TO_ID_MAP = {
    'LICENSE1': 'ID1',
    'LICENSE2': 'ID2',
    'LICENSE3': 'ID3',
    'LICENSE4': 'ID4',
    'LICENSE5': 'ID5',
    'LICENSE6': 'ID6',
}


IDS = [
    'correct_task', 'incorrect_task_no_ids', 'incorrect_task_to_many_ids'
]


CORRECT_DOCS = {
    'correct_task': {
        '_id': 'correct_task',
        'licenses': [{'license': 'LICENSE1'}, {'license': 'LICENSE2'}],
        'license_ids': [{'id': 'ID1'}, {'id': 'ID2'}],
        'unique_drivers': [
            {'unique_driver_id': 'driver1'},
            {'unique_driver_id': 'driver2'}
        ]
    },
    'incorrect_task_no_ids': {
        '_id': 'incorrect_task_no_ids',
        'licenses': [{'license': 'LICENSE3'}, {'license': 'LICENSE4'}],
        'license_ids': [{'id': 'ID3'}, {'id': 'ID4'}],
        'unique_drivers': [
            {'unique_driver_id': 'driver3'},
            {'unique_driver_id': 'driver4'}
        ]
    },
    'incorrect_task_to_many_ids': {
        '_id': 'incorrect_task_to_many_ids',
        'licenses': [{'license': 'LICENSE5'}, {'license': 'LICENSE6'}],
        'license_ids': [{'id': 'ID5'}, {'id': 'ID6'}, {'id': 'ID7'}],
        'unique_drivers': [
            {'unique_driver_id': 'driver5'},
            {'unique_driver_id': 'driver6'}
        ]
    },
}


INTERVAL_MINUTES = 5


@async.inline_callbacks
def _check_db():
    for id in IDS:
        real_doc = yield db.union_unique_drivers.find_one({'_id': id})
        assert CORRECT_DOCS[id] == real_doc


@async.inline_callbacks
def _bulk_store(data_type, values, validate=True, log_extra=None):
    assert data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES
    response = [
        {'id': LOGIN_TO_ID_MAP[license], 'license': license}
        for license in values
    ]
    yield
    async.return_value(response)


@pytest.mark.config(ENSURE_UNION_UNIQUE_DRIVERS_PD_SETTINGS={
    'enabled': False,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 0, 'minute': 0},
})
@pytest.inline_callbacks
@pytest.mark.filldb(event_monitor='empty')
@pytest.mark.now('2019-12-21 00:00:00.000')
def test_do_stuff_disabled():
    yield ensure_union_unique_drivers_personal_ids.do_stuff(
        datetime.datetime.now())
    errors_number = (
        yield union_unique_drivers_personal_ids_monitorings.check_cron_status(
            'runtime_errors', INTERVAL_MINUTES))
    warnings_number = (
        yield union_unique_drivers_personal_ids_monitorings.check_cron_status(
            'revise_warnings', INTERVAL_MINUTES))
    assert errors_number == 0
    assert warnings_number == 0


@pytest.mark.config(ENSURE_UNION_UNIQUE_DRIVERS_PD_SETTINGS={
    'enabled': True,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 0, 'minute': 0},
})
@pytest.mark.filldb(event_monitor='empty')
@pytest.mark.now('2019-12-21 00:00:00.000')
@pytest.inline_callbacks
def test_do_stuff_readonly(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        async.return_value((yield _bulk_store(data_type, values,
                                              validate, log_extra)))

    yield ensure_union_unique_drivers_personal_ids.do_stuff(
        datetime.datetime.now())
    errors_number = (
        yield union_unique_drivers_personal_ids_monitorings.check_cron_status(
            'runtime_errors', INTERVAL_MINUTES))
    warnings_number = (
        yield union_unique_drivers_personal_ids_monitorings.check_cron_status(
            'revise_warnings', INTERVAL_MINUTES))
    assert errors_number == 0
    assert warnings_number == 0


@pytest.mark.config(ENSURE_UNION_UNIQUE_DRIVERS_PD_SETTINGS={
    'enabled': True,
    'add_ids': True,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 0, 'minute': 0},
})
@pytest.inline_callbacks
def test_do_stuff_write_mode(patch, sleep):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        async.return_value((yield _bulk_store(data_type, values,
                                              validate, log_extra)))

    yield ensure_union_unique_drivers_personal_ids.do_stuff(
        datetime.datetime.now())
    yield sleep(90)
    errors_number = (
        yield union_unique_drivers_personal_ids_monitorings.check_cron_status(
            'runtime_errors', INTERVAL_MINUTES))
    warnings_number = (
        yield union_unique_drivers_personal_ids_monitorings.check_cron_status(
            'revise_warnings', INTERVAL_MINUTES))
    assert errors_number == 0
    assert warnings_number == 2
    yield _check_db()
