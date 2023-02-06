import base64

import pytest


async def test_currency_validation(state_agents_created, validate_payment):
    """
        Check bad request error on unknown currency type.
    """
    state = await state_agents_created()

    await validate_payment(
        virtual_client_id=state.default_virtual_client_id,
        items_currency='BAD',
        status_code=400,
    )


@pytest.mark.parametrize('valid_inn', ['7743013901', '774623831540'])
async def test_inn_valid(state_agents_created, validate_payment, valid_inn):
    """
        Check OK on create with valid inn checksum.
    """
    state = await state_agents_created()

    await validate_payment(
        virtual_client_id=state.default_virtual_client_id,
        supplier_inn=valid_inn,
        status_code=200,
    )


@pytest.mark.parametrize('invalid_inn', ['6743013901', '674623831540'])
async def test_inn_invalid(
        state_agents_created, validate_payment, invalid_inn,
):
    """
        Check bad request error on invalid inn checksum.
    """
    state = await state_agents_created()

    await validate_payment(
        virtual_client_id=state.default_virtual_client_id,
        supplier_inn=invalid_inn,
        status_code=400,
    )


async def test_zero_sum_validation(state_agents_created, validate_payment):
    """
        Check bad request error on claim with zero sum over its items.
    """
    state = await state_agents_created()

    await validate_payment(
        virtual_client_id=state.default_virtual_client_id,
        price='0.00',
        status_code=400,
    )

    await validate_payment(
        virtual_client_id=state.default_virtual_client_id,
        items_count=1,
        item_count=0,
        status_code=400,
    )


@pytest.mark.config(CARGO_PAYMENTS_MARK_CODE_VALIDATION_ENABLED=False)
async def test_invalid_mark_code(state_agents_created, validate_payment):
    """
        Check 400 on create with invalid mark code.
    """
    state = await state_agents_created()

    invalid_mark = {
        'kind': 'gs1_data_matrix_base64',
        'code': base64.b64encode(
            b'8005112000\x1d21zZyR5SDcpc0KD\x1d0104060511218058005112000',
        ).decode(),
    }
    await validate_payment(
        virtual_client_id=state.default_virtual_client_id,
        item_mark=invalid_mark,
        status_code=400,
    )
