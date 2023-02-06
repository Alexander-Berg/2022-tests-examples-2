import pytest


@pytest.mark.parametrize(
    'media_info,image_id',
    [
        (
            {'screen_height': 100, 'screen_width': 140},
            (
                'http://mds.yandex.net/get-feeds-media/1396527/'
                'd8cdff968fc50bf75058753ca0786f38f2b21ae2/media-1000-750'
            ),
        ),
        (
            {'screen_height': 2000, 'screen_width': 2000},
            (
                'http://mds.yandex.net/get-feeds-media/1396527/'
                'd8cdff968fc50bf75058753ca0786f38f2b21ae2/media-2000-2000'
            ),
        ),
        (
            {'screen_height': 750, 'screen_width': 702},
            (
                'http://mds.yandex.net/get-feeds-media/1396527/'
                'd8cdff968fc50bf75058753ca0786f38f2b21ae2/media-1000-750'
            ),
        ),
        (
            None,
            (
                'http://mds.yandex.net/get-feeds-media/1396527/'
                'd8cdff968fc50bf75058753ca0786f38f2b21ae2/media-1000-1000'
            ),
        ),
    ],
)
@pytest.mark.now('2018-12-05T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_convert_media_id_to_url.sql'])
async def test_convert_media_id_to_url_avatars(
        taxi_feeds, pgsql, media_info, image_id,
):
    data = {'service': 'service', 'channels': ['driver:1']}
    if media_info:
        data.update({'media_info': media_info})

    response = await taxi_feeds.post('/v1/fetch', json=data)

    assert response.status_code == 200
    payloads = [feed['payload'] for feed in response.json()['feed']]
    assert payloads == [
        {'media_id': image_id, 'text': 'Best order you can do!'},
        {'text': 'Tariff changes: get extra pie'},
    ]


@pytest.mark.now('2018-12-05T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_convert_media_id_to_url.sql'])
async def test_convert_media_id_to_url_s3(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch', json={'service': 'service', 'channels': ['driver:2']},
    )
    assert response.status_code == 200

    payloads = [feed['payload'] for feed in response.json()['feed']]
    assert payloads == [
        {
            'text': 'Media in S3',
            'media_id': 'https://feeds.s3.yandex.net/taxi/media2',
        },
    ]


@pytest.mark.now('2018-12-05T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_convert_media_id_to_url.sql'])
async def test_custom_media_field(taxi_feeds, pgsql):
    image_id = (
        'http://mds.yandex.net/get-feeds-media/1396527/'
        'd8cdff968fc50bf75058753ca0786f38f2b21ae2/media-1000-750'
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'other_service',
            'channels': ['user:1'],
            'media_info': {'screen_height': 100, 'screen_width': 140},
        },
    )

    assert response.status_code == 200
    payloads = [feed['payload'] for feed in response.json()['feed']]
    assert payloads == [
        {'content': image_id, 'text': 'Test custom media_id field name'},
    ]


@pytest.mark.now('2018-12-05T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_convert_media_id_to_url.sql'])
@pytest.mark.parametrize(
    'request_autoscale_mode,service_autoscale_mode,image_url',
    [
        (None, None, 'media-100-100'),
        (None, 'disabled', 'orig'),
        (None, 'server', 'media-100-100'),
        (None, 'client', 'media-{w}x{h}'),
        ('disabled', None, 'orig'),
        ('server', None, 'media-100-100'),
        ('client', None, 'media-{w}x{h}'),
        ('server', 'client', 'media-100-100'),
        ('client', 'server', 'media-{w}x{h}'),
    ],
)
async def test_autoscale_modes(
        taxi_feeds,
        taxi_config,
        request_autoscale_mode,
        service_autoscale_mode,
        image_url,
        pgsql,
):
    taxi_config.set_values(
        {
            'FEEDS_SERVICES': {
                'other_service': {
                    'description': 'description',
                    'feed_count': 3,
                    'max_feed_ttl_hours': 24,
                    'polling_delay_sec': 60,
                    'media': {
                        'autoscale_mode': service_autoscale_mode,
                        'media_name_template': 'media-{w}x{h}',
                    },
                },
            },
        },
    )
    await taxi_feeds.invalidate_caches()

    expected_image_url = (
        f'http://mds.yandex.net/get-feeds-media/1396527/'
        f'd8cdff968fc50bf75058753ca0786f38f2b21ae2/{image_url}'
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'other_service',
            'channels': ['user:1'],
            'media_info': {
                'screen_height': 100,
                'screen_width': 94,
                'autoscale_mode': request_autoscale_mode,
            },
        },
    )

    assert response.status_code == 200

    image_url = response.json()['feed'][0]['payload']['media_id']
    assert image_url == expected_image_url
