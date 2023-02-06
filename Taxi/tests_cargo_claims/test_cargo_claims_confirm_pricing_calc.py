import pytest


@pytest.fixture(name='create_and_cancel_claim_with_segment')
async def _create_and_cancel_claim_with_segment(
        taxi_cargo_claims,
        get_default_headers,
        create_segment_with_performer,
        mock_waybill_info,
        mock_cargo_pricing_calc,
):
    async def wrapper():
        claim_info = await create_segment_with_performer()

        response = await taxi_cargo_claims.post(
            '/v2/claims/cancel',
            params={'claim_id': claim_info.claim_id},
            json={'version': 1, 'cancel_state': 'paid'},
            headers=get_default_headers(),
        )
        assert response.status_code == 200
        assert response.json()['status'] == 'cancelled'
        return claim_info

    return wrapper


async def test_stq(
        stq_runner,
        create_and_cancel_claim_with_segment,
        mock_cargo_pricing_confirm_usage,
):
    segment_info = await create_and_cancel_claim_with_segment()
    claim_id = segment_info.claim_id
    await stq_runner.cargo_claims_confirm_cancel_calc.call(
        task_id=f'{claim_id}_confirm_usage',
        kwargs={'claim_id': claim_id},
        expect_fail=False,
    )
    assert mock_cargo_pricing_confirm_usage.mock.times_called == 1


async def test_cancel_stq_create(stq, create_and_cancel_claim_with_segment):
    segment_info = await create_and_cancel_claim_with_segment()
    claim_id = segment_info.claim_id
    stq_call = await stq.cargo_claims_confirm_cancel_calc.wait_call()
    assert stq_call['kwargs']['claim_id'] == claim_id
