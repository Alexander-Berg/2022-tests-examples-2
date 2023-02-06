import datetime

import pytest


def make_channels(channels_list):
    return [{'channel': name} for name in channels_list]


def make_service_to_id(pgsql):
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT id, name FROM services')
    result = {}
    for row in cursor:
        result[row[1]] = row[0]
    return result


def make_channel_to_id(pgsql):
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT id, name FROM channels')
    result = {}
    for row in cursor:
        result[row[1]] = row[0]
    return result


def uuid_to_str(uuid):
    return uuid.replace('-', '')


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_smoke(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id_0',
            'service': 'service',
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': {'text': 'Very important feed '},
            'channels': [{'channel': 'park:dbid'}],
        },
    )

    assert response.status_code == 200
    created = []
    feed_id = response.json()['feed_ids'].get('park:dbid')
    created.append(feed_id)

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id_0',
            'service': 'service',
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': {'text': 'Very important feed 2'},
            'channels': [{'channel': 'park:dbid'}],
        },
    )

    assert response.status_code == 200
    feed_id = response.json()['feed_ids'].get('park:dbid')
    created.append(feed_id)

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT id, name FROM services')

    services = cursor.fetchall()

    assert len(services) == 1
    assert services[0][1] == 'service'

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT name FROM channels')

    channels = cursor.fetchall()

    assert len(channels) == 1
    assert channels[0][0] == 'park:dbid'
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT feed_id FROM feeds')
    feed_ids = [row[0].replace('-', '') for row in cursor]
    assert len(feed_ids) == len(created)
    assert set(feed_ids) == set(created)


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_create(taxi_feeds, pgsql):
    payload = {'text': 'Happy new year'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': payload,
            'channels': make_channels(channels),
            'status': 'read',
            'meta': {'var': 0},
        },
    )

    assert response.status_code == 200

    services = make_service_to_id(pgsql)
    channels = make_channel_to_id(pgsql)

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        'SELECT feed_id, service_id, request_id, payload FROM feeds',
    )

    feeds = cursor.fetchall()

    assert len(feeds) == 1
    feed = feeds[0]

    assert feed[1] == services[service]
    assert feed[2] == request_id
    assert feed[3] == payload

    cursor.execute(
        'SELECT feed_id, channel_id, status, meta FROM feed_channel_status',
    )
    feed_channel_status = cursor.fetchall()
    assert len(feed_channel_status) == len(channels)
    for row in feed_channel_status:
        feed_id, channel, status, meta = row
        assert feed_id == feed[0]
        assert channel in channels.values()
        assert status == 'read'
        assert meta == {'var': 0}


async def test_create_child_with_another_request_id(taxi_feeds, pgsql):
    payload = {'text': 'Happy new year'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'

    request_id = 'request_id_0'
    another_request_id = 'request_id_1'

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
    parent_feed_id = next(iter(response.json()['feed_ids'].items()))[1]

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': another_request_id,
            'parent_feed_id': parent_feed_id,
            'service': service,
            'payload': payload,
            'channels': make_channels(channels),
        },
    )
    assert response.status_code == 200
    feed_id = next(iter(response.json()['feed_ids'].items()))[1]

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(f'SELECT request_id FROM feeds WHERE feed_id=\'{feed_id}\'')

    assert next(cursor)[0] == request_id


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'max_feed_ttl_hours': 1,
            'polling_delay_sec': 60,
        },
    },
)
async def test_create_expire_not_soon(taxi_feeds, pgsql):
    expire = datetime.datetime.now() + datetime.timedelta(hours=48)
    payload = {'text': 'Happy new year'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

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

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT expire FROM feeds')

    feeds = cursor.fetchall()

    assert len(feeds) == 1
    feed = feeds[0]
    assert (
        feed[0].timestamp()
        < (expire - datetime.timedelta(hours=1)).timestamp()
    )


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
        },
    },
)
async def test_create_expire_soon(taxi_feeds, pgsql):
    expire = datetime.datetime.now() + datetime.timedelta(hours=1)
    payload = {'text': 'Happy new year'}
    channels = ['park:dbid', 'city:moscow;position:director']
    service = 'service'
    request_id = 'request_id_0'

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

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT expire FROM feeds')

    feeds = cursor.fetchall()

    assert len(feeds) == 1
    feed = feeds[0]
    assert (
        feed[0].timestamp()
        <= (datetime.datetime.now() + datetime.timedelta(hours=23)).timestamp()
    )


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_etags(taxi_feeds, pgsql):
    payload = {'text': 'Happy new year'}
    channels = ['park:dbid', 'city:moscow;position:director']

    service = 'service'
    request_id = 'request_id'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id,
            'service': service,
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': payload,
            'channels': make_channels(channels),
        },
    )
    assert response.status_code == 200

    services_to_id = make_service_to_id(pgsql)

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT id, name, service_id, etag FROM channels')
    channels_db = cursor.fetchall()
    old_etags = {}
    assert len(channels_db) == 2
    for channel in channels_db:
        assert channel[1] in channels
        assert channel[2] == services_to_id[service]
        old_etags[channel[1]] = channel[3]

    channels = [
        'park:dbid',
        'city:moscow;position:director',
        'city:moscow;position:cleaners',
    ]
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id + '1',
            'service': service,
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': payload,
            'channels': make_channels(channels),
        },
    )
    assert response.status_code == 200

    cursor.execute('SELECT id, name, service_id, etag FROM channels')
    channels_db = cursor.fetchall()
    assert len(channels_db) == 3
    for channel in channels_db:
        if channel[1] in old_etags:
            assert channel[3] != old_etags[channel[1]]
        old_etags[channel[1]] = channel[3]

    channels = ['park:dbid', 'city:moscow;position:cleaners']
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': request_id + '1',
            'service': service,
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': payload,
            'channels': make_channels(channels),
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT id, name, service_id, etag FROM channels')
    channels_db = cursor.fetchall()
    assert len(channels_db) == 3

    for channel in channels_db:
        if channel[1] in old_etags.keys() - set(channels):
            assert channel[3] == old_etags[channel[1]]
        else:
            assert channel[3] != old_etags[channel[1]]


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_create_with_params(taxi_feeds, pgsql, load_json):
    response = await taxi_feeds.post(
        '/v1/create', json=load_json('request_with_params.json'),
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()

    cursor.execute(
        """
        SELECT feed_id, payload FROM feeds
        WHERE request_id = 'test_create_with_params'
        """,
    )
    feeds = list(cursor.fetchall())
    assert len(feeds) == 1

    assert feeds[0][1] == {
        'title': 'Hi, {user}! \\{no_param\\}',
        'text': 'Here is your {value}{sign}',
    }
    feed_id = feeds[0][0]

    cursor.execute(
        f"""
        SELECT C.name, FP.payload_overrides, FP.payload_params
          FROM feed_payload FP
        JOIN feed_channel_status S
          ON (S.feed_id = FP.feed_id AND S.channel_id = FP.channel_id)
        JOIN channels C ON (C.id = S.channel_id)
        WHERE FP.feed_id = '{feed_id}'
        ORDER BY C.name
        """,
    )
    feed_payloads = list(cursor.fetchall())

    assert len(feed_payloads) == 3
    assert feed_payloads == [
        (
            'user:1',
            None,
            '{"(value,100)","(sign,$)","(user,\\"Vladimir 1\\")"}',
        ),
        (
            'user:2',
            None,
            '{"(value,200)","(sign,₽)","(user,\\"Vladimir 2\\")"}',
        ),
        (
            'user:3',
            {
                'title': 'Unique title for {user}',
                'new_field': 'Unique field for {user}',
            },
            '{"(value,300)","(sign,\\" rub.\\")","(user,\\"Vladimir 3\\")"}',
        ),
    ]


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_create_with_escaped_braces_params(taxi_feeds, pgsql, load_json):
    payload = {'text': 'Happy \\{year\\} new year!'}
    channels = ['park:dbid']

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id',
            'service': 'service',
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': payload,
            'channels': make_channels(channels),
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """
        SELECT C.name, F.payload, S.status
        FROM feeds F
        JOIN feed_channel_status S ON (S.feed_id = F.feed_id)
        JOIN channels C ON (C.id = S.channel_id)
        WHERE F.request_id = 'request_id'
        ORDER BY C.name
    """,
    )
    feeds = cursor.fetchall()
    assert len(feeds) == 1
    feed = feeds[0]

    assert feed[0] == 'park:dbid'
    assert feed[1] == {'text': 'Happy \\{year\\} new year!'}


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_duplicated_channel(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'err',
            'service': 'service',
            'expire': '2019-12-03T00:00:00.000000Z',
            'payload': {'title': 'title'},
            'channels': [
                {'channel': 'user:1'},
                {'channel': 'user:2'},
                {'channel': 'user:1'},
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_create_with_params_bad(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'err',
            'service': 'service',
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': {'title': '{param} is required'},
            'channels': [{'channel': 'user:1'}],
        },
    )
    assert response.status_code == 400

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'err',
            'service': 'service',
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': {
                'title': 'No param here, but it' 's contained in overrides',
            },
            'channels': [
                {
                    'channel': 'user:1',
                    'payload_overrides': {'title': '{param} is required'},
                },
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'format_str',
    [
        'Missing opening brace}',
        'Missing closing {brace',
        'Empty param name {}',
        '{Unexpected opening brace{}',
        '{unknown_parameter}',
    ],
)
@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_create_with_params_bad_format_str(
        taxi_feeds, format_str, pgsql,
):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'err',
            'service': 'service',
            'expire': '2019-12-03T00:00:00.000000Z',
            'payload': {'format_str': format_str},
            'channels': [
                {'channel': 'user:1', 'payload_params': {'param': 'value'}},
            ],
        },
    )
    assert response.status_code == 400


async def test_create_with_params_bad_publish_at(taxi_feeds):
    expire = datetime.datetime.now() + datetime.timedelta(hours=24)

    publish_at = datetime.datetime.now() + datetime.timedelta(hours=12)

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'err',
            'service': 'service',
            'expire': expire.isoformat() + 'Z',
            'payload': {'title': '{param} is required'},
            'channels': [{'channel': 'user:1'}],
            'publish_at': publish_at.isoformat() + 'Z',
        },
    )
    assert response.status_code == 400

    publish_at = datetime.datetime.now() + datetime.timedelta(hours=48)

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'err',
            'service': 'service',
            'expire': expire.isoformat() + 'Z',
            'payload': {'title': '{param} is required'},
            'channels': [{'channel': 'user:1'}],
            'publish_at': publish_at.isoformat() + 'Z',
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {'description': 'description', 'polling_delay_sec': 60},
    },
)
async def test_create_without_exipre_and_no_config_expire(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id_0',
            'service': 'service',
            'payload': {'text': 'Very important feed '},
            'channels': [{'channel': 'park:dbid'}],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT expire FROM feeds')

    feeds = cursor.fetchall()

    assert len(feeds) == 1
    assert feeds[0][0] is None


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'max_feed_ttl_hours': 1,
            'polling_delay_sec': 60,
        },
    },
)
async def test_create_without_exipre_and_config_expire(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id_0',
            'service': 'service',
            'payload': {'text': 'Very important feed '},
            'channels': [{'channel': 'park:dbid'}],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT expire FROM feeds')

    feeds = cursor.fetchall()

    assert len(feeds) == 1
    assert feeds[0][0] is not None


async def test_create_idempotency_token(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        headers={'X-Idempotency-Token': 'IdempotencyToken'},
        json={
            'request_id': 'request_id_0',
            'service': 'service',
            'payload': {'text': 'Very important feed '},
            'channels': [{'channel': 'park:dbid'}],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT count(*) FROM feeds')
    feeds_count = cursor.fetchall()

    response = await taxi_feeds.post(
        '/v1/create',
        headers={'X-Idempotency-Token': 'IdempotencyToken'},
        json={
            'request_id': 'request_id_0',
            'service': 'service',
            'payload': {'text': 'Very important feed '},
            'channels': [{'channel': 'park:dbid'}],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT count(*) FROM feeds')
    assert feeds_count == cursor.fetchall()


async def test_create_idempotency_token_payload_override(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        headers={'X-Idempotency-Token': 'token'},
        json={
            'request_id': 'request_id',
            'service': 'service',
            'payload': {'text': 'text'},
            'channels': [
                {'channel': 'user_1'},
                {'channel': 'user_2', 'payload_overrides': {'title': 'foo'}},
            ],
        },
    )

    assert response.status_code == 200


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_client_provided_feed_id(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'service': 'service',
            'request_id': 'request_id',
            'payload': {'text': 'text'},
            'channels': [
                {
                    'channel': 'has_feed_id',
                    'feed_id': 'b78a4c19beec418d9ec091ef1d146952',
                },
                {'channel': 'no_feed_id'},
            ],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """SELECT C.name, F.feed_id
           FROM feeds F
           JOIN feed_channel_status S ON (S.feed_id = F.feed_id)
           JOIN channels C ON (C.id = S.channel_id)
           ORDER BY C.name""",
    )

    feeds = cursor.fetchall()
    assert len(feeds) == 2
    assert feeds[0] == ('has_feed_id', 'b78a4c19-beec-418d-9ec0-91ef1d146952')
    assert feeds[1][0] == 'no_feed_id'
    assert feeds[1][1] != 'b78a4c19-beec-418d-9ec0-91ef1d146952'


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_client_provided_bad_feed_id(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'service': 'service',
            'payload': {'text': 'text'},
            'channels': [{'channel': 'channel', 'feed_id': 'bad uuid'}],
        },
    )

    assert response.status_code == 400


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_idempotency(taxi_feeds, pgsql):
    request_data = {
        'request_id': 'request_id_0',
        'service': 'service',
        'expire': '2019-12-03T12:21:48.203515Z',
        'payload': {'text': 'Very important feed '},
        'channels': [{'channel': 'park:dbid'}, {'channel': 'user:marge'}],
    }
    first_response = await taxi_feeds.post(
        '/v1/create',
        headers={'X-Idempotency-Token': 'IdempotencyToken'},
        json=request_data,
    )

    assert first_response.status_code == 200
    first_data = first_response.json()

    second_response = await taxi_feeds.post(
        '/v1/create',
        headers={'X-Idempotency-Token': 'IdempotencyToken'},
        json=request_data,
    )

    assert second_response.status_code == 200
    second_data = second_response.json()
    assert first_data == second_data


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {'description': 'description', 'polling_delay_sec': 60},
        'service_with_max_expire': {
            'description': 'description',
            'polling_delay_sec': 60,
            'max_feed_ttl_hours': 72,
        },
    },
)
@pytest.mark.now('2019-12-01T00:00:00Z')
@pytest.mark.parametrize('service', ['service', 'service_with_max_expire'])
async def test_create_parent_feed_expire(taxi_feeds, pgsql, service):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id_0',
            'service': service,
            'payload': {'text': 'Very important feed '},
            'channels': [{'channel': 'user:1'}],
            'expire': '2019-12-03T00:00:00.000000Z',
        },
    )

    assert response.status_code == 200
    parent_feed_id = response.json()['feed_ids']['user:1']

    await taxi_feeds.invalidate_caches()

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id_0',
            'service': service,
            'parent_feed_id': parent_feed_id,
            'payload': {'text': 'Very important feed '},
            'channels': [{'channel': 'user:1'}],
        },
    )

    assert response.status_code == 200
    child_feed_id = response.json()['feed_ids']['user:1']

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT feed_id, expire FROM feeds;')
    expires = {uuid_to_str(row[0]): row[1] for row in cursor}

    assert expires[child_feed_id] == expires[parent_feed_id]
