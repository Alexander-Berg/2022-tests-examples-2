import datetime

import pytest

# This files contains only tests specific to async approvement logic.
# Other tests can be found in test_internal_payment_price_set_handlers.py

PAYMENT_ID = 'payment_id-1'

DEFAULT_BODY = {
    'contractor': {'park_id': 'park-id-1', 'contractor_id': 'contractor-id-1'},
    'price': '111',
    'merchant_id': 'merchant-id-5',
    'seller': {
        'name': 'Пятёрочка',
        'address': 'Москва, ул. Пушкина, д. Колотушкина',
    },
    'integrator': 'integration-api-mobi',
    'currency': 'rub',
}


@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PRICE_LIMIT='1499.99')
@pytest.mark.parametrize('metadata', [None, {'asd': 'qwe'}])
async def test_correct_payment_pay_async_post(
        taxi_contractor_merch_payments,
        mock_merchant_profiles,
        stq,
        testpoint,
        metadata,
):

    body = DEFAULT_BODY

    if metadata:
        body = {**DEFAULT_BODY, 'metadata': metadata}

    park_id = DEFAULT_BODY.get('contractor')['park_id']
    contractor_id = DEFAULT_BODY.get('contractor')['contractor_id']

    price = DEFAULT_BODY['price']

    merchant_id = DEFAULT_BODY['merchant_id']
    seller = DEFAULT_BODY.get('seller')

    integrator = DEFAULT_BODY['integrator']
    metadata = body.get('metadata')

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/pay-async',
        params={'payment_id': PAYMENT_ID},
        json=body,
    )

    assert response.status == 200
    assert stq.contractor_merch_payments_payment_process.has_calls

    task = stq.contractor_merch_payments_payment_process.next_call()
    assert task['id'] == f'{park_id}_{contractor_id}_{PAYMENT_ID}'
    assert task['args'] == []

    async_pay_params = {
        'merchant_id': merchant_id,
        'price': price,
        'integrator': integrator,
    }

    if seller:
        async_pay_params['seller'] = seller
    if metadata:
        async_pay_params['metadata'] = metadata

    kwargs_asserts = {
        'payment_id': PAYMENT_ID,
        'park_id': park_id,
        'contractor_id': contractor_id,
        'action_type': 'approve',
        'payment_method': 'async',
        'async_pay_params': async_pay_params,
    }

    task['kwargs'].pop('log_extra')
    assert task['kwargs'] == kwargs_asserts


@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENT_TTL_SEC=200)
@pytest.mark.parametrize(
    'valid,custom_ttl',
    [
        pytest.param(True, None),
        pytest.param(
            False,
            None,
            marks=pytest.mark.now(
                str(datetime.datetime.now() + datetime.timedelta(hours=1)),
            ),
        ),
        pytest.param(
            True,
            40000,
            marks=pytest.mark.now(
                str(datetime.datetime.now() + datetime.timedelta(hours=1)),
            ),
        ),
    ],
)
async def test_custom_payment_ttl(
        taxi_contractor_merch_payments,
        mock_merchant_profiles,
        stq,
        valid,
        custom_ttl,
):
    mock_merchant_profiles.payment_ttl_sec = custom_ttl

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/pay-async',
        params={'payment_id': PAYMENT_ID},
        json=DEFAULT_BODY,
    )
    if not valid:
        assert response.status == 410
    else:
        assert response.status == 200
    assert stq.contractor_merch_payments_payment_process.has_calls == valid
    assert mock_merchant_profiles.merchant.times_called == 1
