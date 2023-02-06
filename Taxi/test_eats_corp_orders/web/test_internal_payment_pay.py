import pytest


@pytest.mark.now('2022-02-22T22:01:00+0000')
async def test_success_payment(internal_pay_response, stq):

    status = await internal_pay_response()
    assert status == 200

    assert stq.eats_corp_orders_pay.has_calls


@pytest.mark.now('2022-02-22T22:01:00+0000')
@pytest.mark.pgsql('eats_corp_orders', files=['existing_order.sql'])
async def test_ok_when_order_already_created(internal_pay_response, stq):

    status = await internal_pay_response()
    assert status == 200

    assert not stq.eats_corp_orders_pay.has_calls
