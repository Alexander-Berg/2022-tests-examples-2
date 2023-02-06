import pytest


@pytest.mark.parametrize(
    'order_id,yt_response_path,expected_shard_id',
    [
        (
            'c26b158d12b84cde88942f70d9440a8c',
            'src_response_c26b158d12b84cde88942f70d9440a8c.json',
            0,
        ),
        (
            '1bca80e551b7b9456229930eaf60175c',
            'src_response_1bca80e551b7b9456229930eaf60175c.json',
            63,
        ),
        (
            '8d6d75b65013437cbb21e954e5c6e74b',
            'src_response_8d6d75b65013437cbb21e954e5c6e74b_shard_override'
            '.json',
            0,
        ),
    ],
)
@pytest.mark.parametrize('collection', ['order_proc', 'orders'])
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_shard_id(
        taxi_archive_api,
        yt_client,
        db,
        order_id,
        yt_response_path,
        expected_shard_id,
        collection,
):
    yt_client.add_lookup_rows_response(
        '{"id":"%s"}' % (order_id,), filename=yt_response_path, yson=True,
    )

    response = taxi_archive_api.post(
        'archive/%s/restore' % collection,
        json={'id': order_id, 'update': False},
    )

    assert response.status_code == 200
    response = response.json()
    assert response[0]['status'] == 'restored'

    mongo_collection = getattr(db, collection)
    doc = mongo_collection.find_one({'_id': order_id})
    assert doc is not None
    assert doc['_shard_id'] == expected_shard_id
