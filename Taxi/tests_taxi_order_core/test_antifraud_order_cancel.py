import pytest


@pytest.mark.parametrize(
    'order_status, order_taxi_status, cancellable',
    [
        ('pending', None, False),
        ('assigned', 'driving', False),
        ('finished', 'complete', True),
    ],
)
async def test_order_statuses(
        taxi_order_core,
        mongodb,
        order_status,
        order_taxi_status,
        cancellable,
        stq,
        now,
        mockserver,
):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        assert req.query['item_id'] == 'basic-order'
        assert 'due' not in req.query
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    assert (
        mongodb.order_proc.update(
            {'_id': 'basic-order'},
            {
                '$set': {
                    'order.status': order_status,
                    'order.taxi_status': order_taxi_status,
                },
            },
        )['nModified']
        == 1
    )

    expected_taxi_status = 'cancelled' if cancellable else order_taxi_status
    expected_code = 200 if cancellable else 406
    expected_processing_calls = 1 if cancellable else 0

    with stq.flushing():
        assert stq.is_empty
        response = await taxi_order_core.post(
            '/internal/antifraud/v1/cancel-order',
            params={'order_id': 'basic-order'},
        )
        assert response.status_code == expected_code
        new_proc = mongodb.order_proc.find_one({'_id': 'basic-order'})
        assert new_proc['order']['taxi_status'] == expected_taxi_status

        assert create_event.times_called == expected_processing_calls


@pytest.mark.parametrize(
    'cancel_order_id, fraud_archived, expected_status, expected_archive_calls',
    [
        ('fraud-order', False, 200, 0),
        ('fraud-order', True, 200, 1),
        ('unknown-order', False, 404, 1),
    ],
)
async def test_archive_restore(
        taxi_order_core,
        mongodb,
        stq,
        now,
        archive_api,
        cancel_order_id,
        fraud_archived,
        expected_status,
        expected_archive_calls,
        mockserver,
):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        assert req.query['item_id'] == cancel_order_id
        assert 'due' not in req.query
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    fraud_order_id = 'fraud-order'
    if fraud_archived:
        proc = mongodb.order_proc.find_one({'_id': fraud_order_id})
        archive_api.set_order_proc([proc])
        mongodb.order_proc.delete_one({'_id': fraud_order_id})

    cancellable = expected_status == 200

    with stq.flushing():
        assert stq.is_empty

        response = await taxi_order_core.post(
            '/internal/antifraud/v1/cancel-order',
            params={'order_id': cancel_order_id},
        )
        assert response.status_code == expected_status
        assert (
            archive_api.order_proc_restore.times_called
            == expected_archive_calls
        )

        if cancellable:
            new_proc = mongodb.order_proc.find_one({'_id': cancel_order_id})
            assert new_proc['order']['taxi_status'] == 'cancelled'

        assert create_event.times_called == (1 if cancellable else 0)
