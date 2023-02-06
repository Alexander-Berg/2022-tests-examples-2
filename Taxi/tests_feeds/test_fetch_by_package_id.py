import pytest


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_package_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_simple(taxi_feeds, load_json):
    response = await taxi_feeds.post(
        '/v1/fetch_by_package_id',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'package_ids': ['p1'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    feeds = {feed['feed_id']: feed for feed in data['feed']}
    assert feeds == load_json('service_feeds.json')


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_package_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_tags(taxi_feeds, load_json):
    response = await taxi_feeds.post(
        '/v1/fetch_by_package_id',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'package_ids': ['p1'],
            'tags': ['a'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    feeds = {feed['feed_id']: feed for feed in data['feed']}

    expected_feeds = load_json('service_feeds.json')
    assert feeds == expected_feeds

    response = await taxi_feeds.post(
        '/v1/fetch_by_package_id',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'package_ids': ['p1'],
            'tags': ['b'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    feeds = {feed['feed_id']: feed for feed in data['feed']}

    del expected_feeds['111c69c8afe947ba887fd6404428b31c']

    assert feeds == expected_feeds


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_package_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 4,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
            'cache': {'enable': True, 'channels_enable': True},
        },
    },
)
async def test_cache(taxi_feeds, load_json):
    response = await taxi_feeds.post(
        '/v1/fetch_by_package_id',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'package_ids': ['p1'],
        },
    )

    assert response.status_code == 400
