import datetime
import json

import pytest


@pytest.mark.experiments3(filename='migrate_to_ydb_future.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_single.yaml'],
)
async def test_migrate_to_ydb_yt_history_rollout_not_started(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    queue = processing.testsuite.foo
    item_id = '14648896842964516938'
    events = await queue.events(item_id)
    assert events['events']

    # one event restored in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    pg_rows = list(cursor)
    assert len(pg_rows) == 1

    # no events in ydb
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    ydb_rows = cursor[0].rows
    assert not ydb_rows


@pytest.mark.experiments3(
    clauses=[],
    default_value={
        'migrate_to_ydb': True,
        'rollout_timestamp': datetime.datetime.now().isoformat()[:-7],
        # dynamic calculation needed because we can't mock now() in PG
        # cut microseconds to get smth like '2022-03-31T11:30:40'
    },
    match={'enabled': True, 'predicate': {'type': 'true'}},
    consumers=['processing/migrate_to_ydb'],
    name='processing_migrate_to_ydb',
)
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
async def test_migrate_to_ydb_rollout_already_started(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    @testpoint('ProcessingNgQueue::DoProcessingIteration::MigrationPath')
    def fetch_migration_path(data):
        assert data['migration_path'] == 'kMigrantQueueInYDB'

    queue = processing.testsuite.foo
    item_id = '0123456789'

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'create'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    events = await queue.events(item_id)
    assert events['events']

    assert fetch_migration_path.times_called > 0

    # no events in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    pg_rows = list(cursor)
    assert not pg_rows

    # one event in ydb
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    ydb_rows = cursor[0].rows
    assert len(ydb_rows) == 1


@pytest.mark.experiments3(filename='migrate_to_ydb_future.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
async def test_migrate_to_ydb_rollout_not_started(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    @testpoint('ProcessingNgQueue::DoProcessingIteration::MigrationPath')
    def fetch_migration_path(data):
        assert data['migration_path'] == 'kMigrantQueueInPG'

    queue = processing.testsuite.foo
    item_id = '0123456789'

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'create'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    events = await queue.events(item_id)
    assert events['events']

    assert fetch_migration_path.times_called > 0

    # one event in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    pg_rows = list(cursor)
    assert len(pg_rows) == 1

    # nothing in ydb
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    ydb_rows = cursor[0].rows
    assert not ydb_rows


@pytest.mark.experiments3(filename='migrate_to_ydb.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_single.yaml'],
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data.sql'])
async def test_migrate_to_ydb_pg_yt_history(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    @testpoint('ProcessingNgQueue::DoProcessingIteration::MigrationPath')
    def fetch_migration_path(data):
        assert data['migration_path'] == 'kMigrantRestoredQueueInPG'

    queue = processing.testsuite.foo
    item_id = '14648896842964516938'

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'regular'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    events = await queue.events(item_id)
    assert events['events']

    assert fetch_migration_path.times_called > 0

    # two events in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute(
        'SELECT event_id FROM processing.events '
        'ORDER BY handling_order_key ASC, order_key ASC',
    )
    pg_rows = list(cursor)
    assert len(pg_rows) == 3
    assert pg_rows[0][0] == '961efda8b0ae413d8d646a1a8e451385'
    assert pg_rows[1][0] == '961efda8b0ae413d8d646a1a8e451386'
    assert pg_rows[2][0] == event_id

    # no events in ydb
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    ydb_rows = cursor[0].rows
    assert not ydb_rows


@pytest.mark.experiments3(filename='migrate_to_ydb.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_single.yaml'],
)
async def test_migrate_to_ydb_yt_ydb_history(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    ydb_query = """
        --!syntax_v1
        INSERT INTO `events` (
            scope,
            queue,
            item_id,
            event_id,
            order_key,
            created,
            payload_v2,
            idempotency_token,
            need_handle,
            updated,
            due,
            need_start
        )
        VALUES(
            JUST('testsuite'),
            JUST('foo'),
            JUST('14648896842964516938'),
            JUST('abcdef000002'),
            1,
            JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
            '{"kind": "regular"}',
            JUST('idempotency_token_2'),
            JUST(TRUE),
            JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
            JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
            JUST(TRUE)
        );
    """
    ydb.execute(ydb_query)

    @testpoint('ProcessingNgQueue::DoProcessingIteration::MigrationPath')
    def fetch_migration_path(data):
        assert data['migration_path'] == 'kMigrantRestoredQueueInYDB'

    queue = processing.testsuite.foo
    item_id = '14648896842964516938'

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'regular'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    events = await queue.events(item_id)
    assert events['events']

    assert fetch_migration_path.times_called > 0

    # no events in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    pg_rows = list(cursor)
    assert not pg_rows

    # two events in ydb
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    ydb_rows = cursor[0].rows
    assert len(ydb_rows) == 3


@pytest.mark.experiments3(filename='migrate_to_ydb.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
async def test_migrate_to_ydb_ydb_history(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    ydb_query = """
        --!syntax_v1
        INSERT INTO `events` (
            scope,
            queue,
            item_id,
            event_id,
            order_key,
            created,
            payload_v2,
            idempotency_token,
            need_handle,
            updated,
            due,
            need_start
        )
        VALUES(
            JUST('testsuite'),
            JUST('foo'),
            JUST('0123456789'),
            JUST('abcdef000002'),
            1,
            JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
            '{"kind": "create"}',
            JUST('idempotency_token_2'),
            JUST(TRUE),
            JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
            JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
            JUST(TRUE)
        );
    """
    ydb.execute(ydb_query)

    @testpoint('ProcessingNgQueue::DoProcessingIteration::MigrationPath')
    def fetch_migration_path(data):
        assert data['migration_path'] == 'kMigrantQueueInYDB'

    queue = processing.testsuite.foo
    item_id = '0123456789'

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'regular'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    events = await queue.events(item_id)
    assert events['events']

    assert fetch_migration_path.times_called > 0

    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}" '
        'ORDER BY handling_order_key ASC, order_key ASC'.format(
            db_name, item_id,
        ),
    )
    assert len(cursor) == 1
    rows = cursor[0].rows
    assert len(rows) == 2

    assert rows[0]['item_id'].decode('utf-8') == item_id
    assert rows[0]['event_id'].decode('utf-8') == 'abcdef000002'
    json_payload = json.loads(rows[0]['payload_v2'].decode())
    assert json_payload['kind'] == 'create'

    assert rows[1]['item_id'].decode('utf-8') == item_id
    assert rows[1]['event_id'].decode('utf-8') == event_id
    json_payload = json.loads(rows[1]['payload_v2'])
    assert json_payload['kind'] == 'regular'


@pytest.mark.experiments3(filename='migrate_to_ydb.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
async def test_migrate_to_ydb_no_history(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    @testpoint('FetchQueueEventsFromYt')
    def fetch_from_yt_tp(data):
        return

    @testpoint('ProcessingNgQueue::DoProcessingIteration::MigrationPath')
    def fetch_migration_path(data):
        assert data['migration_path'] == 'kMigrantQueueInYDB'

    queue = processing.testsuite.foo
    item_id = '123'

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'create'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    events = await queue.events(item_id)
    assert events['events']

    assert fetch_from_yt_tp.times_called == 0
    assert fetch_migration_path.times_called > 0

    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    row = cursor[0].rows[0]
    assert row['item_id'].decode('utf-8') == item_id
    assert row['event_id'].decode('utf-8') == event_id
    json_payload = json.loads(row['payload_v2'])
    assert json_payload['kind'] == 'create'


@pytest.mark.experiments3(filename='migrate_to_ydb.json')
@pytest.mark.pgsql('processing_db', files=['pg_events.sql'])
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
async def test_migrate_to_ydb_pg_history(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    @testpoint('ProcessingNgQueue::DoProcessingIteration::MigrationPath')
    def fetch_migration_path(data):
        assert data['migration_path'] == 'kMigrantQueueInPG'

    queue = processing.testsuite.foo
    item_id = '0123456789'

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'regular'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    events = await queue.events(item_id)
    assert events['events']

    assert fetch_migration_path.times_called > 0

    # two events in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    pg_rows = list(cursor)
    assert len(pg_rows) == 2

    # nothing in ydb
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    ydb_rows = cursor[0].rows
    assert not ydb_rows


@pytest.mark.experiments3(filename='migrate_to_ydb.json')
@pytest.mark.processing_queue_config(
    'happy-queue.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_single.yaml'],
)
async def test_migrate_to_ydb_yt_history(
        processing, stq, testpoint, pgsql, mocked_time, yt_apply, ydb,
):
    @testpoint('ProcessingNgQueue::DoProcessingIteration::MigrationPath')
    def fetch_migration_path(data):
        assert data['migration_path'] == 'kMigrantRestoredQueueInYDB'

    queue = processing.testsuite.foo
    item_id = '14648896842964516938'

    event_id = await queue.send_event(
        item_id=item_id,
        payload={'kind': 'regular'},
        idempotency_token='idempotency_token',
    )
    assert event_id

    events = await queue.events(item_id)
    assert events['events']

    assert fetch_migration_path.times_called > 0

    # no events in pg
    cursor = pgsql['processing_db'].cursor()
    cursor.execute('SELECT * FROM processing.events')
    pg_rows = list(cursor)
    assert not pg_rows

    # two events in ydb
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )
    assert len(cursor) == 1
    ydb_rows = cursor[0].rows
    assert len(ydb_rows) == 2
