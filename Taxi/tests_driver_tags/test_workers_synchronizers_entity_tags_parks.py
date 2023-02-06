import datetime

import psycopg2
import pytest

from tests_driver_tags import queries

# For catching distlocked periodic task
@pytest.fixture(name='testpoint_entity_tags_parks_synchronizer')
def _testpoint_entity_tags_parks_synchronizer(testpoint):
    class Context:
        @staticmethod
        @testpoint('entity-tags-parks-synchronizer-finished')
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
    DRIVER_TAGS_ENTITY_TAGS_PARKS_SYNCHRONIZER={
        'enabled': False,
        'changes_limit': 100,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_disabled(
        taxi_driver_tags,
        testpoint_entity_tags_parks_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-parks-synchronizer'):
        await testpoint_entity_tags_parks_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 0

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    assert list(cursor) == []
    cursor.execute('SELECT * FROM contractors.processing_queue')
    assert list(cursor) == []


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_PARKS_SYNCHRONIZER={
        'enabled': True,
        'changes_limit': 100,
        'store_batch_size': 3,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.tags_v1_entity_index(
    entity_tags_list=[
        ('park', 'dbid1', 1),
        ('park', 'dbid2', 2),
        ('park', 'dbid9999', 3),
    ],
    last_processed_revision=3,
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        'INSERT INTO contractors.profiles (park_id, profile_id) VALUES '
        + ','.join(
            [
                '(\'dbid{}\', \'uuid{}\')'.format(
                    str((index % 3) + 1), str(index),
                )
                for index in range(1, 15)
            ],
        ),
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_park_changes(
        taxi_driver_tags,
        testpoint_entity_tags_parks_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-parks-synchronizer'):
        await testpoint_entity_tags_parks_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 1

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    # not all updated profiles exist in our db, but revision must be highest
    assert list(cursor) == [
        ('entity-tags-parks', '3'),
        ('entity-tags-parks-state', ''),
    ]
    cursor.execute(
        """
        SELECT park_id, profile_id, source_event_timestamp
        FROM contractors.processing_queue as p
        INNER JOIN contractors.profiles as n ON p.contractor_id = n.id
        ORDER BY n.id
        """,
    )
    assert list(cursor) == [
        (
            'dbid' + str((index % 3) + 1),
            'uuid' + str(index),
            rev_to_ts((index % 3) + 1),
        )
        for index in range(1, 15)
        if index % 3 in [0, 1]
    ]


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_PARKS_SYNCHRONIZER={
        'enabled': True,
        'changes_limit': 100,
        'store_batch_size': 3,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.tags_v1_entity_index(
    entity_tags_list=[], last_processed_revision=7,
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        'INSERT INTO contractors.profiles (park_id, profile_id) VALUES '
        + ','.join(
            [
                '(\'dbid{}\', \'uuid{}\')'.format(
                    str((index % 3) + 1), str(index),
                )
                for index in range(1, 15)
            ],
        ),
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_no_park_changes(
        taxi_driver_tags,
        testpoint_entity_tags_parks_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-parks-synchronizer'):
        await testpoint_entity_tags_parks_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 1

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    # no parks got updated, but revision should've been
    assert list(cursor) == [('entity-tags-parks', '7')]
    cursor.execute(
        """SELECT park_id, profile_id FROM contractors.processing_queue as p
           INNER JOIN contractors.profiles as n ON p.contractor_id = n.id
           ORDER BY n.id""",
    )
    assert list(cursor) == []


@pytest.mark.config(
    DRIVER_TAGS_ENTITY_TAGS_PARKS_SYNCHRONIZER={
        'enabled': True,
        'changes_limit': 100,
        'store_batch_size': 3,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.tags_v1_entity_index(
    entity_tags_list=[('park', 'dbid1', 28), ('park', 'dbid2', 64)],
    last_processed_revision=99,
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles (id, park_id, profile_id)
        VALUES (1, 'dbid1', 'uuid1'),
               (2, 'dbid1', 'uuid2'),
               (3, 'dbid1', 'uuid3'),
               (4, 'dbid1', 'uuid4'),
               (5, 'dbid2', 'uuid1'),
               (6, 'dbid2', 'uuid2')
        """,
        """
        INSERT INTO state.revisions(target, revision)
        VALUES ('entity-tags-parks', '28'),
               ('entity-tags-parks-state', 'dbid1__2__28')
        """,
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_park_changes_with_initial_state(
        taxi_driver_tags,
        testpoint_entity_tags_parks_synchronizer,
        pgsql,
        tags_mocks,
):
    async with taxi_driver_tags.spawn_task('entity-tags-parks-synchronizer'):
        await testpoint_entity_tags_parks_synchronizer.finished.wait_call()

    assert tags_mocks.has_calls() == 1

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    # not all updated profiles exist in our db, but revision must be highest
    assert list(cursor) == [
        ('entity-tags-parks', '64'),  # only processed revisions are stored
        ('entity-tags-parks-state', ''),
    ]
    cursor.execute(
        """
        SELECT id, park_id, profile_id, source_event_timestamp
        FROM contractors.processing_queue as p
        INNER JOIN contractors.profiles as n ON p.contractor_id = n.id
        ORDER BY n.id
        """,
    )
    assert list(cursor) == [
        (3, 'dbid1', 'uuid3', rev_to_ts(28)),
        (4, 'dbid1', 'uuid4', rev_to_ts(28)),
        (5, 'dbid2', 'uuid1', rev_to_ts(64)),
        (6, 'dbid2', 'uuid2', rev_to_ts(64)),
    ]
