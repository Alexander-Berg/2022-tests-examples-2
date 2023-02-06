from collections import defaultdict  # pylint: disable=C5521
import datetime

import psycopg2
import pytest

from tests_driver_tags import queries

# For catching distlocked periodic task
@pytest.fixture(name='testpoint_contractor_processor')
def _testpoint_contractor_processor(testpoint):
    class Context:
        @staticmethod
        @testpoint('contractor-processor-finished')
        def finished(data):
            pass

    return Context()


DUMMY_STREAM = {
    'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
    'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
}


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.config(
    DRIVER_TAGS_CONTRACTOR_PROCESSOR={
        'enabled': True,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
)
async def test_empty(taxi_driver_tags, testpoint_contractor_processor, pgsql):
    # does nothing due to empty db
    async with taxi_driver_tags.spawn_task('contractor-processor'):
        await testpoint_contractor_processor.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_CONTRACTOR_IDS_FROM_QUEUE)
    assert [] == list(cursor)


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
            (id, park_id, profile_id, unique_driver_id)
        VALUES (1498, 'dbid1', 'uuid1', 'udid4'),
               (4492, 'dbid3', 'uuid1', 'udid1')
        """,
        """
        INSERT INTO contractors.processing_queue (contractor_id) VALUES (1498)
        """,
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_CONTRACTOR_PROCESSOR={
        'enabled': False,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
)
async def test_disabled(
        taxi_driver_tags, testpoint_contractor_processor, pgsql,
):
    async with taxi_driver_tags.spawn_task('contractor-processor'):
        await testpoint_contractor_processor.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_CONTRACTOR_IDS_FROM_QUEUE)
    assert [(1498,)] == list(cursor)


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
            (id, park_id, profile_id, unique_driver_id)
        VALUES (1498, 'dbid1', 'uuid1', 'udid4'),
               (4492, 'dbid3', 'uuid1', 'udid1')
        """,
        """
        INSERT INTO contractors.processing_queue (contractor_id)
        VALUES (1498), (34543)
        """,
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_CONTRACTOR_PROCESSOR={
        'enabled': True,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
)
async def test_no_tags(
        taxi_driver_tags, testpoint_contractor_processor, pgsql,
):
    async with taxi_driver_tags.spawn_task('contractor-processor'):
        await testpoint_contractor_processor.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_CONTRACTOR_IDS_FROM_QUEUE)
    assert [] == list(cursor)


@pytest.mark.match_tags(
    entity_type='park',
    entity_value='dbid1',
    entity_tags_info={
        'tag0': {'topics': ['priority']},
        'tag1': {'topics': ['simple']},
        'stag0': {'topics': ['subventions']},
    },
)
@pytest.mark.match_tags(
    entity_type='dbid_uuid',
    entity_value='dbid1_uuid1',
    entity_tags_info={
        'tag2': {'topics': ['priority']},
        'tag3': {'topics': ['topic1']},
    },
)
@pytest.mark.match_tags(
    entity_type='udid',
    entity_value='udid1',
    entity_tags_info={
        'tag4': {'topics': ['priority']},
        'stag1': {'topics': ['subventions']},
    },
)
@pytest.mark.match_tags(
    entity_type='udid',
    entity_value='udid2',
    entity_tags_info={
        'tag9': {'topics': ['missing']},
        'mtag0': {'topics': ['priority', 'subventions']},
    },
)
@pytest.mark.match_tags(
    entity_type='park_car_id',
    entity_value='dbid3_car3',
    entity_tags_info={'tag5': {'topics': ['priority']}},
)
@pytest.mark.match_tags(
    entity_type='park_car_id',
    entity_value='dbid1_car1',
    entity_tags_info={'tag8': {'topics': ['wrong']}},
)
@pytest.mark.match_tags(
    entity_type='park_car_id',
    entity_value='dbid1_car9',
    entity_tags_info={'stag2': {'topics': ['subventions']}},
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
            (id, park_id, profile_id, unique_driver_id, car_id)
        VALUES (1498, 'dbid1', 'uuid1', 'udid1', 'car1'),
               (2391, 'dbid2', 'uuid6', 'udid9', 'car9'),
               (3421, 'dbid1', 'uuid2', 'udid2', 'car2'),
               (4492, 'dbid3', 'uuid3', 'udid3', 'car3')
        """,
        """
        INSERT INTO contractors.processing_queue
            (contractor_id, source_event_timestamp)
        VALUES
            (1498, NULL),
            (2391, '2022-01-21 10:10:10+03'),
            (3421, '2022-01-21 10:10:10+03'),
            (4492, '2022-01-22 10:10:10+03'),
            (34543, NULL) -- non-existing one
        """,
        """
        INSERT INTO tags.snapshots_processing_queue
            (revision, contractor_id, topic_id, is_empty)
        VALUES (9999, 1498, 1, FALSE), (9998, 2391, 1, FALSE)
        """,
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_CONTRACTOR_PROCESSOR={
        'enabled': True,
        'process_batch_size': 200,
        'request_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
async def test_base(taxi_driver_tags, testpoint_contractor_processor, pgsql):
    async with taxi_driver_tags.spawn_task('contractor-processor'):
        await testpoint_contractor_processor.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_CONTRACTOR_IDS_FROM_QUEUE)
    assert [] == list(cursor)

    cursor.execute(
        """
        SELECT contractor_id, topic_id, source_event_timestamp, is_empty
        FROM tags.snapshots_processing_queue
        ORDER BY contractor_id, topic_id
        """,
    )
    mytz = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    ts1 = datetime.datetime(2022, 1, 21, 10, 10, 10, tzinfo=mytz)
    ts2 = ts1 + datetime.timedelta(days=1)
    assert sorted(list(cursor)) == [
        (1498, 1, None, False),
        (1498, 2, None, False),
        (2391, 1, ts1, True),  # ensure is_empty overriden
        (2391, 2, ts1, True),
        (3421, 1, ts1, False),
        (3421, 2, ts1, False),
        (4492, 1, ts2, False),
        (4492, 2, ts2, True),
    ]
    cursor.execute(
        """SELECT revision FROM tags.snapshots_processing_queue
            WHERE contractor_id = 1498 AND topic_id = 1
        """,
    )
    # ensure revision changed
    assert list(cursor)[0][0] != 9999

    cursor.execute('SELECT id, name FROM tags.names ORDER BY name')
    mapping = {k: v for k, v in cursor}
    assert sorted(mapping.values()) == [
        'mtag0',
        'stag0',
        'stag1',
        'tag0',
        'tag2',
        'tag4',
        'tag5',
    ]

    cursor.execute(
        'SELECT contractor_id, topic_id, tag_ids FROM tags.snapshots',
    )
    rows = list(cursor)
    # ensure snapshots only from watched topics are in db
    assert len([row for row in rows if row[1] in [1, 2]]) == len(rows)

    result = defaultdict(lambda: defaultdict(list))
    for row in rows:
        result[row[1]][row[0]] = sorted([mapping[tag] for tag in row[2]])

    assert result == defaultdict(
        lambda: defaultdict(list),
        {
            1: defaultdict(
                list,
                {
                    1498: ['tag0', 'tag2', 'tag4'],
                    3421: ['mtag0', 'tag0'],
                    4492: ['tag5'],
                },
            ),
            2: defaultdict(
                list, {1498: ['stag0', 'stag1'], 3421: ['mtag0', 'stag0']},
            ),
        },
    )
