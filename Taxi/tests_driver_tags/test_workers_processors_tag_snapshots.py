from collections import defaultdict  # pylint: disable=C5521
import datetime
import json

import psycopg2
import pytest

SNAPSHOTS_PROCESSOR = 'tag-snapshots-processor'
SNAPSHOTS_PROCESSOR_SUBVENTIONS = 'tag-snapshots-processor-subventions'

# For catching distlocked periodic task
@pytest.fixture(name='testpoint_tag_snapshots')
def _testpoint_tag_snapshots(testpoint):
    class Context:
        @staticmethod
        @testpoint('tag-snapshots-processor-finished')
        def finished(data):
            pass

        @staticmethod
        @testpoint('tag-snapshots-processor-subventions-finished')
        def subventions_finished(data):
            pass

    return Context()


DUMMY_STREAM = {
    'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
    'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
}


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles (id, park_id, profile_id)
        VALUES (1, 'dbid1', 'uuid1')
        """,
        """
        INSERT INTO tags.snapshots_processing_queue
            (revision, contractor_id, topic_id)
        VALUES (1, 1, 1)
        """,
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_TAG_SNAPSHOTS_PROCESSOR={
        'enabled': False,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
)
async def test_disabled(taxi_driver_tags, testpoint_tag_snapshots, pgsql):
    async with taxi_driver_tags.spawn_task(SNAPSHOTS_PROCESSOR):
        await testpoint_tag_snapshots.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute('SELECT revision FROM tags.snapshots_processing_queue')
    assert [(1,)] == list(cursor)


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.config(
    DRIVER_TAGS_TAG_SNAPSHOTS_PROCESSOR={
        'enabled': True,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
)
async def test_empty(taxi_driver_tags, testpoint_tag_snapshots, pgsql):
    # does nothing due to empty db
    async with taxi_driver_tags.spawn_task(SNAPSHOTS_PROCESSOR):
        await testpoint_tag_snapshots.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute('SELECT contractor_id FROM contractors.processing_queue')
    assert [] == list(cursor)


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
            (id, park_id, profile_id)
        VALUES
            -- single topic
            (1, 'dbid1', 'uuid1'), -- only one new snapshot
            (2, 'dbid2', 'uuid2'), -- two, old and new (full diff)
            (3, 'dbid3', 'uuid3'), -- two, old and new (added)
            (4, 'dbid4', 'uuid4'), -- two, old and new (removed)
            (5, 'dbid5', 'uuid5'), -- three, one must be skipped
            (6, 'dbid6', 'uuid6'), -- three, w/ zerodiff
            (7, 'dbid7', 'uuid7'), -- has unwatched topic

            -- multiple topics
            (8, 'dbid8', 'uuid8'), -- both topics have updates
            (9, 'dbid9', 'uuid9'), -- only one topic has updates

            -- is_empty=True snapshot cases
            (10, 'dbid10', 'uuid10'), -- no olds
            (11, 'dbid11', 'uuid11'), -- old empty
            (12, 'dbid12', 'uuid12')  -- old filled
        """,
        """
        INSERT INTO tags.names (id, name)
        VALUES (1, 'tag1'), (2, 'tag2'), (3, 'tag3'), (4, 't4'), (5, 't5'),
               (6, 'stag0'), (7, 'stag1')
        """,
        """
        INSERT INTO tags.snapshots (id,  contractor_id, topic_id, tag_ids)
        VALUES (1, 1, 1, '{1}'),

               (2, 2, 1, '{2}'),
               (3, 2, 1, '{1}'),

               (4, 3, 1, '{2}'),
               (5, 3, 1, '{1, 2}'),

               (6, 4, 1, '{2, 3}'),
               (7, 4, 1, '{3}'),

               (8,  5, 1, '{3}'),
               (9,  5, 1, '{1}'),
               (10, 5, 1, '{2}'),

               (11, 6, 1, '{2}'),
               (12, 6, 1, '{1, 3}'),
               (13, 6, 1, '{2}'),

               (14, 7, 99, '{4}'),
               (15, 7, 99, '{5}'),

               (16, 8, 1, '{2}'),
               (17, 8, 1, '{4, 5}'),
               (18, 8, 2, '{6}'),
               (19, 8, 2, '{7}'),

               (20, 9, 1, '{1, 3}'),
               (21, 9, 1, '{3}'),
               (22, 9, 2, '{6}'),

               (23, 11, 1, '{}'),
               (24, 12, 1, '{1, 3}')
        """,
        """
INSERT INTO tags.snapshots_processing_queue
(revision, contractor_id, topic_id, source_event_timestamp)
VALUES
-- single topic
(1, 1, 1, '2022-01-21 10:10:10+03'), -- produce event without old_tags
(2, 2, 1, '2022-01-22 10:10:10+03'), -- base case, produce event
(3, 3, 1, NULL),                     -- base case, produce event
(4, 4, 1, '2022-01-22 10:10:10+03'), -- base case, produce event
(5, 5, 1, NULL),                     -- base case, produce event
(6, 6, 1, '2022-01-21 10:10:10+03'), -- no event due to zerodiff
(7, 99, 1, NULL),                    -- no event due to non-existing contractor
(8, 7, 99, '2022-01-21 10:10:10+03'), -- no event due to non-watched topic

-- multi topic
(9, 8, 1, '2022-01-21 10:10:10+03'), -- two topics updated, produce event
(10, 8, 2, '2022-01-21 10:10:10+03'), -- two topics updated, produce event
(11, 9, 1, '2022-01-22 10:10:10+03') -- only one topic updated, produce event
        """,
        """
INSERT INTO tags.snapshots_processing_queue
(revision, contractor_id, topic_id, source_event_timestamp, is_empty)
VALUES
--is_empty=True
(12, 10, 1, '2022-01-21 10:10:10+03', True), -- no old, no event
(13, 11, 1, '2022-01-21 10:10:10+03', True), -- old empty, no event
(14, 12, 1, '2022-01-21 10:10:10+03', True)  -- old filled, produce event
        """,
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_TAG_SNAPSHOTS_PROCESSOR={
        'enabled': True,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
)
async def test_base(
        taxi_driver_tags, testpoint_tag_snapshots, testpoint, pgsql,
):
    events = []

    @testpoint('logbroker_publish')
    def commit(data):
        events.append({'data': json.loads(data['data']), 'name': data['name']})

    async with taxi_driver_tags.spawn_task(SNAPSHOTS_PROCESSOR):
        await testpoint_tag_snapshots.finished.wait_call()
    async with taxi_driver_tags.spawn_task(SNAPSHOTS_PROCESSOR_SUBVENTIONS):
        await testpoint_tag_snapshots.subventions_finished.wait_call()

    assert commit.times_called == 9

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(
        'SELECT contractor_id, topic_id FROM tags.snapshots_processing_queue',
    )

    # this is unwatched topic, so it will be in db
    assert [(7, 99)] == list(cursor)

    cursor.execute('SELECT id, name FROM tags.names ORDER BY name')
    mapping = {k: v for k, v in cursor}
    assert ['stag0', 'stag1', 't4', 't5', 'tag1', 'tag2', 'tag3'] == sorted(
        mapping.values(),
    )

    cursor.execute(
        'SELECT contractor_id, topic_id, tag_ids FROM tags.snapshots',
    )
    rows = list(cursor)
    # db has 2 snapshots for unwatched topic
    assert len([row for row in rows if row[1] in [1, 2]]) == len(rows) - 2

    result = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row[1] in [1, 2]:
            result[row[1]][row[0]] = sorted([mapping[tag] for tag in row[2]])

    # make sure we have unique keys and no duplicates in db
    assert sum([len(v) for v in result.values()]) == len(rows) - 2

    assert result == defaultdict(
        lambda: defaultdict(list),
        {
            1: defaultdict(
                list,
                {
                    1: ['tag1'],
                    2: ['tag1'],
                    3: ['tag1', 'tag2'],
                    4: ['tag3'],
                    5: ['tag2'],
                    6: ['tag2'],
                    8: ['t4', 't5'],
                    9: ['tag3'],
                },
            ),
            2: defaultdict(list, {8: ['stag1'], 9: ['stag0']}),
        },
    )

    mytz = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    ts1 = datetime.datetime(2022, 1, 21, 10, 10, 10, tzinfo=mytz)
    ts2 = ts1 + datetime.timedelta(days=1)
    assert events == [
        {
            'data': {
                'topic': 'priority',
                'park_id': 'dbid1',
                'profile_id': 'uuid1',
                'old_tags': [],
                'new_tags': ['tag1'],
                'source_timestamp': ts1.timestamp() * 1000,
            },
            'name': 'tag-events',
        },
        {
            'data': {
                'topic': 'priority',
                'park_id': 'dbid2',
                'profile_id': 'uuid2',
                'old_tags': ['tag2'],
                'new_tags': ['tag1'],
                'source_timestamp': ts2.timestamp() * 1000,
            },
            'name': 'tag-events',
        },
        {
            'data': {
                'topic': 'priority',
                'park_id': 'dbid3',
                'profile_id': 'uuid3',
                'old_tags': ['tag2'],
                'new_tags': ['tag1', 'tag2'],
            },
            'name': 'tag-events',
        },
        {
            'data': {
                'topic': 'priority',
                'park_id': 'dbid4',
                'profile_id': 'uuid4',
                'old_tags': ['tag2', 'tag3'],
                'new_tags': ['tag3'],
                'source_timestamp': ts2.timestamp() * 1000,
            },
            'name': 'tag-events',
        },
        {
            'data': {
                'topic': 'priority',
                'park_id': 'dbid5',
                'profile_id': 'uuid5',
                'old_tags': ['tag3'],
                'new_tags': ['tag2'],
            },
            'name': 'tag-events',
        },
        {
            'data': {
                'new_tags': ['t4', 't5'],
                'old_tags': ['tag2'],
                'park_id': 'dbid8',
                'profile_id': 'uuid8',
                'source_timestamp': ts1.timestamp() * 1000,
                'topic': 'priority',
            },
            'name': 'tag-events',
        },
        {
            'data': {
                'new_tags': ['tag3'],
                'old_tags': ['tag1', 'tag3'],
                'park_id': 'dbid9',
                'profile_id': 'uuid9',
                'source_timestamp': ts2.timestamp() * 1000,
                'topic': 'priority',
            },
            'name': 'tag-events',
        },
        {
            'data': {
                'new_tags': [],
                'old_tags': ['tag1', 'tag3'],
                'park_id': 'dbid12',
                'profile_id': 'uuid12',
                'source_timestamp': ts1.timestamp() * 1000,
                'topic': 'priority',
            },
            'name': 'tag-events',
        },
        {
            'data': {
                'new_tags': ['stag1'],
                'old_tags': ['stag0'],
                'park_id': 'dbid8',
                'profile_id': 'uuid8',
                'source_timestamp': ts1.timestamp() * 1000,
                'topic': 'subventions',
            },
            'name': 'tag-events-subventions',
        },
    ]
