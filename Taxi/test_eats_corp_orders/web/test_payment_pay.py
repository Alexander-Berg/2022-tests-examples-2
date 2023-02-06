import uuid

import pytest

from eats_corp_orders.internal import constants
from test_eats_corp_orders import conftest


@conftest.skip_teamcity_old_redis
@pytest.mark.redis_store(file='redis_payment_completed')
@pytest.mark.config(
    EATS_CORP_ORDERS_TIMEOUT_SETTINGS={'wait_for_payment_ttl': 0},
)
@pytest.mark.now('2022-02-22T22:01:00+0000')
async def test_success_payment_with_qr_code(pay_response, stq):
    status, _ = await pay_response()
    assert status == 200
    assert stq.eats_corp_orders_pay.has_calls


@conftest.skip_teamcity_old_redis
@pytest.mark.config(
    EATS_CORP_ORDERS_TIMEOUT_SETTINGS={'wait_for_payment_ttl': 0.1},
)
@pytest.mark.now('2022-02-22T22:01:00+0000')
async def test_error_timeout_wait_for_payments(pay_response, stq):
    status, body = await pay_response({'idempotency_key': uuid.uuid4().hex})
    assert status == 408
    assert body['code'] == constants.ErrorCode.payment_timeout.value
    assert stq.eats_corp_orders_pay.has_calls


@pytest.mark.now('2022-02-22T23:00:00+0000')
async def test_error_user_code_expired(pay_response, stq):
    status, body = await pay_response()
    assert status == 403
    assert body['code'] == constants.ErrorCode.user_code_expired.value
    assert not stq.eats_corp_orders_pay.has_calls


@pytest.mark.now('2022-02-22T22:01:00+0000')
async def test_error_user_code_not_found(pay_response, stq):
    status, body = await pay_response({'user_code': 'incorrect_code'})
    assert status == 403
    assert body['code'] == constants.ErrorCode.user_code_not_found.value
    assert not stq.eats_corp_orders_pay.has_calls


@pytest.mark.parametrize(
    'authorization',
    ['terminal_id:wrong_token', 'wrong_id:secret_token', 'incorrect_format'],
)
async def test_error_incorrect_terminal_token(
        pay_response, authorization, stq,
):
    status, body = await pay_response(
        {'authorization': authorization, 'idempotency_key': uuid.uuid4().hex},
    )
    assert status == 401
    assert body['code'] == constants.ErrorCode.unauthorized.value
    assert not stq.eats_corp_orders_pay.has_calls


# todo: test case when order already created in pg
