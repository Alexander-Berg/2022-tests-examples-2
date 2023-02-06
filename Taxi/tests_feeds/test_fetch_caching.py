import pytest


def _feed_ids(response):
    return [feed['feed_id'] for feed in response.json()['feed']]


async def _set_caching_mode(taxi_feeds, taxi_config, cache_enabled):
    taxi_config.set_values(
        {
            'FEEDS_SERVICES': {
                'caching_service': {
                    'cache': {
                        'enable': cache_enabled,
                        'channels_enable': cache_enabled,
                    },
                    'description': 'test',
                    'feed_count': 2,
                    'max_feed_ttl_hours': 24,
                    'polling_delay_sec': 60,
                    'polling_delay_randomize_sec': 0,
                },
            },
        },
    )
    await taxi_feeds.invalidate_caches()


@pytest.mark.now('2018-12-10T00:00:00+00:00')
@pytest.mark.pgsql('feeds-pg', files=['fetch_caching.sql'])
async def test_fetch_earlier_than(taxi_feeds, pgsql):
    # Fetch first 2 youngest records
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['user:111111', 'city:moscow'],
            'earlier_than': '2018-12-31T00:00:00Z',
        },
    )
    assert response.status_code == 200
    assert _feed_ids(response) == [
        '555c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
    ]

    # Fetch older records (older than 444...)
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['user:111111', 'city:moscow'],
            'earlier_than': '2018-12-04T00:00:00.0Z',
        },
    )
    assert response.status_code == 200
    assert _feed_ids(response) == ['333c69c8afe947ba887fd6404428b31c']


@pytest.mark.now('2018-12-10T00:00:00+00:00')
@pytest.mark.pgsql('feeds-pg', files=['fetch_caching.sql'])
async def test_fetch_newer_than(taxi_feeds, pgsql, testpoint):
    # Fetch first 2 oldest records
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['user:111111', 'city:moscow'],
            'newer_than': '2018-11-01T00:00:00Z',
        },
    )
    assert response.status_code == 200
    assert _feed_ids(response) == [
        '333c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
    ]

    # Fetch newer records (newer than 444...)
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['user:111111', 'city:moscow'],
            'newer_than': '2018-12-04T00:00:00Z',
        },
    )
    assert response.status_code == 200
    assert _feed_ids(response) == ['555c69c8afe947ba887fd6404428b31c']


@pytest.mark.now('2018-12-16T00:00:00+00:00')
@pytest.mark.pgsql('feeds-pg', files=['fetch_caching.sql'])
async def test_fetch_by_id(taxi_feeds, pgsql, testpoint):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'caching_service',
            'channels': ['user:111111', 'city:moscow'],
            'feed_ids': [
                '111c69c8afe947ba887fd6404428b31c',
                '222c69c8afe947ba887fd6404428b31c',
                '333c69c8afe947ba887fd6404428b31c',
                '444c69c8afe947ba887fd6404428b31c',
                '555c69c8afe947ba887fd6404428b31c',
                '666c69c8afe947ba887fd6404428b31c',
                '777c69c8afe947ba887fd6404428b31c',
                '888c69c8afe947ba887fd6404428b31c',
                '999c69c8afe947ba887fd6404428b31c',
            ],
        },
    )
    assert response.status_code == 200
    assert _feed_ids(response) == [
        '333c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
        '555c69c8afe947ba887fd6404428b31c',
        '888c69c8afe947ba887fd6404428b31c',
    ]


@pytest.mark.now('2018-12-10T00:00:00+00:00')
@pytest.mark.pgsql('feeds-pg', files=['fetch_caching.sql'])
@pytest.mark.parametrize(
    'request_type,request_value',
    [
        ('earlier_than', '2018-12-31T00:00:00Z'),
        ('earlier_than', '2018-12-04T00:00:00.0Z'),
        ('newer_than', '2018-11-01T00:00:00Z'),
        ('newer_than', '2018-12-04T00:00:00Z'),
    ],
)
async def test_fetch_cache_vs_nocache(
        taxi_feeds, taxi_config, pgsql, testpoint, request_type, request_value,
):
    async def _fetch(caching_enabled):
        await _set_caching_mode(taxi_feeds, taxi_config, caching_enabled)

        response = await taxi_feeds.post(
            '/v1/fetch',
            json={
                'service': 'caching_service',
                'channels': ['user:111111', 'city:moscow'],
                request_type: request_value,
            },
        )
        assert response.status_code == 200
        return response.json()

    cached = await _fetch(True)
    notcached = await _fetch(False)
    assert cached == notcached


@pytest.mark.now('2018-12-10T00:00:00+00:00')
@pytest.mark.pgsql('feeds-pg', files=['fetch_caching.sql'])
async def test_fetch_by_id_cache_vs_nocache(
        taxi_feeds, taxi_config, pgsql, testpoint,
):
    async def _fetch_by_id(caching_enabled):
        await _set_caching_mode(taxi_feeds, taxi_config, caching_enabled)

        response = await taxi_feeds.post(
            '/v1/fetch_by_id',
            json={
                'service': 'caching_service',
                'channels': ['user:111111', 'city:moscow'],
                'feed_ids': [
                    '111c69c8afe947ba887fd6404428b31c',
                    '222c69c8afe947ba887fd6404428b31c',
                    '333c69c8afe947ba887fd6404428b31c',
                    '444c69c8afe947ba887fd6404428b31c',
                    '555c69c8afe947ba887fd6404428b31c',
                    '666c69c8afe947ba887fd6404428b31c',
                    '777c69c8afe947ba887fd6404428b31c',
                    '888c69c8afe947ba887fd6404428b31c',
                    '999c69c8afe947ba887fd6404428b31c',
                ],
            },
        )
        assert response.status_code == 200
        return response.json()

    cached = await _fetch_by_id(True)
    notcached = await _fetch_by_id(False)
    cached['feed'] = sorted(cached['feed'], key=lambda x: x['feed_id'])
    notcached['feed'] = sorted(notcached['feed'], key=lambda x: x['feed_id'])
    assert cached == notcached


@pytest.mark.pgsql('feeds-pg', files=['channels_cache.sql'])
async def test_channels_cache(taxi_feeds, testpoint, taxi_config):
    @testpoint('channels-cache-finish')
    def channels_cache_finish(data):
        pass

    await taxi_feeds.enable_testpoints()
    value = await channels_cache_finish.wait_call()
    assert value['data'] == {
        'caching_service': {
            'user:111111': {
                'etag': '358af30761eb454db8af9c8f9666e5a8',
                'id': 1,
                'name': 'user:111111',
                'service_id': 100,
            },
        },
    }

    taxi_config.set_values(
        {
            'FEEDS_SERVICES': {
                'caching_service': {
                    'cache': {'enable': True, 'channels_enable': False},
                    'description': 'test',
                    'feed_count': 2,
                    'max_feed_ttl_hours': 24,
                    'polling_delay_sec': 60,
                    'polling_delay_randomize_sec': 0,
                },
                'other_service': {
                    'cache': {'enable': True, 'channels_enable': True},
                    'description': 'other test service',
                    'expirable_status': {
                        'default_status': 'viewed',
                        'reset_meta': True,
                    },
                    'max_feed_ttl_hours': 100,
                    'polling_delay_sec': 60,
                    'polling_delay_randomize_sec': 0,
                },
            },
        },
    )
    await taxi_feeds.invalidate_caches()

    value = await channels_cache_finish.wait_call()
    assert value['data'] == {
        'other_service': {
            'city:moscow': {
                'etag': '458af30761eb454db8af9c8f9666e5a8',
                'id': 0,
                'name': 'city:moscow',
                'service_id': 102,
            },
        },
    }


@pytest.mark.now('2018-12-10T00:00:00+00:00')
@pytest.mark.pgsql('feeds-pg', files=['fetch_low_feed_count.sql'])
async def test_fetch_low_feed_count(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['channel_0', 'channel_1'],
            'earlier_than': '2018-12-10T00:00:00Z',
        },
    )
    assert response.status_code == 200
    assert _feed_ids(response) == [
        '999c69c8afe947ba887fd6404428b31c',
        '888c69c8afe947ba887fd6404428b31c',
    ]

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['channel_0', 'channel_1'],
            'newer_than': '2018-12-01T00:00:00Z',
        },
    )
    assert response.status_code == 200
    assert _feed_ids(response) == [
        '222c69c8afe947ba887fd6404428b31c',
        '333c69c8afe947ba887fd6404428b31c',
    ]
