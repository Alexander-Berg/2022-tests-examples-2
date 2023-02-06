from __future__ import unicode_literals

import datetime

import pytest

from taxi.core import db

from taxi_maintenance.stuff import update_exams


EXAMS = {
    'id1': {
        'course': 'course1',
        'exam_date': datetime.datetime(2017, 5, 1),
        'result': 5,
    },
    'id2': {
        'course': 'course2',
        'exam_date': datetime.datetime(2017, 5, 2),
        'result': 5,
    },
    'id3': {
        'course': 'course1',
        'exam_date': datetime.datetime(2017, 5, 3),
        'result': 1,
    },
    'id4': {
        'course': 'course1',
        'exam_date': datetime.datetime(2017, 5, 4),
        'result': 3,
    },
    'id5': {
        'course': 'course2',
        'exam_date': datetime.datetime(2017, 5, 5),
        'result': 4,
    },
}


@pytest.mark.parametrize('last_update,expected', [
    (None, {
        'id1': [EXAMS['id3'], EXAMS['id2']],
        'id2': None,
        'id3': [EXAMS['id4']],
        'id4': [EXAMS['id5']],
    }),
    (datetime.datetime(2017, 6, 1, 11, 0, 59), {
        'id1': [EXAMS['id3'], EXAMS['id2']],
        'id2': None,
        'id3': [EXAMS['id4']],
        'id4': None,
    }),
    (datetime.datetime(2017, 6, 1, 11, 30), {
        'id1': [EXAMS['id3'], EXAMS['id2']],
        'id2': None,
        'id3': [EXAMS['id4']],
        'id4': None,
    }),
    (datetime.datetime(2017, 6, 1, 12, 1), {
        'id1': None,
        'id2': None,
        'id3': None,
        'id4': None,
    }),
])
@pytest.mark.now('2017-06-20T10:00:00.0')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_update_exams(last_update, expected):
    if last_update:
        yield update_exams.update_exams_event(last_update=last_update)
    yield update_exams.do_stuff()
    for driver_id, exams in expected.viewitems():
        driver = yield db.unique_drivers.find_one(driver_id)
        assert driver.get('exams') == exams, driver_id
    recent_event = yield update_exams.update_exams_event.get_recent()
    assert recent_event['last_update'] == datetime.datetime(2017, 6, 20, 10)
