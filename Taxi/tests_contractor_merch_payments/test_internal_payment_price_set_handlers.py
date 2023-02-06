import decimal
import enum

import pytest

from tests_contractor_merch_payments import utils

PRICE_LIMIT = '1499.99'


class HandlerTypes(enum.Enum):
    PRICE = 'price'
    ASYNC_PAY = 'async_pay'


HANDLERS = [HandlerTypes.PRICE, HandlerTypes.ASYNC_PAY]


def get_endpoint(taxi_contractor_merch_payments, handler):
    async def _price(**kwarg):
        return await taxi_contractor_merch_payments.put(
            '/internal/contractor-merch-payments/v1/payment/price', **kwarg,
        )

    async def _async_pay(**kwarg):
        return await taxi_contractor_merch_payments.post(
            '/internal/contractor-merch-payments/v1/payment/pay-async',
            **kwarg,
        )

    if handler == HandlerTypes.PRICE:
        return _price
    if handler == HandlerTypes.ASYNC_PAY:
        return _async_pay
    assert False


@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PRICE_LIMIT=PRICE_LIMIT)
@pytest.mark.parametrize(
    'body, payment_id, status',
    [
        pytest.param(
            {
                'merchant_id': 'merchant-id-1',
                'price': '228',
                'currency': 'RUB',
                'integrator': 'payments-bot',
                'metadata': {
                    'telegram_chat_id': 0,
                    'telegram_personal_id': 'telegram-personal-id-0',
                },
            },
            'payment_id-1',
            'merchant_accepted',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-6',
                'seller': {
                    'name': 'Пятёрочка',
                    'address': 'Москва, ул. Пушкина, д. Колотушкина',
                },
                'price': '200',
                'currency': 'RUB',
                'integrator': 'integration-api-mobi',
            },
            'payment_id-6',
            'target_success',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-9',
                'price': '500',
                'currency': 'RUB',
                'integrator': 'payments-bot',
                'metadata': {
                    'telegram_chat_id': 124,
                    'telegram_personal_id': 'telegram-personal-id-10',
                },
            },
            'payment_id-10',
            'merchant_accepted',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-5',
                'price': '111',
                'currency': 'rub',
                'integrator': 'integration-api-mobi',
                'external_id': 'vse_v_artstaila',
            },
            'payment_id-9',
            'merchant_accepted',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-12',
                'price': '400',
                'currency': 'rub',
                'integrator': 'integration-api-universal',
            },
            'payment_id-12',
            'merchant_accepted',
        ),
    ],
)
@pytest.mark.parametrize('handler_types', HANDLERS)
async def test_correct_payment_price_put(
        taxi_contractor_merch_payments,
        mock_merchant_profiles,
        pgsql,
        body,
        payment_id,
        status,
        handler_types,
):
    price = body['price']
    merchant_id = body['merchant_id']
    integrator = body['integrator']

    seller = body.get('seller')
    metadata = body.get('metadata')
    external_id = body.get('external_id')

    response = await get_endpoint(
        taxi_contractor_merch_payments, handler_types,
    )(params={'payment_id': payment_id}, json=body)

    park_id, contractor_id = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['park_id', 'contractor_id'],
    )

    assert response.status == 200
    assert response.json()['contractor'] == {
        'park_id': park_id,
        'contractor_id': contractor_id,
    }

    payment = utils.get_fields_by_payment_id(
        pgsql,
        payment_id,
        [
            'merchant_id',
            'seller',
            'price',
            'integrator',
            'metadata',
            'status',
            'external_id',
        ],
    )

    assert payment == (
        merchant_id,
        utils.to_composite_type(seller, ['name', 'address']),
        decimal.Decimal(price),
        integrator,
        metadata,
        status,
        external_id,
    )


@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PRICE_LIMIT=PRICE_LIMIT)
@pytest.mark.parametrize(
    'body, payment_id, response_code',
    [
        pytest.param(
            {
                'merchant_id': 'merchant-id-100',
                'price': '1000',
                'currency': 'RUB',
                'integrator': 'integration-api-mobi',
            },
            'payment_id-100',
            'payment_not_found',
            id='payment_not_found',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-7',
                'price': '300',
                'currency': 'RUB',
                'integrator': 'payments-bot',
                'metadata': {
                    'telegram_chat_id': 0,
                    'telegram_personal_id': 'telegram-personal-id-0',
                },
            },
            'payment_id-7',
            'payment_expired',
            id='payment_expired',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-2',
                'price': '200',
                'currency': 'RUB',
                'integrator': 'integration-api-mobi',
            },
            'payment_id-2',
            'price_already_set',
            id='price_already_set',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-7',
                'price': '250',
                'currency': 'RUB',
                'integrator': 'integration-api-mobi',
            },
            'payment_id-2',
            'payment_not_found',
            id='payment_not_found-pt2',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-1',
                'price': '100',
                'currency': 'EUR',
                'integrator': 'integration-api-mobi',
            },
            'payment_id-1',
            'unsupported_currency',
            id='unsupported_currency',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-11',
                'price': '100',
                'currency': 'RUB',
                'integrator': 'integration-api-mobi',
            },
            'payment_id-11',
            'merchant_canceled',
            id='merchant_canceled',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-0',
                'price': '100',
                'currency': 'RUB',
                'integrator': 'integration-api-mobi',
                'external_id': 'vse_v_artstaila',
            },
            'payment_id-0',
            'used_payment',
            id='external_id_already_set',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-2',
                'price': '250',
                'currency': 'rub',
                'integrator': 'payments-bot',
                'external_id': 'external_id-2',
            },
            'payment_id-2',
            'used_payment',
            id='payment_started_but_had_no_external_id',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-1',
                'price': '100',
                'currency': 'rub',
                'integrator': 'integration-api-mobi',
                'external_id': 'external_id-0',
            },
            'payment_id-1',
            'used_external_id',
            id='used_external_id',
        ),
    ],
)
@pytest.mark.parametrize('handler_types', HANDLERS)
async def test_incorrect_payment_price_put(
        taxi_contractor_merch_payments,
        mock_merchant_profiles,
        mock_driver_tags,
        load_json,
        body,
        payment_id,
        response_code,
        handler_types,
):
    response = await get_endpoint(
        taxi_contractor_merch_payments, handler_types,
    )(params={'payment_id': payment_id}, json=body)

    expected_response = load_json(f'error_responses/{response_code}.json')

    assert response.status == expected_response['status']
    assert response.json() == expected_response['response']


@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PRICE_LIMIT=PRICE_LIMIT)
@pytest.mark.parametrize(
    'body, payment_id, response_code',
    [
        pytest.param(
            {
                'merchant_id': 'merchant-id-9',
                'price': '2000',
                'currency': 'RUB',
                'integrator': 'payments-bot',
                'metadata': {
                    'telegram_chat_id': 124,
                    'telegram_personal_id': 'telegram-personal-id-10',
                },
            },
            'payment_id-10',
            'price_limit_exceeded',
            id='price_limit_exceeded',
        ),
        pytest.param(
            {
                'merchant_id': 'merchant-id-5',
                'price': '1500',
                'currency': 'rub',
                'integrator': 'integration-api-mobi',
            },
            'payment_id-9',
            'price_limit_exceeded',
            id='price_limit_exceeded',
        ),
    ],
)
@pytest.mark.parametrize('handler_types', HANDLERS)
async def test_incorrect_payment_price_limit_exceeded(
        taxi_contractor_merch_payments,
        mock_merchant_profiles,
        load_json,
        body,
        payment_id,
        response_code,
        handler_types,
):
    response = await get_endpoint(
        taxi_contractor_merch_payments, handler_types,
    )(params={'payment_id': payment_id}, json=body)

    expected_response = load_json(f'error_responses/{response_code}.json')

    assert response.status == expected_response['status']
    assert response.json() == expected_response['response']
