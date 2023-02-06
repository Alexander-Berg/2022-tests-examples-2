import pytest


@pytest.fixture
async def create_c2c_with_performer(taxi_cargo_claims, state_controller):
    state_controller.use_create_version('v2_cargo_c2c')
    claim_info = await state_controller.apply(target_status='performer_found')
    return claim_info
