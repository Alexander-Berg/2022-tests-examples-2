import datetime

import pytest

from taxi.core import db
from taxi.internal import dbh


@pytest.inline_callbacks
def test_get_stats():
    # Beacuse of TTL index we can't use fixtures
    now = datetime.datetime.utcnow().replace(minute=0, microsecond=0)
    doc = {
        '_id': '0',
        'name': 'test',
        'created': now,
        'foo': 1,
        'bar': 2,
        'maurice': 3,
    }
    yield db.event_stats.insert(doc)
    doc = {
        '_id': '1',
        'name': 'test',
        'created': now - datetime.timedelta(minutes=1),
        'foo': 1,
        'maurice': 3,
    }
    yield db.event_stats.insert(doc)

    stats = yield dbh.event_stats.Doc.get_stats(
        'test',
        now - datetime.timedelta(minutes=5),
        now + datetime.timedelta(minutes=1),
    )
    assert stats == {
        'foo': 2,
        'bar': 2,
        'maurice': 6,
    }

    stats = yield dbh.event_stats.Doc.get_stats(
        'test',
        now - datetime.timedelta(minutes=5),
        now + datetime.timedelta(minutes=1),
        fields=['foo', 'bar']
    )
    assert stats == {
        'foo': 2,
        'bar': 2,
    }

    stats = yield dbh.event_stats.Doc.get_stats_list(
        'test',
        now - datetime.timedelta(minutes=5),
        now + datetime.timedelta(minutes=1),
        fields=['foo', 'bar']
    )
    assert sorted(stats) == [
        {'_id': '1', 'foo': 1},
        {'_id': '0', 'bar': 2, 'foo': 1},
    ]
