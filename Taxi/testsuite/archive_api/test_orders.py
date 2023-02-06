import itertools

import bson
import bson.codec_options
import bson.json_util
import pytest

from taxi_tests.utils import ordered_object


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_ids(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/orders', json={'params': ['order_id']},
    )
    assert response.status_code == 400


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_too_many_ids(taxi_archive_api, yt_client):
    request_ids = []
    for i in range(2500):
        request_ids.append(str(i))

    response = taxi_archive_api.post(
        'archive/orders', json={'ids': request_ids},
    )
    assert response.status_code == 400


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_wrong_ids(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/orders',
        json={'ids': ['non_existing_id_1', 'non_existing_id_2']},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    response_json = bson.BSON(response.content).decode()
    assert len(response_json['items']) == 0


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_mongo(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/orders',
        json={'ids': ['order_id_1', 'order_id_2', 'order_id_4']},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'

    response_json = bson.BSON(response.content).decode()
    expected_response = {
        'items': [
            {'source': 'mongo', 'doc': {'_id': 'order_id_1', '_shard_id': 0}},
            {'source': 'mongo', 'doc': {'_id': 'order_id_2', '_shard_id': 0}},
        ],
    }
    ordered_object.assert_eq(
        response_json['items'], expected_response['items'], [''],
    )


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_yt(taxi_archive_api, yt_client, load_json):
    for ids_list in itertools.permutations(
            [
                '57a29ad8ffae49f08bc4e3f269c81d2f',
                '2f448d09f9af49509107965b4d0217e6',
                'wrong_order_id',
            ],
    ):
        query = (
            '* FROM [//home/taxi/unstable/private/mongo/bson/orders] '
            'WHERE id IN ("%s", "%s", "%s")'
        ) % ids_list
        yt_client.add_select_rows_response(
            query, 'src_response_yt_only.json', yson=True,
        )

    response = taxi_archive_api.post(
        'archive/orders',
        json={
            'ids': [
                '57a29ad8ffae49f08bc4e3f269c81d2f',
                'wrong_order_id',
                '2f448d09f9af49509107965b4d0217e6',
            ],
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'

    options = bson.codec_options.CodecOptions(tz_aware=True)
    response_json = bson.BSON(response.content).decode(codec_options=options)
    expected_response = {
        'items': [
            {
                'source': 'yt',
                'doc': {'_id': '57a29ad8ffae49f08bc4e3f269c81d2f'},
            },
            {
                'source': 'yt',
                'doc': {'_id': '2f448d09f9af49509107965b4d0217e6'},
            },
        ],
    }
    ordered_object.assert_eq(
        response_json['items'], expected_response['items'], [''],
    )


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_mongo_yt(taxi_archive_api, yt_client, load_json):
    for ids_list in itertools.permutations(
            ['57a29ad8ffae49f08bc4e3f269c81d2f', 'wrong_order_id'],
    ):
        query = (
            '* FROM [//home/taxi/unstable/private/mongo/bson/orders] '
            'WHERE id IN ("%s", "%s")'
        ) % ids_list
        yt_client.add_select_rows_response(
            query, 'src_response_yt_mongo.json', yson=True,
        )

    response = taxi_archive_api.post(
        'archive/orders',
        json={
            'ids': [
                '57a29ad8ffae49f08bc4e3f269c81d2f',
                'wrong_order_id',
                'archive_api_order_id',
            ],
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'

    options = bson.codec_options.CodecOptions(tz_aware=True)
    response_json = bson.BSON(response.content).decode(codec_options=options)
    expected_response = {
        'items': [
            {
                'source': 'mongo',
                'doc': {'_id': 'archive_api_order_id', '_shard_id': 0},
            },
            {
                'source': 'yt',
                'doc': {'_id': '57a29ad8ffae49f08bc4e3f269c81d2f'},
            },
        ],
    }
    ordered_object.assert_eq(
        response_json['items'], expected_response['items'], [''],
    )


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_mongo_only(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/orders', json={'ids': ['order_id_1', 'order_id_2']},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'

    response_json = bson.BSON(response.content).decode()
    expected_response = {
        'items': [
            {'source': 'mongo', 'doc': {'_id': 'order_id_1', '_shard_id': 0}},
            {'source': 'mongo', 'doc': {'_id': 'order_id_2', '_shard_id': 0}},
        ],
    }
    ordered_object.assert_eq(
        response_json['items'], expected_response['items'], [''],
    )


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_yt_excluded(taxi_archive_api, yt_client, load_json):
    for ids_list in itertools.permutations(
            ['57a29ad8ffae49f08bc4e3f269c81d2f', 'wrong_order_id'],
    ):
        query = (
            '* FROM [//home/taxi/unstable/collections/orders] '
            'WHERE id IN ("%s", "%s")'
        ) % ids_list
        yt_client.add_select_rows_response(
            query, 'src_response_yt_mongo.json', yson=True,
        )

    response = taxi_archive_api.post(
        'archive/orders',
        json={
            'ids': [
                '57a29ad8ffae49f08bc4e3f269c81d2f',
                'wrong_order_id',
                'archive_api_order_id',
            ],
            'lookup_yt': False,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'

    options = bson.codec_options.CodecOptions(tz_aware=True)
    response_json = bson.BSON(response.content).decode(codec_options=options)
    expected_response = {
        'items': [
            {
                'source': 'mongo',
                'doc': {'_id': 'archive_api_order_id', '_shard_id': 0},
            },
        ],
    }
    ordered_object.assert_eq(
        response_json['items'], expected_response['items'], [''],
    )
