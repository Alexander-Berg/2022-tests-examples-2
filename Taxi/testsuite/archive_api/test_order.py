import json

import bson
import pytest


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_id(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/order', json={'param': 'order_id'},
    )
    assert response.status_code == 400


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_wrong_id(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/order', json={'id': 'non_existing_id'},
    )
    assert response.status_code == 404


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_mongo(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/order', json={'id': 'archive_api_order_id'},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    response_json = bson.BSON(response.content).decode()
    assert response_json == {
        'source': 'mongo',
        'doc': {'_id': 'archive_api_order_id', '_shard_id': 0},
    }


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_yt(taxi_archive_api, yt_client, load_json):
    yt_client.add_lookup_rows_response(
        '{"id":"6cb1375ef6474c3b8e1beb7b9f7aff64"}',
        'src_response.json',
        yson=True,
    )

    response = taxi_archive_api.post(
        'archive/order', json={'id': '6cb1375ef6474c3b8e1beb7b9f7aff64'},
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    response_json = bson.BSON(response.content).decode()
    assert response_json == {
        'source': 'yt',
        'doc': {'_id': '6cb1375ef6474c3b8e1beb7b9f7aff64'},
    }


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_yt_excluded(taxi_archive_api, yt_client, load_json):
    yt_client.add_lookup_rows_response(
        '{"id":"6cb1375ef6474c3b8e1beb7b9f7aff64"}',
        'src_response.json',
        yson=True,
    )

    response = taxi_archive_api.post(
        'archive/order',
        json={'id': '6cb1375ef6474c3b8e1beb7b9f7aff64', 'lookup_yt': False},
    )

    assert response.status_code == 404


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_yt_error_all(taxi_archive_api, yt_client, mockserver):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows_test(request):
        headers = {
            'Content-Type': 'application/x-yt-yson-binary',
            'Trailer': 'X-YT-Error, X-YT-Response-Code, X-YT-Response-Message',
            'X-YT-Error': json.dumps(
                {'code': 1, 'message': 'yt error message', 'inner_errors': []},
            ),
            'X-YT-Response-Code': 1,
            'X-YT-Response-Message': 'yt error message',
        }
        return mockserver.make_response(headers=headers)

    response = taxi_archive_api.post(
        'archive/order', json={'id': '6cb1375ef6474c3b8e1beb7b9f7aff64'},
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'yt_error_uri',
    ['/yt/yt-test/api/v3/lookup_rows', '/yt/yt-repl/api/v3/lookup_rows'],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_yt_error_one(
        taxi_archive_api, yt_client, mockserver, load_json, yt_error_uri,
):
    @mockserver.json_handler(yt_error_uri)
    def lookup_rows_test(request):
        headers = {
            'Content-Type': 'application/x-yt-yson-binary',
            'Trailer': 'X-YT-Error, X-YT-Response-Code, X-YT-Response-Message',
            'X-YT-Error': json.dumps(
                {'code': 1, 'message': 'yt error message', 'inner_errors': []},
            ),
            'X-YT-Response-Code': 1,
            'X-YT-Response-Message': 'yt error message',
        }
        return mockserver.make_response(headers=headers)

    yt_client.add_lookup_rows_response(
        '{"id":"6cb1375ef6474c3b8e1beb7b9f7aff64"}',
        'src_response.json',
        yson=True,
    )

    response = taxi_archive_api.post(
        'archive/order', json={'id': '6cb1375ef6474c3b8e1beb7b9f7aff64'},
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    response_json = bson.BSON(response.content).decode()
    assert response_json == {
        'source': 'yt',
        'doc': {'_id': '6cb1375ef6474c3b8e1beb7b9f7aff64'},
    }
