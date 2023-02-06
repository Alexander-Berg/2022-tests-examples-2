import datetime

import psycopg2
import pytest

# For catching distlocked periodic task
@pytest.fixture(name='testpoint_unique_drivers_synchronizer')
def _testpoint_unique_drivers_synchronizer(testpoint):
    class Context:
        @staticmethod
        @testpoint('unique-drivers-synchronizer-finished')
        def finished(data):
            pass

    return Context()


@pytest.fixture(name='mock_unique_drivers')
def _mock_unique_drivers(mockserver):
    class Context:
        def __init__(self):
            self.revision = 1
            self.unique_driver_ids = {}
            self.mock_retrieve_by_profiles = {}
            self.mock_retrieve_by_uniques = {}
            self.udid_to_profiles = {}
            self.deleted_ids = set()

        def add_driver(self, park_id, driver_profile_id, unique_driver_id):
            joined_id = '_'.join([park_id, driver_profile_id])
            self.unique_driver_ids[joined_id] = {
                'udid': unique_driver_id,
                'revision': self.revision,
            }
            self.udid_to_profiles[unique_driver_id] = [
                {
                    'park_id': park_id,
                    'driver_profile_id': driver_profile_id,
                    'park_driver_profile_id': joined_id,
                    'revision': self.revision,
                },
            ]
            self.revision += 1

        def delete_id(self, id_):
            self.deleted_ids.add(id_)

        def to_rev(self, rev):
            return str(rev) + '_0'

        def set_revision(self, rev):
            self.revision = rev

        def get_revision(self, checked=False):
            return self.to_rev(self.revision - (2 if checked else 1))

        def generate_stream(self):
            licenses_by_unique_drivers = {
                'revision': self.to_rev(self.revision),
                'items': [],
            }
            license_by_driver_profile = {
                'revision': self.to_rev(self.revision),
                'items': [],
            }
            for profile, val in self.unique_driver_ids.items():
                revision = val['revision']
                licenses_by_unique_drivers['items'].append(
                    {
                        'id': val['udid'],
                        'is_deleted': val['udid'] in self.deleted_ids,
                        'revision': self.to_rev(revision),
                        'data': {
                            'license_ids': [
                                val['udid'] + '__' + str(revision),
                            ],
                        },
                    },
                )
                license_by_driver_profile['items'].append(
                    {
                        'id': profile,
                        'is_deleted': profile in self.deleted_ids,
                        'revision': self.to_rev(revision),
                        'data': {
                            'license_id': val['udid'] + '__' + str(revision),
                        },
                    },
                )
            return {
                'licenses_by_unique_drivers': licenses_by_unique_drivers,
                'license_by_driver_profile': license_by_driver_profile,
            }

    context = Context()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_retrieve_by_profiles(request):
        response_uniques = []
        profile_id_in_set = request.json.get('profile_id_in_set')
        for profile in profile_id_in_set:
            record = {'park_driver_profile_id': profile}
            if profile not in context.deleted_ids:
                if profile in context.unique_driver_ids:
                    udid = context.unique_driver_ids[profile]['udid']
                    if udid not in context.deleted_ids:
                        record['data'] = {'unique_driver_id': udid}
            response_uniques.append(record)

        return {'uniques': response_uniques}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _mock_retrieve_by_uniques(request):
        resp_profiles = []
        for udid in request.json['id_in_set']:
            data = []
            for profile in context.udid_to_profiles[udid]:
                if udid in context.deleted_ids:
                    continue
                if profile['park_driver_profile_id'] in context.deleted_ids:
                    continue
                data.append(
                    {
                        'park_id': profile['park_id'],
                        'driver_profile_id': profile['driver_profile_id'],
                        'park_driver_profile_id': profile[
                            'park_driver_profile_id'
                        ],
                    },
                )
            resp_profiles.append({'unique_driver_id': udid, 'data': data})
        return {'profiles': resp_profiles}

    context.mock_retrieve_by_profiles = _mock_retrieve_by_profiles
    context.mock_retrieve_by_uniques = _mock_retrieve_by_uniques

    return context


def make_ts(timestamp):
    return datetime.datetime.fromtimestamp(
        timestamp, tz=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
    )


DUMMY_STREAM = {
    'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
    'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
}


@pytest.mark.config(
    DRIVER_TAGS_UNIQUE_DRIVERS_SYNCHRONIZER={
        'enabled': False,
        'store_batch_size': 500,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_disabled(
        taxi_driver_tags,
        bindings_updates_mock,
        mock_unique_drivers,
        testpoint_unique_drivers_synchronizer,
        pgsql,
):
    mock_unique_drivers.add_driver('dbid1', 'uuid1', 'udid1')
    mock_unique_drivers.add_driver('dbid3', 'uuid1', 'udid1')
    mock_unique_drivers.add_driver('dbid1', 'uuid2', 'udid2')
    # last one will be skipped due to only_checked_documents flag
    mock_unique_drivers.add_driver('dummy_dbid', 'dummy_uuid', 'dummy_udid')

    bindings_updates_mock.set_stream(mock_unique_drivers.generate_stream())

    async with taxi_driver_tags.spawn_task('unique-drivers-synchronizer'):
        await testpoint_unique_drivers_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute('SELECT * FROM state.revisions')
    assert list(cursor) == []
    cursor.execute('SELECT * FROM contractors.profiles')
    assert list(cursor) == []
    cursor.execute('SELECT * FROM contractors.processing_queue')
    assert list(cursor) == []


@pytest.mark.config(
    DRIVER_TAGS_UNIQUE_DRIVERS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 500,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_empty(
        taxi_driver_tags,
        bindings_updates_mock,
        mock_unique_drivers,
        testpoint_unique_drivers_synchronizer,
        pgsql,
):
    async with taxi_driver_tags.spawn_task('unique-drivers-synchronizer'):
        await testpoint_unique_drivers_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute('SELECT * FROM state.revisions ORDER BY target DESC')
    assert list(cursor) == [
        ('unique_drivers', '0_0'),
        ('driver_profiles', '0_0'),
    ]
    cursor.execute('SELECT * FROM contractors.profiles')
    assert list(cursor) == []
    cursor.execute('SELECT * FROM contractors.processing_queue')
    assert list(cursor) == []


@pytest.mark.config(
    DRIVER_TAGS_UNIQUE_DRIVERS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 500,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_base(
        taxi_driver_tags,
        bindings_updates_mock,
        mock_unique_drivers,
        testpoint_unique_drivers_synchronizer,
        pgsql,
):
    mock_unique_drivers.add_driver('dbid1', 'uuid1', 'udid1')
    mock_unique_drivers.add_driver('dbid3', 'uuid1', 'udid1')
    mock_unique_drivers.add_driver('dbid1', 'uuid2', 'udid2')
    # last one will be skipped due to only_checked_documents flag
    mock_unique_drivers.add_driver('dummy_dbid', 'dummy_uuid', 'dummy_udid')

    bindings_updates_mock.set_stream(mock_unique_drivers.generate_stream())

    async with taxi_driver_tags.spawn_task('unique-drivers-synchronizer'):
        await testpoint_unique_drivers_synchronizer.finished.wait_call()

    rev = mock_unique_drivers.get_revision(True)
    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(
        """
        SELECT target, revision
        FROM state.revisions
        WHERE target IN ('unique_drivers', 'driver_profiles')
        ORDER BY target DESC
        """,
    )
    assert list(cursor) == [('unique_drivers', rev), ('driver_profiles', rev)]

    cursor.execute(
        """
        SELECT id, park_id, profile_id, unique_driver_id
        FROM contractors.profiles
        ORDER BY park_id, profile_id
        """,
    )
    assert list(cursor) == [
        (1, 'dbid1', 'uuid1', 'udid1'),
        (2, 'dbid1', 'uuid2', 'udid2'),
        (3, 'dbid3', 'uuid1', 'udid1'),
    ]
    cursor.execute(
        """
        SELECT contractor_id FROM contractors.processing_queue
        ORDER BY contractor_id
        """,
    )

    assert list(cursor) == [(1,), (2,), (3,)]


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
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_UNIQUE_DRIVERS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 500,
        'job_interval_ms': 100000,
    },
)
async def test_update_only_changed_profile(
        taxi_driver_tags,
        bindings_updates_mock,
        mock_unique_drivers,
        testpoint_unique_drivers_synchronizer,
        pgsql,
):
    mock_unique_drivers.add_driver('dbid1', 'uuid1', 'udid1')
    mock_unique_drivers.add_driver('dbid3', 'uuid1', 'udid1')
    # last one will be skipped due to only_checked_documents flag
    mock_unique_drivers.add_driver('dummy_dbid', 'dummy_uuid', 'dummy_udid')

    bindings_updates_mock.set_stream(mock_unique_drivers.generate_stream())

    async with taxi_driver_tags.spawn_task('unique-drivers-synchronizer'):
        await testpoint_unique_drivers_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()

    cursor.execute(
        """
        SELECT id, park_id, profile_id, unique_driver_id
        FROM contractors.profiles
        ORDER BY id
        """,
    )
    assert list(cursor) == [
        (1498, 'dbid1', 'uuid1', 'udid1'),
        (4492, 'dbid3', 'uuid1', 'udid1'),
    ]
    cursor.execute('SELECT contractor_id FROM contractors.processing_queue')
    assert list(cursor) == [(1498,)]


@pytest.mark.now('2020-10-01T12:00:00+0000')
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """INSERT INTO contractors.profiles
            (id, park_id, profile_id, unique_driver_id) VALUES
            (111, 'dbid1', 'uuid1', 'udid1'),
            (112, 'dbid3', 'uuid1', 'udid1'),
            (113, 'dbid1', 'uuid2', 'udid2'),
            (114, 'dbid2', 'uuid8', 'udid3')""",
    ],
)
@pytest.mark.config(
    DRIVER_TAGS_UNIQUE_DRIVERS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 500,
        'job_interval_ms': 100000,
    },
)
async def test_deleted_ids(
        taxi_driver_tags,
        bindings_updates_mock,
        mock_unique_drivers,
        testpoint_unique_drivers_synchronizer,
        pgsql,
):
    mock_unique_drivers.set_revision(1554915158)
    mock_unique_drivers.add_driver('dbid1', 'uuid1', 'udid1')
    mock_unique_drivers.set_revision(1554924558)
    mock_unique_drivers.add_driver('dbid3', 'uuid1', 'udid1')
    mock_unique_drivers.add_driver('dbid1', 'uuid2', 'udid2')
    rev283 = 1554995158
    mock_unique_drivers.set_revision(rev283)
    mock_unique_drivers.add_driver('dbid2', 'uuid8', 'udid3')
    mock_unique_drivers.add_driver('dbid9', 'uuid9', 'udid9')
    # last one will be skipped due to only_checked_documents flag
    mock_unique_drivers.add_driver('dummy_dbid', 'dummy_uuid', 'dummy_udid')

    mock_unique_drivers.delete_id('udid1')
    mock_unique_drivers.delete_id('dbid2_uuid8')

    bindings_updates_mock.set_stream(mock_unique_drivers.generate_stream())

    async with taxi_driver_tags.spawn_task('unique-drivers-synchronizer'):
        await testpoint_unique_drivers_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()

    cursor.execute(
        """
        SELECT id, park_id, profile_id, unique_driver_id
        FROM contractors.profiles WHERE deleted_at IS NULL
        ORDER BY id
        """,
    )
    assert list(cursor) == [
        (1, 'dbid9', 'uuid9', 'udid9'),
        (111, 'dbid1', 'uuid1', None),
        (112, 'dbid3', 'uuid1', None),
        (113, 'dbid1', 'uuid2', 'udid2'),
    ]

    cursor.execute(
        """
        SELECT id, park_id, profile_id, unique_driver_id, deleted_at
        FROM contractors.profiles WHERE deleted_at IS NOT NULL
        """,
    )
    assert list(cursor) == [(114, 'dbid2', 'uuid8', 'udid3', make_ts(rev283))]
    cursor.execute(
        """SELECT contractor_id FROM contractors.processing_queue
           ORDER BY contractor_id ASC""",
    )
    # only newly added profile, 122 - got update but wasn't changed
    assert list(cursor) == [(1,), (111,), (112,)]


@pytest.mark.config(
    DRIVER_TAGS_UNIQUE_DRIVERS_SYNCHRONIZER={
        'enabled': True,
        'store_batch_size': 500,
        'job_interval_ms': 100000,
    },
)
@pytest.mark.pgsql(
    'driver-tags',
    queries=[
        """INSERT INTO contractors.profiles
            (id, park_id, profile_id) VALUES
            (111, 'dbid1', 'uuid1'),
            (311, 'dbid3', 'uuid1'),
            (122, 'dbid1', 'uuid2'),
            (283, 'dbid2', 'uuid8')""",
        """INSERT INTO contractors.processing_queue
            (contractor_id, revision) VALUES
            (111, 9994),
            (311, 9995),
            (122, 9996),
            (283, 9997)""",
    ],
)
@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
async def test_update_queue_revision(
        taxi_driver_tags,
        bindings_updates_mock,
        mock_unique_drivers,
        testpoint_unique_drivers_synchronizer,
        pgsql,
):
    mock_unique_drivers.add_driver('dbid1', 'uuid1', 'udid1')
    mock_unique_drivers.add_driver('dbid3', 'uuid1', 'udid1')
    mock_unique_drivers.add_driver('dbid1', 'uuid2', 'udid2')
    mock_unique_drivers.add_driver('dbid2', 'uuid8', 'udid3')
    # last one will be skipped due to only_checked_documents flag
    mock_unique_drivers.add_driver('dummy_dbid', 'dummy_uuid', 'dummy_udid')

    bindings_updates_mock.set_stream(mock_unique_drivers.generate_stream())

    async with taxi_driver_tags.spawn_task('unique-drivers-synchronizer'):
        await testpoint_unique_drivers_synchronizer.finished.wait_call()

    cursor = pgsql['driver-tags'].cursor()
    cursor.execute(
        """SELECT contractor_id, revision
        FROM contractors.processing_queue
        ORDER BY contractor_id""",
    )

    queue = list(cursor)
    assert len(queue) == 4
    assert [v[0] for v in queue] == [111, 122, 283, 311]
    assert [] == [v for v in queue if v[1] in [9994, 9995, 9996, 9997]]
