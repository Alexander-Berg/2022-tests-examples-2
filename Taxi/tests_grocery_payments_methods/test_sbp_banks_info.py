import pytest

from tests_grocery_payments_methods import consts
from tests_grocery_payments_methods import models

BANKS = [models.SbpBankInfo(bank_name=f'bank_name:{i}') for i in range(5)]


@pytest.fixture(name='sbp_banks_info')
def _sbp_banks_info(taxi_grocery_payments_methods):
    async def _inner(headers=None):
        headers = headers or consts.DEFAULT_HEADERS
        return await taxi_grocery_payments_methods.post(
            '/internal/payments-methods/v1/sbp-banks-info',
            json={},
            headers=headers,
        )

    return _inner


async def test_basic(sbp_banks_info, grocery_payments_methods_configs):
    grocery_payments_methods_configs.sbp_banks(banks=BANKS)

    response = await sbp_banks_info()

    assert response.json() == {
        'sbp_banks_info': [bank.to_raw_response() for bank in BANKS],
    }
