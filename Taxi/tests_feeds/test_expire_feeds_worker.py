import pytest


@pytest.mark.config(
    FEEDS_EXPIRE_FEEDS_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'max_deleted_feeds': 100,
    },
    FEEDS_SERVICES={
        'tariffeditor': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['expire_feeds.sql'])
@pytest.mark.now('2020-01-13T00:00:00Z')
async def test_remove_private_feed(taxi_feeds, taxi_config, pgsql, testpoint):
    @testpoint('expire-feeds-worker-finished')
    def worker_finished(data):
        pass

    async with taxi_feeds.spawn_task('distlock/expire-feeds-worker'):
        await worker_finished.wait_call()

        cursor = pgsql['feeds-pg'].cursor()
        query = 'SELECT feed_id FROM feeds ORDER BY created'
        cursor.execute(query)
        assert list(cursor) == [
            ('44444444-4444-4444-4444-444444444444',),
            ('55555555-5555-5555-5555-555555555555',),
        ]

        cursor = pgsql['feeds-pg'].cursor()
        cursor.execute('SELECT etag FROM channels')
        etags = [row[0] for row in cursor]
        assert '358af307-61eb-454d-b8af-9c8f9666e5a8' not in etags
        assert len(etags) == 3


@pytest.mark.config(
    FEEDS_EXPIRE_FEEDS_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'max_deleted_feeds': 100,
    },
    FEEDS_SERVICES={
        'tariffeditor': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['expire_feeds.sql'])
@pytest.mark.now('2020-01-13T00:00:00Z')
async def test_shard_turnof(taxi_feeds, pgsql, testpoint, statistics):
    @testpoint('expire-feeds-worker-finished')
    def worker_finished(data):
        pass

    statistics.fallbacks = ['__default__.highload']
    await taxi_feeds.invalidate_caches()

    async with taxi_feeds.spawn_task('distlock/expire-feeds-worker'):
        await worker_finished.wait_call()

        cursor = pgsql['feeds-pg'].cursor()
        query = 'SELECT count(*) FROM feeds'
        cursor.execute(query)
        assert list(cursor)[0][0] == 5
