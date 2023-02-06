import bson
import pytest


@pytest.mark.config(ORDER_CORE_TAKEOUT_SET_FIELDS_WHITELIST=['new-field'])
async def test_takeout_order_proc_set_fields(taxi_order_core):
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
        'takeout.version': {'$exists': False},
        'revision': revision,
        'update': {'$set': {'new-field': 'new-value'}},
    }

    # perform update
    response = await taxi_order_core.post(
        '/internal/takeout/v1/order-proc/set-fields',
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
    assert response['document']['updated'] > updated_before


@pytest.mark.config(ORDER_CORE_TAKEOUT_SET_FIELDS_WHITELIST=['new-field'])
@pytest.mark.parametrize(
    'order_id,revision,takeout_version,expect_status',
    [
        (
            'no-order',
            {'order.version': 111, 'processing.version': 17},
            73,
            409,
        ),
        (
            'no-order',
            {'order.version': {'$exists': False}, 'processing.version': 17},
            73,
            200,
        ),
        (
            'no-processing',
            {'order.version': 4, 'processing.version': 17},
            73,
            409,
        ),
        (
            'no-processing',
            {'order.version': 4, 'processing.version': {'$exists': False}},
            73,
            200,
        ),
        (
            'no-takeout',
            {'order.version': 4, 'processing.version': 17},
            73,
            409,
        ),
        (
            'no-takeout',
            {'order.version': 4, 'processing.version': 17},
            {'$exists': False},
            200,
        ),
        (
            'no-takeout',
            {'order.version': 4, 'processing.version': 17},
            None,
            400,
        ),
    ],
)
async def test_internal_order_proc_set_fields_errors(
        taxi_order_core, order_id, revision, takeout_version, expect_status,
):
    params = {'order_id': order_id}
    update_request = {
        'revision': revision,
        'update': {'$set': {'new-field': 'new-value'}},
        'takeout.version': takeout_version,
    }
    response = await taxi_order_core.post(
        '/internal/takeout/v1/order-proc/set-fields',
        params=params,
        data=bson.BSON.encode(update_request),
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == expect_status


@pytest.mark.config(ORDER_CORE_TAKEOUT_SET_FIELDS_WHITELIST=['new-field'])
@pytest.mark.parametrize(
    'order_id, app, expected_code',
    [
        ('foo', 'iphone', 200),
        ('foo', 'android', 409),
        ('bar', 'iphone', 404),
        ('restore_me', 'iphone', 409),
        ('restore_me_iphone', 'iphone', 200),
    ],
)
@pytest.mark.parametrize(
    'restore_success_code', ['restored', 'updated', 'mongo'],
)
async def test_or_conflict(
        taxi_order_core,
        mongodb,
        load_json,
        mockserver,
        order_id,
        app,
        expected_code,
        restore_success_code,
):
    archived_data = {i['_id']: i for i in load_json('archived_data.json')}

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    async def _order_proc_restore(request):
        assert order_id == request.json['id']
        assert request.json.get('update', False)

        archived = archived_data.get(order_id)
        if not archived:
            return [{'id': order_id, 'status': 'not_found'}]

        mongodb.order_proc.insert(archived)
        return [{'id': order_id, 'status': restore_success_code}]

    update_request = {
        'revision': {'order.version': 4, 'processing.version': 17},
        'filter': {'$or': [{'order.application': app}]},
        'update': {'$set': {'new-field': 'new-value'}},
        'takeout.version': {'$exists': False},
    }
    response = await taxi_order_core.post(
        '/internal/takeout/v1/order-proc/set-fields',
        data=bson.BSON.encode(update_request),
        params={'order_id': order_id, 'order_id_type': 'client_id'},
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == expected_code
