import json

import bson
import pytest

from taxi_tests.utils import ordered_object


@pytest.fixture()
def mock_order_archive(mockserver, load_json):
    @mockserver.json_handler('/order-archive/v2/order_proc/retrieve')
    def mock_archive_order_proc(request):
        data = json.loads(request.get_data())
        assert data['indexes'] == ['reorder']
        assert data['verified']
        assert data['id'] in ['order_archive_id', 'order_archive_reorder_id']

        proc = load_json('src_response_pd.json')['doc']
        proc['_id'] = 'order_archive_id'
        proc['reorder'] = {'id': 'order_archive_reorder_id'}
        return mockserver.make_response(bson.BSON.encode({'doc': proc}))


@pytest.mark.now('2018-02-16T15:00:00Z')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=False),
        ),
        pytest.param(
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=True),
        ),
    ],
)
def test_no_param_id(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'param': 'order_id'},
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
            '472a25573dff4cc58adf51dcabcf1842',
            True,
            [{'id': '472a25573dff4cc58adf51dcabcf1842', 'status': 'restored'}],
            False,
            True,
        ),
        pytest.param(
            'order_archive_id',
            True,
            [{'id': 'order_archive_id', 'status': 'restored'}],
            False,
            True,
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=True),
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_single(
        taxi_archive_api,
        yt_client,
        db,
        mock_order_archive,
        request_id,
        request_update,
        response_json,
        mongo_exist_before,
        mongo_exist_after,
):
    def check_db(should_exist):
        order_proc = db.order_proc.find_one({'_id': request_id})
        assert (order_proc is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"472a25573dff4cc58adf51dcabcf1842"}',
        'src_response.json',
        yson=True,
    )

    check_db(mongo_exist_before)

    response = taxi_archive_api.post(
        'archive/order_proc/restore',
        json={'id': request_id, 'update': request_update},
    )

    assert response.status_code == 200
    assert response.json() == response_json

    check_db(mongo_exist_after)


@pytest.mark.parametrize(
    'request_ids, request_update, response_json, mongo_exist_params',
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
            ['archive_api_order_id', '472a25573dff4cc58adf51dcabcf1842'],
            False,
            [
                {'id': 'archive_api_order_id', 'status': 'mongo'},
                {
                    'id': '472a25573dff4cc58adf51dcabcf1842',
                    'status': 'restored',
                },
            ],
            [
                {'id': 'archive_api_order_id', 'before': True, 'after': True},
                {
                    'id': '472a25573dff4cc58adf51dcabcf1842',
                    'before': False,
                    'after': True,
                },
            ],
        ),
        (
            [
                '70a9e9e49117481a89413f109a785f56',
                'ad75c0e9e4014c05bd0b94aa22ecd7ab',
                'archive_api_order_id',
            ],
            True,
            [
                {
                    'id': '70a9e9e49117481a89413f109a785f56',
                    'status': 'restored',
                },
                {
                    'id': 'ad75c0e9e4014c05bd0b94aa22ecd7ab',
                    'status': 'restored',
                },
                {'id': 'archive_api_order_id', 'status': 'updated'},
            ],
            [
                {
                    'id': '70a9e9e49117481a89413f109a785f56',
                    'before': False,
                    'after': True,
                },
                {
                    'id': 'ad75c0e9e4014c05bd0b94aa22ecd7ab',
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
        order_proc = db.order_proc.find_one({'_id': request_id})
        assert (order_proc is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"472a25573dff4cc58adf51dcabcf1842"}',
        'src_response.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        (
            '{"id":"70a9e9e49117481a89413f109a785f56"}'
            '{"id":"ad75c0e9e4014c05bd0b94aa22ecd7ab"}'
        ),
        'src_response_bulk.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        (
            '{"id":"ad75c0e9e4014c05bd0b94aa22ecd7ab"}'
            '{"id":"70a9e9e49117481a89413f109a785f56"}'
        ),
        'src_response_bulk.json',
        yson=True,
    )

    for params in mongo_exist_params:
        check_db(params['id'], params['before'])

    response = taxi_archive_api.post(
        'archive/order_proc/restore',
        json={'ids': request_ids, 'update': request_update},
    )

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), response_json, [''])

    for params in mongo_exist_params:
        check_db(params['id'], params['after'])


@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True, ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=True,
)
def test_restore_bulk_order_archive(taxi_archive_api):
    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'ids': ['id-1', 'id-2']},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'order_id',
    [
        pytest.param(
            '472a25573dff4cc58adf51dcabcf1842',
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=False),
        ),
        pytest.param(
            'order_archive_id',
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=True),
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_conflict(
        taxi_archive_api,
        yt_client,
        db,
        testpoint,
        mock_order_archive,
        order_id,
):
    @testpoint('archive::restore')
    @testpoint('archive::restore-proc-v2')
    def archive_restore_parallel(data):
        db.order_proc.insert({'_id': order_id, '_shard_id': 0})

    def check_db(should_exist):
        order_proc = db.order_proc.find_one({'_id': order_id})
        assert (order_proc is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"472a25573dff4cc58adf51dcabcf1842"}',
        'src_response.json',
        yson=True,
    )

    check_db(False)

    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'id': order_id},
    )

    assert response.status_code == 200
    assert response.json() == [{'id': order_id, 'status': 'conflict'}]

    check_db(True)


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=False),
        ),
        pytest.param(
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=True),
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_reorder_mongo(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'id': 'reorder_id_reorder_1'},
    )
    assert response.status_code == 200
    assert response.json() == [
        {'id': 'reorder_id_reorder_1', 'status': 'mongo'},
    ]


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_reorder_yt(taxi_archive_api, yt_client, db):
    translate_query = (
        'id FROM '
        '[//home/taxi/unstable/replica/mongo/indexes/order_proc/order_id] '
        'WHERE (order_id = "reorder_id_reorder_2" AND source = "reorder_id")'
    )
    yt_client.add_select_rows_response(
        translate_query, 'src_response_reorder_translate.json',
    )
    yt_client.add_lookup_rows_response(
        '{"id":"reorder_id_reorder_2"}',
        'src_response_reorder_empty.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        '{"id":"order_id_reorder_2"}', 'src_response_reorder.json', yson=True,
    )

    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'id': 'reorder_id_reorder_2'},
    )
    assert response.status_code == 200
    assert response.json() == [
        {'id': 'reorder_id_reorder_2', 'status': 'restored'},
    ]

    doc = db.order_proc.find_one({'_id': 'order_id_reorder_2'})
    assert doc is not None
    assert doc['reorder']['id'] == 'reorder_id_reorder_2'


@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True, ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=True,
)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_reorder_order_archive(
        taxi_archive_api, db, mock_order_archive,
):
    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'id': 'order_archive_reorder_id'},
    )
    assert response.status_code == 200
    assert response.json() == [
        {'id': 'order_archive_reorder_id', 'status': 'restored'},
    ]

    doc = db.order_proc.find_one({'_id': 'order_archive_id'})
    assert doc is not None
    assert doc['reorder']['id'] == 'order_archive_reorder_id'


@pytest.mark.parametrize(
    'order_id',
    [
        pytest.param(
            '172a25573dff4cc58adf51dcabcf1842',
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=False),
        ),
        pytest.param(
            'order_archive_id',
            marks=pytest.mark.config(ARCHIVE_API_PROC_USE_ORDER_ARCHIVE=True),
        ),
    ],
)
@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True,
    ARCHIVE_API_PERSONAL_DATA_WRITE_MODE={
        '__default__': 'old_way',
        'restore_single_order_proc': 'both_fallback',
    },
)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_pd_in_restore_single(
        taxi_archive_api,
        yt_client,
        db,
        mockserver,
        mock_order_archive,
        order_id,
):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_store')
    def mock_personal_bulk_store_licenses(request):
        request_json = json.loads(request.get_data())
        response = []
        for entity in request_json['items']:
            assert 'value' in entity
            response.append(
                {'id': entity['value'] + 'ID', 'value': entity['value']},
            )
        return {'items': response}

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def mock_bulk_store_phones(request):
        request_json = json.loads(request.get_data())
        response = []
        for entity in request_json['items']:
            assert 'value' in entity
            response.append(
                {'id': entity['value'] + 'ID', 'value': entity['value']},
            )
        return {'items': response}

    request_update = True
    response_json = [{'id': order_id, 'status': 'restored'}]
    mongo_exist_before = False
    mongo_exist_after = True

    def check_db(should_exist):
        order_proc = db.order_proc.find_one({'_id': order_id})
        assert (order_proc is not None) == should_exist
        if (order_proc is not None) and should_exist:
            assert (
                order_proc['order']['performer']['driver_license_personal_id']
                == 'license2ID'
            )
            for candidate, id in zip(
                    order_proc['candidates'],
                    [
                        'license1ID',
                        'license2ID',
                        'license3ID',
                        'license11ID',
                        'license12ID',
                    ],
            ):
                assert candidate['driver_license_personal_id'] == id
            for candidate, id in zip(
                    order_proc['candidates'],
                    [
                        '+79123456781ID',
                        '+79123456782ID',
                        '+79123456783ID',
                        None,
                        'phone-id-for-license12',
                    ],
            ):
                assert candidate.get('phone_personal_id') == id
            assert order_proc['lookup']['state'][
                'excluded_license_pd_ids_for_phone'
            ] == ['license3ID', 'license4ID']

    yt_client.add_lookup_rows_response(
        '{"id":"172a25573dff4cc58adf51dcabcf1842"}',
        'src_response_pd.json',
        yson=True,
    )

    check_db(mongo_exist_before)

    response = taxi_archive_api.post(
        'archive/order_proc/restore',
        json={'id': order_id, 'update': request_update},
    )

    assert response.status_code == 200
    assert response.json() == response_json

    check_db(mongo_exist_after)
