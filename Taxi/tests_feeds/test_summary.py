import pytest


@pytest.mark.now('2018-12-07T01:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_summary.sql'])
async def test_summary_no_categories(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'categories': [],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.now('2018-12-07T01:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_summary.sql'])
async def test_summary_all_categories(taxi_feeds):
    all_categories = ['counts', 'tags']

    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'categories': all_categories,
        },
    )
    assert response.status_code == 200
    for category in all_categories:
        assert category in response.json()


@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_summary.sql'])
@pytest.mark.parametrize('categories', [None, ['counts']])
async def test_summary_counts(taxi_feeds, pgsql, categories):
    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'categories': categories,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'counts': {
            'total': 6,
            'published': 3,
            'read': 1,
            'viewed': 1,
            'removed': 1,
        },
    }

    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1'],
            'categories': categories,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'counts': {
            'total': 6,
            'published': 5,
            'read': 0,
            'viewed': 1,
            'removed': 0,
        },
    }

    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:2'],
            'categories': categories,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'counts': {
            'total': 4,
            'published': 1,
            'read': 1,
            'viewed': 1,
            'removed': 1,
        },
    }


@pytest.mark.now('2018-12-07T01:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_summary_with_time_period.sql'])
async def test_summary_counts_with_time_period(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'from': '2018-11-01T00:00:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'counts': {
            'total': 3,
            'published': 1,
            'read': 1,
            'viewed': 0,
            'removed': 1,
        },
    }

    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'from': '2018-12-01T23:59:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'counts': {
            'total': 2,
            'published': 0,
            'read': 1,
            'viewed': 0,
            'removed': 1,
        },
    }

    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'from': '2018-12-01T00:00:00.000000Z',
            'to': '2018-12-02T23:59:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'counts': {
            'total': 2,
            'published': 1,
            'read': 1,
            'viewed': 0,
            'removed': 0,
        },
    }

    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'to': '2018-12-02T23:59:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'counts': {
            'total': 2,
            'published': 1,
            'read': 1,
            'viewed': 0,
            'removed': 0,
        },
    }

    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'to': '2018-12-07T00:00:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'counts': {
            'total': 3,
            'published': 1,
            'read': 1,
            'viewed': 0,
            'removed': 1,
        },
    }


@pytest.mark.now('2018-12-07T01:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_summary_tags.sql'])
async def test_summary_tags(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'categories': ['tags'],
        },
    )
    assert response.status_code == 200

    response_tags = set(response.json()['tags'])
    assert response_tags == {'tag1', 'tag2'}


@pytest.mark.config(
    FEEDS_SERVICES={
        'service_not_in_bd': {
            'description': 'description',
            'max_feed_ttl_hours': 1,
            'polling_delay_sec': 60,
        },
    },
)
@pytest.mark.parametrize(
    'categories', [None, ['counts'], ['tags'], ['counts', 'tags']],
)
@pytest.mark.now('2018-12-07T01:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_summary.sql'])
async def test_summary_no_service_in_db(taxi_feeds, categories):
    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'service_not_in_bd',
            'channels': ['channel:1', 'channel:2'],
            'categories': categories,
        },
    )
    assert response.status_code == 200


@pytest.mark.now('2018-12-07T01:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_summary.sql'])
async def test_summary_no_service_in_config(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/summary',
        json={
            'service': 'some_service',
            'channels': ['channel:1', 'channel:2'],
        },
    )
    assert response.status_code == 400
