import pytest


@pytest.mark.parametrize(
    'performer,attempt_status,reason',
    [
        ('dbid1_uuid1', 'accepted', 'manual'),
        ('dbid1_uuid2', 'overridden', 'overridden'),
        ('dbid1_uuid1', None, 'auto'),
    ],
)
async def test_handle_driving(
        stq_runner,
        create_dispatch_attempt,
        get_dispatch_attempt,
        create_order,
        get_order,
        get_order_audit,
        performer,
        attempt_status,
        reason,
):
    order = create_order(status='pending')
    if attempt_status is not None:
        create_dispatch_attempt(status='pending', performer_id='dbid1_uuid1')
    dbid, uuid = performer.split('_')
    await stq_runner.manual_dispatch_handle_driving.call(
        task_id='task_id_1',
        kwargs={
            'order_id': order['order_id'],
            'performer_dbid': dbid,
            'performer_uuid': uuid,
            'lookup_version': 1,
        },
    )

    attempts = get_dispatch_attempt(order_id=order['order_id'])
    audit = get_order_audit(order['order_id'], projection=('reason', 'status'))
    audit = [x for x in audit if x['status'] == 'assigned']
    order = get_order(order['order_id'], projection=('status', 'performer_id'))
    if attempt_status is not None:
        assert len(attempts) == 1
        assert attempts[0]['status'] == attempt_status
    else:
        assert not attempts
    assert order == {'status': 'assigned', 'performer_id': performer}
    assert audit == [{'status': 'assigned', 'reason': reason}]


async def test_wrong_transition(stq_runner, create_order, get_order):
    order = create_order(status='finished')
    await stq_runner.manual_dispatch_handle_driving.call(
        task_id='task_id_1',
        kwargs={
            'order_id': order['order_id'],
            'performer_dbid': 'dbid1',
            'performer_uuid': 'uuid1',
            'lookup_version': 1,
        },
    )

    assert get_order(order['order_id'])['status'] == 'finished'
