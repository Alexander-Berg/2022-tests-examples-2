import copy

import pytest

import tests_feeds.feeds_common as fc

DATA_BASE = 'test_batch_fetch.sql'
NOW = '2018-12-02T00:00:00.0Z'


async def fetch(taxi_feeds, *requests):
    response = await taxi_feeds.post('/v1/batch/fetch', {'items': requests})
    assert response.status_code == 200
    assert len(requests) == len(response.json()['items'])
    return response


@pytest.mark.now(NOW)
@pytest.mark.pgsql('feeds-pg', files=['test_batch_fetch.sql'])
async def test_many_service_copies_with_same_params(taxi_feeds):
    json = {'service': 'service', 'channels': ['user:1']}
    await fetch(taxi_feeds, *[copy.deepcopy(json) for _ in range(100)])


@pytest.mark.now(NOW)
@pytest.mark.pgsql('feeds-pg', files=[DATA_BASE])
async def test_two_services_with_different_params(taxi_feeds):
    await fetch(
        taxi_feeds,
        {'service': 'other_service', 'channels': ['user:1']},
        {'service': 'service', 'channels': ['user:4']},
    )


@pytest.mark.now(NOW)
@pytest.mark.pgsql('feeds-pg', files=[DATA_BASE])
async def test_one_service_fail(taxi_feeds):
    json = {
        'items': [
            {'service': 'service', 'channels': ['user:1']},
            {'service': 'unknown_service', 'channels': ['position:cool_boy']},
        ],
    }

    response = await taxi_feeds.post('/v1/batch/fetch', json)
    assert response.status_code == 400


@pytest.mark.now(NOW)
@pytest.mark.pgsql('feeds-pg', files=[DATA_BASE])
async def test_etags(taxi_feeds, pgsql):
    response = await fetch(
        taxi_feeds, {'service': 'service', 'channels': ['user:1']},
    )

    assert response.json()['items'][0]['etag_changed']

    response = await fetch(
        taxi_feeds,
        {
            'service': 'service',
            'channels': ['user:1'],
            'etag': response.json()['items'][0]['response']['etag'],
        },
    )

    data = response.json()
    assert not data['items'][0]['etag_changed']

    fc.insert_feed_in_db(
        'service', ['user:4'], {'text': 'Hi!'}, '11111', NOW, pgsql,
    )

    response = await fetch(
        taxi_feeds, {'service': 'service', 'channels': ['user:4'], 'etag': ''},
    )

    data = response.json()
    assert data['items'][0]['etag_changed']

    fc.insert_feed_in_db(
        'service', ['user:1'], {'text': 'Hi!'}, '11111', NOW, pgsql,
    )

    response = await fetch(
        taxi_feeds,
        {
            'service': 'service',
            'channels': ['user:4'],
            'etag': data['items'][0]['response']['etag'],
        },
    )
    assert not response.json()['items'][0]['etag_changed']


@pytest.mark.now('2018-12-03T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_payload_args.sql'])
async def test_payload_args(taxi_feeds, load_json):
    response = await fetch(
        taxi_feeds,
        {'service': 'service', 'channels': ['user:1', 'user:2']},
        {'service': 'other_service', 'channels': ['user:1', 'user:2']},
    )

    data = response.json()['items']
    service_feeds = {
        feed['feed_id']: feed for feed in data[0]['response']['feed']
    }

    assert service_feeds == load_json('payload_args_feeds.json')

    other_service_feeds = {
        feed['feed_id']: feed for feed in data[1]['response']['feed']
    }

    assert other_service_feeds == load_json(
        'payload_args_feeds_other_service.json',
    )
