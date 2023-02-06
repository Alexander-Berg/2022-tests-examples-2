import pytest

# For catching distlocked periodic task
@pytest.fixture(name='testpoint_contractor_processor')
def _testpoint_contractor_processor(testpoint):
    class Context:
        @staticmethod
        @testpoint('contractor-processor-finished')
        def finished(data):
            pass

    return Context()


@pytest.fixture(name='testpoint_dist_lock_wrapper')
def _testpoint_dist_lock_wrapper(testpoint):
    class Context:
        @staticmethod
        @testpoint('dist-lock-wrapper-contractor-processor-finished')
        def finished(data):
            pass

    return Context()


DUMMY_STREAM = {
    'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
    'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
}

DEFAULT_QUERIES = [
    """INSERT INTO contractors.profiles
        (id, park_id, profile_id, unique_driver_id)
       VALUES (1498, 'dbid', 'uuid', 'udid')""",
    'INSERT INTO contractors.processing_queue (contractor_id) VALUES (1498)',
]


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql('driver-tags', queries=DEFAULT_QUERIES)
@pytest.mark.config(
    DRIVER_TAGS_CONTRACTOR_PROCESSOR={
        'enabled': True,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
    DRIVER_TAGS_WORKERS_HOST_SETTINGS={},
)
async def test_no_host(
        taxi_driver_tags, testpoint_contractor_processor, pgsql,
):
    async with taxi_driver_tags.spawn_task('contractor-processor'):
        await testpoint_contractor_processor.finished.wait_call()

    # clean queue since no prefered host specified
    cursor = pgsql['driver-tags'].cursor()
    cursor.execute('SELECT contractor_id FROM contractors.processing_queue')
    assert [] == list(cursor)


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql('driver-tags', queries=DEFAULT_QUERIES)
@pytest.mark.config(
    DRIVER_TAGS_CONTRACTOR_PROCESSOR={
        'enabled': True,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
    DRIVER_TAGS_WORKERS_HOST_SETTINGS={'contractor-processor': ''},
)
async def test_empty_host(
        taxi_driver_tags, testpoint_contractor_processor, pgsql,
):
    async with taxi_driver_tags.spawn_task('contractor-processor'):
        await testpoint_contractor_processor.finished.wait_call()

    # clean queue since empty host specified is equal to no host
    cursor = pgsql['driver-tags'].cursor()
    cursor.execute('SELECT contractor_id FROM contractors.processing_queue')
    assert [] == list(cursor)


@pytest.mark.unique_drivers(stream=DUMMY_STREAM)
@pytest.mark.pgsql('driver-tags', queries=DEFAULT_QUERIES)
@pytest.mark.config(
    DRIVER_TAGS_CONTRACTOR_PROCESSOR={
        'enabled': True,
        'process_batch_size': 200,
        'job_interval_ms': 100000,
    },
    DRIVER_TAGS_WORKERS_HOST_SETTINGS={
        'contractor-processor': 'some-host-xxx',
    },
)
async def test_other_host(
        taxi_driver_tags,
        testpoint_contractor_processor,
        testpoint_dist_lock_wrapper,
        pgsql,
):
    async with taxi_driver_tags.spawn_task('contractor-processor'):
        await testpoint_dist_lock_wrapper.finished.wait_call()

    # job was not launched
    cursor = pgsql['driver-tags'].cursor()
    cursor.execute('SELECT contractor_id FROM contractors.processing_queue')
    assert [(1498,)] == list(cursor)
