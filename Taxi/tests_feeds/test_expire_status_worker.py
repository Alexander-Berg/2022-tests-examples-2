import pytest

import tests_feeds.feeds_common as fc


@pytest.mark.config(
    FEEDS_EXPIRE_STATUS_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'max_reset_statuses': 100,
    },
)
@pytest.mark.pgsql('feeds-pg', files=['expire_status.sql'])
@pytest.mark.now('2018-12-20T00:00:00Z')
async def test_worker(taxi_feeds, taxi_config, pgsql, testpoint):
    @testpoint('expire-status-worker-finished')
    def worker_finished(data):
        pass

    @testpoint('expire-status-worker-finished/service')
    def service_finished(data):
        assert data == {
            'updated_channels': [
                {
                    'service_id': 10,
                    'channel': 'service:user:2',
                    'feed_id': '11111111111111111111111111111111',
                    'status': 'published',
                    'meta': None,
                },
            ],
        }

    @testpoint('expire-status-worker-finished/other_service')
    def other_service_finished(data):
        assert data == {
            'updated_channels': [
                {
                    'service_id': 20,
                    'channel': 'other_service:user:1',
                    'feed_id': '22222222222222222222222222222222',
                    'status': 'viewed',
                    'meta': {'a': 3},
                },
            ],
        }

    async with taxi_feeds.spawn_task('distlock/expire-status-worker'):
        await worker_finished.wait_call()
        assert service_finished.times_called == 1
        assert other_service_finished.times_called == 1

        feed_1 = '11111111-1111-1111-1111-111111111111'
        feed_2 = '22222222-2222-2222-2222-222222222222'
        expire = fc.make_msk_datetime(2018, 12, 30, 3, 0)

        cursor = pgsql['feeds-pg'].cursor()
        cursor.execute(
            """
            SELECT feed_id, channel_id, status, expire, meta
            FROM feed_channel_status
            ORDER BY feed_id, channel_id;
        """,
        )
        assert list(cursor) == [
            (feed_1, 0, 'read', expire, {'a': 1}),
            (feed_1, 1, 'published', None, None),
            (feed_2, 2, 'viewed', None, {'a': 3}),
            (feed_2, 3, 'read', None, {'a': 4}),
        ]
