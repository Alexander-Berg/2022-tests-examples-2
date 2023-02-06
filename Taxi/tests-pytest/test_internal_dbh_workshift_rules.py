import datetime
import uuid

import pytest

from taxi.internal import dbh


@pytest.inline_callbacks
def test_idempotency():
    workshift_doc = dbh.workshift_rules.Doc()
    new_id = uuid.uuid4().hex
    workshift_doc._id = new_id
    workshift_doc.request_id = 'foo'

    doc = yield dbh.workshift_rules.Doc.create(workshift_doc)
    assert doc['request_id'] == 'foo'
    with pytest.raises(dbh.workshift_rules.AlreadyExists) as excinfo:
        yield dbh.workshift_rules.Doc.create(workshift_doc)
    assert excinfo.value.object_id == doc['_id']


@pytest.mark.parametrize('shift_begin,shift_end,begin,end,expected_response', [
    (
        datetime.datetime(2018, 8, 1, 7, 0),
        datetime.datetime(2018, 8, 3, 7, 0),
        datetime.datetime(2018, 8, 4, 7, 0),
        datetime.datetime(2018, 8, 5, 7, 0),
        False
    ),
    (
        datetime.datetime(2018, 8, 4, 7, 0),
        datetime.datetime(2018, 8, 5, 7, 0),
        datetime.datetime(2018, 8, 1, 7, 0),
        datetime.datetime(2018, 8, 3, 7, 0),
        False
    ),
    (
        datetime.datetime(2018, 8, 1, 7, 0),
        datetime.datetime(2018, 8, 3, 7, 0),
        datetime.datetime(2018, 8, 2, 7, 0),
        datetime.datetime(2018, 8, 4, 7, 0),
        True
    ),
    (
        datetime.datetime(2018, 8, 3, 7, 0),
        datetime.datetime(2018, 8, 5, 7, 0),
        datetime.datetime(2018, 8, 2, 7, 0),
        datetime.datetime(2018, 8, 4, 7, 0),
        True
    ),
    (
        datetime.datetime(2018, 8, 3, 7, 0),
        datetime.datetime(2018, 8, 4, 7, 0),
        datetime.datetime(2018, 8, 1, 7, 0),
        datetime.datetime(2018, 8, 5, 7, 0),
        True
    ),
    (
        datetime.datetime(2018, 8, 1, 7, 0),
        None,
        datetime.datetime(2018, 8, 4, 7, 0),
        datetime.datetime(2018, 8, 5, 7, 0),
        True
    ),
    (
        datetime.datetime(2018, 8, 8, 7, 0),
        None,
        datetime.datetime(2018, 8, 4, 7, 0),
        datetime.datetime(2018, 8, 5, 7, 0),
        False
    ),
    (
        datetime.datetime(2018, 8, 4, 7, 0),
        None,
        datetime.datetime(2018, 8, 2, 7, 0),
        datetime.datetime(2018, 8, 5, 7, 0),
        True
    ),
    (
        datetime.datetime(2018, 8, 1, 7, 0),
        datetime.datetime(2018, 8, 3, 7, 0),
        datetime.datetime(2018, 8, 4, 7, 0),
        None,
        False
    ),
    (
        datetime.datetime(2018, 8, 1, 7, 0),
        datetime.datetime(2018, 8, 5, 7, 0),
        datetime.datetime(2018, 8, 4, 7, 0),
        None,
        True
    ),
    (
        datetime.datetime(2018, 8, 5, 7, 0),
        datetime.datetime(2018, 8, 6, 7, 0),
        datetime.datetime(2018, 8, 4, 7, 0),
        None,
        True
    ),
])
def test_intervals(shift_begin, shift_end, begin, end, expected_response):
    response = dbh.workshift_rules.Doc._is_overlapping_intervals(
        shift_begin, shift_end, begin, end
    )
    assert response == expected_response
