import pytest

from . import consts
from . import headers
from . import models


def _cibus_error_desc(err, desc='Unknown Error'):
    return f'CibusError [{err}] - [{desc}]'


@pytest.fixture(name='fail_callback')
async def _fail_callback(taxi_grocery_cibus):
    async def _do(err='-1', status_code=200, token=consts.DEFAULT_TOKEN):
        response = await taxi_grocery_cibus.post(
            '/cibus/integration/v1/fail',
            params={'token': token, 'err': err},
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


@pytest.mark.parametrize(
    'err_code, db_error_code',
    [
        ('-1', 'unknown_error'),
        ('171', 'token_expired'),
        ('310', 'user_inactive'),
        ('311', 'blacklisted'),
        ('P-12', 'payment_failed'),
        ('P-14', 'bad_time'),
        ('P-15', 'limit_of_deals'),
        ('P-16', 'not_enough_funds'),
        ('P-22', 'not_enough_funds'),
        ('P-17', 'restaurant_not_approved'),
        ('P-37', 'exceed_system_price_limit'),
        ('1234', 'unknown_error'),
        ('P-11', 'unknown_error'),
    ],
)
async def test_request_db(
        grocery_cibus_db, fail_callback, err_code, db_error_code,
):
    payment = models.Payment()
    grocery_cibus_db.insert_payment(payment)

    for _ in range(2):
        await fail_callback(err=err_code)
        result_payment = grocery_cibus_db.load_payment(payment.invoice_id)

        assert result_payment.status == models.PaymentStatus.fail
        assert result_payment.deal_id is None
        assert result_payment.error_code == db_error_code
        assert result_payment.error_desc == _cibus_error_desc(err_code)


async def test_description_from_config(
        grocery_cibus_db, fail_callback, grocery_cibus_configs,
):
    err = 'some-err'
    desc = 'some-desc'
    config_value = {err: desc}
    grocery_cibus_configs.set_cibus_error_descriptions(value=config_value)

    payment = models.Payment()
    grocery_cibus_db.insert_payment(payment)

    await fail_callback(err=err)
    result_payment = grocery_cibus_db.load_payment(payment.invoice_id)

    assert result_payment.error_desc == _cibus_error_desc(err, desc)


async def test_not_found(grocery_cibus_db, fail_callback):
    payment = models.Payment()
    grocery_cibus_db.insert_payment(payment)

    await fail_callback(status_code=404, token='some-another-token')
    result_payment = grocery_cibus_db.load_payment(payment.invoice_id)

    assert result_payment.status == models.PaymentStatus.init
    assert result_payment.deal_id is None
    assert result_payment.error_code is None
    assert result_payment.error_desc is None
