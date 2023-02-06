async def test_status_resolution_success(state_controller):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='new')
    assert 'status_response' not in claim_info.claim_full_response

    claim_info = await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )
    assert claim_info.claim_full_response['status_resolution'] == 'success'


async def test_status_resolution_failed(state_controller):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='cancelled')
    assert claim_info.claim_full_response['status_resolution'] == 'failed'
