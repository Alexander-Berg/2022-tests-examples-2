import bson
import copy
import datetime
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import event_monitor
from taxi.external import personal
from taxi_maintenance.stuff import ensure_taxi_parks_personal_ids


PHONE_TO_ID_MAP = {
    'PHONE': 'PHONEPDID',
    'APHONE': 'APHONEPDID',
    'BPHONE': 'BPHONEPDID',
    'C0PHONE': 'C0PHONEPDID',
    'C1PHONE': 'C1PHONEPDID',
}


EMAIL_TO_ID_MAP = {
    'EMAIL': 'EMAILPDID',
    'AEMAIL': 'AEMAILPDID',
    'BEMAIL': 'BEMAILPDID',
}


LOGIN_TO_ID_MAP = {
    'LOGIN': 'LOGINPDID',
}


INN_TO_ID_MAP = {
    'INN': 'INNPDID',
    'C0INN': 'C0INNPDID',
    'C1INN': 'C1INNPDID',
    'P0INN': 'P0INNPDID',
    'P1INN': 'P1INNPDID'
}


IDS = ['correct_park', 'empty_park', 'wrong_ids', 'incorrect_park',
       'not_full_data_1', 'not_full_data_2']


CORRECT_FIELDS = {
    'phone': 'PHONE',
    'admin_phone': 'APHONE',
    'billing_phone': 'BPHONE',
    'email': 'EMAIL',
    'admin_email': 'AEMAIL',
    'billing_email': 'BEMAIL',
    'yandex_login': 'LOGIN',
    'phone_pd_id': 'PHONEPDID',
    'admin_phone_pd_id': 'APHONEPDID',
    'billing_phone_pd_id': 'BPHONEPDID',
    'email_pd_id': 'EMAILPDID',
    'admin_email_pd_id': 'AEMAILPDID',
    'billing_email_pd_id': 'BEMAILPDID',
    'yandex_login_pd_id': 'LOGINPDID',
    'real_clids': [
        {
            'phone': 'C0PHONE',
            'phone_pd_id': 'C0PHONEPDID'
        },
        {
            'phone': 'C1PHONE',
            'phone_pd_id': 'C1PHONEPDID'
        }
    ],
    'account': {
        'details': {
            'inn': 'INN',
            'inn_pd_id': 'INNPDID'
        },
        'log': {
            'details': [
                {
                    'previous': {
                      'inn': 'P0INN',
                      'inn_pd_id': 'P0INNPDID'
                    },
                    'current': {
                      'inn': 'C0INN',
                      'inn_pd_id': 'C0INNPDID'
                    }
                },
                {
                    'previous': {
                        'inn': 'P1INN',
                        'inn_pd_id': 'P1INNPDID'
                    },
                    'current': {
                        'inn': 'C1INN',
                        'inn_pd_id': 'C1INNPDID'
                    }
                }
            ]
        }
    }
  }


@async.inline_callbacks
def _check_db():
    for id in IDS:
        real_doc = yield db.parks.find_one({'_id': id})
        if id == 'empty_park':
            expected_doc = {}
        else:
            expected_doc = copy.deepcopy(CORRECT_FIELDS)
            if id == 'not_full_data_1':
                expected_doc['account']['details'] = {}
                expected_doc['account']['log'] = {}
                expected_doc['real_clids'] = [{}]
            elif id == 'not_full_data_2':
                expected_doc['account'] = {}
                expected_doc['real_clids'] = []
        expected_doc['_id'] = id
        expected_doc['updated_ts'] = real_doc['updated_ts']
        expected_doc['updated'] = real_doc['updated']
        assert expected_doc == real_doc


def _set_updated_ts():

    index = 1
    for id in IDS:
        db.parks.update(
            {'_id': id},
            {'$set': {
                'updated_ts': bson.timestamp.Timestamp(1, index),
                'updated': datetime.datetime.utcnow()
            }},
        )
        index += 1
    assert db.parks.find(
        {'updated_ts': {'$exists': False}}).cursor.count() == 0


@async.inline_callbacks
def _bulk_store(data_type, values, validate=True, log_extra=None):
    assert (data_type in (
        personal.PERSONAL_TYPE_PHONES,
        personal.PERSONAL_TYPE_EMAILS,
        personal.PERSONAL_TYPE_YANDEX_LOGINS,
        personal.PERSONAL_TYPE_TINS,
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
    if data_type == personal.PERSONAL_TYPE_YANDEX_LOGINS:
        response = [
            {'id': LOGIN_TO_ID_MAP[login], 'login': login}
            for login in values
        ]
    if data_type == personal.PERSONAL_TYPE_TINS:
        response = [
            {'id': INN_TO_ID_MAP[tin], 'tin': tin}
            for tin in values
        ]
    yield async.return_value(response)


@pytest.mark.config(ENSURE_TAXI_PARKS_PD_SETTINGS={
    'enabled': False,
    'add_ids': False,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.inline_callbacks
def test_do_stuff_disabled():
    yield ensure_taxi_parks_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_taxi_parks_event.get_recent())
    assert event is None


@pytest.mark.config(ENSURE_TAXI_PARKS_PD_SETTINGS={
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
    yield ensure_taxi_parks_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_taxi_parks_event.get_recent())
    assert event['last_updated'] == bson.timestamp.Timestamp(1, 6)


@pytest.mark.config(ENSURE_TAXI_PARKS_PD_SETTINGS={
    'enabled': True,
    'add_ids': True,
    'log_mismatch': True,
    'sleep_time': 0,
    'chunk_size': 1,
    'full_run_time': {'hour': 2, 'minute': 0},
})
@pytest.mark.now('2019-10-25T11:00:00')
@pytest.inline_callbacks
def test_do_stuff_write_mode(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        async.return_value((yield _bulk_store(data_type, values,
                                              validate, log_extra)))

    _set_updated_ts()
    yield ensure_taxi_parks_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_taxi_parks_event.get_recent())
    yield _check_db()
    assert event['last_updated'] > bson.timestamp.Timestamp(1, 6)

    yield ensure_taxi_parks_personal_ids.do_stuff(datetime.datetime.now())
    event = (yield event_monitor.
             ensure_personal_ids_in_taxi_parks_event.get_recent())
    yield _check_db()
    assert event['last_updated'] > bson.timestamp.Timestamp(1, 6)
