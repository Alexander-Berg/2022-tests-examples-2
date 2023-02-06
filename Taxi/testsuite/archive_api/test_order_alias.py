import bson
import bson.codec_options
import bson.json_util
import pytest


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_id(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/order', json={'lookup': {'alias': True}},
    )
    assert response.status_code == 400


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_wrong_id(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/order',
        json={'id': 'non_existing_id', 'lookup': {'alias': True}},
    )
    assert response.status_code == 404


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_mongo(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/order',
        json={'id': 'alias_order_id', 'lookup': {'alias': True}},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    response_json = bson.BSON(response.content).decode()
    assert response_json == {
        'source': 'mongo',
        'doc': {
            '_id': 'tmp_order_id',
            '_shard_id': 0,
            'performer': {'taxi_alias': {'id': 'alias_order_id'}},
        },
    }


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_yt(taxi_archive_api, yt_client, load_json):
    query = (
        '* FROM '
        '[//home/taxi/unstable/replica/mongo/indexes/order_proc/order_id] '
        'AS index JOIN [//home/taxi/unstable/private/mongo/bson/orders] '
        'AS order ON index.id = order.id '
        'WHERE (index.order_id = "6cb1375ef6474c3b8e1beb7b9f7aff64" '
        'AND index.source IN ("order_id", "performer_alias_id", '
        '"candidate_alias_id"))'
    )
    yt_client.add_select_rows_response(query, 'src_response.json', yson=True)

    response = taxi_archive_api.post(
        'archive/order',
        json={
            'id': '6cb1375ef6474c3b8e1beb7b9f7aff64',
            'lookup': {'alias': True},
        },
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
    query = (
        '* FROM '
        '[//home/taxi/unstable/replica/mongo/indexes/order_proc/order_id] '
        'AS index JOIN [//home/taxi/private/mongo/bson/orders] AS order '
        'ON index.id = order.id '
        'WHERE (index.order_id = "6cb1375ef6474c3b8e1beb7b9f7aff64" '
        'AND index.source IN ("order_id", "performer_alias_id", '
        '"candidate_alias_id"))'
    )
    yt_client.add_select_rows_response(query, 'src_response.json', yson=True)

    response = taxi_archive_api.post(
        'archive/order',
        json={
            'id': '6cb1375ef6474c3b8e1beb7b9f7aff64',
            'lookup': {'alias': True},
            'lookup_yt': False,
        },
    )

    assert response.status_code == 404
