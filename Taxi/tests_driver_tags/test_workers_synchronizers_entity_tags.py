import datetime

import psycopg2
import pytest

from tests_driver_tags import queries

# For catching distlocked periodic task
@pytest.fixture(name='testpoint_entity_tags_synchronizer')
def _testpoint_entity_tags_synchronizer(testpoint):
    class Context:
        @staticmethod
        @testpoint('entity-tags-synchronizer-finished')
        def finished(data):
            pass

    return Context()


DUMMY_STREAM = {
    'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
    'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
}


def rev_to_ts(rev):
    return datetime.datetime(
        1970,
        1,
        1,
        3,
        0,
        0,
        rev * 1000,
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
    )


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_SYNCHRONIZER={
        'enabled': False,
        'changes_limit': 100,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_disabled(
        taxi_driver_tags,
        testpoint_entity_tags_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-synchronizer'):
        await testpoint_entity_tags_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 0

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    assert list(cursor) == []
    cursor.execute('SELECT * FROM contractors.processing_queue')
    assert list(cursor) == []


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_SYNCHRONIZER={
        'enabled': True,
        'changes_limit': 100,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.tags_v1_entity_index(
    entity_tags_list=[
        ('park_car_id', 'dbid' + str(index) + '_car' + str(index), index)
        for index in range(1, 14)
    ],
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        'INSERT INTO contractors.profiles(park_id, profile_id, car_id) VALUES '
        + ','.join(
            [
                '(\'dbid{}\', \'uuid{}\', \'car{}\')'.format(
                    str(index % 8), str(index), str(index % 16),
                )
                for index in range(1, 24)
            ],
        ),
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_park_car_id_changes(
        taxi_driver_tags,
        testpoint_entity_tags_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-synchronizer'):
        await testpoint_entity_tags_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 1

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    # not all updated profiles exist in our db, but revision must be highest
    assert list(cursor) == [('entity-tags', '13')]
    cursor.execute(
        """SELECT park_id, profile_id, car_id, source_event_timestamp
           FROM contractors.processing_queue as p
           INNER JOIN contractors.profiles as n ON p.contractor_id = n.id
           ORDER BY n.id""",
    )
    assert list(cursor) == [
        (
            'dbid' + str(index % 8),
            'uuid' + str(index),
            'car' + str(index % 16),
            rev_to_ts(index % 8),
        )
        for index in range(1, 24)
        if index < 8 or index > 16
    ]


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_SYNCHRONIZER={
        'enabled': True,
        'changes_limit': 100,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.tags_v1_entity_index(
    entity_tags_list=[('udid', 'udid1', 1), ('udid', 'udid2', 4)],
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
               (park_id, profile_id, unique_driver_id)
        VALUES ('dbid1', 'uuid1', 'udid1'),
               ('dbid2', 'uuid2', 'udid2'),
               ('dbid3', 'uuid3', 'udid3'),
               ('dbid4', 'uuid4', 'udid1'),
               ('dbid5', 'uuid5', 'udid2'),
               ('dbid6', 'uuid6', 'udid3')
        """,
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_udid_changes(
        taxi_driver_tags,
        testpoint_entity_tags_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-synchronizer'):
        await testpoint_entity_tags_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 1

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    # not all updated profiles exist in our db, but revision must be highest
    assert list(cursor) == [('entity-tags', '4')]
    cursor.execute(
        """SELECT park_id, profile_id, unique_driver_id, source_event_timestamp
           FROM contractors.processing_queue as p
           INNER JOIN contractors.profiles as n ON p.contractor_id = n.id
           ORDER BY n.id""",
    )
    assert list(cursor) == [
        ('dbid1', 'uuid1', 'udid1', rev_to_ts(1)),
        ('dbid2', 'uuid2', 'udid2', rev_to_ts(4)),
        ('dbid4', 'uuid4', 'udid1', rev_to_ts(1)),
        ('dbid5', 'uuid5', 'udid2', rev_to_ts(4)),
    ]


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_SYNCHRONIZER={
        'enabled': True,
        'changes_limit': 100,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.tags_v1_entity_index(
    entity_tags_list=[
        ('udid', 'udid1', 1),
        ('park', 'dbid1', 2),
        ('park_car_id', 'dbid1_car2', 3),
        ('park_car_id', 'dbid2_car2', 4),
        ('udid', 'udid4', 5),
    ],
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """INSERT INTO contractors.profiles
        (park_id, profile_id, unique_driver_id, car_id) VALUES
        ('dbid1', 'uuid1', 'udid1', 'car1'),
        ('dbid1', 'uuid2', 'udid2', 'car2'),
        ('dbid2', 'uuid3', 'udid2', 'car2'),
        ('dbid2', 'uuid4', 'udid3', 'car3'),
        ('dbid2', 'uuid5', 'udid3', 'car4'),
        ('dbid3', 'uuid6', 'udid3', 'car5'),
        ('dbid3', 'uuid7', 'udid1', 'car6'),
        ('dbid3', 'uuid8', 'udid1', 'car7'),
        ('dbid3', 'uuid9', 'udid4', 'car8')
        """,
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_mixed_changes(
        taxi_driver_tags,
        testpoint_entity_tags_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-synchronizer'):
        await testpoint_entity_tags_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 1

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    # not all updated profiles exist in our db, but revision must be highest
    assert list(cursor) == [('entity-tags', '5')]
    cursor.execute(
        """SELECT park_id, profile_id, unique_driver_id, car_id, source_event_timestamp
           FROM contractors.processing_queue as p
           INNER JOIN contractors.profiles as n ON p.contractor_id = n.id
           ORDER BY n.id""",
    )
    assert list(cursor) == [
        ('dbid1', 'uuid1', 'udid1', 'car1', rev_to_ts(1)),
        ('dbid1', 'uuid2', 'udid2', 'car2', rev_to_ts(3)),
        ('dbid2', 'uuid3', 'udid2', 'car2', rev_to_ts(4)),
        ('dbid3', 'uuid7', 'udid1', 'car6', rev_to_ts(1)),
        ('dbid3', 'uuid8', 'udid1', 'car7', rev_to_ts(1)),
        ('dbid3', 'uuid9', 'udid4', 'car8', rev_to_ts(5)),
    ]


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_SYNCHRONIZER={
        'enabled': True,
        'changes_limit': 1,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.tags_v1_entity_index(
    entity_tags_list=[
        ('udid', 'udid' + str(index), index) for index in range(1, 6)
    ],
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """INSERT INTO contractors.profiles
        (park_id, profile_id, unique_driver_id) VALUES """
        + ','.join(
            [
                '(\'dbid{x}\', \'uuid{x}\', \'udid{y}\')'.format(
                    x=str(index), y=str(index % 7),
                )
                for index in range(1, 29, 2)
            ],
        ),
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_small_changes_limit(
        taxi_driver_tags,
        testpoint_entity_tags_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-synchronizer'):
        await testpoint_entity_tags_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 1

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    # not all updated profiles exist in our db, but revision must be highest
    assert list(cursor) == [('entity-tags', '1')]
    cursor.execute(
        """SELECT park_id, profile_id, unique_driver_id, source_event_timestamp
           FROM contractors.processing_queue as p
           INNER JOIN contractors.profiles as n ON p.contractor_id = n.id
           ORDER BY n.id""",
    )
    assert list(cursor) == [
        (
            'dbid' + str(index),
            'uuid' + str(index),
            'udid' + str(index % 7),
            rev_to_ts(index % 7),
        )
        for index in range(1, 28, 2)
        if index % 7 == 1
    ]


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_SYNCHRONIZER={
        'enabled': True,
        'changes_limit': 1,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.tags_v1_entity_index(
    entity_tags_list=[], last_processed_revision=7,
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """INSERT INTO contractors.profiles
        (park_id, profile_id, unique_driver_id) VALUES """
        + ','.join(
            [
                '(\'dbid{x}\', \'uuid{x}\', \'udid{y}\')'.format(
                    x=str(index), y=str(index % 7),
                )
                for index in range(1, 29, 2)
            ],
        ),
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_no_changes_with_updated_revision(
        taxi_driver_tags,
        testpoint_entity_tags_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-synchronizer'):
        await testpoint_entity_tags_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 1

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    # no profiles got updated, but revision should've been
    assert list(cursor) == [('entity-tags', '7')]
    cursor.execute(
        """SELECT park_id, profile_id, unique_driver_id
           FROM contractors.processing_queue as p
           INNER JOIN contractors.profiles as n ON p.contractor_id = n.id
           ORDER BY n.id""",
    )
    assert list(cursor) == []
