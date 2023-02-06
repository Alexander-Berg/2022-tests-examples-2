# pylint: disable=no-member
import contextlib

import pytest

from taxi import db as taxi_db
from taxi.util import context_timings
from taxi.util import performance


@pytest.fixture
def mongodb_collections():
    return ['corp_users']


async def test_timings(
        loop,
        _mongo_settings,
        mongodb,
        mongodb_settings,
        enable_mongo_connections_cache,
        patch,
):
    original_time_context = context_timings.time_context

    @patch('taxi.util.context_timings.time_context')
    @contextlib.contextmanager
    def _time_context(scope_name):
        with original_time_context(scope_name) as ctx:
            yield ctx

    all_collections = taxi_db.get_collections()
    collections = {
        name: (
            all_collections.get(name, None)
            or taxi_db.CollectionData.from_schema(mongodb_settings[name])
        )
        for name in mongodb.get_aliases()
    }
    timings_db = taxi_db.create_db(
        _mongo_settings,
        collections=collections,
        loop=loop,
        enable_timings=True,
    )

    time_storage = performance.TimeStorage('test')
    context_timings.time_storage.set(time_storage)
    assert await timings_db.corp_users.save({'_id': '1', 'name': 'one'}) == '1'
    assert {'_id': '1', 'name': 'one'} == await timings_db.corp_users.find_one(
        {'_id': '1'},
    )
    assert [{'_id': '1', 'name': 'one'}] == [
        item async for item in timings_db.corp_users.find()
    ]
    find_clock = time_storage.get_times_for_log()[
        'corp_users.' 'users.find_clock'
    ]
    await timings_db.corp_users.update({'_id': '1'}, {'$set': {'name': 'two'}})
    assert (
        find_clock
        == time_storage.get_times_for_log()['corp_users.users.find_clock']
    )
    assert [
        {'_id': '1', 'name': 'two'},
    ] == await timings_db.corp_users.find().skip(0).limit(1).to_list(None)
    assert (
        find_clock
        < time_storage.get_times_for_log()['corp_users.users.find_clock']
    )
    assert [
        {'_id': '1', 'name': 'two'},
    ] == await timings_db.corp_users.aggregate([]).to_list(None)
    assert {
        'corp_users.users.save_clock',
        'corp_users.users.find_one_clock',
        'corp_users.users.find_clock',
        'corp_users.users.update_clock',
        'corp_users.users.aggregate_clock',
    }.issubset(time_storage.get_times_for_log())
    assert len(_time_context.calls) == 7
