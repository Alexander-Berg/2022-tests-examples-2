import datetime
import operator

import bson
import pytest


@pytest.mark.parametrize(
    'order_id, found', [('foo', True), ('undefined', False)],
)
async def test_internal_order_proc_logging(
        taxi_order_core, testpoint, order_id, found,
):
    @testpoint('bson-logging')
    def log_bson_tp(data):
        pass

    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode({'fields': []}),
        params={'order_id': order_id},
        headers={'Content-Type': 'application/bson'},
    )
    if found:
        assert response.status_code == 200
        assert response.content_type == 'application/bson'
        assert log_bson_tp.times_called == 2
    else:
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        assert log_bson_tp.times_called == 1


@pytest.mark.parametrize('require_latest', [True, False])
async def test_internal_order_proc_get_fields(
        taxi_order_core, testpoint, require_latest,
):
    @testpoint('get-fields')
    def get_fields_tp(data):
        assert data['from_master'] == require_latest

    fields = [
        'commit_state',
        'created',
        'lookup.state.wave',
        'lookup.params',
        'candidates.subvention_geoareas.name',
        'lookup.nonexistent_field',
    ]
    request_params = {'fields': fields}
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode(request_params),
        params={'order_id': 'foo', 'require_latest': require_latest},
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200
    assert response.content_type == 'application/bson'
    response_body = bson.BSON.decode(response.content)
    assert response_body == {
        'document': {
            '_id': 'foo',
            'candidates': [],
            'commit_state': 'done',
            'created': datetime.datetime(2020, 1, 24, 14, 6, 55, 77000),
            'lookup': {},
            'order': {'version': 4},
            'processing': {'version': 17},
        },
        'revision': {'order.version': 4, 'processing.version': 17},
    }
    assert get_fields_tp.times_called == 1


@pytest.mark.config(
    ORDER_CORE_UPDATE_ORDER_PROC_WHITELIST=[
        'new-field',
        'status',
        'candidates',
        'processing.version',
    ],
)
async def test_internal_order_proc_set_fields(taxi_order_core):
    # fetch current 'revision'
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode({'fields': ['_id', 'updated']}),
        params={'order_id': 'foo'},
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200
    assert response.content_type == 'application/bson'
    response = bson.BSON.decode(response.content)
    revision = response['revision']
    updated_before = response['document']['updated']

    params = {'order_id': 'foo'}
    update_request = {
        'revision': revision,
        'update': {
            '$set': {'new-field': 'new-value'},
            '$unset': {'status': ''},
            '$push': {'candidates': {'foo': 'bar'}},
            '$inc': {'processing.version': 1},
        },
    }

    # perform update
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/set-fields',
        params=params,
        data=bson.BSON.encode(update_request),
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200

    # validate update's effects
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        params={'order_id': 'foo'},
        headers={'Content-Type': 'application/bson'},
        data=bson.BSON.encode(
            {'fields': ['new-field', 'status', 'candidates.foo', 'updated']},
        ),
    )
    assert response.status_code == 200
    assert response.content_type == 'application/bson'
    response = bson.BSON.decode(response.content)
    assert response['document']['new-field'] == 'new-value'
    assert 'status' not in response['document']
    assert response['document']['candidates'] == [{'foo': 'bar'}]
    assert response['document']['processing']['version'] == 18
    assert response['document']['updated'] > updated_before


@pytest.mark.config(
    ORDER_CORE_UPDATE_ORDER_PROC_WHITELIST=[
        'new-field',
        'status',
        'candidates',
        'processing.version',
    ],
)
async def test_internal_order_proc_set_fields_response(taxi_order_core):
    # fetch current 'revision'
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode(
            {'fields': ['_id', 'new-field', 'status', 'candidates.foo']},
        ),
        params={'order_id': 'foo'},
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200
    assert response.content_type == 'application/bson'
    response = bson.BSON.decode(response.content)
    revision = response['revision']

    assert 'new-field' not in response['document']
    assert 'status' in response['document']
    assert not response['document']['candidates']
    assert response['document']['processing']['version'] == 17

    params = {'order_id': 'foo'}
    update_request = {
        'revision': revision,
        'update': {
            '$set': {'new-field': 'new-value'},
            '$unset': {'status': ''},
            '$push': {'candidates': {'foo': 'bar'}},
            '$inc': {'processing.version': 1},
        },
        'fields': ['_id', 'new-field', 'status', 'candidates.foo'],
    }

    # perform update
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/set-fields',
        params=params,
        data=bson.BSON.encode(update_request),
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200

    # validate update's effects
    assert response.content_type == 'application/bson'
    response = bson.BSON.decode(response.content)
    assert response['document']['new-field'] == 'new-value'
    assert 'status' not in response['document']
    assert response['document']['candidates'] == [{'foo': 'bar'}]
    assert response['document']['processing']['version'] == 18


async def test_internal_order_proc_get_fields_early(taxi_order_core):
    fields = [
        'commit_state',
        'created',
        'lookup.state.wave',
        'lookup.params',
        'candidates.subvention_geoareas.name',
        'lookup.nonexistent_field',
    ]
    request_params = {'fields': fields}
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode(request_params),
        params={'order_id': 'no-order', 'require_latest': True},
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200
    assert response.content_type == 'application/bson'
    response_body = bson.BSON.decode(response.content)
    assert response_body == {
        'document': {
            '_id': 'no-order',
            'candidates': [],
            'commit_state': 'done',
            'created': datetime.datetime(2020, 1, 24, 14, 6, 55, 77000),
            'lookup': {},
            'processing': {'version': 17},
        },
        'revision': {
            'order.version': {'$exists': False},
            'processing.version': 17,
        },
    }


@pytest.mark.config(ORDER_CORE_UPDATE_ORDER_PROC_WHITELIST=['new-field'])
@pytest.mark.parametrize(
    'order_id,revision,expect_status',
    [
        ('no-order', {'order.version': 111, 'processing.version': 17}, 409),
        (
            'no-order',
            {'order.version': {'$exists': False}, 'processing.version': 17},
            200,
        ),
        ('no-processing', {'order.version': 4, 'processing.version': 17}, 409),
        (
            'no-processing',
            {'order.version': 4, 'processing.version': {'$exists': False}},
            200,
        ),
    ],
)
async def test_internal_order_proc_set_fields_early(
        taxi_order_core, order_id, revision, expect_status,
):
    params = {'order_id': order_id}
    update_request = {
        'revision': revision,
        'update': {'$set': {'new-field': 'new-value'}},
    }
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/set-fields',
        params=params,
        data=bson.BSON.encode(update_request),
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == expect_status


@pytest.mark.parametrize(
    'order_id, id_type, expected_code',
    [
        ('foo', None, 200),
        ('foo', 'exact_id', 200),
        ('foo', 'client_id', 200),
        ('foo', 'any_id', 200),
        ('foo', 'alias_id', 404),
        ('alias-foo', None, 404),
        ('alias-foo', 'exact_id', 404),
        ('alias-foo', 'client_id', 404),
        ('alias-foo', 'any_id', 200),
        ('alias-foo', 'alias_id', 200),
        ('reorder-foo', None, 404),
        ('reorder-foo', 'exact_id', 404),
        ('reorder-foo', 'client_id', 200),
        ('reorder-foo', 'any_id', 200),
        ('reorder-foo', 'alias_id', 404),
    ],
)
async def test_get_fields_ids(
        taxi_order_core, order_id, id_type, expected_code,
):
    params = {'order_id': order_id}
    if id_type is not None:
        params['order_id_type'] = id_type
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode({'fields': []}),
        params=params,
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'order_id, id_type, expected_code',
    [
        ('foo', None, 200),
        ('foo', 'exact_id', 200),
        ('foo', 'client_id', 200),
        ('foo', 'any_id', 200),
        ('foo', 'alias_id', 404),
        ('alias-foo', None, 404),
        ('alias-foo', 'exact_id', 404),
        ('alias-foo', 'client_id', 404),
        ('alias-foo', 'any_id', 200),
        ('alias-foo', 'alias_id', 200),
        ('reorder-foo', None, 404),
        ('reorder-foo', 'exact_id', 404),
        ('reorder-foo', 'client_id', 200),
        ('reorder-foo', 'any_id', 200),
        ('reorder-foo', 'alias_id', 404),
    ],
)
@pytest.mark.config(ORDER_CORE_UPDATE_ORDER_PROC_WHITELIST=['new-field'])
async def test_set_fields_ids(
        taxi_order_core, order_id, id_type, expected_code,
):
    params = {'order_id': order_id}
    if id_type is not None:
        params['order_id_type'] = id_type
    update_request = {
        'revision': {'order.version': 4, 'processing.version': 17},
        'update': {'$set': {'new-field': 'new-value'}},
    }

    # perform update
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/set-fields',
        params=params,
        data=bson.BSON.encode(update_request),
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'order_id, id_type, request_filter, expected_code',
    [
        ('foo', 'exact_id', None, 200),
        ('foo', 'exact_id', {'order.user_id': 'bar'}, 200),
        ('foo', 'exact_id', {'order.user_id': 'invalid'}, 404),
        ('alias-foo', 'alias_id', None, 200),
        ('alias-foo', 'alias_id', {'order.user_id': 'bar'}, 200),
        ('alias-foo', 'alias_id', {'order.user_id': 'invalid'}, 404),
    ],
)
async def test_get_fields_filter(
        taxi_order_core, order_id, id_type, request_filter, expected_code,
):
    params = {'order_id': order_id}
    if id_type is not None:
        params['order_id_type'] = id_type
    body = {'fields': []}
    if request_filter is not None:
        body['filter'] = request_filter
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode(body),
        params=params,
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == expected_code


@pytest.mark.experiments3(
    filename='forbid_edit_takeout_anonymized_order_experiment_no_match.json',
)
@pytest.mark.parametrize(
    'order_id, app, expected_code, expected_error_code_message',
    [
        ('foo', 'iphone', 200, None),
        ('foo', 'android', 409, 'race_condition'),
        ('reorder-foo', 'iphone', 200, None),
        ('bar', 'iphone', 404, 'no_such_order'),
        pytest.param(
            'foo',
            'android',
            409,
            'race_condition',
            marks=(
                pytest.mark.experiments3(
                    filename='forbid_edit_takeout_anonymized_order_experiment_match.json',  # noqa
                )
            ),
            id='not anonymized, exp_match',
        ),
        pytest.param(
            'foo-takeout-anonymized',
            'iphone',
            200,
            None,
            marks=(
                pytest.mark.experiments3(
                    filename='forbid_edit_takeout_anonymized_order_experiment_no_match.json',  # noqa
                )
            ),
            id='anonymized, exp_no_match',
        ),
        pytest.param(
            'foo-takeout-anonymized',
            'iphone',
            409,
            'order_is_anonymized',
            marks=(
                pytest.mark.experiments3(
                    filename='forbid_edit_takeout_anonymized_order_experiment_match.json',  # noqa
                )
            ),
            id='anonymized, exp_match',
        ),
    ],
)
@pytest.mark.config(ORDER_CORE_UPDATE_ORDER_PROC_WHITELIST=['new-field'])
async def test_or_conflict(
        taxi_order_core,
        order_id,
        app,
        expected_code,
        expected_error_code_message,
):
    update_request = {
        'revision': {'order.version': 4, 'processing.version': 17},
        'filter': {'$or': [{'order.application': app}]},
        'update': {'$set': {'new-field': 'new-value'}},
        'fields': [],
    }
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/set-fields',
        data=bson.BSON.encode(update_request),
        params={'order_id': order_id, 'order_id_type': 'client_id'},
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == expected_code
    if expected_code != 200:
        assert response.json()['code'] == expected_error_code_message


@pytest.mark.parametrize(
    'order_id, autorestore, expected_status, expected_restores',
    [
        ('existing_order', True, 200, 0),
        ('restore_me', True, 200, 1),
        ('never_exists', True, 404, 1),
        ('existing_order', False, 200, 0),
        ('restore_me', False, 404, 0),
        ('never_exists', False, 404, 0),
    ],
)
@pytest.mark.parametrize('order_id_type', [None, 'exact_id', 'client_id'])
@pytest.mark.parametrize(
    'restore_success_code', ['restored', 'updated', 'mongo'],
)
async def test_restore_from_archive(
        taxi_order_core,
        mockserver,
        mongodb,
        load_json,
        order_id,
        expected_status,
        autorestore,
        expected_restores,
        order_id_type,
        restore_success_code,
):
    archived_data = {i['_id']: i for i in load_json('archived_data.json')}

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    async def order_proc_restore(request):
        assert order_id == request.json['id']
        assert request.json.get('update', False)

        archived = archived_data.get(order_id)
        if not archived:
            return [{'id': order_id, 'status': 'not_found'}]

        mongodb.order_proc.insert(archived)
        return [{'id': order_id, 'status': restore_success_code}]

    params = {'order_id': order_id, 'autorestore': autorestore}
    if order_id_type:
        params.update({'order_id_type': order_id_type})
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode({'fields': ['_id']}),
        params=params,
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == expected_status
    assert order_proc_restore.times_called == expected_restores
    if expected_status == 200:
        assert response.content_type == 'application/bson'
        response_body = bson.BSON.decode(response.content)
        assert response_body['document']['_id'] == order_id


@pytest.mark.parametrize(
    'conflict_times,expect_fail',
    [(0, False), (1, False), (2, True), (3, True), (4, True)],
)
async def test_restore_conflict(
        taxi_order_core,
        mockserver,
        mongodb,
        load_json,
        conflict_times,
        expect_fail,
):
    order_id = 'restore_me'
    archived_data = {i['_id']: i for i in load_json('archived_data.json')}

    test_state = {'conflict_times': conflict_times}

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    async def order_proc_restore(request):
        assert order_id == request.json['id']
        assert request.json.get('update', False)

        if test_state['conflict_times']:
            test_state['conflict_times'] -= 1
            return [{'id': order_id, 'status': 'conflict'}]

        archived = archived_data.get(order_id)
        mongodb.order_proc.insert(archived)
        return [{'id': order_id, 'status': 'restored'}]

    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode({'fields': ['_id']}),
        params={'order_id': order_id, 'autorestore': True},
        headers={'Content-Type': 'application/bson'},
    )

    if expect_fail:
        assert response.status_code == 500
    else:
        assert response.status_code == 200
        assert response.content_type == 'application/bson'
        response_body = bson.BSON.decode(response.content)
        assert response_body['document']['_id'] == order_id
        assert order_proc_restore.times_called == (conflict_times + 1)


@pytest.mark.parametrize('order_id_type', ['alias_id', 'any_id'])
@pytest.mark.parametrize('autorestore', [True, False])
async def test_bad_order_id_type(
        taxi_order_core, mockserver, order_id_type, autorestore, mongodb,
):
    order_id = 'not_exists_in_mongo'

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    async def _order_proc_restore(request):
        return [{'id': order_id, 'status': 'restored'}]

    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode({'fields': ['_id']}),
        params={
            'order_id': order_id,
            'autorestore': autorestore,
            'order_id_type': order_id_type,
        },
        headers={'Content-Type': 'application/bson'},
    )

    if autorestore:
        assert response.status_code == 400
        assert response.json()['code'] == 'bad_order_id_type'
    else:
        assert response.status_code == 404


@pytest.mark.parametrize('autorestore', [True, False])
@pytest.mark.parametrize(
    'archive_status,expect_status,expected_code',
    [
        ('conflict', 500, None),
        ('not_found', 404, 'no_such_order'),
        ('undefined', 500, None),
        (None, 500, None),
    ],
)
async def test_restore_failures(
        taxi_order_core,
        mockserver,
        autorestore,
        archive_status,
        expect_status,
        expected_code,
):
    order_id = 'not_exists_in_mongo'

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    async def _order_proc_restore(request):
        if archive_status:
            return [{'id': order_id, 'status': archive_status}]
        return mockserver.make_response(status=500, json={})

    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-fields',
        data=bson.BSON.encode({'fields': ['_id']}),
        params={'order_id': order_id, 'autorestore': autorestore},
        headers={'Content-Type': 'application/bson'},
    )
    if autorestore:
        assert response.status_code == expect_status
        if expected_code:
            assert response.json()['code'] == expected_code
    else:
        assert response.status_code == 404


@pytest.mark.parametrize(
    'request_filter, expected_ids',
    [
        (None, ['foo', 'foo-multiorder']),
        ({'order.application': {'$in': ['iphone']}}, ['foo']),
    ],
)
async def test_internal_order_proc_bulk_get_fields(
        taxi_order_core, request_filter, expected_ids,
):
    expected_orders = {
        'foo': {
            '_id': 'foo',
            'candidates': [],
            'commit_state': 'done',
            'created': datetime.datetime(2020, 1, 24, 14, 6, 55, 77000),
            'lookup': {},
            'order': {'application': 'iphone'},
        },
        'foo-multiorder': {
            '_id': 'foo-multiorder',
            'order': {'application': 'android'},
        },
    }
    fields = [
        'commit_state',
        'created',
        'lookup.state.wave',
        'lookup.params',
        'candidates.subvention_geoareas.name',
        'lookup.nonexistent_field',
        'order.application',
    ]
    request_body = {'fields': fields, 'order_ids': ['foo', 'foo-multiorder']}
    if request_filter is not None:
        request_body['filter'] = request_filter
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/bulk-get-fields',
        data=bson.BSON.encode(request_body),
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200
    assert response.content_type == 'application/bson'
    documents = bson.BSON.decode(response.content)['documents']
    assert sorted(documents, key=operator.itemgetter('_id')) == [
        expected_orders[order_id] for order_id in expected_ids
    ]


@pytest.mark.parametrize(
    'request_body',
    [
        {'unused': {}},
        {'order_ids': []},
        {'order_ids': {'order-id': '123'}},
        {'order_ids': ['order-id'] * 20},
        {'order_ids': ['order-id'], 'filter': 'fltr'},
    ],
)
@pytest.mark.config(ORDER_CORE_BULK_LIMIT=10)
async def test_internal_order_proc_bulk_get_fields_400(
        taxi_order_core, request_body,
):
    request_body['fields'] = ['fld']
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/bulk-get-fields',
        data=bson.BSON.encode(request_body),
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_params, request_filter, expected_hint, expected_ids',
    [
        (
            {'phone_id': '5d4d016491272f03f6ab5cfd'},
            None,
            {'order.user_phone_id': 1},
            ['foo', 'foo-multiorder'],
        ),
        (
            {'user_uid': '4034021924'},
            None,
            {'order.user_uid': 1},
            ['foo', 'foo-multiorder'],
        ),
        (
            {'user_id': 'bar'},
            None,
            {'order.user_id': 1, 'status': 1},
            ['foo', 'foo-multiorder'],
        ),
        (
            {'phone_id': '5d4d016491272f03f6ab5cf1'},
            None,
            {'order.user_phone_id': 1},
            [],
        ),
        ({'user_uid': 'invalid-user-uid'}, None, {'order.user_uid': 1}, []),
        (
            {'user_id': 'invalid-user-id'},
            None,
            {'order.user_id': 1, 'status': 1},
            [],
        ),
        (
            {'phone_id': '5d4d016491272f03f6ab5cfd'},
            {'order.application': {'$in': ['iphone']}},
            {'order.user_phone_id': 1},
            ['foo'],
        ),
        (
            {'user_uid': '4034021924'},
            {'order.application': {'$in': ['iphone']}},
            {'order.user_uid': 1},
            ['foo'],
        ),
        (
            {'user_id': 'bar'},
            {'order.application': {'$in': ['iphone']}},
            {'order.user_id': 1, 'status': 1},
            ['foo'],
        ),
        (
            {
                'phone_id': '5d4d016491272f03f6ab5cfd',
                'user_uid': '4034021924',
                'user_id': 'bar',
            },
            None,
            {'order.user_phone_id': 1},
            ['foo', 'foo-multiorder'],
        ),
    ],
)
@pytest.mark.parametrize('require_latest', [True, False])
async def test_internal_order_proc_search_fields(
        taxi_order_core,
        request_params,
        request_filter,
        expected_ids,
        expected_hint,
        require_latest,
        testpoint,
):
    @testpoint('search-fields')
    def search_fields_tp(data):
        assert data['from_master'] == require_latest
        assert data['hint'] == expected_hint

    expected_orders = {
        'foo': {
            '_id': 'foo',
            'candidates': [],
            'commit_state': 'done',
            'created': datetime.datetime(2020, 1, 24, 14, 6, 55, 77000),
            'lookup': {},
            'order': {'application': 'iphone'},
        },
        'foo-multiorder': {
            '_id': 'foo-multiorder',
            'order': {'application': 'android'},
        },
    }
    fields = [
        'commit_state',
        'created',
        'lookup.state.wave',
        'lookup.params',
        'candidates.subvention_geoareas.name',
        'lookup.nonexistent_field',
        'order.application',
    ]
    request_body = {'fields': fields}
    if request_filter is not None:
        request_body['filter'] = request_filter
    params = request_params.copy()
    params['require_latest'] = require_latest
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/search-fields',
        data=bson.BSON.encode(request_body),
        params=params,
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200
    assert response.content_type == 'application/bson'
    documents = bson.BSON.decode(response.content)['documents']
    assert sorted(documents, key=operator.itemgetter('_id')) == [
        expected_orders[order_id] for order_id in expected_ids
    ]

    assert search_fields_tp.times_called == 1


@pytest.mark.parametrize(
    'request_params, request_body',
    [
        ({'unused': {}}, {}),
        ({'phone_id': 'invalid'}, {}),
        ({'user_id': 'user-id'}, {'filter': 'fltr'}),
    ],
)
async def test_internal_order_proc_search_fields_400(
        taxi_order_core, request_params, request_body,
):
    request_body['fields'] = ['fld']
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/search-fields',
        data=bson.BSON.encode(request_body),
        params=request_params,
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 400
