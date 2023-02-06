import uuid

import bson.code
import bson.son
import pymongo
import pytest

from taxi.conf import settings
from taxi.core import db
from taxi.core.db import classes as db_classes


# FIXME: check `aggregate` (`CommandCursor`, `Cursor`, `dict`),
# `group` (`CommandCursor`) and `map_reduce` (`dict`, `Collection`),
# `inline_map_reduce` (`list`, `dict`).


def test_check_thread_pool(monkeypatch, stub, asyncenv):
    saved = settings.MONGO['taxi']['min_threads_free']
    settings.MONGO['taxi']['min_threads_free'] = 10
    working = range(51)
    pool = stub(max=60, working=working)
    reactor = stub(
        getThreadPool=lambda: pool, running=asyncenv == 'async'
    )
    monkeypatch.setattr('taxi.core.async.reactor', reactor)

    # In blocking environment this check is skipped
    if asyncenv == 'blocking':
        assert db_classes._check_thread_pool('taxi') is None

    # In asynchronous environment exception will be raised if not enough
    # free threads left
    if asyncenv == 'async':
        expected = 'Thread pool is busy (51/60). Used threshold is 10 for taxi'
        with pytest.raises(db.ExceededPoolSize) as excinfo:
            db_classes._check_thread_pool('taxi')
        assert expected in excinfo.value

        # Otherwise check returns nothing
        del working[0]
        assert db_classes._check_thread_pool('taxi') is None
    settings.MONGO['taxi']['min_threads_free'] = saved


def test_execute_in_thread(monkeypatch, mock):
    @mock
    def _check_thread_pool(connection_name):
        return

    @mock('taxi.core.threads.defer_to_thread')
    def defer_to_thread(target, *args, **kwargs):
        return target(*args, **kwargs)

    @mock
    def target(x, y=None):
        return 42

    monkeypatch.setattr(db_classes, '_check_thread_pool', _check_thread_pool)

    result = db_classes._execute_in_thread('taxi', target, 5, y=15)
    assert _check_thread_pool.calls == [{'connection_name': 'taxi'}]
    assert defer_to_thread.calls == [
        {'target': target, 'args': (5,), 'kwargs': {'y': 15}}
    ]
    assert target.calls == [{'x': 5, 'y': 15}]
    assert result == 42


def test_connections(monkeypatch, stub):
    # We have 5 connections, written in dictionary
    connections = [
        'taxi',
        'noncritical',
        'archive',
        'logs',
        'localizations',
    ]
    for connection_name in connections:
        assert connection_name in db_classes.connections
        connection = db_classes.connections[connection_name]
        assert isinstance(connection[0],
                          (db_classes.LazyMongoClient, pymongo.MongoClient))
        assert isinstance(connection[1],
                          (db_classes.LazyMongoClient, pymongo.MongoClient))

    # Check that connections was created with `_connect=False`
    calls = []
    pymongo_stub = stub(MongoClient=lambda **kwargs: calls.append(kwargs),
                        version='2.7.1')
    monkeypatch.setattr(db_classes, 'pymongo', pymongo_stub)
    lazy_client = db._connect('taxi')
    assert len(calls) == 0
    lazy_client.get_client()
    assert len(calls) == 1
    kwargs = calls.pop(0)
    assert kwargs['connect'] is False

    # Check that connection params are taken from settings
    with pytest.raises(KeyError):
        db._connect('unknown')
    assert not calls


@pytest.inline_callbacks
def test_wrappers(monkeypatch):
    dbname = 'test' + uuid.uuid4().hex
    coll = db_classes.CollectionWrapper('taxi', dbname, 'test')

    doc_id = yield coll.save({'_id': '1', 'tags': ['cat', 'dog']})
    assert doc_id == '1'

    doc_id = yield coll.insert({'_id': '2', 'tags': ['cat']})
    assert doc_id == '2'

    result = yield coll.update(
        {'_id': '3'}, {'_id': '3', 'tags': ['mouse', 'dog', 'cat']},
        upsert=True
    )
    assert result['n'] == 1

    doc = yield coll.find_and_modify(
        {'_id': '4'}, {'_id': '4', 'tags': ['mouse', 'cat']}, upsert=True,
        new=True
    )
    assert doc['_id'] == '4'

    assert (yield coll.count()) == (yield coll.find().count()) == 4

    result = yield coll.aggregate([
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": bson.son.SON([("count", -1), ("_id", -1)])}
    ])
    assert len(result) == 2

    mapper = bson.code.Code(
        """
        function () {
            this.tags.forEach(function(z) {
                emit(z, 1);
            });
        }
        """)

    reducer = bson.code.Code(
        """
        function (key, values) {
            var total = 0;
            for (var i = 0; i < values.length; i++) {
                total += values[i];
            }
            return total;
        }
        """)

    result = yield coll.map_reduce(mapper, reducer, "myresults")
    assert (yield result.find().count()) == 3

    result = yield coll.map_reduce(
        mapper, reducer, "myresults", full_response=True
    )
    assert result['counts']['emit'] == 8

    reducer = bson.code.Code(
        """
        function(obj, prev){
            prev.count++;
        }
        """)
    results = yield coll.group(
        key={"x": 1}, condition={}, initial={"count": 0}, reduce=reducer
    )
    assert len(results) == 1
