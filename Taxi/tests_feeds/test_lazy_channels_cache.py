import pytest


@pytest.mark.now('2018-12-10T00:00:00+00:00')
@pytest.mark.pgsql('feeds-pg', files=['fetch_lazy.sql'])
async def test_load_missing(taxi_feeds, testpoint):
    await taxi_feeds.enable_testpoints()

    @testpoint('get-channels-from-cache')
    def get_channels_from_cache(data):
        pass

    @testpoint('load-missing-channels')
    def load_missing_channels(data):
        pass

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['user:111111'],
            'earlier_than': '2018-12-31T00:00:00Z',
        },
    )
    assert response.status_code == 200

    from_cache = await get_channels_from_cache.wait_call()
    assert from_cache['data']['channels'] == []

    missing = await load_missing_channels.wait_call()
    assert missing['data']['channels'] == ['user:111111']

    await taxi_feeds.invalidate_caches(clean_update=False)

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'caching_service',
            'channels': ['user:111111', 'user:222222', 'city:moscow'],
            'earlier_than': '2018-12-31T00:00:00Z',
        },
    )
    assert response.status_code == 200

    from_cache = await get_channels_from_cache.wait_call()
    assert from_cache['data']['channels'] == ['user:111111']

    missing = await load_missing_channels.wait_call()
    assert set(missing['data']['channels']) == set(
        ['user:222222', 'city:moscow'],
    )
