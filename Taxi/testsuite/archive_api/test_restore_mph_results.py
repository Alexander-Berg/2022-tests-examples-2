import pytest

from taxi_tests.utils import ordered_object


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_id(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/mph_results/restore', json={'param': 'order_id'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    (
        'request_id, request_update, response_json, '
        'mongo_exist_before, mongo_exist_after'
    ),
    [
        (
            'non_existing_id',
            False,
            [{'id': 'non_existing_id', 'status': 'not_found'}],
            False,
            False,
        ),
        (
            'archive_api_order_id',
            False,
            [{'id': 'archive_api_order_id', 'status': 'mongo'}],
            True,
            True,
        ),
        (
            'archive_api_order_id',
            True,
            [{'id': 'archive_api_order_id', 'status': 'updated'}],
            True,
            True,
        ),
        (
            'dfbf834a2bc642e88f53cd91270ff5c3',
            True,
            [{'id': 'dfbf834a2bc642e88f53cd91270ff5c3', 'status': 'restored'}],
            False,
            True,
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_single(
        taxi_archive_api,
        yt_client,
        db,
        request_id,
        request_update,
        response_json,
        mongo_exist_before,
        mongo_exist_after,
):
    def check_db(should_exist):
        mph = db.mph_results.find_one({'_id': request_id})
        assert (mph is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"dfbf834a2bc642e88f53cd91270ff5c3"}',
        'src_response.json',
        yson=True,
    )

    check_db(mongo_exist_before)

    response = taxi_archive_api.post(
        'archive/mph_results/restore',
        json={'id': request_id, 'update': request_update},
    )

    assert response.status_code == 200
    assert response.json() == response_json

    check_db(mongo_exist_after)


@pytest.mark.parametrize(
    ('request_ids, request_update, response_json, ' 'mongo_exist_params'),
    [
        (
            ['non_existing_id'],
            False,
            [{'id': 'non_existing_id', 'status': 'not_found'}],
            [{'id': 'non_existing_id', 'before': False, 'after': False}],
        ),
        (
            ['non_existing_id_1', 'non_existing_id_2'],
            False,
            [
                {'id': 'non_existing_id_1', 'status': 'not_found'},
                {'id': 'non_existing_id_2', 'status': 'not_found'},
            ],
            [
                {'id': 'non_existing_id_1', 'before': False, 'after': False},
                {'id': 'non_existing_id_2', 'before': False, 'after': False},
            ],
        ),
        (
            ['non_existing_id', 'archive_api_order_id'],
            False,
            [
                {'id': 'non_existing_id', 'status': 'not_found'},
                {'id': 'archive_api_order_id', 'status': 'mongo'},
            ],
            [
                {'id': 'non_existing_id', 'before': False, 'after': False},
                {'id': 'archive_api_order_id', 'before': True, 'after': True},
            ],
        ),
        (
            ['non_existing_id', 'archive_api_order_id'],
            True,
            [
                {'id': 'non_existing_id', 'status': 'not_found'},
                {'id': 'archive_api_order_id', 'status': 'updated'},
            ],
            [
                {'id': 'non_existing_id', 'before': False, 'after': False},
                {'id': 'archive_api_order_id', 'before': True, 'after': True},
            ],
        ),
        (
            ['archive_api_order_id', 'dfbf834a2bc642e88f53cd91270ff5c3'],
            False,
            [
                {'id': 'archive_api_order_id', 'status': 'mongo'},
                {
                    'id': 'dfbf834a2bc642e88f53cd91270ff5c3',
                    'status': 'restored',
                },
            ],
            [
                {'id': 'archive_api_order_id', 'before': True, 'after': True},
                {
                    'id': 'dfbf834a2bc642e88f53cd91270ff5c3',
                    'before': False,
                    'after': True,
                },
            ],
        ),
        (
            [
                '4ec76da99eee45e6870e404e016694a9',
                '655013f9bf784723a2099c85d9fe88a3',
                'archive_api_order_id',
            ],
            True,
            [
                {
                    'id': '4ec76da99eee45e6870e404e016694a9',
                    'status': 'restored',
                },
                {
                    'id': '655013f9bf784723a2099c85d9fe88a3',
                    'status': 'restored',
                },
                {'id': 'archive_api_order_id', 'status': 'updated'},
            ],
            [
                {
                    'id': '4ec76da99eee45e6870e404e016694a9',
                    'before': False,
                    'after': True,
                },
                {
                    'id': '655013f9bf784723a2099c85d9fe88a3',
                    'before': False,
                    'after': True,
                },
                {'id': 'archive_api_order_id', 'before': True, 'after': True},
            ],
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_bulk(
        taxi_archive_api,
        yt_client,
        db,
        request_ids,
        request_update,
        response_json,
        mongo_exist_params,
):
    def check_db(request_id, should_exist):
        mph = db.mph_results.find_one({'_id': request_id})
        assert (mph is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"dfbf834a2bc642e88f53cd91270ff5c3"}',
        'src_response.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        (
            '{"id":"4ec76da99eee45e6870e404e016694a9"}'
            '{"id":"655013f9bf784723a2099c85d9fe88a3"}'
        ),
        'src_response_bulk.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        (
            '{"id":"655013f9bf784723a2099c85d9fe88a3"}'
            '{"id":"4ec76da99eee45e6870e404e016694a9"}'
        ),
        'src_response_bulk.json',
        yson=True,
    )

    for params in mongo_exist_params:
        check_db(params['id'], params['before'])

    response = taxi_archive_api.post(
        'archive/mph_results/restore',
        json={'ids': request_ids, 'update': request_update},
    )

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), response_json, [''])

    for params in mongo_exist_params:
        check_db(params['id'], params['after'])


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_conflict(taxi_archive_api, yt_client, db, testpoint):
    @testpoint('archive::restore_bulk')
    def archive_restore_parallel(data):
        db.mph_results.insert({'_id': 'dfbf834a2bc642e88f53cd91270ff5c3'})

    def check_db(should_exist):
        mph = db.mph_results.find_one(
            {'_id': 'dfbf834a2bc642e88f53cd91270ff5c3'},
        )
        assert (mph is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"dfbf834a2bc642e88f53cd91270ff5c3"}',
        'src_response.json',
        yson=True,
    )

    check_db(False)

    response = taxi_archive_api.post(
        'archive/mph_results/restore',
        json={'id': 'dfbf834a2bc642e88f53cd91270ff5c3'},
    )

    assert response.status_code == 200
    assert response.json() == [
        {'id': 'dfbf834a2bc642e88f53cd91270ff5c3', 'status': 'conflict'},
    ]

    check_db(True)
