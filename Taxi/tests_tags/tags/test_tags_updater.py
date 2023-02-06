import datetime
import math
from typing import Optional

import pytest

from tests_tags.tags import constants
from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime.now()
_MINUTE_AFTER = _NOW + datetime.timedelta(minutes=1)
_TAGS_UPDATER_CHUNK_SIZE = 4
_TAGS_UPDATER_TOPIC_CHUNK_SIZE = 2
_TASK_TICKET = 'TASKTICKET-1234'
_LOGIN = 'password'


def _verify_tags_update_queue_empty(db):
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM service.tags_update_queue')

    rows = list(row for row in cursor)
    assert rows[0][0] == 0


def _verify_all_tags_have_bigger_revision(db, revision: int):
    tags = tags_select.select_table_named('state.tags', 'revision', db)
    for tag in tags:
        assert tag['revision'] > revision


def _init(
        db,
        count_of_tags: int,
        count_of_providers: int,
        provider_active: bool = True,
        insert_queries: bool = True,
):
    cursor = db.cursor()
    cursor.execute(
        tags_tools.insert_tag_names([tags_tools.TagName(0, 'tag0')]),
    )
    queries = []
    for i in range(0, count_of_providers):
        cursor.execute(
            tags_tools.insert_providers(
                [
                    tags_tools.Provider(
                        i, 'provider' + str(i), '', provider_active,
                    ),
                ],
            ),
        )
        if insert_queries:
            queries.append(
                yql_tools.Query(
                    'query' + str(i),
                    i,
                    ['tag0'],
                    _NOW,
                    _NOW,
                    enabled=provider_active,
                    ticket=_TASK_TICKET,
                    tags_limit=1000,
                ),
            )

    if insert_queries:
        cursor.execute(yql_tools.insert_queries(queries))

    for tag_id in range(0, count_of_tags):
        cursor.execute(
            tags_tools.insert_entities(
                [
                    tags_tools.Entity(
                        tag_id, 'entity' + str(tag_id), 'dbid_uuid',
                    ),
                ],
            ),
        )
    for provider_id in range(0, count_of_providers):
        for tag_id in range(0, count_of_tags):
            cursor.execute(
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            0, provider_id, tag_id, entity_type='dbid_uuid',
                        ),
                    ],
                ),
            )

    return queries if insert_queries else []


async def _change_query_state(
        taxi_tags, activate: bool, query: yql_tools.Query,
):
    await yql_tools.change_query_active_state(
        taxi_tags, query, _LOGIN, activate,
    )


def _verify_tags_update_queue_entry(
        entry,
        last_processed_revision: int,
        process_upto_revision: Optional[int],
        action: str,
):
    assert entry['last_processed_revision'] == last_processed_revision
    assert entry['action'] == action
    assert entry['process_upto_revision'] == process_upto_revision


@pytest.mark.config(TAGS_UPDATER_CHUNK_SIZE=_TAGS_UPDATER_CHUNK_SIZE)
async def test_provider_basic(taxi_tags, pgsql):
    db = pgsql['tags']
    # insert 10 tags for one provider
    queries = _init(db, 10, 1)

    await _change_query_state(taxi_tags, False, queries[0])

    first_revision = tags_tools.get_first_revision(db)
    latest_revision = tags_tools.get_latest_revision(db)
    for i in range(0, 3):
        # verify, that on each run tags-updater processes
        # TAGS_UPDATER_CHUNK_SIZE tags or less (if there are less tags)
        updates = tags_select.select_table_named(
            'service.tags_update_queue', 'provider_id', db,
        )
        assert len(updates) == 1
        _verify_tags_update_queue_entry(
            updates[0],
            0 if i == 0 else first_revision + _TAGS_UPDATER_CHUNK_SIZE * i,
            latest_revision + 1,
            'remove',
        )

        await tags_tools.activate_task(taxi_tags, 'tags-updater')

    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    # verify, that 3 iterations were enough to process all tags
    _verify_tags_update_queue_empty(db)
    _verify_all_tags_have_bigger_revision(db, latest_revision)


@pytest.mark.config(TAGS_UPDATER_CHUNK_SIZE=_TAGS_UPDATER_CHUNK_SIZE)
async def test_provider_reentrancy_disabled_query(taxi_tags, pgsql):
    db = pgsql['tags']
    queries = _init(db, 10, 1, False)

    await _change_query_state(taxi_tags, True, queries[0])

    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    updates = tags_select.select_table_named(
        'service.tags_update_queue', 'provider_id', db,
    )
    assert len(updates) == 1

    await _change_query_state(taxi_tags, False, queries[0])

    latest_revision = tags_tools.get_latest_revision(db)
    updates = tags_select.select_table_named(
        'service.tags_update_queue', 'provider_id', db,
    )
    # verify, that update task was popped out
    assert len(updates) == 1
    _verify_tags_update_queue_entry(
        updates[0], 0, latest_revision + 1, 'remove',
    )


@pytest.mark.config(TAGS_UPDATER_CHUNK_SIZE=_TAGS_UPDATER_CHUNK_SIZE)
async def test_provider_reentrancy_enabled_query(taxi_tags, pgsql):
    db = pgsql['tags']
    queries = _init(db, 10, 1, True)
    first_revision = tags_tools.get_first_revision(db)
    latest_revision_before_update = tags_tools.get_latest_revision(db)

    await _change_query_state(taxi_tags, False, queries[0])

    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    updates = tags_select.select_table_named(
        'service.tags_update_queue', 'provider_id', db,
    )
    assert len(updates) == 1

    await _change_query_state(taxi_tags, True, queries[0])

    updates = tags_select.select_table_named(
        'service.tags_update_queue', 'action', db,
    )
    assert len(updates) == 1
    _verify_tags_update_queue_entry(
        updates[0],
        first_revision + _TAGS_UPDATER_CHUNK_SIZE,
        latest_revision_before_update + 1,
        'remove',
    )


async def _set_provider_status_active(
        taxi_tags, provider_name: str, status: bool,
):
    query = 'v1/providers/activation_status?id=%s' % provider_name
    response = await taxi_tags.put(query, {'activate': status})
    assert response.status_code == 200


@pytest.mark.config(TAGS_UPDATER_CHUNK_SIZE=_TAGS_UPDATER_CHUNK_SIZE)
async def test_provider_reentrancy_usual_provider(taxi_tags, pgsql):
    db = pgsql['tags']
    _init(db, 10, 1, provider_active=True, insert_queries=False)

    await _set_provider_status_active(taxi_tags, 'provider0', False)
    first_revision = tags_tools.get_first_revision(db)
    latest_revision = tags_tools.get_latest_revision(db)

    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    updates = tags_select.select_table_named(
        'service.tags_update_queue', 'provider_id', db,
    )
    assert len(updates) == 1
    _verify_tags_update_queue_entry(
        updates[0],
        first_revision + _TAGS_UPDATER_CHUNK_SIZE,
        latest_revision + 1,
        'update',
    )

    await _set_provider_status_active(taxi_tags, 'provider0', True)

    latest_revision = tags_tools.get_latest_revision(db)
    updates = tags_select.select_table_named(
        'service.tags_update_queue', 'provider_id', db,
    )
    assert len(updates) == 1
    # assert, that latest revision has been updated
    _verify_tags_update_queue_entry(
        updates[0],
        first_revision + _TAGS_UPDATER_CHUNK_SIZE,
        latest_revision + 1,
        'update',
    )


def _verify_got_tags_after_revision(db, tags_count: int, revision: int):
    cursor = db.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM state.tags WHERE revision>' + str(revision),
    )

    rows = list(row for row in cursor)
    assert rows[0][0] == tags_count


@pytest.mark.config(TAGS_UPDATER_CHUNK_SIZE=1)
async def test_two_providers_processing(taxi_tags, pgsql):
    db = pgsql['tags']
    queries = _init(db, 100, 2)

    await _change_query_state(taxi_tags, False, queries[0])
    await _change_query_state(taxi_tags, False, queries[1])

    for _ in range(0, 99):
        await tags_tools.activate_task(taxi_tags, 'tags-updater')

    updates = tags_select.select_table_named(
        'service.tags_update_queue', 'action', db,
    )
    assert len(updates) == 2

    # this test may fail in one case per ~10^30. If it fails on this assert,
    # you are either very lucky, or you just have broken it
    # verify both tasks were processed at least one time
    assert updates[0]['last_processed_revision'] > 0
    assert updates[1]['last_processed_revision'] > 0


def _update_tags_with_revision_less_then(db, updated: int):
    cursor = db.cursor()
    # force update revision
    cursor.execute(
        'UPDATE state.tags SET provider_id=0 WHERE provider_id=0 AND revision<'
        + str(updated),
    )


@pytest.mark.config(TAGS_UPDATER_CHUNK_SIZE=_TAGS_UPDATER_CHUNK_SIZE)
# test the following scenario. We have task to update provider's tags
# Tags-updater has already processed some of them
# Other tags were processed from another place (uploader maybe)
# check, that tags-updater will finish correctly
async def test_provider_update_from_another_place(taxi_tags, pgsql):
    db = pgsql['tags']
    queries = _init(db, 10, 1)
    await _change_query_state(taxi_tags, False, queries[0])

    latest_revision = tags_tools.get_latest_revision(db)
    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    _update_tags_with_revision_less_then(db, latest_revision + 1)

    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    _verify_all_tags_have_bigger_revision(db, latest_revision)
    _verify_tags_update_queue_empty(db)


@pytest.mark.pgsql(
    'tags', files=['pg_tags_initial.sql', 'pg_topics_initial.sql'],
)
async def test_topic_basic(taxi_tags, pgsql):
    db = pgsql['tags']

    latest_revision = tags_tools.get_latest_revision(db)
    count_tag_record = tags_tools.get_count_tag_record(db, 'tag2')

    body = {'topic': 'topic0', 'tags': ['tag2']}
    response = await taxi_tags.post(
        'v2/admin/topics/items', body, headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200

    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', db,
    )
    assert len(rows) == 1
    assert rows[0]['tag_name_id'] == 2002
    assert rows[0]['last_processed_revision'] == 0
    assert rows[0]['process_upto_revision'] == latest_revision + 1

    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', db,
    )
    assert rows == []

    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    latest_revision_on_tag = tags_tools.get_latest_revision_on_tag(db, 'tag2')
    assert latest_revision + count_tag_record == latest_revision_on_tag


@pytest.mark.pgsql(
    'tags', files=['pg_tags_initial.sql', 'pg_topics_initial.sql'],
)
@pytest.mark.config(TAGS_UPDATER_CHUNK_SIZE=_TAGS_UPDATER_TOPIC_CHUNK_SIZE)
async def test_topic_update_chunk(taxi_tags, pgsql):
    db = pgsql['tags']

    latest_revision = tags_tools.get_latest_revision(db)
    count_tag_record = tags_tools.get_count_tag_record(db, 'tag2')

    body = {'topic': 'topic0', 'tags': ['tag2']}
    response = await taxi_tags.post(
        'v2/admin/topics/items', body, headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200

    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', db,
    )
    assert len(rows) == 1
    assert rows[0]['tag_name_id'] == 2002
    assert rows[0]['last_processed_revision'] == 0
    assert rows[0]['process_upto_revision'] == latest_revision + 1

    count = math.ceil(count_tag_record / _TAGS_UPDATER_TOPIC_CHUNK_SIZE)
    for index in range(count):
        await tags_tools.activate_task(taxi_tags, 'tags-updater')
        rows = tags_select.select_table_named(
            'service.topics_tags_update_queue', 'tag_name_id', db,
        )
        assert bool(rows) == (index < count - 1)

    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    latest_revision_on_tag = tags_tools.get_latest_revision_on_tag(db, 'tag2')
    assert latest_revision + count_tag_record == latest_revision_on_tag


@pytest.mark.pgsql(
    'tags', files=['pg_tags_initial.sql', 'pg_topics_initial.sql'],
)
@pytest.mark.config(TAGS_UPDATER_CHUNK_SIZE=_TAGS_UPDATER_TOPIC_CHUNK_SIZE)
async def test_topic_reset_update(taxi_tags, pgsql):
    db = pgsql['tags']

    latest_revision = tags_tools.get_latest_revision(db)

    body = {'topic': 'topic0', 'tags': ['tag2']}
    response = await taxi_tags.post(
        'v2/admin/topics/items', body, headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200

    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', db,
    )
    assert len(rows) == 1
    assert rows[0]['tag_name_id'] == 2002
    assert rows[0]['last_processed_revision'] == 0
    assert rows[0]['process_upto_revision'] == latest_revision + 1

    await tags_tools.activate_task(taxi_tags, 'tags-updater')

    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', db,
    )
    assert len(rows) == 1
    assert rows[0]['tag_name_id'] == 2002
    assert rows[0]['last_processed_revision'] > 0
    assert rows[0]['process_upto_revision'] == latest_revision + 1

    await tags_tools.activate_task(taxi_tags, 'customs-officer')

    response = await taxi_tags.post(
        'v2/admin/topics/delete_items',
        body,
        headers=constants.TEST_LOGIN_HEADER,
    )
    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', db,
    )
    assert response.status_code == 200
    assert len(rows) == 1
    assert rows[0]['tag_name_id'] == 2002
    assert rows[0]['last_processed_revision'] > 0
    assert rows[0]['process_upto_revision'] > latest_revision + 1


@pytest.mark.config(
    TAGS_PG_THROTTLING_SETTINGS={
        'tags-updater': {'pg_warning': {'is_disabled': True}},
    },
)
async def test_throttling(taxi_tags, statistics, testpoint):
    # init fallbacks
    statistics.fallbacks = ['tags.pg_warning']
    await taxi_tags.invalidate_caches()

    @testpoint('throttled')
    def _throttled_testpoint(data):
        pass

    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    assert _throttled_testpoint.has_calls
