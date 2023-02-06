import pytest


def prepare_request_claim(request: dict):
    request['c2c_data'] = {
        'payment_type': 'payment_type',
        'payment_method_id': 'payment_id',
        'partner_tag': 'boxberry',
    }
    del request['items'][0]['size']


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
async def test_check_status(state_controller, get_full_claim):
    state_controller.use_create_version('v2_cargo_c2c')
    claim_info = await state_controller.apply(target_status='performer_draft')
    claim_id = claim_info.claim_id

    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'performer_draft'

    response = await get_full_claim(claim_id)
    assert response['taxi_order_id'] == 'taxi_order_id_1'
    assert response['yandex_uid'] == 'user_id'
