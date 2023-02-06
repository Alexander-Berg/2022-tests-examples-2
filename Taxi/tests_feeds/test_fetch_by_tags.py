import pytest

TESTCASES = (
    'tags,expected_feeds',
    [
        pytest.param(None, [3, 2, 1], id='tags=None'),
        pytest.param([], [3, 2, 1], id='tags='),
        pytest.param(['a'], [3, 2], id='tags=a'),
        pytest.param(['b'], [3], id='tags=b'),
        pytest.param(['a', 'b'], [3, 2], id='tags=a,b'),
        pytest.param(['a', 'bad'], [3, 2], id='tags=a,bad'),
        pytest.param(['bad'], [], id='tags=bad'),
    ],
)


@pytest.mark.parametrize(*TESTCASES)
@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_tags.sql'])
async def test_fetch_by_tags(taxi_feeds, pgsql, tags, expected_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={'service': 'service', 'channels': ['channel'], 'tags': tags},
    )

    assert response.status_code == 200

    feeds = [int(feed['feed_id'][0:1]) for feed in response.json()['feed']]
    assert feeds == expected_feeds

    if tags:
        request_tags = set(tags)
        for feed in response.json()['feed']:
            feed_tags = set(feed['tags'])
            assert feed_tags.intersection(request_tags)


@pytest.mark.parametrize(*TESTCASES)
@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_tags.sql'])
async def test_fetch_by_id_and_tags(taxi_feeds, pgsql, tags, expected_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'feed_ids': [
                '111c69c8afe947ba887fd6404428b31c',
                '222c69c8afe947ba887fd6404428b31c',
                '333c69c8afe947ba887fd6404428b31c',
            ],
            'channels': ['channel'],
            'tags': tags,
        },
    )

    assert response.status_code == 200

    feeds = [int(feed['feed_id'][0:1]) for feed in response.json()['feed']]
    feeds.sort(key=lambda fid: -fid)
    assert feeds == expected_feeds


@pytest.mark.parametrize(
    'tags,expected_feeds',
    [
        pytest.param(None, [4], id='tags=None'),
        pytest.param([], [4], id='tags='),
        pytest.param(['a'], [4], id='tags=a'),
        pytest.param(['b'], [], id='tags=b'),
        pytest.param(['a', 'b'], [4], id='tags=a,b'),
        pytest.param(['a', 'bad'], [4], id='tags=a,bad'),
        pytest.param(['bad'], [], id='tags=bad'),
    ],
)
@pytest.mark.config(
    FEEDS_GEO_CLUSTERING={
        'neighbors_number': 100,
        'zoom_levels': [
            {
                'zoom_level': 1,
                'distance_threshold_meters': 0.1,
                'choosing_bounds': {'lower': 0, 'upper': 1e18},
            },
        ],
    },
    FEEDS_CLUSTERING_WORKER={
        'enable': True,
        'work_interval_minutes': 3,
        'limit': 1000,
    },
)
@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_tags.sql'])
async def test_fetch_by_geo_and_tags(taxi_feeds, tags, expected_feeds):
    await taxi_feeds.run_task('distlock/clustering-worker')
    response = await taxi_feeds.post(
        '/v1/fetch_by_geo',
        json={
            'service': 'service',
            'geo': {
                'bottom_left': {'latitude': 55, 'longitude': 38},
                'top_right': {'latitude': 56, 'longitude': 39},
                'type': 'box',
            },
            'channels': ['geo_channel'],
            'tags': tags,
        },
    )

    assert response.status_code == 200

    feeds = [int(feed['feed_id'][0:1]) for feed in response.json()['feed']]
    feeds.sort(key=lambda fid: -fid)
    assert feeds == expected_feeds


@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_tags.sql'])
async def test_fetch_caching(taxi_feeds, pgsql, testpoint):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['channel'],
            'tags': ['a'],
        },
    )
    assert response.status_code == 400

    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'caching_service',
            'channels': ['channel'],
            'feed_ids': ['999c69c8afe947ba887fd6404428b31c'],
            'tags': ['a'],
        },
    )
    assert response.status_code == 400
