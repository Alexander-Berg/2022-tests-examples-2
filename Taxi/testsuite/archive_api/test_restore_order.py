import json

import pytest

from taxi_tests.utils import ordered_object


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_id(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/orders/restore', json={'param': 'order_id'},
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
            '35707319ba47436c96a4d2b3971dc2bd',
            True,
            [{'id': '35707319ba47436c96a4d2b3971dc2bd', 'status': 'restored'}],
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
        order = db.orders.find_one({'_id': request_id})
        assert (order is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"35707319ba47436c96a4d2b3971dc2bd"}',
        'src_response.json',
        yson=True,
    )

    check_db(mongo_exist_before)

    response = taxi_archive_api.post(
        'archive/orders/restore',
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
            ['archive_api_order_id', '35707319ba47436c96a4d2b3971dc2bd'],
            False,
            [
                {'id': 'archive_api_order_id', 'status': 'mongo'},
                {
                    'id': '35707319ba47436c96a4d2b3971dc2bd',
                    'status': 'restored',
                },
            ],
            [
                {'id': 'archive_api_order_id', 'before': True, 'after': True},
                {
                    'id': '35707319ba47436c96a4d2b3971dc2bd',
                    'before': False,
                    'after': True,
                },
            ],
        ),
        (
            [
                'c990c717b1f7450eb5c63ed5fb50ce25',
                '11df442e4af341cd8be29b9f30d987f1',
                'archive_api_order_id',
            ],
            True,
            [
                {
                    'id': 'c990c717b1f7450eb5c63ed5fb50ce25',
                    'status': 'restored',
                },
                {
                    'id': '11df442e4af341cd8be29b9f30d987f1',
                    'status': 'restored',
                },
                {'id': 'archive_api_order_id', 'status': 'updated'},
            ],
            [
                {
                    'id': 'c990c717b1f7450eb5c63ed5fb50ce25',
                    'before': False,
                    'after': True,
                },
                {
                    'id': '11df442e4af341cd8be29b9f30d987f1',
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
        order = db.orders.find_one({'_id': request_id})
        assert (order is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"35707319ba47436c96a4d2b3971dc2bd"}',
        'src_response.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        (
            '{"id":"c990c717b1f7450eb5c63ed5fb50ce25"}'
            '{"id":"11df442e4af341cd8be29b9f30d987f1"}'
        ),
        'src_response_bulk.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        (
            '{"id":"11df442e4af341cd8be29b9f30d987f1"}'
            '{"id":"c990c717b1f7450eb5c63ed5fb50ce25"}'
        ),
        'src_response_bulk.json',
        yson=True,
    )

    for params in mongo_exist_params:
        check_db(params['id'], params['before'])

    response = taxi_archive_api.post(
        'archive/orders/restore',
        json={'ids': request_ids, 'update': request_update},
    )

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), response_json, [''])

    for params in mongo_exist_params:
        check_db(params['id'], params['after'])


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_conflict(taxi_archive_api, yt_client, db, testpoint):
    @testpoint('archive::restore')
    def archive_restore_parallel(data):
        db.orders.insert(
            {'_id': '35707319ba47436c96a4d2b3971dc2bd', '_shard_id': 0},
        )

    def check_db(should_exist):
        order = db.orders.find_one({'_id': '35707319ba47436c96a4d2b3971dc2bd'})
        assert (order is not None) == should_exist

    yt_client.add_lookup_rows_response(
        '{"id":"35707319ba47436c96a4d2b3971dc2bd"}',
        'src_response.json',
        yson=True,
    )

    check_db(False)

    response = taxi_archive_api.post(
        'archive/orders/restore',
        json={'id': '35707319ba47436c96a4d2b3971dc2bd'},
    )

    assert response.status_code == 200
    assert response.json() == [
        {'id': '35707319ba47436c96a4d2b3971dc2bd', 'status': 'conflict'},
    ]

    check_db(True)


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_reorder_mongo(taxi_archive_api, yt_client):
    response = taxi_archive_api.post(
        'archive/orders/restore', json={'id': 'reorder_id_reorder_1'},
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
        'archive/orders/restore', json={'id': 'reorder_id_reorder_2'},
    )
    assert response.status_code == 200
    assert response.json() == [
        {'id': 'reorder_id_reorder_2', 'status': 'restored'},
    ]

    doc = db.orders.find_one({'_id': 'order_id_reorder_2'})
    assert doc is not None
    assert doc['reorder']['id'] == 'reorder_id_reorder_2'


@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True,
    ARCHIVE_API_PERSONAL_DATA_WRITE_MODE={
        '__default__': 'old_way',
        'restore_single_order': 'both_fallback',
    },
)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_pd_in_restore_single(taxi_archive_api, yt_client, db, mockserver):
    request_id = '15707319ba47436c96a4d2b3971dc2bd'
    response_json = [
        {'id': '15707319ba47436c96a4d2b3971dc2bd', 'status': 'restored'},
    ]

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_store_license(request):
        return _personal_store(request)

    @mockserver.json_handler('/personal/v1/tins/store')
    def mock_store_tin(request):
        return _personal_store(request)

    yt_client.add_lookup_rows_response(
        '{"id":"15707319ba47436c96a4d2b3971dc2bd"}',
        'src_response_pd.json',
        yson=True,
    )

    response = taxi_archive_api.post(
        'archive/orders/restore', json={'id': request_id, 'update': False},
    )

    assert response.status_code == 200
    assert response.json() == response_json

    _check_db(db, request_id, True, True)


@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True,
    ARCHIVE_API_PERSONAL_DATA_WRITE_MODE={'__default__': 'both_no_fallback'},
)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_pd_in_restore_bulk(taxi_archive_api, yt_client, db, mockserver):
    request_ids = [
        '1990c717b1f7450eb5c63ed5fb50ce25',
        '21df442e4af341cd8be29b9f30d987f1',
    ]
    response_json = [
        {'id': '1990c717b1f7450eb5c63ed5fb50ce25', 'status': 'restored'},
        {'id': '21df442e4af341cd8be29b9f30d987f1', 'status': 'restored'},
    ]
    restored_docs = [
        {
            '_id': '1990c717b1f7450eb5c63ed5fb50ce25',
            'performer': {
                'driver_license': 'license1',
                'driver_license_personal_id': 'license1ID',
            },
            'payment_tech': {
                'inn_for_receipt': 'inn1',
                'inn_for_receipt_id': 'inn1ID',
            },
        },
        {
            '_id': '21df442e4af341cd8be29b9f30d987f1',
            'performer': {
                'driver_license': 'license2',
                'driver_license_personal_id': 'license2ID',
            },
            'payment_tech': {
                'inn_for_receipt': 'inn2',
                'inn_for_receipt_id': 'inn2ID',
            },
        },
    ]

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_store')
    def mock_bulk_store_licenses(request):
        request_json = json.loads(request.get_data())
        response = []
        for entity in request_json['items']:
            assert 'value' in entity
            response.append(
                {'id': entity['value'] + 'ID', 'value': entity['value']},
            )
        return {'items': response}

    @mockserver.json_handler('/personal/v1/tins/bulk_store')
    def mock_bulk_store_tins(request):
        request_json = json.loads(request.get_data())
        response = []
        for entity in request_json['items']:
            assert 'value' in entity
            response.append(
                {'id': entity['value'] + 'ID', 'value': entity['value']},
            )
        return {'items': response}

    def _check_db(should_exist, doc):
        order = db.orders.find_one({'_id': doc['_id']})
        assert (order is not None) == should_exist
        if order:
            assert (
                order['performer']['driver_license']
                == doc['performer']['driver_license']
            )
            assert (
                order['performer']['driver_license_personal_id']
                == doc['performer']['driver_license_personal_id']
            )
            assert (
                order['payment_tech']['inn_for_receipt_id']
                == doc['payment_tech']['inn_for_receipt_id']
            )
            assert (
                order['payment_tech']['inn_for_receipt_id']
                == doc['payment_tech']['inn_for_receipt_id']
            )

    yt_client.add_lookup_rows_response(
        (
            '{"id":"1990c717b1f7450eb5c63ed5fb50ce25"}'
            '{"id":"21df442e4af341cd8be29b9f30d987f1"}'
        ),
        'src_response_bulk.json',
        yson=True,
    )
    yt_client.add_lookup_rows_response(
        (
            '{"id":"21df442e4af341cd8be29b9f30d987f1"}'
            '{"id":"1990c717b1f7450eb5c63ed5fb50ce25"}'
        ),
        'src_response_bulk_pd.json',
        yson=True,
    )

    for doc in restored_docs:
        _check_db(False, doc)

    response = taxi_archive_api.post(
        'archive/orders/restore', json={'ids': request_ids, 'update': False},
    )

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), response_json, [''])

    for doc in restored_docs:
        _check_db(True, doc)


@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True,
    ARCHIVE_API_PERSONAL_DATA_WRITE_MODE={'__default__': 'old_way'},
)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_error_in_personal_old_way(
        taxi_archive_api, yt_client, db, mockserver,
):
    request_id = '15707319ba47436c96a4d2b3971dc2bd'
    mongo_exist_before = False
    mongo_exist_after = True

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_store_license(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/personal/v1/tins/store')
    def mock_store_tin(request):
        return mockserver.make_response('', 500)

    yt_client.add_lookup_rows_response(
        '{"id":"15707319ba47436c96a4d2b3971dc2bd"}',
        'src_response_pd.json',
        yson=True,
    )

    _check_db(db, request_id, mongo_exist_before, False)

    response = taxi_archive_api.post(
        'archive/orders/restore', json={'id': request_id, 'update': True},
    )

    assert response.status_code == 200

    _check_db(db, request_id, mongo_exist_after, False)


@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True,
    ARCHIVE_API_PERSONAL_DATA_WRITE_MODE={'__default__': 'both_fallback'},
)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_error_in_personal_fallback(
        taxi_archive_api, yt_client, db, mockserver,
):
    request_id = '15707319ba47436c96a4d2b3971dc2bd'
    mongo_exist_before = False
    mongo_exist_after = True

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_store_license(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/personal/v1/tins/store')
    def mock_store_tin(request):
        return mockserver.make_response('', 500)

    yt_client.add_lookup_rows_response(
        '{"id":"15707319ba47436c96a4d2b3971dc2bd"}',
        'src_response_pd.json',
        yson=True,
    )

    _check_db(db, request_id, mongo_exist_before, False)

    response = taxi_archive_api.post(
        'archive/orders/restore', json={'id': request_id, 'update': True},
    )

    assert response.status_code == 200

    _check_db(db, request_id, mongo_exist_after, False)


@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True,
    ARCHIVE_API_PERSONAL_DATA_WRITE_MODE={'__default__': 'both_no_fallback'},
)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_error_in_personal_no_fallback(
        taxi_archive_api, yt_client, db, mockserver,
):
    request_id = '15707319ba47436c96a4d2b3971dc2bd'
    mongo_exist_before = False
    mongo_exist_after = False

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_store_license(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/personal/v1/tins/store')
    def mock_store_tin(request):
        return mockserver.make_response('', 500)

    yt_client.add_lookup_rows_response(
        '{"id":"15707319ba47436c96a4d2b3971dc2bd"}',
        'src_response_pd.json',
        yson=True,
    )

    _check_db(db, request_id, mongo_exist_before, False)

    response = taxi_archive_api.post(
        'archive/orders/restore', json={'id': request_id, 'update': True},
    )

    assert response.status_code == 500

    _check_db(db, request_id, mongo_exist_after, False)


def _check_db(db, request_id, should_exist, id_exist):
    order = db.orders.find_one({'_id': request_id})
    assert (order is not None) == should_exist
    if order:
        assert order['performer']['driver_license'] == 'license'
        assert order['payment_tech']['inn_for_receipt'] == 'inn'
    if order and id_exist:
        assert order['performer']['driver_license_personal_id'] == 'licenseID'
        assert order['payment_tech']['inn_for_receipt_id'] == 'innID'
    elif order:
        assert 'driver_license_personal_id' not in order['performer']
        assert 'inn_for_receipt_id' not in order['payment_tech']


def _personal_store(request):
    request_json = json.loads(request.get_data())
    assert 'value' in request_json
    return {'id': request_json['value'] + 'ID', 'value': request_json['value']}
