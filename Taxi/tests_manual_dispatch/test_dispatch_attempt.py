# pylint: disable=redefined-outer-name
import datetime

import pytest


@pytest.fixture
def create_locked_order(create_order):
    create_order(
        order_id='order_id_1',
        owner_operator_id='yandex_uid_1',
        lock_expiration_ts=datetime.datetime.now()
        + datetime.timedelta(days=1),
    )


@pytest.mark.parametrize(
    'message,status', [(None, 'pending'), ('no_answer', 'declined')],
)
async def test_offer_success(
        taxi_manual_dispatch,
        create_locked_order,
        get_dispatch_attempt,
        stq,
        headers,
        message,
        status,
):
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/offer',
        headers=headers,
        json={
            'order_id': 'order_id_1',
            'park_id': 'dbid1',
            'driver_id': 'uuid1',
            'decline_message': message,
        },
    )
    assert response.status_code == 200
    assert stq.manual_dispatch_update_attempt_info.times_called == 1
    call_kwargs = stq.manual_dispatch_update_attempt_info.next_call()['kwargs']
    del call_kwargs['log_extra']
    assert call_kwargs == {'attempt_id': 1, 'clear_only': False}
    attempt = get_dispatch_attempt(
        attempt_id=response.json()['attempt_id'],
        excluded=('updated_ts', 'id'),
    )
    attempt['expiration_time'] = attempt.pop('expiration_ts') - attempt.pop(
        'created_ts',
    )
    assert attempt == {
        'expiration_time': datetime.timedelta(minutes=1),
        'operator_id': 'yandex_uid_1',
        'order_id': 'order_id_1',
        'message': message,
        'status': status,
        'performer_id': 'dbid1_uuid1',
    }


async def test_no_such_order(taxi_manual_dispatch, headers):
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/offer',
        headers=headers,
        json={
            'order_id': 'doesntexist',
            'park_id': 'dbid1',
            'driver_id': 'uuid1',
        },
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found'


async def test_duplicate_order_attempt(
        taxi_manual_dispatch,
        headers,
        create_dispatch_attempt,
        create_locked_order,
):
    create_dispatch_attempt(order_id='order_id_1', operator_id='other_guy')
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/offer',
        headers=headers,
        json={
            'order_id': 'order_id_1',
            'park_id': 'dbid1',
            'driver_id': 'uuid1',
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'duplicate_order_attempt'


async def test_duplicate_operator_attempt(
        taxi_manual_dispatch,
        headers,
        create_dispatch_attempt,
        create_order,
        create_locked_order,
):
    create_order(order_id='order_id_2')
    create_dispatch_attempt(order_id='order_id_2', operator_id='yandex_uid_1')
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/offer',
        headers=headers,
        json={
            'order_id': 'order_id_1',
            'park_id': 'dbid1',
            'driver_id': 'uuid1',
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'duplicate_operator_attempt'


@pytest.mark.parametrize(
    'owner_operator_id,lock_expiration_ts',
    [
        ('yandex_uid_1', datetime.datetime(1970, 1, 1)),
        ('yandex_uid_2', datetime.datetime.now() + datetime.timedelta(days=1)),
        (None, datetime.datetime(1970, 1, 1)),
    ],
)
async def test_not_locked(
        taxi_manual_dispatch,
        headers,
        create_order,
        owner_operator_id,
        lock_expiration_ts,
):
    create_order(
        order_id='order_id_1',
        owner_operator_id=owner_operator_id,
        lock_expiration_ts=lock_expiration_ts,
    )
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/offer',
        headers=headers,
        json={
            'order_id': 'order_id_1',
            'park_id': 'dbid1',
            'driver_id': 'uuid1',
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'not_locked'


async def test_not_pending(taxi_manual_dispatch, headers, create_order):
    create_order(
        order_id='order_id_1',
        owner_operator_id='yandex_uid_1',
        status='assigned',
        lock_expiration_ts=datetime.datetime.now()
        + datetime.timedelta(days=1),
    )
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/offer',
        headers=headers,
        json={
            'order_id': 'order_id_1',
            'park_id': 'dbid1',
            'driver_id': 'uuid1',
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'search_ended'


async def test_abort_success(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        headers,
        get_dispatch_attempt,
        stq,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(
        order_id='order_id_1', operator_id='yandex_uid_1',
    )
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/abort',
        headers=headers,
        json={'attempt_id': attempt['id'], 'message': 'foo bar'},
    )
    assert response.status_code == 200
    assert get_dispatch_attempt(
        attempt_id=attempt['id'], projection=('status', 'message'),
    ) == {'status': 'cancelled', 'message': 'foo bar'}
    assert stq.manual_dispatch_update_attempt_info.times_called == 1
    call_kwargs = stq.manual_dispatch_update_attempt_info.next_call()['kwargs']
    del call_kwargs['log_extra']
    assert call_kwargs == {'attempt_id': 1, 'clear_only': True}


@pytest.mark.parametrize(
    'status,operator_id,attempt_id',
    [
        ('pending', 'yandex_uid_1', 0),
        ('cancelled', 'yandex_uid_1', 1),
        ('pending', 'yandex_uid_2', 1),
    ],
)
async def test_abort_404(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        headers,
        get_dispatch_attempt,
        status,
        operator_id,
        attempt_id,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(
        order_id='order_id_1', operator_id=operator_id, status=status,
    )
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/abort',
        headers=headers,
        json={'attempt_id': attempt_id, 'message': 'foo bar'},
    )
    assert response.status_code == 404
    assert get_dispatch_attempt(
        attempt_id=attempt['id'], projection=('status', 'operator_id'),
    ) == {'status': status, 'operator_id': operator_id}
