import pytest

from eats_corp_orders.internal import constants


@pytest.mark.now('2022-02-22T22:01:00+0000')
@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['existing_order.sql', 'pg_eats_corp_orders.sql'],
)
async def test_success(
        taxi_eats_corp_orders_web,
        check_codes_db,
        check_redis_array,
        order_id,
        terminal_id,
        terminal_token,
        idempotency_key,
        stq,
        check_order_status_db,
        load_json,
        cancel_token,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment/cancel',
        json={
            'order_id': order_id,
            'authorization': f'{terminal_id}:{terminal_token}',
            'cancel_token': cancel_token,  # todo: remove this param
        },
    )
    assert response.status == 200

    assert stq.eats_corp_orders_cancel.has_calls
    check_order_status_db(
        order_id, 'failed', None, constants.ErrorCode.order_cancelled.value,
    )
    check_redis_array(
        f'payment_{terminal_id}_{idempotency_key}',
        load_json('redis_order_rejected.json'),
    )


@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['existing_order.sql', 'pg_eats_corp_orders.sql'],
)
async def test_works_with_cancel_token(
        taxi_eats_corp_orders_web,
        order_id,
        terminal_id,
        terminal_token,
        cancel_token,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment/cancel',
        json={
            'order_id': order_id,
            'authorization': f'{terminal_id}:{terminal_token}',
            'cancel_token': cancel_token,
        },
    )
    assert response.status == 200


@pytest.mark.pgsql('eats_corp_orders', files=['pg_eats_corp_orders.sql'])
async def test_fails_if_no_body(taxi_eats_corp_orders_web, yandex_uid):
    response = await taxi_eats_corp_orders_web.post('/v1/payment/cancel')
    assert response.status == 400


@pytest.mark.pgsql('eats_corp_orders', files=['pg_eats_corp_orders.sql'])
async def test_fails_if_no_authorization(
        taxi_eats_corp_orders_web, yandex_uid, order_id, cancel_token,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment/cancel',
        json={
            'order_id': order_id,
            'cancel_token': cancel_token,  # todo: remove this param
            'authorization': '',
        },
    )
    assert response.status == 401


@pytest.mark.pgsql(
    'eats_corp_orders', files=['existing_order.sql', 'other_terminal.sql'],
)
async def test_fails_if_other_terminal(
        taxi_eats_corp_orders_web, yandex_uid, order_id, terminal_token,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment/cancel',
        json={
            'order_id': order_id,
            'authorization': f'other_terminal_id:{terminal_token}',
            'cancel_token': '',
        },
    )
    assert response.status == 403


@pytest.mark.pgsql('eats_corp_orders', files=['pg_eats_corp_orders.sql'])
async def test_fails_if_order_not_exists(
        taxi_eats_corp_orders_web,
        yandex_uid,
        order_id,
        terminal_id,
        terminal_token,
        cancel_token,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment/cancel',
        json={
            'order_id': order_id,
            'authorization': f'{terminal_id}:{terminal_token}',
            'cancel_token': cancel_token,
        },
    )
    assert response.status == 404
