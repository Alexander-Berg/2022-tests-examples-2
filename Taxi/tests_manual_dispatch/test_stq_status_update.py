import pytest


@pytest.mark.parametrize(
    'status,taxi_status,has_performer,expected_status',
    [
        ('finished', 'expired', False, 'search_failed'),
        ('finished', 'expired', True, 'expired'),
        ('finished', 'cancelled', True, 'cancelled_by_taxi'),
        ('finished', 'complete', True, 'finished'),
        ('finished', 'failed', False, 'failed'),
        ('cancelled', None, False, 'cancelled'),
    ],
)
async def test_handle_finish(
        stq_runner,
        get_order,
        create_order,
        status,
        taxi_status,
        has_performer,
        expected_status,
        create_dispatch_attempt,
        get_dispatch_attempt,
):
    order = create_order(lookup_version=0)
    attempt = create_dispatch_attempt(
        order_id=order['order_id'], status='pending',
    )
    await stq_runner.manual_dispatch_handle_finish.call(
        task_id=order['order_id'],
        kwargs={
            'taxi_status': taxi_status,
            'status': status,
            'has_performer': has_performer,
            'lookup_version': 1,
        },
        expect_fail=False,
    )
    updated_order = get_order(order['order_id'], ['lookup_version', 'status'])
    updated_attempt = get_dispatch_attempt(
        attempt_id=attempt['id'], projection=('status',),
    )
    assert updated_attempt['status'] == 'cancelled'
    assert updated_order == {'lookup_version': 1, 'status': expected_status}


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_handle_autoreorder(
        stq_runner,
        get_order,
        create_order,
        stq,
        create_dispatch_attempt,
        mock_set_order_fields,
):
    order = create_order(lookup_version=0)
    create_dispatch_attempt(order_id='order_id_1', status='accepted')
    await stq_runner.manual_dispatch_handle_autoreorder.call(
        task_id='very_random_uuid',
        kwargs={'order_id': order['order_id'], 'lookup_version': 1},
        expect_fail=False,
    )
    updated_order = get_order(order['order_id'], ['lookup_version', 'status'])
    assert updated_order == {'lookup_version': 1, 'status': 'pending'}
    assert mock_set_order_fields['handler'].times_called == 1


async def test_autoreorder_wrong_transition(
        stq_runner,
        get_order,
        create_order,
        stq,
        create_dispatch_attempt,
        mock_set_order_fields,
):
    order = create_order(lookup_version=0, status='error')
    await stq_runner.manual_dispatch_handle_autoreorder.call(
        task_id='very_random_uuid',
        kwargs={'order_id': order['order_id'], 'lookup_version': 1},
        expect_fail=False,
    )
    assert get_order(order['order_id'])['status'] == 'error'
    assert mock_set_order_fields['handler'].times_called == 0


@pytest.mark.parametrize(
    'queue,kwargs',
    [
        (
            'manual_dispatch_handle_finish',
            {
                'taxi_status': 'complete',
                'status': 'cancelled',
                'has_performer': True,
                'lookup_version': 1,
            },
        ),
        (
            'manual_dispatch_handle_autoreorder',
            {'order_id': 'order_id_1', 'lookup_version': 1},
        ),
        (
            'manual_dispatch_handle_driving',
            {
                'order_id': 'order_id_1',
                'performer_dbid': 'dbid1',
                'performer_uuid': 'performer_uuid_1',
                'lookup_version': 1,
            },
        ),
    ],
)
async def test_wrong_lookup_version(
        stq_runner, get_order, create_order, queue, kwargs,
):
    order = create_order(lookup_version=5, status='finished')
    await getattr(stq_runner, queue).call(
        task_id=order['order_id'], kwargs=kwargs, expect_fail=False,
    )
    updated_order = get_order(order['order_id'], ['lookup_version', 'status'])
    assert updated_order == {
        'lookup_version': order['lookup_version'],
        'status': order['status'],
    }


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.parametrize(
    'queue,kwargs,delayed',
    [
        (
            'manual_dispatch_handle_finish',
            {
                'taxi_status': 'complete',
                'status': 'finished',
                'has_performer': True,
                'lookup_version': 4,
            },
            {
                'status': 'finished',
                'lookup_version': 4,
                'order_id': 'order_id_1',
                'performer_id': None,
                'reason': 'handle_finish',
            },
        ),
        (
            'manual_dispatch_handle_autoreorder',
            {'order_id': 'order_id_1', 'lookup_version': 1},
            {
                'status': 'pending',
                'lookup_version': 1,
                'order_id': 'order_id_1',
                'performer_id': None,
                'reason': 'autoreorder',
            },
        ),
        (
            'manual_dispatch_handle_driving',
            {
                'order_id': 'order_id_1',
                'performer_dbid': 'dbid1',
                'performer_uuid': 'uuid1',
                'lookup_version': 4,
            },
            {
                'status': 'assigned',
                'lookup_version': 4,
                'order_id': 'order_id_1',
                'performer_id': 'dbid1_uuid1',
                'reason': 'auto',
            },
        ),
    ],
)
async def test_no_such_order(
        stq_runner,
        get_order,
        create_order,
        queue,
        kwargs,
        get_delayed_updates,
        delayed,
):
    await getattr(stq_runner, queue).call(
        task_id='order_id_1', kwargs=kwargs, expect_fail=False,
    )
    assert get_delayed_updates(excluded=('id', 'created_ts')) == [delayed]
    assert get_order('order_id_1') is None
