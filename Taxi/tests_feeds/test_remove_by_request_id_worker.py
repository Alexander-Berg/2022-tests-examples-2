import pytest


async def _get_feed_count(pgsql):
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT count(*) FROM feeds;')
    return list(cursor)[0][0]


async def _get_remove_request_count(pgsql):
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT count(*) FROM remove_requests_by_request_id;')
    return list(cursor)[0][0]


async def _run_worker(taxi_feeds, pgsql, testpoint, expected_stats=None):
    @testpoint('remove-by-request-id-worker-finished')
    def worker_finished(data):
        pass

    @testpoint('remove-statistics')
    def remove_statistics(data):
        if expected_stats is not None:
            for key in expected_stats.keys():
                assert data[key] == expected_stats[key], f'Key failed: {key}'

    async with taxi_feeds.spawn_task('distlock/remove-by-request-id-worker'):
        if expected_stats is not None:
            await remove_statistics.wait_call()
        await worker_finished.wait_call()


@pytest.mark.config(
    FEEDS_REMOVE_BY_REQUEST_ID_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'max_deleted_feeds': 3,
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_worker.sql'])
@pytest.mark.now('2018-12-20T00:00:00Z')
async def test_worker(taxi_feeds, pgsql, testpoint):
    # Each remove request requires two runs:
    # on first run some feeds are removed, on second run no feeds left
    # and remove request deleted from queue
    assert await _get_feed_count(pgsql) == 4
    assert await _get_remove_request_count(pgsql) == 3

    # request_id=my_notification_1
    await _run_worker(
        taxi_feeds,
        pgsql,
        testpoint,
        {
            'request_id': 'my_notification_1',
            'n_deleted_feeds': 1,
            'n_deleted_statuses': 1,
            'statuses': [
                {
                    'channel': 'user:1',
                    'feed_id': '36f29b888314418fb8836d7400eb3c43',
                },
            ],
        },
    )
    await _run_worker(taxi_feeds, pgsql, testpoint, {'statuses': []})
    assert await _get_feed_count(pgsql) == 3
    assert await _get_remove_request_count(pgsql) == 2

    # request_id=my_notification_2
    await _run_worker(
        taxi_feeds,
        pgsql,
        testpoint,
        {
            'request_id': 'my_notification_2',
            'n_deleted_feeds': 1,
            'n_deleted_statuses': 1,
            'statuses': [
                {
                    'channel': 'user:2',
                    'feed_id': 'b27edf7c10e346e681bd047a7ef5f494',
                },
            ],
        },
    )
    await _run_worker(taxi_feeds, pgsql, testpoint, {'statuses': []})
    assert await _get_feed_count(pgsql) == 2
    assert await _get_remove_request_count(pgsql) == 1

    # request_id=my_notification_3
    await _run_worker(
        taxi_feeds,
        pgsql,
        testpoint,
        {
            'request_id': 'my_notification_3',
            'n_deleted_feeds': 1,
            'n_deleted_statuses': 2,
            'statuses': [
                {
                    'channel': 'user:1',
                    'feed_id': 'dfd998fbf1b14b20ac2e5abaf48ba386',
                },
                {
                    'channel': 'user:2',
                    'feed_id': 'dfd998fbf1b14b20ac2e5abaf48ba386',
                },
            ],
        },
    )
    await _run_worker(taxi_feeds, pgsql, testpoint, {'statuses': []})
    assert await _get_feed_count(pgsql) == 1
    assert await _get_remove_request_count(pgsql) == 0


@pytest.mark.config(
    FEEDS_REMOVE_BY_REQUEST_ID_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'max_deleted_feeds': 3,
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_worker_limit.sql'])
@pytest.mark.now('2018-12-20T00:00:00Z')
async def test_worker_limit(taxi_feeds, taxi_config, pgsql, testpoint):
    assert await _get_feed_count(pgsql) == 6
    assert await _get_remove_request_count(pgsql) == 1

    await _run_worker(taxi_feeds, pgsql, testpoint)
    assert await _get_feed_count(pgsql) == 3
    assert await _get_remove_request_count(pgsql) == 1

    await _run_worker(taxi_feeds, pgsql, testpoint)
    assert await _get_feed_count(pgsql) == 2
    assert await _get_remove_request_count(pgsql) == 1

    await _run_worker(taxi_feeds, pgsql, testpoint)
    assert await _get_feed_count(pgsql) == 2
    assert await _get_remove_request_count(pgsql) == 0


@pytest.mark.config(
    FEEDS_REMOVE_BY_REQUEST_ID_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'max_deleted_feeds': 3,
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_worker_recursive.sql'])
@pytest.mark.now('2018-12-20T00:00:00Z')
async def test_worker_recursive(taxi_feeds, taxi_config, pgsql, testpoint):
    assert await _get_feed_count(pgsql) == 4
    assert await _get_remove_request_count(pgsql) == 1

    await _run_worker(
        taxi_feeds,
        pgsql,
        testpoint,
        {
            'n_deleted_feeds': 3,
            'n_deleted_statuses': 3,
            'statuses': [
                {
                    'channel': 'user:1',
                    'feed_id': '75e46d20e0d941c1af604d354dd46ca0',
                },
                {
                    'channel': 'user:2',
                    'feed_id': '38672090b4ef4a3382d064c6d9642971',
                },
                {
                    'channel': 'user:3',
                    'feed_id': '57422b02229e42bdac084c589c4024c2',
                },
            ],
        },
    )
    assert await _get_feed_count(pgsql) == 1
    assert await _get_remove_request_count(pgsql) == 1

    await _run_worker(taxi_feeds, pgsql, testpoint, {'statuses': []})
    assert await _get_feed_count(pgsql) == 1
    assert await _get_remove_request_count(pgsql) == 0
