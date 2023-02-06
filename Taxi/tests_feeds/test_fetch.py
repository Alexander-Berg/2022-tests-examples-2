import pytest

import tests_feeds.feeds_common as fc


async def test_smoke(taxi_feeds, pgsql):
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'Hi!'},
        '11111',
        '2019-12-31 23:59:59Z',
        pgsql,
    )
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200


async def test_bad_request(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={'service': 'service_no_exist', 'channels': ['park:dbid']},
    )

    assert response.status_code == 400

    response = await taxi_feeds.post(
        '/v1/fetch', json={'service': 'service', 'channels': []},
    )

    assert response.status_code == 400


async def test_etags(taxi_feeds, pgsql):
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'Happy new year!'},
        '11111',
        '2019-12-11 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data['feed'][0]['payload'] == {'text': 'Happy new year!'}

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'etag': data['etag'],
        },
    )

    assert response.status_code == 304

    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'Hi!'},
        '11111',
        '2019-12-31 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'etag': data['etag'],
        },
    )

    assert response.status_code == 200

    data = response.json()

    fc.insert_feed_in_db(
        'service',
        ['park:112132313'],
        {'text': 'Hi!'},
        '11111',
        '2019-12-31 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'etag': data['etag'],
        },
    )
    assert response.status_code == 304


async def test_channel_no_exist(taxi_feeds, pgsql):
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 0!'},
        '11111',
        '2018-12-31 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={'service': 'service', 'channels': ['city:moscow;position:ceo']},
    )
    assert response.status_code == 200


async def test_channel_no_exist_and_exist(taxi_feeds, pgsql):
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 0!'},
        '11111',
        '2018-12-11 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': [
                'city:moscow;position:ceo',
                'city:moscow;position:director',
            ],
        },
    )
    assert response.status_code == 200
    assert len(response.json()['feed']) == 1


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
async def test_only_last_3(taxi_feeds, pgsql):
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 0!'},
        '11111',
        '2018-12-31 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 1!'},
        '11111',
        '2019-01-01 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 2!'},
        '11111',
        '2019-01-02 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 3!'},
        '11111',
        '2019-01-03 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 4!'},
        '11111',
        '2019-01-04 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data['feed']) == 3
    assert data['has_more']

    assert data['feed'][0]['payload'] == {'text': 'number 4!'}
    assert data['feed'][0]['created'] == '2019-01-04T23:59:59+0000'

    assert data['feed'][1]['payload'] == {'text': 'number 3!'}
    assert data['feed'][1]['created'] == '2019-01-03T23:59:59+0000'

    assert data['feed'][2]['payload'] == {'text': 'number 2!'}
    assert data['feed'][2]['created'] == '2019-01-02T23:59:59+0000'


@pytest.mark.config(
    FEEDS_SERVICES={
        'service_not_in_db': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
async def test_service_not_in_db(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service_not_in_db',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
async def test_only_last_3_and_3_exist(taxi_feeds, pgsql):
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 0!'},
        '11111',
        '2018-12-31 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 1!'},
        '11111',
        '2019-01-01 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 2!'},
        '11111',
        '2019-01-02 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data['feed']) == 3
    assert not data['has_more']


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
async def test_only_last_3_and_2_exist(taxi_feeds, pgsql):
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 0!'},
        '11111',
        '2018-12-31 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 1!'},
        '11111',
        '2019-01-01 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data['feed']) == 2
    assert not data['has_more']


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
async def test_earlier_than(taxi_feeds, pgsql):
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 0!'},
        '11111',
        '2018-12-31 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 1!'},
        '11111',
        '2019-01-01 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 2!'},
        '11111',
        '2019-01-02 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 3!'},
        '11111',
        '2019-01-03 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 4!'},
        '11111',
        '2019-01-04 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 5!'},
        '11111',
        '2019-01-05 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 6!'},
        '11111',
        '2019-01-06 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 7!'},
        '11111',
        '2019-01-07 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 8!'},
        '11111',
        '2019-01-08 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 9!'},
        '11111',
        '2019-01-09 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 10!'},
        '11111',
        '2019-01-10 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 11!'},
        '11111',
        '2020-01-11 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 12!'},
        '11111',
        '2020-01-12 23:59:59Z',
        pgsql,
    )
    fc.insert_feed_in_db(
        'service',
        ['city:moscow;position:director'],
        {'text': 'number 13!'},
        '11111',
        '2021-01-13 23:59:59Z',
        pgsql,
    )

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'earlier_than': '2019-01-05T23:59:00.000000Z',
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert len(data) == 5


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'service',
            'feed_count': 4,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_newer_then.sql'])
@pytest.mark.now('2019-12-12T00:00:00Z')
async def test_newer_then(taxi_feeds):

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['test_further_then'],
            'newer_than': '2018-12-01T01:00:00.000000Z',
        },
    )

    assert response.status_code == 200

    data = response.json()['feed']
    assert [x['feed_id'] for x in data] == [
        '222c69c8afe947ba887fd6404428b31c',
        '333c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
        '555c69c8afe947ba887fd6404428b31c',
    ]


@pytest.mark.config(
    FEEDS_SERVICES={
        'test_removed': {
            'description': 'Service for unpublished test',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_removed.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_removed(taxi_feeds):
    # Message 111... is published in 'city:moscow' and
    #                   removed from 'user:111111'
    # Message 222... is vice versa
    # Message 333... is published in both channels
    # Request must return message 333... only

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'test_removed',
            'channels': ['city:moscow', 'user:111111'],
        },
    )

    assert response.status_code == 200
    assert response.json()['feed'] == [
        {
            'feed_id': '333c69c8afe947ba887fd6404428b31c',
            'package_id': 'p1',
            'request_id': 'request_1',
            'created': '2018-12-01T00:00:00+0000',
            'expire': '2019-12-01T00:00:00+0000',
            'payload': {},
            'last_status': {
                'created': '2018-12-01T00:00:00+0000',
                'status': 'published',
            },
        },
    ]


@pytest.mark.now('2018-12-03T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_last_status.sql'])
async def test_last_status(taxi_feeds, load_json):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={'service': 'service', 'channels': ['channel:1', 'channel:2']},
    )

    assert response.status_code == 200
    assert response.json() == load_json('test_last_status_response.json')


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_same_publish_at_feeds.sql'])
@pytest.mark.now('2018-12-10T00:00:00Z')
async def test_same_publish_at(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert {x['feed_id'] for x in data['feed']} == {
        '666c69c8afe947ba887fd6404428b31c',
        '555c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
        '333c69c8afe947ba887fd6404428b31c',
        '222c69c8afe947ba887fd6404428b31c',
    }
    assert data['has_more']

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'earlier_than': '2018-12-03T00:00:00.000000Z',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert {x['feed_id'] for x in data['feed']} == {
        '555c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
        '333c69c8afe947ba887fd6404428b31c',
        '222c69c8afe947ba887fd6404428b31c',
    }
    assert data['has_more']

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'newer_than': '2018-12-01T23:00:00.000000Z',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert {x['feed_id'] for x in data['feed']} == {
        '222c69c8afe947ba887fd6404428b31c',
        '333c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
        '555c69c8afe947ba887fd6404428b31c',
    }
    assert data['has_more']

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'newer_than': '2018-12-01T00:00:00.000000Z',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert {x['feed_id'] for x in data['feed']} == {
        '111c69c8afe947ba887fd6404428b31c',
        '222c69c8afe947ba887fd6404428b31c',
        '333c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
        '555c69c8afe947ba887fd6404428b31c',
    }
    assert data['has_more']


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
@pytest.mark.pgsql(
    'feeds-pg', files=['test_same_publish_at_feeds_has_no_more.sql'],
)
@pytest.mark.now('2018-12-10T00:00:00Z')
async def test_same_publish_at_has_no_more(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert {x['feed_id'] for x in data['feed']} == {
        '444c69c8afe947ba887fd6404428b31c',
        '333c69c8afe947ba887fd6404428b31c',
        '222c69c8afe947ba887fd6404428b31c',
        '111c69c8afe947ba887fd6404428b31c',
    }
    assert not data['has_more']

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'newer_than': '2018-12-01T00:00:00.000000Z',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert {x['feed_id'] for x in data['feed']} == {
        '111c69c8afe947ba887fd6404428b31c',
        '222c69c8afe947ba887fd6404428b31c',
        '333c69c8afe947ba887fd6404428b31c',
        '444c69c8afe947ba887fd6404428b31c',
    }
    assert not data['has_more']

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'earlier_than': '2018-12-01T00:00:00.000000Z',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert not data['feed']
    assert not data['has_more']

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['city:moscow;position:director'],
            'newer_than': '2018-12-09T00:00:00.000000Z',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert not data['feed']
    assert not data['has_more']


@pytest.mark.now('2018-12-05T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_meta_statistics.sql'])
async def test_meta_statistics(taxi_feeds, load_json):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={'service': 'service', 'channels': ['driver:1', 'channel:2']},
    )

    assert response.status_code == 200
    assert response.json() == load_json('test_meta_statistics_response.json')


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 4,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_parent_feed.sql'])
async def test_parent_feed(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch', json={'service': 'service', 'channels': ['user:1']},
    )

    assert response.status_code == 200
    parent_feed_id = response.json()['feed'][1]['parent_feed_id']
    assert parent_feed_id == '75e46d20e0d941c1af604d354dd46ca0'


@pytest.mark.now('2018-12-03T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_payload_args.sql'])
async def test_payload_args(taxi_feeds, load_json):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={'service': 'service', 'channels': ['user:1', 'user:2']},
    )

    assert response.status_code == 200

    data = response.json()
    feeds = {feed['feed_id']: feed for feed in data['feed']}

    assert feeds == load_json('payload_args_feeds.json')


@pytest.mark.now('2018-12-03T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_escaped_braces_param.sql'])
async def test_escaped_braces_param(taxi_feeds, load_json):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={'service': 'service', 'channels': ['user:1', 'user:2']},
    )

    assert response.status_code == 200

    data = response.json()
    feeds = {feed['feed_id']: feed for feed in data['feed']}

    assert feeds == load_json('test_escaped_braces_params_response.json')
