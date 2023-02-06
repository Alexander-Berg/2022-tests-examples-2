import bson


async def test_change_price_with_callback_url(
        taxi_cargo_claims, state_controller, stq_runner,
):
    state_controller.set_options(with_callback_url=True)
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_id,
        args=[claim_id, '123.0', 'some reson'],
        expect_fail=False,
    )


async def test_change_price_not_found(
        taxi_cargo_claims, state_controller, stq_runner,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_id,
        args=[claim_id, '123.0', 'some reson'],
        expect_fail=True,
    )


async def test_change_price(
        taxi_cargo_claims, state_controller, stq_runner, stq,
):
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_id,
        args=[claim_id, '123.0', 'some reson'],
        expect_fail=False,
    )

    new_claim_info = await state_controller.get_claim_info()
    assert (
        new_claim_info.claim_full_response['pricing']['final_price']
        == '147.6000'
    )

    # Check no recursion
    assert stq.cargo_claims_change_claim_order_price.times_called == 0


async def test_zero_response(
        taxi_cargo_claims, state_controller, stq_runner, mockserver,
):
    @mockserver.json_handler('/archive-api/archive/order')
    def _order(request):
        response = {
            'doc': {'payment_tech': {'without_vat_to_pay': {'ride': 0}}},
        }
        return mockserver.make_response(bson.BSON.encode(response), status=200)

    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_id,
        args=[claim_id, '1234.0', 'initial_price'],
        expect_fail=False,
    )

    new_claim_info = await state_controller.get_claim_info()
    assert (
        new_claim_info.claim_full_response['pricing']['final_price']
        == '1480.8000'
    )


async def test_new_pricing_flow_support_change(
        taxi_cargo_claims, state_controller, stq_runner,
):

    state_controller.set_options(cargo_pricing_flow=True)
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_id,
        args=[claim_id, '123.0', 'some reson'],
        expect_fail=False,
    )

    new_claim_info = await state_controller.get_claim_info()
    assert (
        new_claim_info.claim_full_response['pricing']['final_price']
        == '147.6000'
    )


async def test_dragon_order(
        taxi_cargo_claims,
        state_controller,
        stq_runner,
        create_segment_with_performer,
        stq,
):
    state_controller.set_options(cargo_pricing_flow=True)
    segment = await create_segment_with_performer()

    new_price = '123.0'
    reason_code = 'some reson'
    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=f'order/{segment.cargo_order_id}',
        args=[f'order/{segment.cargo_order_id}', new_price, reason_code],
        expect_fail=False,
    )

    assert stq.cargo_claims_change_claim_order_price.times_called == 1
    next_call = stq.cargo_claims_change_claim_order_price.next_call()
    assert (
        next_call['id']
        == f'order/{segment.cargo_order_id}' + '_' + segment.claim_id
    )
    assert next_call['kwargs']['cargo_ref_id'] == segment.claim_id
    assert next_call['kwargs']['new_price'] == new_price
    assert next_call['kwargs']['reason_code'] == reason_code
