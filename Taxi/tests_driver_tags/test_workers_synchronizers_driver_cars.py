import datetime

import psycopg2
import pytest

from tests_driver_tags import queries

GET_QUEUE_PROFILES = """
    SELECT park_id, profile_id, source_event_timestamp
    FROM contractors.processing_queue as q
    LEFT JOIN contractors.profiles as p
        ON q.contractor_id = p.id
    ORDER BY q.contractor_id
    """

# For catching distlocked periodic task
@pytest.fixture(name='testpoint_driver_cars_synchronizer')
def _testpoint_driver_cars_synchronizer(testpoint):
    class Context:
        @staticmethod
        @testpoint('driver-cars-synchronizer-finished')
        def finished(data):
            pass

    return Context()


DUMMY_STREAM = {
    'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
    'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
}


@pytest.mark.config(
    DRIVER_TAGS_DRIVER_CARS_SYNCHRONIZER={
        'enabled': False,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_disabled(
        taxi_driver_tags, testpoint_driver_cars_synchronizer, pgsql,
):
    async with taxi_driver_tags.spawn_task('driver-cars-synchronizer'):
        await testpoint_driver_cars_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute('SELECT * FROM state.revisions')
    assert list(cursor) == []
    cursor.execute('SELECT * FROM contractors.profiles')
    assert list(cursor) == []
    cursor.execute('SELECT * FROM contractors.processing_queue')
    assert list(cursor) == []


@pytest.mark.config(
    DRIVER_TAGS_DRIVER_CARS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_base(
        taxi_driver_tags, testpoint_driver_cars_synchronizer, pgsql,
):
    async with taxi_driver_tags.spawn_task('driver-cars-synchronizer'):
        await testpoint_driver_cars_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    assert list(cursor) == [
        ('driver_cars', '0_1546300762_1'),
        ('driver_cars_unchecked', '0_1546300762_1'),
    ]

    cursor.execute(queries.GET_PROFILES_WITH_CARID)
    assert [(r[1], r[2], r[3]) for r in list(cursor)] == [
        ('dbid1', 'uuid1', 'car1'),
        ('dbid2', 'uuid1', 'car3'),
        ('dbid2', 'uuid12', None),
    ]
    cursor.execute(GET_QUEUE_PROFILES)

    mytz = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    ts1 = datetime.datetime(2019, 1, 1, 2, 59, 20, tzinfo=mytz)
    ts2 = ts1 + datetime.timedelta(seconds=1)
    ts3 = ts2 + datetime.timedelta(seconds=1)
    assert list(cursor) == [
        ('dbid1', 'uuid1', ts1),
        ('dbid2', 'uuid1', ts2),
        ('dbid2', 'uuid12', ts3),
    ]


@pytest.mark.config(
    DRIVER_TAGS_DRIVER_CARS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO state.revisions (target, revision)
        VALUES ('driver_cars', '0_1546300760_1'),
               ('driver_cars_unchecked', '0_1546300760_1')
        """,
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_base_with_initial_revision(
        taxi_driver_tags, testpoint_driver_cars_synchronizer, pgsql,
):
    async with taxi_driver_tags.spawn_task('driver-cars-synchronizer'):
        await testpoint_driver_cars_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(queries.GET_REVISIONS)
    assert list(cursor) == [
        ('driver_cars', '0_1546300762_1'),
        ('driver_cars_unchecked', '0_1546300762_1'),
    ]

    cursor.execute(queries.GET_PROFILES_WITH_CARID)
    assert [(r[1], r[2], r[3]) for r in list(cursor)] == [
        ('dbid2', 'uuid1', 'car3'),
        ('dbid2', 'uuid12', None),
    ]
    cursor.execute(GET_QUEUE_PROFILES)

    mytz = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    ts1 = datetime.datetime(2019, 1, 1, 2, 59, 20, tzinfo=mytz)
    ts2 = ts1 + datetime.timedelta(seconds=1)
    ts3 = ts2 + datetime.timedelta(seconds=1)
    assert list(cursor) == [('dbid2', 'uuid1', ts2), ('dbid2', 'uuid12', ts3)]


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
            (id, park_id, profile_id, car_id)
        VALUES (1498, 'dbid1', 'uuid1', 'car1'),
               (1531, 'dbid2', 'uuid1', 'car2'),
               (4492, 'dbid2', 'uuid12', NULL)
        """,
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_DRIVER_CARS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
async def test_update_only_changed_profile(
        taxi_driver_tags, testpoint_driver_cars_synchronizer, pgsql,
):
    async with taxi_driver_tags.spawn_task('driver-cars-synchronizer'):
        await testpoint_driver_cars_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()

    cursor.execute(queries.GET_PROFILES_WITH_CARID)
    assert list(cursor) == [
        (1498, 'dbid1', 'uuid1', 'car1'),
        (1531, 'dbid2', 'uuid1', 'car3'),
        (4492, 'dbid2', 'uuid12', None),
    ]
    cursor.execute(GET_QUEUE_PROFILES)
    mytz = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    myts = datetime.datetime(2019, 1, 1, 2, 59, 21, tzinfo=mytz)
    assert list(cursor) == [('dbid2', 'uuid1', myts)]


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
            (id, park_id, profile_id, car_id)
        VALUES (1498, 'dbid1', 'uuid1', 'car1'),
               (1531, 'dbid2', 'uuid1', 'car3'),
               (4492, 'dbid2', 'uuid12', 'supercar8')
        """,
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_DRIVER_CARS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 100,
        'job_interval_ms': 100000,
    },
)
async def test_deleted_id(
        taxi_driver_tags, testpoint_driver_cars_synchronizer, pgsql,
):
    async with taxi_driver_tags.spawn_task('driver-cars-synchronizer'):
        await testpoint_driver_cars_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()

    cursor.execute(queries.GET_PROFILES_WITH_CARID)
    assert list(cursor) == [
        (1498, 'dbid1', 'uuid1', 'car1'),
        (1531, 'dbid2', 'uuid1', 'car3'),
        (4492, 'dbid2', 'uuid12', None),
    ]
    cursor.execute(GET_QUEUE_PROFILES)
    mytz = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    myts = datetime.datetime(2019, 1, 1, 2, 59, 22, tzinfo=mytz)
    assert list(cursor) == [('dbid2', 'uuid12', myts)]
