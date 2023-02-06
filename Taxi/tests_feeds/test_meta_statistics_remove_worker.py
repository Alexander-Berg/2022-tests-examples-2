import pytest


@pytest.mark.config(
    FEEDS_REMOVE_STATISTICS_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'update_query_timeout': 30000,
    },
    FEEDS_SERVICES={
        'service': {
            'description': 'Service for test',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'statistics': {'enable': True, 'remove_delay_sec': 120},
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['feeds.sql'])
@pytest.mark.now('2018-12-20T00:00:00Z')
async def test_worker(taxi_feeds, taxi_config, pgsql, testpoint):
    @testpoint('remove-feeds-statistics-worker-finished')
    def worker_finished(data):
        pass

    async with taxi_feeds.spawn_task(
            'distlock/remove-feeds-statistics-worker',
    ):
        await worker_finished.wait_call()

        cursor = pgsql['feeds-pg'].cursor()
        cursor.execute(
            """
            SELECT request_id FROM feeds_statistics
            WHERE service_id = 1;
        """,
        )
        meta_counters = list(cursor)
        assert len(meta_counters) == 1

        assert meta_counters[0][0] == 'request_1'
