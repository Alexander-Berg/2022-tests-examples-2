import pytest


@pytest.mark.now('2019-12-12T00:00:00Z')
@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 30,
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_fetch_random_polling_delay.sql'])
async def test_random_polling_delay(taxi_feeds, pgsql):
    polling_delays = []
    for _ in range(500):
        response = await taxi_feeds.post(
            '/v1/fetch', json={'service': 'service', 'channels': ['user:1']},
        )

        assert response.status_code == 200
        polling_delays.append(response.json()['polling_delay'])

    assert len(set(polling_delays)) < len(polling_delays)
    assert all(60 <= delay <= 90 for delay in polling_delays)
