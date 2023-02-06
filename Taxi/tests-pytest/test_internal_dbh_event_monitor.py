import datetime

import pytest

from taxi.internal import dbh


@pytest.inline_callbacks
def test_register_event():
    doc_id = yield dbh.event_monitor.Doc.register_event({
        'created': datetime.datetime(2016, 9, 21, 12, 0, 0),
        'name': 'test',
        'foo': 'bar',
    })
    doc = yield dbh.event_monitor.Doc._find_one({
        dbh.event_monitor.Doc._id: doc_id
    })
    assert doc is not None
    doc = dbh.event_monitor.Doc(doc)

    assert doc.name == 'test'
    assert doc.created == datetime.datetime(2016, 9, 21, 12, 0, 0)
    assert doc['foo'] == 'bar'
