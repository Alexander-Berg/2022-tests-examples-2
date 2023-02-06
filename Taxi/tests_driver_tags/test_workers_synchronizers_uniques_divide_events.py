import datetime

import psycopg2
import pytest

from tests_driver_tags import queries

TZ = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
DEFAULT_TS = datetime.datetime(1970, 1, 1, 3, 0, 0, tzinfo=TZ)

CONFIG = {
    '__default__': {
        '__default__': {
            'logs-enabled': False,
            'is-enabled': False,
            'sleep-ms': 5000,
        },
    },
    'driver-tags': {
        '__default__': {
            'logs-enabled': True,
            'is-enabled': True,
            'sleep-ms': 1,
        },
    },
}
DUMMY_STREAM = {
    'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
    'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
}
LB_MSG = {
    'producer': {'source': 'admin', 'login': 'login'},
    'unique_driver': {
        'id': '000000000000000000000001',
        'park_driver_profile_ids': [{'id': 'dbid1_uuid1'}],
    },
    'decoupled_unique_driver': {
        'id': '000000000000000000000002',
        'park_driver_profile_ids': [
            {'id': 'dbid2_uuid2'},
            {'id': 'dbid3_uuid3'},
        ],
    },
}


@pytest.mark.config(UNIQUE_DRIVERS_SERVICES_CONSUMERS_SETTINGS=CONFIG)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_insert_divide_profiles(
        taxi_driver_tags, logbroker_helper, testpoint, pgsql,
):
    @testpoint('driver-tags-uniques-divide-events::ProcessMessage')
    def processed(data):
        # pylint: disable=unused-variable
        pass

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    lb_helper = logbroker_helper(taxi_driver_tags)

    await lb_helper.send_json(
        'uniques-divide-events',
        LB_MSG,
        topic='/taxi/unique-drivers/testing/uniques-divide-events',
        cookie='cookie',
    )

    async with taxi_driver_tags.spawn_task('uniques-divide-events'):
        await commit.wait_call()

    cursor = pgsql['driver-tags'].cursor()

    cursor.execute(queries.GET_PROFILES_WITH_UDID)
    assert list(cursor) == [
        (1, 'dbid2', 'uuid2', '000000000000000000000002'),
        (2, 'dbid3', 'uuid3', '000000000000000000000002'),
    ]

    cursor.execute(queries.GET_CONTRACTOR_IDS_WITH_TS_FROM_QUEUE)
    assert list(cursor) == [(1, DEFAULT_TS), (2, DEFAULT_TS)]


@pytest.mark.config(UNIQUE_DRIVERS_SERVICES_CONSUMERS_SETTINGS=CONFIG)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
            (id, park_id, profile_id, unique_driver_id)
        VALUES (1, 'dbid1', 'uuid1', '000000000000000000000001'),
               (2, 'dbid2', 'uuid2', '000000000000000000000002'),
               (3, 'dbid3', 'uuid3', '000000000000000000000005')
        """,
    ],
)
async def test_updates_only_changed_profiles(
        taxi_driver_tags, logbroker_helper, testpoint, pgsql,
):
    @testpoint('driver-tags-uniques-divide-events::ProcessMessage')
    def processed(data):
        # pylint: disable=unused-variable
        pass

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    lb_helper = logbroker_helper(taxi_driver_tags)

    await lb_helper.send_json(
        'uniques-divide-events',
        LB_MSG,
        topic='/taxi/unique-drivers/testing/uniques-divide-events',
        cookie='cookie',
    )

    async with taxi_driver_tags.spawn_task('uniques-divide-events'):
        await commit.wait_call()

    cursor = pgsql['driver-tags'].cursor()

    cursor.execute(queries.GET_PROFILES_WITH_UDID)
    assert list(cursor) == [
        (1, 'dbid1', 'uuid1', '000000000000000000000001'),
        (2, 'dbid2', 'uuid2', '000000000000000000000002'),
        (3, 'dbid3', 'uuid3', '000000000000000000000002'),
    ]

    cursor.execute(queries.GET_CONTRACTOR_IDS_WITH_TS_FROM_QUEUE)
    assert list(cursor) == [(3, DEFAULT_TS)]


@pytest.mark.config(UNIQUE_DRIVERS_SERVICES_CONSUMERS_SETTINGS=CONFIG)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """
        INSERT INTO contractors.profiles
            (id, park_id, profile_id, unique_driver_id)
        VALUES (1, 'dbid1', 'uuid1', '000000000000000000000001'),
               (2, 'dbid2', 'uuid2', NULL),
               (3, 'dbid3', 'uuid3', NULL)
        """,
        """
        INSERT INTO contractors.processing_queue
            (contractor_id, revision)
        VALUES
            (2, 9995),
            (3, 9996)
        """,
    ],
)
async def test_updates_queue_revision(
        taxi_driver_tags, logbroker_helper, testpoint, pgsql,
):
    @testpoint('driver-tags-uniques-divide-events::ProcessMessage')
    def processed(data):
        # pylint: disable=unused-variable
        pass

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    lb_helper = logbroker_helper(taxi_driver_tags)

    await lb_helper.send_json(
        'uniques-divide-events',
        LB_MSG,
        topic='/taxi/unique-drivers/testing/uniques-divide-events',
        cookie='cookie',
    )

    async with taxi_driver_tags.spawn_task('uniques-divide-events'):
        await commit.wait_call()

    cursor = pgsql['driver-tags'].cursor()

    cursor.execute(queries.GET_PROFILES_WITH_UDID)
    assert list(cursor) == [
        (1, 'dbid1', 'uuid1', '000000000000000000000001'),
        (2, 'dbid2', 'uuid2', '000000000000000000000002'),
        (3, 'dbid3', 'uuid3', '000000000000000000000002'),
    ]

    cursor.execute(queries.GET_CONTRACTOR_IDS_WITH_REVISION_FROM_QUEUE)
    queue = list(cursor)
    assert len(queue) == 2
    assert [v[0] for v in queue] == [2, 3]
    assert [] == [v for v in queue if v[1] in [9995, 9996]]
