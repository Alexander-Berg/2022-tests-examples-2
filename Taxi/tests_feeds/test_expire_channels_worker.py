import pytest


@pytest.mark.config(
    FEEDS_REMOVE_UNUSED_CHANNEL_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'expire_interval_sec': 3600,
        'max_deleted_channels_per_service': 100,
    },
)
@pytest.mark.pgsql('feeds-pg', files=['expire_channels.sql'])
@pytest.mark.now('2020-01-01T00:30:00Z')
async def test_remove_channel_worker(taxi_feeds, pgsql, testpoint):
    @testpoint('remove-unused-channels-worker-finished')
    def end_remove(data):
        pass

    async with taxi_feeds.spawn_task('distlock/remove-unused-channels-worker'):
        await end_remove.wait_call()

        cursor = pgsql['feeds-pg'].cursor()
        query = 'SELECT id FROM channels ORDER BY updated'
        cursor.execute(query)
        assert list(cursor) == [(0,), (1,), (2,)]
