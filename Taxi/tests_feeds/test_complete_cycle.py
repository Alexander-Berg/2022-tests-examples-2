import datetime

import pytest


def make_channels(channels_list):
    return [{'channel': name} for name in channels_list]


async def create_request(request_id, service, payload, channels, taxi_feeds):
    expire = datetime.datetime.now() + datetime.timedelta(hours=12)

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire.isoformat() + 'Z',
            'payload': payload,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200


async def fetch_request(
        service, channels, taxi_feeds, etag=None, no_changes=False,
):
    request_body = {'service': service, 'channels': channels}
    if etag:
        request_body['etag'] = etag
    response = await taxi_feeds.post('/v1/fetch', json=request_body)

    if etag and no_changes:
        assert response.status_code == 304
    else:
        assert response.status_code == 200
        return response.json()


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'max_feed_ttl_hours': 1,
            'polling_delay_sec': 60,
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
@pytest.mark.now('2019-12-31T23:00:00+0000')
async def test_create_and_fetch(taxi_feeds, pgsql, mocked_time):
    expire = '2020-02-09T09:00:00.000000Z'
    payload = {'text': 'Happy new year'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire,
            'payload': payload,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200

    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 0, 30))

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert len(data) == 1

    assert data[0]['payload'] == payload
    assert data[0]['created'] == '2019-12-31T23:00:00+0000'


@pytest.mark.now('2019-12-31T23:00:00+0000')
@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
async def test_create_many_and_fetch(taxi_feeds, mocked_time):
    expire = '2020-01-19T09:00:00.000000Z'
    payload_0 = {'text': 'Happy new year!'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire,
            'payload': payload_0,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200

    payload_1 = {'text': 'Happy old new year!'}

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire,
            'payload': payload_1,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200

    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 0, 30))

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert len(data) == 2


@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
async def test_changed_etag(taxi_feeds):
    expire = datetime.datetime.now() + datetime.timedelta(hours=1)
    payload_0 = {'text': 'Happy new year!'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire.isoformat() + 'Z',
            'payload': payload_0,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()

    etag = data['etag']

    payload_1 = {'text': 'Happy old new year!'}

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire.isoformat() + 'Z',
            'payload': payload_1,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert etag != data['etag']


@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
async def test_no_changed_etag(taxi_feeds):
    expire = datetime.datetime.now() + datetime.timedelta(hours=1)
    payload_0 = {'text': 'Happy new year!'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire.isoformat() + 'Z',
            'payload': payload_0,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()

    etag = data['etag']

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert etag == data['etag']


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'max_feed_ttl_hours': 1,
            'polling_delay_sec': 60,
        },
    },
)
@pytest.mark.now('2019-12-31T23:00:00+0000')
@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
async def test_create_fetch_and_remove_from_channel(taxi_feeds, mocked_time):
    payload = {'text': 'Happy new year'}
    channels = ['driver:dbid:uuid0', 'driver:dbid:uuid1']
    service = 'service'
    request_id = 'request_id_0'

    await create_request(request_id, service, payload, channels, taxi_feeds)

    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 0, 30))

    data = await fetch_request(service, channels, taxi_feeds)
    first_feed_id = data['feed'][0]['feed_id']

    assert len(data['feed']) == 1

    await fetch_request(
        service, channels, taxi_feeds, etag=data['etag'], no_changes=True,
    )

    payload = {'text': 'Good morning!'}
    await create_request(request_id, service, payload, channels, taxi_feeds)

    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 1, 30))

    data = await fetch_request(
        service, channels, taxi_feeds, etag=data['etag'],
    )
    assert len(data['feed']) == 2

    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': service,
            'feed_id': first_feed_id,
            'channels': [channels[0]],
        },
    )
    assert response.status_code == 200

    data = await fetch_request(
        service, [channels[0]], taxi_feeds, etag=data['etag'],
    )
    assert len(data['feed']) == 1

    data = await fetch_request(
        service, [channels[1]], taxi_feeds, etag=data['etag'],
    )
    assert len(data['feed']) == 2

    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': service,
            'feed_id': first_feed_id,
            'channels': [channels[1]],
        },
    )
    assert response.status_code == 200

    data = await fetch_request(
        service, [channels[1]], taxi_feeds, etag=data['etag'],
    )
    assert len(data['feed']) == 1


@pytest.mark.now('2019-12-31T23:00:00+0000')
@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
async def test_undying_feeds(taxi_feeds, pgsql, mocked_time):
    payload = {'text': 'Happy new year'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'payload': payload,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200
    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 0, 30))

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert len(data) == 1

    assert data[0]['payload'] == payload


@pytest.mark.now('2019-12-31T23:00:00+0000')
@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
async def test_sort_by_publish_at(taxi_feeds, mocked_time, pgsql):
    expire = '2022-12-31T23:01:00.000000Z'
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire,
            'payload': {'text': 1},
            'channels': make_channels(channels),
            'publish_at': '2019-12-31T23:01:00.000000Z',
        },
    )
    assert response.status_code == 200

    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 0, 30))

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire,
            'payload': {'text': 0},
            'channels': make_channels(channels),
        },
    )
    assert response.status_code == 200

    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 1, 30))

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    data = response.json()

    feeds = data['feed']

    assert len(feeds) == 2

    assert feeds[0]['payload'] == {'text': 1}
    assert feeds[1]['payload'] == {'text': 0}

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire,
            'payload': {'text': 2},
            'channels': make_channels(channels),
            'publish_at': '2019-12-31T23:03:00.000000Z',
        },
    )
    assert response.status_code == 200

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    data = response.json()

    feeds = data['feed']

    assert len(feeds) == 2

    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 10, 0))

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    data = response.json()

    feeds = data['feed']

    assert len(feeds) == 3


@pytest.mark.now('2019-12-31T23:00:00+0000')
@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
async def test_remove_from_not_existed_channel(taxi_feeds, pgsql, mocked_time):
    expire = '2022-12-31T23:01:00.000000Z'
    payload_0 = {'text': 'Happy new year!'}
    channels = ['city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'payload': payload_0,
            'channels': make_channels(channels),
            'expire': expire,
        },
    )

    assert response.status_code == 200

    mocked_time.set(datetime.datetime(2019, 12, 31, 23, 1, 0))

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': [
                'city:moscow;position:director',
                'city:moscow;position:manager',
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert len(data) == 1
    feed_id = data[0]['feed_id']

    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': service,
            'feed_id': feed_id,
            'channels': ['city:moscow;position:manager'],
        },
    )
    assert response.status_code == 200

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert len(data) == 1

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': [
                'city:moscow;position:director',
                'city:moscow;position:manager',
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert not data


pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'max_feed_ttl_hours': 1,
            'polling_delay_sec': 60,
        },
    },
)


@pytest.mark.now('2019-12-31T23:00:00+0000')
@pytest.mark.pgsql('feeds-pg', files=['test_create_and_fetch.sql'])
async def test_create_and_fetch_earlier_then_not_included(
        taxi_feeds, pgsql, mocked_time,
):
    expire = '2020-02-09T09:00:00.000000Z'
    payload = {'text': 'Happy new year'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': expire,
            'payload': payload,
            'channels': make_channels(channels),
        },
    )

    assert response.status_code == 200

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert not data
