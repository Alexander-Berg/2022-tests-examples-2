import pytest

FLOW = 'claims'


async def test_absent_equal_to_unpaid(is_claim_paid, is_order_paid):
    assert not await is_claim_paid()
    assert not await is_order_paid(FLOW)


async def test_no_sum_is_unpaid_too(
        applying_state_no_sum, is_claim_paid, is_order_paid,
):
    assert not await is_claim_paid()
    assert not await is_order_paid(FLOW)


async def test_unpaid_until_hold(
        applying_state_holding, is_claim_paid, is_order_paid,
):
    assert not await is_claim_paid()
    assert not await is_order_paid(FLOW)


async def test_unpaid_if_hold_fail(
        applying_state_hold_fail, is_claim_paid, is_order_paid,
):
    assert not await is_claim_paid()
    assert not await is_order_paid(FLOW)


async def test_paid_if_held(applying_state_held, is_claim_paid, is_order_paid):
    assert await is_claim_paid()
    assert await is_order_paid(FLOW)


@pytest.fixture(name='applying_state_hold_fail')
async def _applying_state_hold_fail(
        applying_state_holding,
        inject_paid_less,
        flush_all,
        run_applying_stq,
        get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


@pytest.fixture(name='is_claim_paid')
def _is_claim_paid(taxi_cargo_finance, claim_id):
    url = '/internal/cargo-finance/v1/claims/payment-status'

    async def wrapper():
        params = {'claim_id': claim_id}
        response = await taxi_cargo_finance.post(url, params=params)
        assert response.status_code == 200
        return response.json()['is_paid']

    return wrapper


@pytest.fixture(name='is_order_paid')
def _is_order_paid(taxi_cargo_finance, claim_id):
    url = '/internal/cargo-finance/pay/order/payment-status'

    async def wrapper(flow):
        params = {'entity_id': claim_id, 'flow': flow}
        response = await taxi_cargo_finance.post(url, params=params)
        assert response.status_code == 200
        return response.json()['is_paid']

    return wrapper
