import datetime

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime.now()
_MINUTE_AGO = _NOW - datetime.timedelta(minutes=1)
_MINUTE_AFTER = _NOW + datetime.timedelta(minutes=1)
_HOUR_AGO = _NOW - datetime.timedelta(hours=1)
_HOUR_AFTER = _NOW + datetime.timedelta(hours=1)
_6SECS_AGO = _NOW - datetime.timedelta(seconds=6)
_4SECS_AGO = _NOW - datetime.timedelta(seconds=4)
_SEC_AGO = _NOW - datetime.timedelta(seconds=1)
_YEAR_AGO = _NOW - datetime.timedelta(days=365)
_180DAYS_AGO = _NOW - datetime.timedelta(days=180)
_120DAYS_AGO = _NOW - datetime.timedelta(days=120)
_100SECS_AFTER = _NOW + datetime.timedelta(seconds=100)

_OUTDATED_TAGS_CUTOFF = datetime.timedelta(hours=1)
_OUTDATED_TAGS = _NOW - _OUTDATED_TAGS_CUTOFF - datetime.timedelta(minutes=1)

_OUTDATED_REQUESTS_CUTOFF = datetime.timedelta(minutes=10)
_OUTDATED_REQUESTS = (
    _NOW - _OUTDATED_REQUESTS_CUTOFF - datetime.timedelta(minutes=1)
)

_DISTANT_FUTURE = _NOW + datetime.timedelta(hours=12)

_OUTDATED_HISTORY_OPERATION = _NOW - datetime.timedelta(days=1, seconds=1)

_QUERIES = [
    yql_tools.Query(f'yql{i}', 2000 + i, [f'tag{i}'], enabled=i != 1)
    for i in range(4)
]


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(1000, 'cron_worker'),
                tags_tools.TagName(1001, 'wamp_ambassador'),
            ],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider.from_id(2000, True),
                tags_tools.Provider.from_id(2001, False),
            ],
        ),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(3000, 'license0', 'driver_license'),
                tags_tools.Entity(3001, 'phone0', 'phone'),
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(
                    name_id=1000,
                    provider_id=2000,
                    entity_id=3000,
                    ttl=_MINUTE_AFTER,
                    updated=_NOW,
                ),
                tags_tools.Tag(
                    name_id=1000,
                    provider_id=2001,
                    entity_id=3000,
                    ttl=_MINUTE_AFTER,
                    updated=_NOW,
                ),
                tags_tools.Tag(
                    name_id=1001,
                    provider_id=2000,
                    entity_id=3000,
                    ttl=_HOUR_AGO,
                    updated=_MINUTE_AGO,
                ),
                tags_tools.Tag(
                    name_id=1001,
                    provider_id=2001,
                    entity_id=3000,
                    ttl=_HOUR_AGO,
                    updated=_MINUTE_AGO,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'revision_delta',
    [
        pytest.param(0, marks=[pytest.mark.now(_NOW.isoformat())]),
        pytest.param(0, marks=[pytest.mark.now(_MINUTE_AGO.isoformat())]),
        pytest.param(2, marks=[pytest.mark.now(_HOUR_AFTER.isoformat())]),
        pytest.param(0, marks=[pytest.mark.now(_HOUR_AGO.isoformat())]),
    ],
)
async def test_time_to_live(taxi_tags, pgsql, revision_delta):
    revision = tags_tools.get_latest_revision(pgsql['tags'])

    await taxi_tags.tests_control()
    await tags_tools.activate_task(taxi_tags, 'customs-officer')

    updated_revision = tags_tools.get_latest_revision(pgsql['tags'])
    assert revision_delta == updated_revision - revision

    #  repeat
    await tags_tools.activate_task(taxi_tags, 'customs-officer')

    repeat_revision = tags_tools.get_latest_revision(pgsql['tags'])
    assert repeat_revision == updated_revision


def _verify_outdated_tags(now, expected_count, db):
    cutoff = now - _OUTDATED_TAGS_CUTOFF - datetime.timedelta(seconds=10)

    cursor = db.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM state.tags WHERE ttl < timestamp \'{cutoff}\';'
        ''.format(cutoff=cutoff.isoformat()),
    )

    rows = list(row for row in cursor)
    assert rows[0][0] == expected_count


def _verify_tokens_count(expected_tokens_count, db):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM service.request_results;')
    rows = list(row for row in cursor)
    assert len(rows) == expected_tokens_count


def _verify_yql_operations_count(idx, expected_yql_operations_count, db):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM service.yql_operations;')
    rows = list(row for row in cursor)
    assert len(rows) == expected_yql_operations_count


def _verify_history_operations_count(expected_history_operations_count, db):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM service.history_operations;')
    rows = list(row for row in cursor)
    assert len(rows) == expected_history_operations_count


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(1000, 'cron_worker'),
                tags_tools.TagName(1001, 'wamp_ambassador'),
            ],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider.from_id(2000, True),
                tags_tools.Provider.from_id(2001, False),
                tags_tools.Provider.from_id(2002, True),
                tags_tools.Provider.from_id(2003, True),
            ],
        ),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(3000, 'long_uuid', 'udid'),
                tags_tools.Entity(3001, 'phone0', 'phone'),
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(
                    name_id=1000,
                    provider_id=2000,
                    entity_id=3000,
                    ttl=_OUTDATED_TAGS,
                    updated=_OUTDATED_TAGS,
                ),
                tags_tools.Tag(
                    name_id=1000,
                    provider_id=2001,
                    entity_id=3000,
                    ttl=_MINUTE_AGO,
                    updated=_NOW,
                ),
                tags_tools.Tag(
                    name_id=1001,
                    provider_id=2000,
                    entity_id=3000,
                    ttl=_NOW,
                    updated=_MINUTE_AGO,
                ),
                tags_tools.Tag(
                    name_id=1001,
                    provider_id=2001,
                    entity_id=3000,
                    ttl=_HOUR_AFTER,
                    updated=_MINUTE_AGO,
                ),
            ],
        ),
        tags_tools.insert_request_results(
            [
                tags_tools.Token(
                    'token0', _NOW - datetime.timedelta(days=5), 200,
                ),
                tags_tools.Token(
                    'token1',
                    _OUTDATED_REQUESTS - datetime.timedelta(hours=1),
                    200,
                ),
                tags_tools.Token('token2', _OUTDATED_REQUESTS, 200),
                tags_tools.Token(
                    'token4',
                    _OUTDATED_REQUESTS + datetime.timedelta(minutes=4),
                    200,
                ),
                tags_tools.Token('token5', _NOW, 200),
            ],
        ),
        yql_tools.insert_queries(_QUERIES),
        yql_tools.insert_operation(
            'operation_00', 2000, 'dbid_uuid', 'failed', _180DAYS_AGO,
        ),
        yql_tools.insert_operation(
            'operation_01', 2000, 'dbid_uuid', 'failed', _120DAYS_AGO,
        ),
        yql_tools.insert_operation(
            'operation_10', 2001, 'dbid_uuid', 'completed', _YEAR_AGO,
        ),
        yql_tools.insert_operation(
            'operation_11',
            2001,
            'dbid_uuid',
            'completed',
            _YEAR_AGO + datetime.timedelta(minutes=1),
        ),
        yql_tools.insert_operation(
            'operation_30', 2003, 'dbid_uuid', 'completed', _180DAYS_AGO,
        ),
        yql_tools.insert_operation(
            'operation_31', 2003, 'dbid_uuid', 'completed', _120DAYS_AGO,
        ),
        tags_tools.insert_history_operations(
            [
                ('id_0', 'path', _NOW - datetime.timedelta(days=1, hours=5)),
                ('id_1', 'path', _NOW - datetime.timedelta(days=1, hours=4)),
                ('id_2', 'path', _NOW - datetime.timedelta(days=1, seconds=1)),
                ('id_3', 'path', _NOW - datetime.timedelta(hours=13)),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'timestamp, outdated_tags_counts, tokens_counts, yql_operation_counts,'
    'history_operations_counts',
    [
        pytest.param(
            _NOW,
            [1, 0, 0],
            [5, 2, 2],
            [6, 2, 2],
            [4, 2, 1],
            marks=[pytest.mark.now(_NOW.isoformat())],
        ),
        pytest.param(
            _OUTDATED_TAGS,
            [0, 0, 0],
            [5, 4, 4],
            [6, 2, 2],
            [4, 2, 2],
            marks=[pytest.mark.now(_OUTDATED_TAGS.isoformat())],
        ),
        # two tags with ttl > updated couldn't be removed
        # since they're not updated by tags_updater
        pytest.param(
            _DISTANT_FUTURE,
            [4, 2, 2],
            [5, 1, 0],
            [6, 2, 2],
            [4, 2, 0],
            marks=[pytest.mark.now(_DISTANT_FUTURE.isoformat())],
        ),
    ],
)
async def test_garbage_collector(
        taxi_tags,
        pgsql,
        timestamp,
        outdated_tags_counts,
        tokens_counts,
        yql_operation_counts,
        history_operations_counts,
):
    pytest.mark.now(timestamp)
    await taxi_tags.tests_control()

    db = pgsql['tags']

    _verify_outdated_tags(timestamp, outdated_tags_counts[0], db)
    _verify_tokens_count(tokens_counts[0], db)
    _verify_yql_operations_count(0, yql_operation_counts[0], db)

    for index in range(1, 3):
        await tags_tools.activate_task(taxi_tags, 'garbage-collector')
        _verify_outdated_tags(timestamp, outdated_tags_counts[index], db)
        _verify_tokens_count(tokens_counts[index], db)
        _verify_yql_operations_count(index, yql_operation_counts[index], db)
        _verify_history_operations_count(history_operations_counts[index], db)
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    _verify_yql_operations_count(2, yql_operation_counts[2], db)


@pytest.mark.config(TAGS_OUTDATED_TAGS_REMOVAL_TIMEOUT=7)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names([tags_tools.TagName(0, 'tag_0')]),
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(0, 'udid0', 'udid'),
                tags_tools.Entity(1, 'udid1', 'udid'),
                tags_tools.Entity(2, 'udid2', 'udid'),
                tags_tools.Entity(3, 'udid3', 'udid'),
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(
                    name_id=0,
                    provider_id=0,
                    entity_id=0,
                    ttl=_NOW - datetime.timedelta(hours=10),
                    # this one was updated just recently
                    updated=_NOW,
                ),
                tags_tools.Tag(
                    name_id=0,
                    provider_id=0,
                    entity_id=1,
                    ttl=_NOW - datetime.timedelta(hours=5),
                    # this one was updated just recently
                    updated=_NOW,
                ),
                tags_tools.Tag(
                    name_id=0,
                    provider_id=0,
                    entity_id=2,
                    ttl=_NOW - datetime.timedelta(hours=10),
                    # this tag is outdated and should be cleared out
                    updated=_NOW - datetime.timedelta(hours=9),
                ),
                tags_tools.Tag(
                    name_id=0,
                    provider_id=0,
                    entity_id=3,
                    ttl=_NOW - datetime.timedelta(hours=5),
                    # this one was updated on time, but is not yet outdated
                    updated=_NOW - datetime.timedelta(hours=5),
                ),
            ],
        ),
    ],
)
async def test_remove_old_deleted_tags(taxi_tags, pgsql):
    db = pgsql['tags']

    assert tags_tools.get_count_tag_record(db, 'tag_0') == 4
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    assert tags_tools.get_count_tag_record(db, 'tag_0') == 3


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_request_results(
            [
                tags_tools.Token('token0', _MINUTE_AGO, None),
                tags_tools.Token('token1', _MINUTE_AFTER, None),
                tags_tools.Token('token2', _SEC_AGO, None),
                tags_tools.Token('token3', _100SECS_AFTER, None),
                tags_tools.Token('token4', _MINUTE_AGO, 200),
                tags_tools.Token('token5', _4SECS_AGO, None),
            ],
        ),
    ],
)
async def test_stuck_request_deleter(taxi_tags, pgsql):
    await tags_tools.activate_task(taxi_tags, 'stuck-request-deleter')
    tags_tools.validate_request_results(
        [
            ('token1', _MINUTE_AFTER, None),
            ('token2', _SEC_AGO, None),
            ('token3', _100SECS_AFTER, None),
            ('token4', _MINUTE_AGO, 200),
        ],
        pgsql['tags'],
    )

    await tags_tools.activate_task(taxi_tags, 'stuck-request-deleter')
    tags_tools.validate_request_results(
        [
            ('token1', _MINUTE_AFTER, None),
            ('token3', _100SECS_AFTER, None),
            ('token4', _MINUTE_AGO, 200),
        ],
        pgsql['tags'],
    )


def _get_entities_ids(pgsql):
    cursor = pgsql['tags'].cursor()
    cursor.execute('SELECT id FROM state.entities ORDER BY id;')
    return list(row[0] for row in cursor)


def _get_entities_deleter_state(pgsql):
    cursor = pgsql['tags'].cursor()
    cursor.execute(
        'SELECT current_id, stop_id FROM service.entities_deleter_state;',
    )
    res = list({'current_id': row[0], 'stop_id': row[1]} for row in cursor)
    assert len(res) <= 1
    if res:
        return res[0]
    return None


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_entities(
            [
                # have tags, ignore
                tags_tools.Entity(0, '0'),
                tags_tools.Entity(1, '1'),
                # only one has tags
                tags_tools.Entity(2, '2'),
                tags_tools.Entity(3, '3'),
                # do not have tags
                tags_tools.Entity(4, '4'),
                tags_tools.Entity(5, '5'),
                # has tags in customs
                tags_tools.Entity(6, '6'),
            ],
        ),
        tags_tools.insert_providers([tags_tools.Provider(0, '0', '0', True)]),
        tags_tools.insert_tag_names([tags_tools.TagName(0, '0')]),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(0, 0, 0),
                tags_tools.Tag(0, 0, 1),
                tags_tools.Tag(0, 0, 2),
            ],
        ),
        tags_tools.insert_tags_customs([tags_tools.Tag(0, 0, 6)], 'append'),
    ],
)
@pytest.mark.config(
    UTAGS_GARBAGE_CRON_SETTINGS={
        '__default__': {
            '__default__': {
                'enabled': False,
                'execution_count': 1,
                'wait_time': 60,
                'limit': 2048,
                'execute_timeout': 1000,
                'statement_timeout': 1000,
            },
            'cleanup_unused_entities': {
                'enabled': True,
                'execution_count': 1,
                'wait_time': 60,
                'limit': 2,
                'execute_timeout': 1000,
                'statement_timeout': 1000,
            },
        },
    },
)
async def test_unused_entities_deleter(taxi_tags, pgsql, mocked_time):
    await taxi_tags.tests_control()
    # init worker
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    assert _get_entities_ids(pgsql) == [0, 1, 2, 3, 4, 5, 6]
    assert _get_entities_deleter_state(pgsql) == {
        'current_id': 0,
        'stop_id': 6,
    }

    # insert new entitiy to check that it shall remain
    tags_tools.apply_queries(
        pgsql['tags'],
        [tags_tools.insert_entities([tags_tools.Entity(7, '7')])],
    )

    # process first chunk
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    assert _get_entities_ids(pgsql) == [0, 1, 2, 3, 4, 5, 6, 7]
    assert _get_entities_deleter_state(pgsql) == {
        'current_id': 2,
        'stop_id': 6,
    }

    # process second chunk
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    assert _get_entities_ids(pgsql) == [0, 1, 2, 4, 5, 6, 7]
    assert _get_entities_deleter_state(pgsql) == {
        'current_id': 4,
        'stop_id': 6,
    }

    # process third chunk
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    assert _get_entities_ids(pgsql) == [0, 1, 2, 6, 7]
    assert _get_entities_deleter_state(pgsql) == {
        'current_id': 6,
        'stop_id': 6,
    }

    # process last chunk
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    assert _get_entities_ids(pgsql) == [0, 1, 2, 6, 7]
    assert _get_entities_deleter_state(pgsql) is None


@pytest.mark.config(
    TAGS_PG_THROTTLING_SETTINGS={
        'garbage-collector': {'pg_warning': {'is_disabled': True}},
    },
)
async def test_throttling(taxi_tags, statistics, testpoint):
    # init fallbacks
    statistics.fallbacks = ['tags.pg_warning']
    await taxi_tags.invalidate_caches()

    @testpoint('throttled')
    def _throttled_testpoint(data):
        pass

    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    assert _throttled_testpoint.has_calls
