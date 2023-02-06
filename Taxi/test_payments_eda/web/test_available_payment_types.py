from payments_eda import consts as service_consts

ALL_TYPES = [
    service_consts.PAYMENT_TYPE_CASH,
    service_consts.PAYMENT_TYPE_CARD,
    service_consts.PAYMENT_TYPE_CORP,
    service_consts.PAYMENT_TYPE_BADGE,
    service_consts.PAYMENT_TYPE_WALLET,
    service_consts.PAYMENT_TYPE_GOOGLE_PAY,
    service_consts.PAYMENT_TYPE_APPLE_PAY,
    service_consts.PAYMENT_TYPE_COOP_ACCOUNT,
    service_consts.PAYMENT_TYPE_CIBUS,
    service_consts.PAYMENT_TYPE_SBP,
    service_consts.PAYMENT_TYPE_SBP_LINK,
    service_consts.PAYMENT_TYPE_SBP_QR,
    service_consts.PAYMENT_TYPE_YANDEX_BANK,
]

SUPPORTED_TYPES = [
    service_consts.PAYMENT_TYPE_CASH,
    service_consts.PAYMENT_TYPE_CARD,
    service_consts.PAYMENT_TYPE_CORP,
    service_consts.PAYMENT_TYPE_BADGE,
    service_consts.PAYMENT_TYPE_WALLET,
    service_consts.PAYMENT_TYPE_GOOGLE_PAY,
    service_consts.PAYMENT_TYPE_APPLE_PAY,
]


async def test_available_payment_types(web_app_client, mock_payment_methods):
    service = service_consts.SERVICE_EATS
    merchant = 'merchant1'
    user_agent = 'user_agent'
    request_json = {'location': [55, 37]}

    @mock_payment_methods('/v1/superapp-available-payment-types')
    async def _available_payment_types(request):
        return {'payment_types': ALL_TYPES, 'merchant_ids': [merchant]}

    response = await web_app_client.post(
        f'/v1/available-payment-types?service={service}',
        json=request_json,
        headers={'User-Agent': user_agent},
    )

    assert response.status == 200
    response_json = await response.json()

    response_payment_types = response_json['payment_types']

    assert response_json['merchant_ids'] == [merchant]
    assert len(response_payment_types) == len(SUPPORTED_TYPES)
    assert all(
        [
            payment_type in SUPPORTED_TYPES
            for payment_type in response_payment_types
        ],
    )

    assert _available_payment_types.times_called == 1

    request = _available_payment_types.next_call()['request']

    assert request.args['service'] == service
    assert request.headers['User-Agent'] == user_agent
    assert request.json == request_json
