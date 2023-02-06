import pytest

from . import headers
from . import models


@pytest.fixture(name='grocery_payments_pay_info')
def _grocery_payments_pay_info(taxi_grocery_payments):
    async def _inner(status_code=200, country=models.Country.Russia, **kwargs):
        response = await taxi_grocery_payments.post(
            '/lavka/v1/payments/v1/pay-info',
            json={'country_iso2': country.country_iso2, **kwargs},
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


async def test_pay_info(grocery_payments_pay_info, grocery_payments_configs):
    country = models.Country.Russia
    service_token = 'service_token'
    merchants = ['merchant']

    grocery_payments_configs.grocery_service_token(service_token)
    grocery_payments_configs.grocery_merchants(merchants)

    response = await grocery_payments_pay_info(country=country)

    assert response['merchants'] == merchants
    assert response['service_token'] == service_token
    assert response['country_region_id'] == country.geobase_country_id
    assert response['country_iso2'] == country.country_iso2
    assert response['currency'] == country.currency


async def test_pay_info_bad_country(grocery_payments_pay_info):
    await grocery_payments_pay_info(country_iso2='bad', status_code=400)


async def test_sbp_bank_info(
        grocery_payments_pay_info,
        grocery_payments_configs,
        grocery_payments_methods,
):
    banks = [models.SbpBankInfo(bank_name=f'bank_name:{i}') for i in range(5)]
    exp_banks_meta = [bank.to_exp_meta() for bank in banks]

    exp_banks_meta[1]['priority'] = 1
    exp_banks_meta[2]['priority'] = 2
    exp_banks_meta[3]['priority'] = 1
    exp_banks_meta[4]['enabled'] = False

    grocery_payments_methods.set_sbp_banks(banks)
    grocery_payments_configs.set_sbp_banks_meta(exp_banks_meta)

    response = await grocery_payments_pay_info(
        payment_type=models.PaymentType.sbp.value,
    )

    assert response['sbp_banks_info'] == [
        banks[2].to_dict(),
        banks[1].to_dict(),
        banks[3].to_dict(),
        banks[0].to_dict(),
    ]
