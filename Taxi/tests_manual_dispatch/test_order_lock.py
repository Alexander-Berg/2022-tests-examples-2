# pylint: disable=redefined-outer-name
import datetime

import pytest

NOW = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
NOW_STR = '2020-01-01T00:00:00+00:00'
NOW_MINUS_15S = datetime.datetime(
    2019, 12, 31, 23, 59, 45, tzinfo=datetime.timezone.utc,
)
NOW_MINUS_15S_STR = '2019-12-31T23:59:45+00:00'
IN_15S = datetime.datetime(2020, 1, 1, 0, 0, 15, tzinfo=datetime.timezone.utc)
IN_30S = datetime.datetime(2020, 1, 1, 0, 0, 30, tzinfo=datetime.timezone.utc)
IN_30S_STR = '2020-01-01T00:00:30+00:00'


@pytest.fixture
def assert_locked(get_order):
    def do_assert_locked(order_id, owner):
        order = get_order(
            order_id, projection=('owner_operator_id', 'lock_expiration_ts'),
        )
        assert order == {
            'owner_operator_id': owner,
            'lock_expiration_ts': IN_30S,
        }

    return do_assert_locked


@pytest.fixture
def assert_unlocked(get_order):
    def do_assert_unlocked(order_id):
        order = get_order(
            order_id, projection=('owner_operator_id', 'lock_expiration_ts'),
        )
        assert order['owner_operator_id'] is None
        assert order['lock_expiration_ts'] < NOW

    return do_assert_unlocked


@pytest.mark.now(NOW_STR)
@pytest.mark.parametrize(
    'kwargs',
    ({}, {'owner_operator_id': 'yandex_uid_1', 'lock_expiration_ts': IN_15S}),
)
async def test_orders_acquire(
        taxi_manual_dispatch,
        headers,
        create_order,
        get_order,
        assert_locked,
        kwargs,
):
    order = create_order(**kwargs)
    response = await taxi_manual_dispatch.post(
        '/v1/orders/acquire',
        json={'order_id': order['order_id']},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'locked_until': IN_30S_STR}
    assert_locked(order['order_id'], headers['X-Yandex-UID'])


@pytest.mark.now(NOW_STR)
@pytest.mark.parametrize(
    'expect_locked,expiration_ts', [(False, IN_30S), (True, NOW_MINUS_15S)],
)
async def test_concurrent_locks(
        taxi_manual_dispatch,
        headers,
        create_order,
        get_order,
        assert_locked,
        assert_unlocked,
        expect_locked,
        expiration_ts,
):
    create_order(
        order_id='order_id_1',
        owner_operator_id=headers['X-Yandex-UID'],
        lock_expiration_ts=expiration_ts,
    )
    create_order(order_id='order_id_2')
    response = await taxi_manual_dispatch.post(
        '/v1/orders/acquire', json={'order_id': 'order_id_2'}, headers=headers,
    )
    if expect_locked:
        assert response.status_code == 200
        assert response.json() == {'locked_until': IN_30S_STR}
        assert_unlocked('order_id_1')
        assert_locked('order_id_2', headers['X-Yandex-UID'])
    else:
        assert response.status_code == 409
        assert response.json()['code'] == 'concurrent_locks'
        assert_locked('order_id_1', headers['X-Yandex-UID'])
        assert_unlocked('order_id_2')


@pytest.mark.now(NOW_STR)
async def test_cant_lock_locked(
        taxi_manual_dispatch, headers, create_order, get_order, assert_locked,
):
    create_order(
        order_id='order_id_1',
        owner_operator_id='operator_id_2',
        lock_expiration_ts=IN_30S_STR,
    )
    response = await taxi_manual_dispatch.post(
        '/v1/orders/acquire', json={'order_id': 'order_id_1'}, headers=headers,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'already_locked',
        'message': 'Order is already locked by another operator',
    }

    assert_locked('order_id_1', 'operator_id_2')


@pytest.mark.now(NOW_STR)
async def test_not_pending(
        taxi_manual_dispatch,
        headers,
        create_order,
        get_order,
        assert_unlocked,
):
    create_order(order_id='order_id_1', status='assigned')
    response = await taxi_manual_dispatch.post(
        '/v1/orders/acquire', json={'order_id': 'order_id_1'}, headers=headers,
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'search_ended'

    assert_unlocked('order_id_1')


async def test_lock_404(taxi_manual_dispatch, headers):
    response = await taxi_manual_dispatch.post(
        '/v1/orders/acquire', json={'order_id': 'order_id_1'}, headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'order_not_found',
        'message': 'Order not found',
    }


@pytest.mark.parametrize('create_lock', ((True, False),))
async def test_unlock(
        taxi_manual_dispatch,
        headers,
        create_order,
        create_lock,
        assert_unlocked,
):
    if create_lock:
        create_order(
            order_id='order_id_1',
            lock_expiration_ts=IN_30S,
            owner_operator_id=headers['X-Yandex-UID'],
        )
    else:
        create_order('order_id_1')
    response = await taxi_manual_dispatch.post(
        '/v1/orders/release', json={'order_id': 'order_id_1'}, headers=headers,
    )
    assert response.status_code == 200
    assert_unlocked('order_id_1')
