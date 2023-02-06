import bson.objectid
import pytest

from taxi_tests.utils import ordered_object


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_id(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/subvention_reasons/restore', json={'param': 'order_id'},
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
            '1a35b0b086514ef3aeef226f98dcca9f',
            True,
            [{'id': '1a35b0b086514ef3aeef226f98dcca9f', 'status': 'restored'}],
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
        sr = db.subvention_reasons.find_one({'order_id': request_id})
        assert (sr is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"order_id":"1a35b0b086514ef3aeef226f98dcca9f"}',
        'src_response.json',
        yson=True,
    )

    check_db(mongo_exist_before)

    response = taxi_archive_api.post(
        'archive/subvention_reasons/restore',
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
            ['archive_api_order_id', '1a35b0b086514ef3aeef226f98dcca9f'],
            False,
            [
                {'id': 'archive_api_order_id', 'status': 'mongo'},
                {
                    'id': '1a35b0b086514ef3aeef226f98dcca9f',
                    'status': 'restored',
                },
            ],
            [
                {'id': 'archive_api_order_id', 'before': True, 'after': True},
                {
                    'id': '1a35b0b086514ef3aeef226f98dcca9f',
                    'before': False,
                    'after': True,
                },
            ],
        ),
        (
            [
                '00687fa6f5ed453588c759d0b4c169cc',
                '011fcd2aebfa42ae8ddf32aa66f21c86',
                'archive_api_order_id',
            ],
            True,
            [
                {
                    'id': '00687fa6f5ed453588c759d0b4c169cc',
                    'status': 'restored',
                },
                {
                    'id': '011fcd2aebfa42ae8ddf32aa66f21c86',
                    'status': 'restored',
                },
                {'id': 'archive_api_order_id', 'status': 'updated'},
            ],
            [
                {
                    'id': '00687fa6f5ed453588c759d0b4c169cc',
                    'before': False,
                    'after': True,
                },
                {
                    'id': '011fcd2aebfa42ae8ddf32aa66f21c86',
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
        sr = db.subvention_reasons.find_one({'order_id': request_id})
        assert (sr is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"order_id":"1a35b0b086514ef3aeef226f98dcca9f"}',
        'src_response.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        '{"order_id":"00687fa6f5ed453588c759d0b4c169cc"}'
        '{"order_id":"011fcd2aebfa42ae8ddf32aa66f21c86"}',
        'src_response_bulk.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        '{"order_id":"011fcd2aebfa42ae8ddf32aa66f21c86"}'
        '{"order_id":"00687fa6f5ed453588c759d0b4c169cc"}',
        'src_response_bulk.json',
        yson=True,
    )

    for params in mongo_exist_params:
        check_db(params['id'], params['before'])

    response = taxi_archive_api.post(
        'archive/subvention_reasons/restore',
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
        db.subvention_reasons.insert(
            {
                '_id': bson.objectid.ObjectId('5ad8c09b9aec010730686ddb'),
                'order_id': '1a35b0b086514ef3aeef226f98dcca9f',
            },
        )

    def check_db(should_exist):
        sub = db.subvention_reasons.find_one(
            {'order_id': '1a35b0b086514ef3aeef226f98dcca9f'},
        )
        assert (sub is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"order_id":"1a35b0b086514ef3aeef226f98dcca9f"}',
        'src_response.json',
        yson=True,
    )

    check_db(False)

    response = taxi_archive_api.post(
        'archive/subvention_reasons/restore',
        json={'id': '1a35b0b086514ef3aeef226f98dcca9f'},
    )

    assert response.status_code == 200
    assert response.json() == [
        {'id': '1a35b0b086514ef3aeef226f98dcca9f', 'status': 'conflict'},
    ]

    check_db(True)
