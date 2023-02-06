import datetime
import pytest

from taxi.core import async
from taxi.core import db
from taxi.external import personal
from taxi_maintenance.stuff import ensure_excluded_drivers_personal_ids
from taxi_maintenance.monrun.common import (
    excluded_drivers_personal_ids_monitorings
)

LOGIN_TO_ID_MAP = {
    'LICENSE1': 'ID1',
    'LICENSE2': 'ID2',
}


IDS = [
    'correct_driver', 'no_license', 'none_license', 'empty_license',
    'wrong_license', 'none_to_id', 'empty_to_id', 'id_to_none',
    'id_to_empty', 'none_to_empty', 'empty_to_none', 'unset_id'
]


CORRECT_DOCS = {
    'correct_driver': {'_id': 'correct_driver', 'd': 'LICENSE1', 'p_id': 'ID1'},
    'no_license': {'_id': 'no_license'},
    'none_license': {'_id': 'none_license', 'd': None, 'p_id': None},
    'empty_license': {'_id': 'empty_license', 'd': '', 'p_id': ''},
    'wrong_license': {'_id': 'wrong_license', 'd': 'LICENSE2', 'p_id': 'ID2'},
    'none_to_id': {'_id': 'none_to_id', 'd': 'LICENSE1', 'p_id': 'ID1'},
    'empty_to_id': {'_id': 'empty_to_id', 'd': 'LICENSE1', 'p_id': 'ID1'},
    'id_to_none': {'_id': 'id_to_none', 'd': None, 'p_id': None},
    'id_to_empty': {'_id': 'id_to_empty', 'd': '', 'p_id': ''},
    'none_to_empty': {'_id': 'none_to_empty', 'd': '', 'p_id': ''},
    'empty_to_none': {'_id': 'empty_to_none', 'd': None, 'p_id': None},
    'unset_id': {'_id': 'unset_id', 'p_id': ''}
}


INTERVAL_MINUTES = 5


@async.inline_callbacks
def _check_db():
    for id in IDS:
        real_doc = yield db.excluded_drivers.find_one({'_id': id})
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


@pytest.mark.config(ENSURE_EXCLUDED_DRIVERS_PD_SETTINGS={
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
    yield ensure_excluded_drivers_personal_ids.do_stuff(
        datetime.datetime.now())
    errors_number = (
        yield excluded_drivers_personal_ids_monitorings.check_cron_status(
            'runtime_errors', INTERVAL_MINUTES))
    warnings_number = (
        yield excluded_drivers_personal_ids_monitorings.check_cron_status(
            'revise_warnings', INTERVAL_MINUTES))
    assert errors_number == 0
    assert warnings_number == 0


@pytest.mark.config(ENSURE_EXCLUDED_DRIVERS_PD_SETTINGS={
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

    yield ensure_excluded_drivers_personal_ids.do_stuff(
        datetime.datetime.now())
    errors_number = (
        yield excluded_drivers_personal_ids_monitorings.check_cron_status(
            'runtime_errors', INTERVAL_MINUTES))
    warnings_number = (
        yield excluded_drivers_personal_ids_monitorings.check_cron_status(
            'revise_warnings', INTERVAL_MINUTES))
    assert errors_number == 0
    assert warnings_number == 0


@pytest.mark.config(ENSURE_EXCLUDED_DRIVERS_PD_SETTINGS={
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
    yield ensure_excluded_drivers_personal_ids.do_stuff(
        datetime.datetime.now())
    yield sleep(90)
    errors_number = (
        yield excluded_drivers_personal_ids_monitorings.check_cron_status(
            'runtime_errors', INTERVAL_MINUTES))
    warnings_number = (
        yield excluded_drivers_personal_ids_monitorings.check_cron_status(
            'revise_warnings', INTERVAL_MINUTES))
    assert errors_number == 0
    assert warnings_number == 7
    yield _check_db()
